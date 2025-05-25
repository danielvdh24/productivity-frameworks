import pandas as pd
from scipy.stats import zscore

# Load
df = pd.read_excel("final_table.xlsx")

# Clean Author column
df["author_clean"] = df["author"].astype(str).str.strip().str.lower()

# Remove non-author rows
valid_rows = (
    df["author_clean"].notna() &
    ~df["author_clean"].str.isnumeric() &
    ~df["author_clean"].isin(["nan"])
)
df = df[valid_rows].copy().reset_index(drop=True)

# Normalize column names
df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

# Extract numeric values safely
def safe_numeric(col):
    return pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0)

df["commits"] = safe_numeric("commits")
df["code_reviews"] = safe_numeric("comments_written")
df["gitlab_actions"] = safe_numeric("gitlab_actions")
df["issues_assigned"] = safe_numeric("issues_assigned")
df["merge_requests_assigned"] = safe_numeric("merge_requests_assigned")
df["task_completion"] = df["issues_assigned"] + df["merge_requests_assigned"]

# Self-assessment input
print("Enter productivity and satisfaction scores (1–5) for each author (format: P S):")
self_rated_performance = {}
self_rated_satisfaction = {}

for author in df["author"]:
    while True:
        try:
            entry = input(f"{author}: ").strip()
            p, s = map(int, entry.split())
            if not (1 <= p <= 5 and 1 <= s <= 5):
                raise ValueError
            self_rated_performance[author] = p * 20  # Convert to 100 scale
            self_rated_satisfaction[author] = s * 20
            break
        except:
            print("Wrong format. Use '4 3' format.")

df["performance_rating"] = df["author"].map(self_rated_performance)
df["satisfaction_rating"] = df["author"].map(self_rated_satisfaction)

# Z-score normalization with fallback
def safe_zscore(series):
    if series.nunique() <= 1:
        return pd.Series([50] * len(series), index=series.index)
    return zscore(series, nan_policy='omit') * 10 + 50

# Scale to 0–1 range
def to_zero_one(series):
    series = pd.Series(series)
    return ((series - series.min()) / (series.max() - series.min())).fillna(0)

# SPACE metric z-scores
z_gitlab = safe_zscore(df["gitlab_actions"])
z_task = safe_zscore(df["task_completion"])
z_perf = safe_zscore(df["performance_rating"])
z_commits = safe_zscore(df["commits"])
z_reviews = safe_zscore(df["code_reviews"])

# Combine and scale to 0–1
df["P_score"] = to_zero_one(0.4 * z_gitlab + 0.4 * z_task + 0.2 * z_perf)
df["A_score"] = to_zero_one(z_commits)
df["C_score"] = to_zero_one(z_reviews)

# Final score (keep satisfaction in full scale, normalize rest)
df["S_score"] = df["satisfaction_rating"] / 100
df["final_score"] = (
    df["S_score"] * 0.2 +
    df["P_score"] * 0.3 +
    df["A_score"] * 0.3 +
    df["C_score"] * 0.2
)

# Rank contributors
df["rank"] = df["final_score"].rank(method="min", ascending=False).astype(int)
df_sorted = df.sort_values("rank")

# Identify inactive contributors
inactive_users = df_sorted[
    (df_sorted["commits"] + df_sorted["task_completion"]) == 0
]["author"].tolist()

# Check for identical scores
if df_sorted["final_score"].nunique() <= 1:
    print("Note: All contributors have the same final score — low or uniform activity may have affected ranking validity.")

# Format SPACE table
space_table = (
    df_sorted[["rank", "author", "S_score", "P_score", "A_score", "C_score", "final_score"]]
    .to_string(index=False)
)

# Define dynamic table border width
line_width = max(len(line) for line in space_table.splitlines())
print("-" * line_width)

# Print activity summary
print("Activity Summary (non-zero counts):")
print(f"- Commits:               {df['commits'].astype(bool).sum()} / {len(df)}")
print(f"- Task Completion:       {df['task_completion'].astype(bool).sum()} / {len(df)}")
print(f"- GitLab Actions:        {df['gitlab_actions'].astype(bool).sum()} / {len(df)}")
print(f"- Comments (Reviews):    {df['code_reviews'].astype(bool).sum()} / {len(df)}")

if inactive_users:
    print(f"- Inactive Contributors: {', '.join(inactive_users)}")
else:
    print("- Inactive Contributors: None")

print("-" * line_width)
print(space_table)
print("-" * line_width)
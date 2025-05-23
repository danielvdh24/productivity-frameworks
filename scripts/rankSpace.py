import pandas as pd

# Load
df = pd.read_excel("final_table.xlsx")

# Clean Author column
df["Author_clean"] = df["Author"].astype(str).str.strip().str.lower()

# Remove non-author rows
valid_rows = (
    ~df["Author_clean"].isin(["metric", "value", "total lines of code", "nan"]) &
    df["Author_clean"].notna() &
    ~df["Author_clean"].str.isnumeric()
)
df = df[valid_rows].copy()

# Filter column names
df = df.reset_index(drop=True)
df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

# Commit count from "Commits (%)"
df["commits"] = df["commits_(%)"].str.extract(r"(\d+)").astype(float)

# Convert numeric
def safe_numeric(col):
    return pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0)

df["code_reviews"] = safe_numeric("comments_written")
df["gitlab_actions"] = safe_numeric("gitlab_actions")
df["issues_assigned"] = safe_numeric("issues_assigned")
df["merge_requests_assigned"] = safe_numeric("merge_requests_assigned")
df["task_completion"] = df["issues_assigned"] + df["merge_requests_assigned"]

# Manual input for self-rated productivity and satisfaction
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
            self_rated_performance[author] = p * 20
            self_rated_satisfaction[author] = s * 20
            break
        except:
            print("Wrong format. Its '4 3')")

df["performance_rating"] = df["author"].map(self_rated_performance)
df["satisfaction_rating"] = df["author"].map(self_rated_satisfaction)

# Normalize helper functioin
def normalize(series):
    max_val = series.max()
    normalized = (series / max_val * 100).fillna(0) if max_val > 0 else 0
    return normalized.clip(upper=99.9)

# Compute SPACE
df["P_score"] = (
    0.4 * normalize(df["gitlab_actions"]) +
    0.4 * normalize(df["task_completion"]) +
    0.2 * normalize(df["performance_rating"])
)

df["A_score"] = normalize(df["commits"])
df["C_score"] = normalize(df["code_reviews"])

# Final SPACE score and rank
df["final_score"] = (
    df["satisfaction_rating"] * 0.2 +
    df["P_score"] * 0.3 +
    df["A_score"] * 0.3 +
    df["C_score"] * 0.2
)
df["rank"] = df["final_score"].rank(method="min", ascending=False).astype(int)

# Print
df_sorted = df.sort_values("rank")
print("--------------------------------------------------------------------------------")
print(
    df_sorted[["rank", "author", "task_completion", "satisfaction_rating", "P_score", "A_score", "C_score", "final_score"]]
    .rename(columns={"satisfaction_rating": "S_score"})
    .to_string(index=False)
)
print("--------------------------------------------------------------------------------")

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Load
df = pd.read_excel("final_table.xlsx")

# Clean Author column
df["author_clean"] = df["author"].astype(str).str.strip().str.lower()

# Remove non-author rows
valid_rows = (
    df["author_clean"].notna() &
    ~df["author_clean"].isin(["nan"]) &
    ~df["author_clean"].str.isnumeric()
)
df = df[valid_rows].copy()

# Normalize column names
df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

# Extract numeric values safely
df["commits"] = pd.to_numeric(df["commits"], errors="coerce").fillna(0)
df["lines"] = pd.to_numeric(df["lines_added"], errors="coerce").fillna(0)
df["reviews"] = pd.to_numeric(df["comments_written"], errors="coerce").fillna(0)

# Normalize using Min-Max Scaling
scaler = MinMaxScaler()
normalized = scaler.fit_transform(df[["commits", "lines", "reviews"]])
df[["norm_commits", "norm_lines", "norm_reviews"]] = normalized

# Compute final Baidu-style weighted score
df["final_score"] = (
    df["norm_commits"] * 0.4 +
    df["norm_lines"] * 0.4 +
    df["norm_reviews"] * 0.2
)

# Rank based on final score
df = df.sort_values(by="final_score", ascending=False).reset_index(drop=True)
df["rank"] = df.index + 1

# Display results
result = df[["rank", "author", "norm_commits", "norm_lines", "norm_reviews", "final_score"]]

# Format Baidu table
baidu_table = result.to_string(index=False)

# Define dynamic table border width
line_width = max(len(line) for line in baidu_table.splitlines())
print("-" * line_width)
print(baidu_table)
print("-" * line_width)
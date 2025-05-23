import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Load
df = pd.read_excel("final_table.xlsx")

# Clean Author column
df["author_clean"] = df["Author"].astype(str).str.strip().str.lower()

# Filter valid authors (exclude summary rows and empty rows)
valid_rows = (
    ~df["author_clean"].isin(["metric", "value", "total lines of code", "nan"]) &
    df["author_clean"].notna() &
    ~df["author_clean"].str.isnumeric()
)
df = df[valid_rows].copy()

# Normalize names
df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

# Extract numerioc values
df["commits"] = df["commits_(%)"].astype(str).str.extract(r"(\d+)").astype(float)
df["lines"] = pd.to_numeric(df["+_lines"], errors="coerce").fillna(0)
df["reviews"] = pd.to_numeric(df["comments_written"], errors="coerce").fillna(0)

# Normalize with Min-Max
scaler = MinMaxScaler()
normalized = scaler.fit_transform(df[["commits", "lines", "reviews"]])
df[["norm_commits", "norm_lines", "norm_reviews"]] = normalized

# Compute final score
df["final_score"] = (
    df["norm_commits"] * 0.4 +
    df["norm_lines"] * 0.4 +
    df["norm_reviews"] * 0.2
)

# Sort and assign rank
df = df.sort_values(by="final_score", ascending=False).reset_index(drop=True)
df["rank"] = df.index + 1

# Print
result = df[["rank", "author", "norm_commits", "norm_lines", "norm_reviews", "final_score"]]
print("--------------------------------------------------------------------------------")
print(result.to_string(index=False))
print("--------------------------------------------------------------------------------")

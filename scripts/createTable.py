import pandas as pd
from collections import defaultdict

# Load CSVs
comments_df = pd.read_csv("all_comments.csv")
issues_df = pd.read_csv("cleaned_issues.csv")
mr_df = pd.read_csv("cleaned_merge_requests.csv")

# Create table structure
final_stats = defaultdict(lambda: {
    "gitlab_actions": 0,
    "comments_written": 0,
    "issues_assigned": 0,
    "merge_requests_assigned": 0
})

# List of system note prefixes - which are not considered as comments
system_note_prefixes = [
    "changed due date", "assigned to", "removed due date", "changed the description",
    "marked the checklist item", "changed title from", "mentioned in commit",
    "mentioned in merge request", "marked this issue", "unassigned",
    "requested review", "added 1 commit", "made the issue confidential",
    "made the issue visible to everyone", "approved this merge request", "created branch"
]

# Process comments
for _, row in comments_df.iterrows():
    author = row["author_username"]
    comment = str(row["comment"]).lower()
    if any(comment.startswith(prefix) for prefix in system_note_prefixes):
        final_stats[author]["gitlab_actions"] += 1
    else:
        final_stats[author]["comments_written"] += 1

# Process issues
for _, row in issues_df.iterrows():
    assignee = row.get("assigned_username")
    if pd.notna(assignee):
        final_stats[assignee]["issues_assigned"] += 1

# Process merge requests
for _, row in mr_df.iterrows():
    assignees_field = str(row.get("assignees", ""))
    matched = False
    for author in final_stats.keys():
        if assignees_field.startswith(author):
            final_stats[author]["merge_requests_assigned"] += 1
            matched = True
            break
    if not matched:
        fallback_author = row.get("author_username")
        if pd.notna(fallback_author):
            final_stats[fallback_author]["merge_requests_assigned"] += 1

# Convert to DataFrame
final_df = pd.DataFrame([
    {"author_username": author, **stats}
    for author, stats in final_stats.items()
])

# Sort by author
final_df.sort_values(by="author_username", inplace=True)

# Export table
excel_path = "contribution_table.xlsx"
final_df.to_excel(excel_path, index=False)

print("Files saved:")
print("- contributions_table.xlsx")

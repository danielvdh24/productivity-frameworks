import pandas as pd
import json
from datetime import datetime, timedelta
from collections import defaultdict
import re

# Survey date
survey_input = input("Enter survey date (YYYY-MM-DD): ")
try:
    survey_day = datetime.strptime(survey_input, "%Y-%m-%d")
except ValueError:
    raise ValueError("Invalid date format. Use YYYY-MM-DD.")

start_date = survey_day - timedelta(days=15)
end_date = survey_day  # up to but not including survey day

print(f"Collecting data from {start_date.date()} to {end_date.date() - timedelta(days=1)}")

# Load NDJSON files into DataFrames
def load_ndjson(path):
    with open(path, 'r', encoding='utf-8') as f:
        return pd.DataFrame([json.loads(line) for line in f])

# File paths
issues_path = "issues.ndjson"
merge_requests_path = "merge_requests.ndjson"
members_path = "project_members.ndjson"

# Load data
issues_df_raw = load_ndjson(issues_path)
mr_df_raw = load_ndjson(merge_requests_path)
members_df = load_ndjson(members_path)

# Remove any emojis
def clean_username(username):
    try:
        return re.sub(r'[\U00010000-\U0010ffff]', '', username)
    except:
        return username

# Build author_id to username mapping
id_to_username = {
    row['user_id']: clean_username(row['user']['username'])
    for _, row in members_df.iterrows()
    if 'user' in row and 'username' in row['user']
}

# Convert timezone format dates to readable dates
def format_date(date_str):
    try:
        return datetime.strptime(date_str[:10], "%Y-%m-%d").strftime("%B %d, %Y")
    except:
        return None

# Parse ISO timestamp from the data and check if in range
def is_in_range(iso_str):
    try:
        if "." in iso_str:
            dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%SZ")
        return start_date <= dt < end_date
    except Exception:
        return False

# Extract comments/notes from merge requests and issues within date range
def extract_notes_from(df, type_name):
    rows = []
    for _, row in df.iterrows():
        try:
            notes = json.loads(row['notes']) if isinstance(row['notes'], str) else row['notes']
        except Exception:
            notes = []
        if isinstance(notes, list):
            for note in notes:
                created_at = note.get('created_at')
                if isinstance(note, dict) and created_at and is_in_range(created_at):
                    rows.append({
                        'type': type_name,
                        'title': row.get('title', ''),
                        'created': format_date(created_at),
                        'author_username': id_to_username.get(note.get('author_id'), 'Unknown'),
                        'comment': note.get('note', '')
                    })
    return rows

comments_df = pd.DataFrame(
    extract_notes_from(issues_df_raw, 'Issue') + extract_notes_from(mr_df_raw, 'Merge Request')
)

# Filter issues and merge requests by created_at
issues_df = issues_df_raw[issues_df_raw['created_at'].apply(lambda x: is_in_range(x) if isinstance(x, str) else False)].copy()
mr_df = mr_df_raw[mr_df_raw['created_at'].apply(lambda x: is_in_range(x) if isinstance(x, str) else False)].copy()

# Add author_username to issues and merge requests
issues_df['author_username'] = issues_df['author_id'].map(id_to_username)
mr_df['author_username'] = mr_df['author_id'].map(id_to_username)

# Replace *_by_id fields in issues and reformat dates
by_id_mappings = [
    ('updated_by_id', 'updated_by_username'),
    ('last_edited_by_id', 'last_edited_username'),
    ('closed_by_id', 'closed_by_username')
]
for old_col, new_col in by_id_mappings:
    if old_col in issues_df.columns:
        issues_df[new_col] = issues_df[old_col].apply(lambda x: id_to_username.get(int(x), 'Unknown') if pd.notna(x) else None)
        issues_df.drop(columns=[old_col], inplace=True)

# Process issue_assignees to assigned_username
issues_df['assigned_username'] = issues_df['issue_assignees'].apply(
    lambda assignees: id_to_username.get(assignees[0]['user_id'], 'Unknown') if isinstance(assignees, list) and assignees else None
)
issues_df.drop(columns=['issue_assignees'], inplace=True, errors='ignore')

# Reorder columns in issues
cols = list(issues_df.columns)
reorder_cols = ['author_username', 'assigned_username'] + [new for _, new in by_id_mappings]
for col in reorder_cols:
    if col in cols:
        cols.insert(1 if col == 'author_username' else 2, cols.pop(cols.index(col)))
issues_df = issues_df[cols]

for col in ['created_at', 'updated_at', 'last_edited_at', 'closed_at']:
    if col in issues_df.columns:
        issues_df[col] = issues_df[col].apply(format_date)

# Format milestone in issues
def format_milestone(m):
    if isinstance(m, dict):
        parts = []
        if m.get('title'): parts.append(f"Title: {m['title']}")
        if m.get('description'): parts.append(f"Description: {m['description']}")
        if m.get('start_date'): parts.append(f"Start: {format_date(m['start_date'])}")
        if m.get('due_date'): parts.append(f"Due: {format_date(m['due_date'])}")
        return " | ".join(parts)
    return None
if 'milestone' in issues_df.columns:
    issues_df['milestone'] = issues_df['milestone'].apply(format_milestone)

# Format notes in issues
def extract_note_text(notes):
    if isinstance(notes, list):
        return "\n---\n".join(
            [f"{n.get('note', '').strip()}\n(by {n.get('author', {}).get('name', 'Unknown')} on {format_date(n.get('created_at', '') or '')})"
             for n in notes if isinstance(n, dict)]
        )
    return None
issues_df['notes'] = issues_df['notes'].apply(extract_note_text)

# Format merge requests
for col in ['created_at', 'updated_at']:
    if col in mr_df.columns:
        mr_df[col] = mr_df[col].apply(format_date)

if 'approvals' in mr_df.columns:
    def format_approvals(ap):
        if isinstance(ap, list):
            return "; ".join([f"{id_to_username.get(i.get('user_id'), 'Unknown')} on {format_date(i.get('created_at'))}" for i in ap if isinstance(i, dict)])
        return None
    mr_df['approvals'] = mr_df['approvals'].apply(format_approvals)

for field, new_name in [('merge_request_assignees', 'assignees'), ('merge_request_reviewers', 'reviewers')]:
    if field in mr_df.columns:
        def extract_users(entries):
            return "; ".join([
                f"{id_to_username.get(e['user_id'], 'Unknown')} on {format_date(e.get('created_at'))}" for e in entries if isinstance(e, dict)
            ]) if isinstance(entries, list) else None
        mr_df[new_name] = mr_df[field].apply(extract_users)
        mr_df.drop(columns=[field], inplace=True)

mr_cols = list(mr_df.columns)
author_idx = mr_cols.index('author_id') if 'author_id' in mr_cols else 1
for col in ['author_username', 'assignees', 'reviewers']:
    if col in mr_cols:
        mr_cols.insert(author_idx + 1, mr_cols.pop(mr_cols.index(col)))
        author_idx += 1
mr_df = mr_df[mr_cols]

if 'notes' in mr_df.columns:
    mr_df['notes'] = mr_df['notes'].apply(extract_note_text)
if 'milestone' in mr_df.columns:
    mr_df['milestone'] = mr_df['milestone'].apply(format_milestone)
if 'events' in mr_df.columns:
    def format_events(events):
        if isinstance(events, list):
            return "; ".join([
                f"{id_to_username.get(e.get('author_id'), 'Unknown')} {e.get('action')} on {format_date(e.get('created_at'))}"
                for e in events if isinstance(e, dict)
            ])
        return None
    mr_df['events'] = mr_df['events'].apply(format_events)

# Save cleaned data to CSV files
issues_df.to_csv("cleaned_issues.csv", index=False)
mr_df.to_csv("cleaned_merge_requests.csv", index=False)
comments_df.to_csv("all_comments.csv", index=False)

# Load comments, issues, and merge requests for final statistics
comments_df = pd.read_csv("all_comments.csv")
issues_df = pd.read_csv("cleaned_issues.csv")
mr_df = pd.read_csv("cleaned_merge_requests.csv")

final_stats = defaultdict(lambda: {
    "gitlab_actions": 0,
    "comments_written": 0,
    "issues_assigned": 0,
    "merge_requests_assigned": 0
})

# Mark as an interface (gitlab_actions) action
system_note_prefixes = [
    "changed due date", "assigned to", "removed due date", "changed the description",
    "marked the checklist item", "changed title from", "mentioned in commit",
    "mentioned in merge request", "marked this issue", "unassigned",
    "requested review", "added 1 commit", "made the issue confidential",
    "made the issue visible to everyone", "approved this merge request", "created branch"
]

# Process comments, issues, and merge requests of each author
for _, row in comments_df.iterrows():
    author = row["author_username"]
    comment = str(row["comment"]).lower()
    if any(comment.startswith(prefix) for prefix in system_note_prefixes):
        final_stats[author]["gitlab_actions"] += 1
    else:
        final_stats[author]["comments_written"] += 1

for _, row in issues_df.iterrows():
    assignee = row.get("assigned_username")
    if pd.notna(assignee):
        final_stats[assignee]["issues_assigned"] += 1

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

final_df = pd.DataFrame([
    {"author_username": author, **stats}
    for author, stats in final_stats.items()
])

# Generate contribution table
final_df.sort_values(by="author_username", inplace=True)
final_df.to_excel("interface_contributions.xlsx", index=False)

print("Files saved:")
print("- cleaned_issues.csv")
print("- cleaned_merge_requests.csv")
print("- all_comments.csv")
print("- interface_contributions.xlsx")
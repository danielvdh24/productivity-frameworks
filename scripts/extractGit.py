import subprocess
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict

# Prompt for survey date
survey_input = input("Enter survey date (YYYY-MM-DD): ")
try:
    survey_day = datetime.strptime(survey_input, "%Y-%m-%d")
except ValueError:
    raise ValueError("Invalid date format. Use YYYY-MM-DD.")

start_date = survey_day - timedelta(days=15)
end_date = survey_day  # up to but not including the survey day

print(f"Collecting commits from {start_date.date()} to {end_date.date() - timedelta(days=1)}")

# Check if inside a Git repository
try:
    subprocess.check_output(["git", "rev-parse", "--is-inside-work-tree"], stderr=subprocess.DEVNULL)
except subprocess.CalledProcessError:
    print("Error: This script must be run inside a Git repository.")
    exit(1)

# Format date range for git log command
git_since = start_date.strftime("%Y-%m-%d")
git_until = (end_date - timedelta(seconds=1)).strftime("%Y-%m-%d")

# Get git log with commit stats
cmd = [
    "git", "log",
    f"--since={git_since}",
    f"--until={git_until}",
    "--pretty=format:%an",
    "--numstat"
]

try:
    output = subprocess.check_output(cmd, universal_newlines=True)
except subprocess.CalledProcessError as e:
    print("Error running git log:", e)
    exit(1)

# Parse log output
stats = defaultdict(lambda: {"commits": 0, "lines_added": 0})

current_author = None
for line in output.splitlines():
    if line.strip() == "":
        continue
    if "\t" not in line and not line[0].isdigit():
        current_author = line.strip()
        stats[current_author]["commits"] += 1
    elif "\t" in line and current_author:
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0].isdigit():
            stats[current_author]["lines_added"] += int(parts[0])

# Create and save Excel file
df = pd.DataFrame([
    {"author": author, "commits": data["commits"], "lines_added": data["lines_added"]}
    for author, data in stats.items()
])

df.sort_values(by="author", inplace=True)
df.to_excel("git_contributions.xlsx", index=False)

print("File saved:")
print("- git_contributions.xlsx")
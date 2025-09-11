import json, os, re

evt = json.load(open(os.environ["GITHUB_EVENT_PATH"]))
title = evt["issue"]["title"]
body = evt["issue"]["body"] or ""

# Parse title: "Submission: <team> - <version>"
m = re.match(r"^Submission:\s*(.+?)\s*-\s*(.+)\s*$", title)
team, version = (
    (m.group(1).strip(), m.group(2).strip()) if m else ("UNKNOWN", "UNKNOWN")
)

print(team, version)
# Grab the first attachment/CSV-like link from the issue body
urls = re.findall(r"\((https?://[^\s)]+)\)", body)
# Keep GitHub asset links or anything ending with .csv
urls = [u for u in urls if ("/assets/" in u) or u.lower().endswith(".csv")]
print(urls)

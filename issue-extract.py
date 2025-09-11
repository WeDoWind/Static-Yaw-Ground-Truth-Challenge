import json, os, re

evt = json.load(open(os.environ["GITHUB_EVENT_PATH"]))
title = evt["issue"]["title"]
body = evt["issue"]["body"] or ""

# Parse title: "Submission: <team> - <version>"
m = re.match(r"^Submission:\s*(.+?)\s*-\s*(.+)\s*$", title)
team, version = (
    (m.group(1).strip(), m.group(2).strip()) if m else ("UNKNOWN", "UNKNOWN")
)

# Grab the first attachment/CSV-like link from the issue body
urls = re.findall(r"\((https?://[^\s)]+)\)", body)
# Keep GitHub asset links or anything ending with .csv
urls = [u for u in urls if ("/assets/" in u) or u.lower().endswith(".csv")]

payload = {
    "issue_number": evt["issue"]["number"],
    "issue_repo": evt["repository"]["full_name"],
    "team": team,
    "version": version,
    "attachment_urls": urls[0],  # first file only; keep it simple
    "issue_html_url": evt["issue"]["html_url"],
    "sender": evt["sender"]["login"],
}
print(json.dumps(payload, indent=2))


with open("payload.json", "w") as f:
    json.dump(payload, f)

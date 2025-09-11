import json, os, re

evt = json.load(open(os.environ["GITHUB_EVENT_PATH"]))
title = evt["issue"]["title"]
content = evt["issue"]["body"] or ""


def find_label(label: str) -> str:
    m = re.search(rf"^###\s*{re.escape(label)}\s*\r?\n+([^\n\r]+)", content, re.M)
    return m.group(1).strip() if m else "UNKNOWN"


team = find_label("Team name")
version = find_label("Submission version / tag")

# Grab the first attachment/CSV-like link from the issue body
urls = re.findall(r"\((https?://[^\s)]+)\)", content)
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

with open("payload.json", "w") as f:
    json.dump(payload, f)

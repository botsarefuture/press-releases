import json
from html import escape, unescape

def load_json_with_escape(filename):
    try:
        with open(filename) as f:
            data = json.load(f)
    except json.JSONDecodeError:
        # If JSON decoding error occurs, load data as string and escape HTML
        with open(filename) as f:
            raw_data = f.read()
        data = []
        lines = raw_data.splitlines()
        i = 0
        while i < len(lines):
            try:
                release = json.loads(lines[i])
                data.append(release)
                i += 1
            except json.JSONDecodeError:
                # If line cannot be decoded as JSON, escape HTML content
                content = ""
                while i < len(lines) and not lines[i].strip().startswith("{"):
                    content += lines[i].strip()
                    i += 1
                data.append({"content": escape(content), "title": "Error: Invalid JSON"})
    return data


def load_releases() -> dict:
    try:
        with open("releases.json", "r") as f:
            releases = json.load(f)
        
        # Unescape HTML content
        for release in releases:
            if "content" in release:
                release["content"] = unescape(release["content"])
        
        return releases
    except Exception:
        return load_json_with_escape("releases.json")

def save_releases(releases: dict):

    with open("releases.json", "w") as f:
        json.dump(releases, f)  # Do not escape when saving
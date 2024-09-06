import json
from html import escape, unescape
from typing import List, Dict, Union, Optional


def load_json_with_escape(filename: str) -> List[Dict[str, Union[str, dict]]]:
    """
    Load JSON data from a file. If JSON decoding fails, escape HTML content.

    :param filename: The name of the file to load data from.
    :return: A list of dictionaries containing the JSON data or escaped HTML content.
    """
    data = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            raw_data = f.read()
            lines = raw_data.splitlines()
            i = 0
            while i < len(lines):
                try:
                    # Try to parse the line as JSON
                    release = json.loads(lines[i])
                    data.append(release)
                    i += 1
                except json.JSONDecodeError:
                    # If JSON parsing fails, escape HTML content
                    content = ""
                    while i < len(lines) and not lines[i].strip().startswith("{"):
                        content += lines[i].strip() + "\n"
                        i += 1
                    data.append(
                        {"content": escape(content), "title": "Error: Invalid JSON"}
                    )
    except IOError as e:
        print(f"Error reading file {filename}: {e}")

    return data


def load_releases() -> List[Dict[str, Union[str, dict]]]:
    """
    Load and unescape releases data from a JSON file.

    :return: A list of dictionaries containing the releases data.
    """
    try:
        with open("releases.json", "r", encoding="utf-8") as f:
            releases = json.load(f)
            # Unescape HTML content if present
            for release in releases:
                if "content" in release:
                    release["content"] = unescape(release["content"])
            return releases
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading releases: {e}")
        return load_json_with_escape("releases.json")


def save_releases(releases: List[Dict[str, Union[str, dict]]]) -> None:
    """
    Save releases data to a JSON file.

    :param releases: A list of dictionaries containing the releases data.
    """
    try:
        with open("releases.json", "w", encoding="utf-8") as f:
            json.dump(releases, f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Error saving releases to file: {e}")

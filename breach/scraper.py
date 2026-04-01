import requests
import random
import re
from bs4 import BeautifulSoup, NavigableString

BASE_URL = "https://scp-wiki.wikidot.com/scp-{}"
HEADERS = {
    "User-Agent": "breach-cli/1.0 (https://github.com/matheusc457/breach)"
}

# Clearance level required per object class
CLASS_CLEARANCE = {
    "safe":        1,
    "euclid":      2,
    "keter":       3,
    "thaumiel":    4,
    "apollyon":    5,
    "archon":      4,
    "neutralized": 1,
    "pending":     1,
    "explained":   1,
}

WARNING_CLASSES = {"keter", "apollyon", "archon"}


def _extract_sections(content) -> dict:
    """Extract Item, Object Class, Containment, and Description from page content."""
    sections = {
        "item":        None,
        "object_class": None,
        "containment": None,
        "description": None,
    }

    # Collect all text blocks with their bold labels
    current_label = None
    current_text = []

    for elem in content.descendants:
        if elem.name == "strong":
            # Save previous section
            if current_label and current_text:
                text = " ".join(current_text).strip()
                _assign_section(sections, current_label, text)
            current_label = elem.get_text(strip=True).rstrip(":")
            current_text = []
        elif current_label and isinstance(elem, NavigableString):
            chunk = str(elem).strip()
            if chunk:
                current_text.append(chunk)

    # Save last section
    if current_label and current_text:
        text = " ".join(current_text).strip()
        _assign_section(sections, current_label, text)

    return sections


def _assign_section(sections: dict, label: str, text: str):
    label_lower = label.lower()
    if "item" in label_lower:
        sections["item"] = text
    elif "object class" in label_lower:
        sections["object_class"] = text.strip()
    elif "containment" in label_lower:
        sections["containment"] = text
    elif "description" in label_lower:
        sections["description"] = text


def _get_tags(soup: BeautifulSoup) -> list[str]:
    tags_div = soup.find("div", class_="page-tags")
    if not tags_div:
        return []
    return [a.get_text(strip=True) for a in tags_div.find_all("a")]


def fetch_scp(number: int) -> dict | None:
    """Fetch and parse a single SCP entry. Returns None if not found."""
    url = BASE_URL.format(f"{number:03d}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=12)
        if resp.status_code != 200:
            return None

        soup = BeautifulSoup(resp.text, "html.parser")

        # 404 detection — wiki returns 200 with an error message
        if soup.find("div", id="404-message") or "does not exist" in resp.text.lower():
            return None

        content = soup.find("div", id="page-content")
        if not content:
            return None

        title_elem = soup.find("div", id="page-title")
        title = title_elem.get_text(strip=True) if title_elem else f"SCP-{number:03d}"

        sections = _extract_sections(content)
        tags = _get_tags(soup)

        obj_class = (sections["object_class"] or "Unknown").strip()
        obj_class_lower = obj_class.lower()

        return {
            "number":       number,
            "number_str":   f"{number:03d}",
            "title":        title,
            "url":          url,
            "object_class": obj_class,
            "containment":  sections["containment"],
            "description":  sections["description"],
            "tags":         tags,
            "clearance_required": CLASS_CLEARANCE.get(obj_class_lower, 3),
            "is_warning":   obj_class_lower in WARNING_CLASSES,
        }

    except requests.RequestException:
        return None


def fetch_random(object_class: str | None = None) -> dict | None:
    """Fetch a random SCP, optionally filtered by object class."""
    attempts = 0

    while attempts < 15:
        number = random.randint(1, 6999)
        data = fetch_scp(number)
        if data is None:
            attempts += 1
            continue
        if object_class:
            if data["object_class"].lower() == object_class.lower():
                return data
            attempts += 1
            continue
        return data

    return None


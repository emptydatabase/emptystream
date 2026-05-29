CATEGORY_GROUPS: dict[str, dict[str, str]] = {
    "Anime": {
        "1_0": "All Anime",
        "1_1": "AMV",
        "1_2": "English-translated",
        "1_3": "Non-English-translated",
        "1_4": "Raw",
    },
    "Audio": {
        "2_0": "All Audio",
        "2_1": "Lossless",
        "2_2": "Lossy",
    },
    "Literature": {
        "3_0": "All Literature",
        "3_1": "English-translated",
        "3_2": "Non-English-translated",
        "3_3": "Raw",
    },
    "Live Action": {
        "4_0": "All Live Action",
        "4_1": "English-translated",
        "4_2": "Non-English-translated",
        "4_3": "Raw",
    },
    "Pictures": {
        "5_0": "All Pictures",
        "5_1": "Photos",
        "5_2": "Graphics",
    },
    "Software": {
        "6_0": "All Software",
        "6_1": "Applications",
        "6_2": "Games",
    },
}

SORT_OPTIONS: dict[str, str] = {
    "seeders": "Seeders",
    "size": "Size",
    "date": "Date",
    "downloads": "Downloads",
}

CATEGORY_LABELS: dict[str, str] = {}
for items in CATEGORY_GROUPS.values():
    for value, label in items.items():
        CATEGORY_LABELS[value] = label

CATEGORY_ICONS: dict[str, str] = {
    "1": "cat-1.svg",
    "2": "cat-2.svg",
    "3": "cat-3.svg",
    "4": "cat-4.svg",
    "5": "cat-5.svg",
    "6": "cat-6.svg",
}

import re
import xml.etree.ElementTree as ET
from datetime import datetime

import urllib.error
import urllib.parse
import urllib.request

_NS = "https://nyaa.si/xmlns/nyaa"
_SORT_MAP = {"seeders": "seeders", "size": "size", "date": "id", "downloads": "downloads"}


def _parse_size(raw: str) -> str:
    try:
        size = int(raw)
    except (ValueError, TypeError):
        return ""
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if size < 1024:
            return f"{size:.0f} {unit}"
        size /= 1024
    return f"{size:.0f} PiB"


def _parse_date(raw: str) -> str:
    try:
        return datetime.strptime(raw, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return ""


def nyaa_search_videos(query: str, category: str, sort: str) -> list[dict]:
    s = _SORT_MAP.get(sort, "seeders")
    url = (
        f"https://nyaa.si/?page=rss"
        f"&q={urllib.parse.quote(query)}"
        f"&c={category}&s={s}&o=desc"
    )
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            tree = ET.parse(resp)
    except (urllib.error.HTTPError, urllib.error.URLError, ET.ParseError, OSError):
        return []

    results = []
    for item in tree.findall(".//item"):
        link = item.findtext("link", "")
        tid_match = re.search(r"/(\d+).torrent$", link)
        if not tid_match:
            continue

        results.append({
            "id": int(tid_match.group(1)),
            "name": item.findtext("title", ""),
            "category": item.findtext(f"{{{_NS}}}categoryId", "0_0") or "0_0",
            "size": _parse_size(item.findtext(f"{{{_NS}}}size", "0") or "0"),
            "date": _parse_date(item.findtext("pubDate", "")),
            "seeders": int(item.findtext(f"{{{_NS}}}seeders", "0") or 0),
            "leechers": int(item.findtext(f"{{{_NS}}}leechers", "0") or 0),
        })

    return results


def nyaa_get_download_url(torrent_id: int) -> str:
    return f"https://nyaa.si/download/{torrent_id}.torrent"

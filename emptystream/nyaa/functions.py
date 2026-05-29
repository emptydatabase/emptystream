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


def nyaa_search_videos(query: str, page: int, category: str, sort: str) -> list[dict]:
    raise NotImplementedError


def nyaa_get_info(torrent_id: int) -> dict:
    raise NotImplementedError


def nyaa_get_download_url(torrent_id: int) -> str:
    raise NotImplementedError

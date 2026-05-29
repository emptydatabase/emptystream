import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from yt_dlp import YoutubeDL

from emptystream.utils import _format_duration


def youtube_search_videos(query: str, start: int, end: int):
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "in_playlist",
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch{end}:{query}", download=False)
    entries = info.get("entries", [])
    page_entries = entries[start:end]

    results = []
    for e in page_entries:
        results.append({
            "id": e["id"],
            "title": e["title"],
            "channel": e.get("channel", ""),
            "duration": _format_duration(e.get("duration")),
            "thumbnail": f"https://i.ytimg.com/vi/{e['id']}/hqdefault.jpg",
        })

    return results


def youtube_get_info(video_id: str) -> dict[str, Any]:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
    return {
        "title": info.get("title", ""),
        "channel": info.get("channel", ""),
        "duration": _format_duration(info.get("duration")),
    }


def youtube_get_stream_urls(video_id: str) -> tuple[str, str]:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "format": "bestvideo+bestaudio",
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
    req = info.get("requested_formats")
    return req[0]["url"], req[1]["url"]


SB_API = "https://sponsor.ajay.app/api/skipSegments"
SB_CATEGORIES = [
    "sponsor", "intro", "outro", "interaction",
    "selfpromo", "preview", "music_offtopic", "filler",
]


def sponsorblock_get_segments(video_id: str) -> list[dict]:
    params = urllib.parse.urlencode([
        ("videoID", video_id),
        ("categories", json.dumps(SB_CATEGORIES)),
    ])
    url = f"{SB_API}?{params}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError, OSError):
        return []
    return [
        {"start": seg["segment"][0], "end": seg["segment"][1], "category": seg["category"]}
        for seg in data
    ]

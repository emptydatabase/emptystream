import json
import urllib.error
from unittest.mock import MagicMock, patch

from emptystream.youtube.functions import (
    sponsorblock_get_segments,
    youtube_get_info,
    youtube_get_stream_urls,
    youtube_search_videos,
)


# ── youtube_search_videos ──────────────────────────────────────

PATCH_TARGET = "emptystream.youtube.functions.YoutubeDL"


@patch(PATCH_TARGET)
def test_search_returns_results(mock_ydl_class):
    mock_ydl = MagicMock()
    mock_ydl_class.return_value.__enter__.return_value = mock_ydl
    mock_ydl.extract_info.return_value = {
        "entries": [
            {"id": "abc123", "title": "Test Video", "channel": "Chan", "duration": 120},
            {"id": "def456", "title": "Video 2", "channel": "Chan", "duration": None},
        ]
    }
    results = youtube_search_videos("test", 0, 9)
    assert len(results) == 2
    assert results[0]["id"] == "abc123"
    assert results[0]["title"] == "Test Video"
    assert results[0]["channel"] == "Chan"
    assert results[0]["duration"] == "2:00"
    assert results[0]["thumbnail"] == "https://i.ytimg.com/vi/abc123/hqdefault.jpg"
    assert results[1]["duration"] == ""


@patch(PATCH_TARGET)
def test_search_respects_slicing(mock_ydl_class):
    mock_ydl = MagicMock()
    mock_ydl_class.return_value.__enter__.return_value = mock_ydl
    mock_ydl.extract_info.return_value = {
        "entries": [
            {"id": f"v{i}", "title": f"Video {i}", "channel": "C"}
            for i in range(20)
        ]
    }
    results = youtube_search_videos("test", 9, 18)
    assert len(results) == 9
    assert results[0]["id"] == "v9"
    assert results[-1]["id"] == "v17"


@patch(PATCH_TARGET)
def test_search_empty_entries(mock_ydl_class):
    mock_ydl = MagicMock()
    mock_ydl_class.return_value.__enter__.return_value = mock_ydl
    mock_ydl.extract_info.return_value = {"entries": []}
    assert youtube_search_videos("test", 0, 9) == []


# ── youtube_get_info ────────────────────────────────────────────

@patch(PATCH_TARGET)
def test_get_info(mock_ydl_class):
    mock_ydl = MagicMock()
    mock_ydl_class.return_value.__enter__.return_value = mock_ydl
    mock_ydl.extract_info.return_value = {
        "title": "Some Video",
        "channel": "Some Channel",
        "duration": 3661,
    }
    info = youtube_get_info("abc123")
    assert info == {"title": "Some Video", "channel": "Some Channel", "duration": "1:01:01"}


# ── youtube_get_stream_urls ──────────────────────────────────────

@patch(PATCH_TARGET)
def test_get_stream_urls(mock_ydl_class):
    mock_ydl = MagicMock()
    mock_ydl_class.return_value.__enter__.return_value = mock_ydl
    mock_ydl.extract_info.return_value = {
        "requested_formats": [{"url": "https://video.url"}, {"url": "https://audio.url"}],
    }
    video_url, audio_url = youtube_get_stream_urls("abc123")
    assert video_url == "https://video.url"
    assert audio_url == "https://audio.url"


# ── sponsorblock_get_segments ────────────────────────────────────

@patch("urllib.request.urlopen")
def test_sponsorblock_success(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps([
        {"segment": [10.0, 20.0], "category": "sponsor"},
        {"segment": [30.0, 35.0], "category": "intro"},
    ]).encode()
    mock_urlopen.return_value.__enter__.return_value = mock_resp
    result = sponsorblock_get_segments("abc123")
    assert len(result) == 2
    assert result[0] == {"start": 10.0, "end": 20.0, "category": "sponsor"}


@patch("urllib.request.urlopen")
def test_sponsorblock_empty_on_http_error(mock_urlopen):
    mock_urlopen.side_effect = urllib.error.HTTPError("", 404, "", {}, None)
    assert sponsorblock_get_segments("abc123") == []


@patch("urllib.request.urlopen")
def test_sponsorblock_empty_on_url_error(mock_urlopen):
    mock_urlopen.side_effect = urllib.error.URLError("fail")
    assert sponsorblock_get_segments("abc123") == []


@patch("urllib.request.urlopen")
def test_sponsorblock_empty_on_bad_json(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"not json"
    mock_urlopen.return_value.__enter__.return_value = mock_resp
    assert sponsorblock_get_segments("abc123") == []

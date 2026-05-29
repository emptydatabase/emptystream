from io import BytesIO
from unittest.mock import MagicMock, patch

import urllib.error

from emptystream.services.nyaa import (
    nyaa_get_download_url,
    nyaa_search_videos,
)

RSS_XML = b"""\
<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:nyaa="https://nyaa.si/xmlns/nyaa" version="2.0">
<channel>
<item>
<title>Test Torrent</title>
<link>https://nyaa.si/download/54321.torrent</link>
<pubDate>Mon, 15 Mar 2026 12:00:00 +0000</pubDate>
<nyaa:seeders>142</nyaa:seeders>
<nyaa:leechers>7</nyaa:leechers>
<nyaa:downloads>8901</nyaa:downloads>
<nyaa:infoHash>abcd1234</nyaa:infoHash>
<nyaa:categoryId>1_2</nyaa:categoryId>
<nyaa:category>Anime - English-translated</nyaa:category>
<nyaa:size>1234567890</nyaa:size>
<nyaa:comments>0</nyaa:comments>
<nyaa:trusted>Yes</nyaa:trusted>
<nyaa:remake>No</nyaa:remake>
<description>Torrent description.</description>
</item>
</channel>
</rss>
"""

class _MockResponse:
    """File-like wrapper that doubles as a context manager, for ET.parse compat."""

    def __init__(self, data: bytes):
        self._buf = BytesIO(data)

    def read(self, size: int = -1):
        return self._buf.read(size)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._buf.close()


def _mock_urlopen(data: bytes):
    """Return a patched urlopen that yields a _MockResponse."""
    mock = MagicMock()
    mock.return_value.__enter__.return_value = _MockResponse(data)
    return mock


@patch("urllib.request.urlopen", new_callable=lambda: _mock_urlopen(RSS_XML))
def test_search_returns_results(mock_urlopen):
    results = nyaa_search_videos("test", "0_0", "seeders")
    assert len(results) == 1
    assert results[0]["id"] == 54321
    assert results[0]["name"] == "Test Torrent"
    assert results[0]["category"] == "1_2"
    assert results[0]["size"] == "1 GiB"
    assert results[0]["date"] == "2026-03-15"
    assert results[0]["seeders"] == 142
    assert results[0]["leechers"] == 7


@patch("urllib.request.urlopen")
def test_search_empty_on_http_error(mock_urlopen):
    mock_urlopen.side_effect = urllib.error.HTTPError("", 404, "", {}, None)
    assert nyaa_search_videos("test", "0_0", "seeders") == []


@patch("urllib.request.urlopen")
def test_search_empty_on_url_error(mock_urlopen):
    mock_urlopen.side_effect = urllib.error.URLError("fail")
    assert nyaa_search_videos("test", "0_0", "seeders") == []


@patch("urllib.request.urlopen", new_callable=lambda: _mock_urlopen(RSS_XML.replace(b"<item>", b"<item2>").replace(b"</item>", b"</item2>")))
def test_search_empty_on_empty_rss(mock_urlopen):
    results = nyaa_search_videos("test", "0_0", "seeders")
    assert results == []


def test_get_download_url():
    url = nyaa_get_download_url(54321)
    assert url == "https://nyaa.si/download/54321.torrent"

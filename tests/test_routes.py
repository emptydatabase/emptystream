from unittest.mock import MagicMock, patch


# ── index ─────────────────────────────────────────────────────

def test_index_returns_200(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"emptystream" in resp.data


# ── search ─────────────────────────────────────────────────────

@patch("emptystream.youtube.routes.youtube_search_videos")
def test_search_no_query(mock_search, client):
    resp = client.get("/youtube/search")
    assert resp.status_code == 200
    assert mock_search.call_count == 0


@patch("emptystream.youtube.routes.youtube_search_videos")
def test_search_with_query(mock_search, client):
    mock_search.return_value = [
        {
            "id": "abc",
            "title": "Test Title",
            "channel": "Test Chan",
            "duration": "1:00",
            "thumbnail": "https://i.ytimg.com/vi/abc/hqdefault.jpg",
        }
    ]
    resp = client.get("/youtube/search?q=test+query")
    assert resp.status_code == 200
    assert b"Test Title" in resp.data
    mock_search.assert_called_once_with("test query", 0, 9)


@patch("emptystream.youtube.routes.youtube_search_videos")
def test_search_pagination_page_2(mock_search, client):
    mock_search.return_value = []
    client.get("/youtube/search?q=test&page=2")
    mock_search.assert_called_once_with("test", 9, 18)


@patch("emptystream.youtube.routes.youtube_search_videos")
def test_search_with_query_error(mock_search, client):
    mock_search.side_effect = Exception("API error")
    resp = client.get("/youtube/search?q=test")
    assert resp.status_code == 200
    assert b"API error" in resp.data


# ── watch ──────────────────────────────────────────────────────

@patch("emptystream.youtube.routes.sponsorblock_get_segments")
@patch("emptystream.youtube.routes.youtube_get_info")
def test_watch_no_video_id(mock_info, mock_sb, client):
    resp = client.get("/youtube/watch")
    assert resp.status_code == 200
    assert b"No video specified" in resp.data
    assert mock_info.call_count == 0


@patch("emptystream.youtube.routes.sponsorblock_get_segments")
@patch("emptystream.youtube.routes.youtube_get_info")
def test_watch_with_video_id(mock_info, mock_sb, client):
    mock_info.return_value = {"title": "My Video", "channel": "My Chan", "duration": "3:00"}
    mock_sb.return_value = [{"start": 10.0, "end": 20.0, "category": "sponsor"}]
    resp = client.get("/youtube/watch?v=abc123")
    assert resp.status_code == 200
    assert b"My Video" in resp.data
    assert b"My Chan" in resp.data
    assert b"SB_SEGMENTS" in resp.data
    mock_info.assert_called_once_with("abc123")
    mock_sb.assert_called_once_with("abc123")


@patch("emptystream.youtube.routes.sponsorblock_get_segments")
@patch("emptystream.youtube.routes.youtube_get_info")
def test_watch_with_info_error(mock_info, mock_sb, client):
    mock_info.side_effect = Exception("fetch failed")
    resp = client.get("/youtube/watch?v=abc123")
    assert resp.status_code == 200
    assert b"fetch failed" in resp.data


# ── stream ─────────────────────────────────────────────────────

@patch("emptystream.youtube.routes.subprocess.Popen")
@patch("emptystream.youtube.routes.youtube_get_stream_urls")
def test_stream_success(mock_get_urls, mock_popen, client):
    mock_get_urls.return_value = ("https://vid.url", "https://aud.url")
    mock_proc = MagicMock()
    mock_proc.stdout.read.side_effect = [b"chunk1", b"chunk2", b""]
    mock_popen.return_value = mock_proc
    resp = client.get("/youtube/stream/abc123")
    assert resp.status_code == 200
    assert resp.mimetype == "video/mp4"
    assert resp.data == b"chunk1chunk2"
    mock_proc.kill.assert_called_once()
    mock_proc.wait.assert_called_once()


@patch("emptystream.youtube.routes.youtube_get_stream_urls")
def test_stream_bad_id_returns_404(mock_get_urls, client):
    mock_get_urls.side_effect = Exception("not found")
    resp = client.get("/youtube/stream/badid")
    assert resp.status_code == 404


# ── static ─────────────────────────────────────────────────────

def test_serves_sponsorblock_js(client):
    resp = client.get("/youtube/static/sponsorblock.js")
    assert resp.status_code == 200
    assert resp.mimetype == "text/javascript"


def test_serves_style_css(client):
    resp = client.get("/static/style.css")
    assert resp.status_code == 200


# ── redirect /search ──────────────────────────────────────────

def test_redirect_search_youtube(client):
    resp = client.get("/search?q=cats&service=youtube")
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/youtube/search?q=cats"


def test_redirect_search_no_query(client):
    resp = client.get("/search")
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/"


def test_redirect_search_bad_service(client):
    resp = client.get("/search?q=cats&service=bad")
    assert resp.status_code == 404


# ── 404 ────────────────────────────────────────────────────────

def test_unknown_route_returns_404(client):
    resp = client.get("/nonexistent")
    assert resp.status_code == 404

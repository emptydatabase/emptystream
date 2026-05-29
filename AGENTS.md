# emptystream — agent guide

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional: PORT override
python app.py          # dev server on :5000 (or $PORT)
```

Runtime deps: `Flask`, `yt-dlp`, `ffmpeg` (on `PATH`), Python 3.10+.

## Tests

```bash
python -m pytest tests/ -v                                              # full suite
python -m pytest tests/test_routes.py -v                                # single file
python -m pytest tests/test_routes.py::test_index_returns_200 -v        # single test
```

CI runs `python -m pytest tests/ -v` on push/PR via `.github/workflows/test.yml`.

3 test files using `conftest.py` fixtures (`app` = Flask app, `client` = test client):
- `test_routes.py` — HTTP route assertions; mocks via `@patch`; checks status codes, response body, mock call args
- `test_utils.py` — pure function edge cases for `_format_duration`
- `test_youtube_functions.py` — yt-dlp wrapper tests; patches `YoutubeDL` and `urllib.request.urlopen` for SponsorBlock

No external services, database, or extra fixtures needed. Add tests for nyaa using same patterns.

## Structure

- `app.py` — entrypoint: `load_dotenv()` → `from emptystream import app` → `app.run(port=...)`
- `emptystream/__init__.py` — re-exports `app` from `routes.py`
- `emptystream/routes.py` — creates `Flask(__name__)`, registers `YoutubeService` and `NyaaService` (via `Service.register_app`), defines `/` (index) and `/search` (redirects to active service's search route, defers to `?service=` param, default `youtube`)
- `emptystream/service.py` — `Service` base class with `id`, `name`, `search_route`, `blueprint` class vars and `register_app` classmethod
- Each service is a package (`emptystream/youtube/`, `emptystream/nyaa/`): `__init__.py` declares the `*Service` subclass + blueprint, `routes.py` has Flask routes, `functions.py` has backend logic
- `emptystream/youtube/` — Blueprint at `/youtube` prefix
  - 3 routes: `/youtube/search?q=&page=` (PER_PAGE=9), `/youtube/watch?v=`, `/youtube/stream/<video_id>`
  - `functions.py` — yt-dlp wrappers + SponsorBlock API client via `urllib.request`
  - `templates/youtube/`, `static/sponsorblock.js`
- `emptystream/nyaa/` — Blueprint at `/nyaa` prefix
  - 3 routes: `/nyaa/search`, `/nyaa/view/<id>`, `/nyaa/download/<id>` — render stub data (`STUB_RESULTS`, `STUB_INFO`), backend search functions in `functions.py` raise `NotImplementedError`
  - `functions.py` — `CATEGORY_GROUPS`, `CATEGORY_LABELS`, `CATEGORY_ICONS`, `SORT_OPTIONS`
  - `templates/nyaa/`, `static/cat-*.svg`
- `emptystream/utils.py` — `_format_duration` (private, used by `youtube/functions.py`)

## Key details

- **Search**: `extract_flat='in_playlist'` (~3s for 100 results); fetches `ytsearch{end}:query` fresh each page (no caching). Thumbnail: `https://i.ytimg.com/vi/{id}/hqdefault.jpg`.
- **Stream**: `format='bestvideo+bestaudio'` → ffmpeg `-c copy -movflags frag_keyframe+empty_moov -f mp4 pipe:1`. Reads 1024-byte chunks. Kills ffmpeg on client disconnect via `finally: proc.kill(); proc.wait()`.
- **SponsorBlock**: Fetched from `sponsor.ajay.app/api/skipSegments` in parallel with video info via `ThreadPoolExecutor`. Injected as `window.SB_SEGMENTS`. Client-side JS auto-skips once then shows "Skip" button on replay. Errors → empty list silently.
- **Static files**: Each blueprint serves its own `static/`; app-level `static/` (style.css, favicon.svg) from `/static/`.
- **Deploy**: systemd service (`emptystream.service`) as unprivileged `emptystream` user from `/opt/emptystream`. Logs: `journalctl -u emptystream -f`.

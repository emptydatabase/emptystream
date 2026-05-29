# emptystream — agent guide

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional: PORT override
python app.py          # dev server on :5000 (or $PORT)
```

Requires `ffmpeg` on PATH, Python 3.10+.

## Tests

```bash
python -m pytest tests/ -v        # full suite, 39 tests, no external services
python -m pytest tests/test_routes.py -v                                # single file
python -m pytest tests/test_routes.py::test_index_returns_200 -v        # single test
```

Tests use `@patch` for yt-dlp, urllib, BeautifulSoup, `subprocess.Popen`. `conftest.py` provides `app` and `client` fixtures. No DB needed.

## CI

GitHub Actions (`.github/workflows/test.yml`) runs `pip install -r requirements.txt && python -m pytest tests/ -v` on push/PR. Python 3.12, ubuntu-latest.

## Architecture

- `app.py` → `emptystream/__init__.py` → `routes.py` creates Flask app, registers services from `emptystream/services/`.
- Service pattern: subclass `Service` (`emptystream/services/service.py`), define `id`, `name`, `search_route`, `blueprint`. Add to `services` list in `routes.py`.
- Each service is a package under `emptystream/services/{youtube,nyaa}/`: `__init__.py` declares the `*Service` subclass + re-exports functions, `routes.py` has Flask routes, `functions.py` has backend logic.
- YouTube Blueprint at `/youtube`, PER_PAGE=9. Nyaa Blueprint at `/nyaa`, PER_PAGE=25.
- Nyaa download returns a redirect to `nyaa.si/download/{id}.torrent`, not a local file.

## Key gotchas

- **YouTube search**: `extract_flat='in_playlist'`; fetches `ytsearch{end}:query` fresh each page (no caching). Thumbnail: `https://i.ytimg.com/vi/{id}/hqdefault.jpg`.
- **Stream**: `bestvideo+bestaudio` → ffmpeg `-c copy -movflags frag_keyframe+empty_moov -f mp4 pipe:1`. Reads 1024-byte chunks. `finally: proc.kill(); proc.wait()` on client disconnect.
- **SponsorBlock**: Parallel fetch via `ThreadPoolExecutor`. Injected as `window.SB_SEGMENTS`. Errors → empty list silently.
- **Nyaa RSS**: Parses `?page=rss` with `xml.etree.ElementTree`. Regex extracts torrent ID from `<link>` (expects `.../<id>.torrent`).
- **Static files**: Each Blueprint serves its own `static/`; app-level `static/` (style.css, favicon.svg) mounts at `/static/`.
- **No linter/formatter/typecheck config** in the repo.
- **Service init files must re-export function names** that tests import directly (e.g., `emptystream.services.youtube` re-exports `youtube_search_videos` from `functions.py`).

## Deploy

systemd service as `emptystream` user from `/opt/emptystream`. Logs: `journalctl -u emptystream -f`.

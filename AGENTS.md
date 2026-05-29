# emptystream — agent guide

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional: PORT override
python app.py          # dev server on :5000 (or $PORT)
```

Runtime deps: `Flask`, `yt-dlp`, `ffmpeg` (on `PATH`), Python 3.10+.
Tests: `python -m pytest tests/ -v` (pytest, no extra setup). CI runs the same on push/PR via `.github/workflows/test.yml`.
No linter, formatter, or typechecker configured in the repo.

## Structure

- `app.py` — entrypoint: `load_dotenv()` → `from emptystream import app` → `app.run(port=...)`
- `emptystream/` — Flask package; `routes.py` creates the app, registers `youtube_bp`, defines `/` (index) and `/search` (redirects to `/youtube/search?q=`)
- `emptystream/youtube/` — Blueprint at `/youtube` prefix with its own `templates/` and `static/` (sponsorblock.js)
  - `routes.py` — 3 routes: `/youtube/search?q=&page=` (PER_PAGE=9), `/youtube/watch?v=`, `/youtube/stream/<video_id>`
  - `functions.py` — yt-dlp wrappers + SponsorBlock API client via `urllib.request`

## Key details

- **Search**: `extract_flat='in_playlist'` (~3s for 100 results); fetches `ytsearch{end}:query` fresh each page (no caching). Thumbnail: `https://i.ytimg.com/vi/{id}/hqdefault.jpg`.
- **Stream**: `format='bestvideo+bestaudio'` → ffmpeg `-c copy -movflags frag_keyframe+empty_moov -f mp4 pipe:1`. Reads 1024-byte chunks. Kills ffmpeg on client disconnect via `finally: proc.kill(); proc.wait()`.
- **SponsorBlock**: Fetched from `sponsor.ajay.app/api/skipSegments` in parallel with video info via `ThreadPoolExecutor`. Injected as `window.SB_SEGMENTS`. Client-side JS auto-skips once then shows "Skip" button on replay. Errors → empty list silently.
- **Static files**: Blueprint serves its own `static/` (sponsorblock.js at `/youtube/static/sponsorblock.js`); top-level `static/` (style.css, favicon.svg) served from app root.

## Deploy

Systemd service (`emptystream.service`) runs as unprivileged `emptystream` user from `/opt/emptystream`. Logs: `journalctl -u emptystream -f`.

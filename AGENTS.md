# emptystream — agent guide

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional: configure PORT
python app.py          # dev server on :5000 (or $PORT)
```

Key runtime deps: `Flask`, `yt-dlp`, `ffmpeg` (must be on `PATH`).
Python 3.10+.
No test framework, linting, or CI — zero config for those.

## Structure

- `app.py` — entry point: `from emptystream import create_app; app = create_app(); app.run()`
- `emptystream/routes.py` — Flask app factory (`Flask(__name__)` resolves templates/static relative to `emptystream/` package dir), 4 routes:
  - `/` → `index.html`
  - `/search?q=&page=` → `search.html` (pagination via `PER_PAGE=9`)
  - `/watch?v=` → `watch.html` (video metadata + SponsorBlock segments)
  - `/stream/<video_id>` → ffmpeg-piped MP4 stream (bad ID returns 404)
- `emptystream/core.py` — yt-dlp wrappers + SponsorBlock API client
- `emptystream/static/` — CSS, `sponsorblock.js`, favicon
- `emptystream/templates/` — Jinja2, `base.html` with shared search bar

## Streaming

`/stream/<video_id>` fetches DASH URLs via yt-dlp (`format='bestvideo+bestaudio'`), merges with ffmpeg (`-c copy`, no re-encode). ffmpeg is killed on client disconnect via `finally: proc.kill(); proc.wait()`.

## Search

Uses `extract_flat='in_playlist'` — fast (~3s for 100 results), basic fields only. Thumbnail URL: `https://i.ytimg.com/vi/{id}/hqdefault.jpg`. Fetches `ytsearch{end}:query` fresh each page (no server-side caching).

## SponsorBlock

Fetched from `sponsor.ajay.app/api/skipSegments` in parallel with video info (`ThreadPoolExecutor`). Injected as `window.SB_SEGMENTS`. Client-side auto-skips each segment once on first encounter; "Skip" button on subsequent plays.

## Deploy

Systemd service (`emptystream.service`) runs as unprivileged `emptystream` user from `/opt/emptystream`. Logs: `journalctl -u emptystream -f`.

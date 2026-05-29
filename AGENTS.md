# emptystream — agent guide

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional: PORT override
python app.py          # dev server on :5000 (or $PORT)
```

Runtime deps: `Flask`, `yt-dlp`, `ffmpeg` (on `PATH`). Python 3.10+.
No test framework, linting, typechecking, or CI — zero config for those.

## Structure

- `app.py` — entrypoint: `load_dotenv()` → `from emptystream import app` → `app.run(port=os.getenv("PORT", "5000"))`
- `emptystream/` — Flask package (`Flask(__name__)` resolves templates/static relative to this dir)
  - `routes.py` — `create_app()` factory; only the `/` → `index.html` route lives here; registers `youtube_bp` blueprint
  - `utils.py` — `_format_duration(seconds)` helper
  - `templates/` — shared Jinja2 layout (`base.html` + `index.html`)
  - `static/` — shared assets (`style.css`, `favicon.svg`)
  - `youtube/` — YouTube service subpackage (Blueprint under `/youtube` prefix):
    - `routes.py` — `youtube_bp` with 3 routes:
      - `/youtube/search?q=&page=` → `search.html` (pagination via `PER_PAGE=9`)
      - `/youtube/watch?v=` → `watch.html` (video metadata + SponsorBlock segments)
      - `/youtube/stream/<video_id>` → ffmpeg-piped MP4 stream (bad ID → 404)
    - `functions.py` — yt-dlp wrappers (`youtube_search_videos`, `youtube_get_info`, `youtube_get_stream_urls`) + SponsorBlock API client
    - `templates/` — `search.html`, `watch.html`
    - `static/` — `sponsorblock.js`

## Search

Uses `extract_flat='in_playlist'` — fast (~3s for 100 results), basic fields only.
Thumbnail URL: `https://i.ytimg.com/vi/{id}/hqdefault.jpg`.
Fetches `ytsearch{end}:query` fresh each page (no server-side caching).

## Streaming

`/youtube/stream/<video_id>` fetches DASH URLs via yt-dlp (`format='bestvideo+bestaudio'`),
merges with ffmpeg (`-c copy -movflags frag_keyframe+empty_moov -f mp4`, no re-encode).
ffmpeg is killed on client disconnect via `finally: proc.kill(); proc.wait()`.
Uses `subprocess.Popen` with `stdout=subprocess.PIPE`, reads 1024-byte chunks.

## SponsorBlock

Fetched from `sponsor.ajay.app/api/skipSegments` via `urllib.request` (parallel with video info via `ThreadPoolExecutor`).
Categories: sponsor, intro, outro, interaction, selfpromo, preview, music_offtopic, filler.
Injected as `window.SB_SEGMENTS`. Client-side auto-skips each segment once on first encounter; "Skip" button on subsequent plays.
Errors → empty list (silently).

## Deploy

Systemd service (`emptystream.service`) runs as unprivileged `emptystream` user from `/opt/emptystream`.
Logs: `journalctl -u emptystream -f`.

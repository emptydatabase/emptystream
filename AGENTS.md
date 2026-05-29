# ytinterface — agent guide

## Run

```bash
python app.py         # dev server on :5000
```

```bash
pip install -r requirements.txt   # install deps
```

Key runtime deps: `Flask`, `yt-dlp`, `ffmpeg` (must be on `PATH`).

## Structure

- `app.py` — entry point: `from ytinterface import create_app; app = create_app(); app.run(debug=True)`
- `ytinterface/routes.py` — Flask app factory with 4 routes:
  - `/` → `index.html`
  - `/search?q=&page=` → `search.html` (pagination via `PER_PAGE=9`)
  - `/watch?v=` → `watch.html` (video metadata + SponsorBlock segments)
  - `/stream/<video_id>` → ffmpeg-piped MP4 stream
- `ytinterface/core.py` — yt-dlp wrappers + SponsorBlock API client:
  - `search_videos(query, start, end)` — flat extraction, `ytsearch{end}:query`
  - `get_video_info(video_id)` — title, channel, duration
  - `get_stream_urls(video_id)` — returns `(video_url, audio_url)` via `format='bestvideo+bestaudio'`
  - `get_sponsorblock_segments(video_id)` — fetches skip segments from sponsor.ajay.app
- `ytinterface/static/sponsorblock.js` — client-side skip button + one-time auto-skip per segment
- `ytinterface/templates/` — Jinja2, single `base.html` with shared search bar
- `ytinterface/static/style.css` — dark theme, no framework

## Streaming

`/stream/<video_id>` fetches DASH URLs via yt-dlp then merges them live with ffmpeg:

```
ffmpeg -i VIDEO_URL -i AUDIO_URL -c copy -movflags frag_keyframe+empty_moov -f mp4 -loglevel quiet pipe:1
```

The response is a streaming fragmented MP4. `-c copy` means no re-encode — CPU-light but codec-dependent. ffmpeg is killed on client disconnect via `finally: proc.kill(); proc.wait()`.

## Search

Uses `extract_flat='in_playlist'` — fast (~3s for 100 results), but only returns basic fields (id, title, channel, duration, thumbnails). Thumbnail URL is constructed as `https://i.ytimg.com/vi/{id}/hqdefault.jpg`.

Pagination: fetches `ytsearch{end}:query` each request (no server-side caching). Page N fetches `N * PER_PAGE` results and slices `[(N-1)*PER_PAGE : N*PER_PAGE]`.

## SponsorBlock

`/watch` fetches skip segments from `sponsor.ajay.app/api/skipSegments` in parallel with video info (via `ThreadPoolExecutor`). Segments are injected as `window.SB_SEGMENTS` in the template. `sponsorblock.js` auto-skips each segment once on first encounter; on subsequent plays a "Skip" button appears instead.

## Gotchas

- No test framework, linting, or CI — zero config for those
- No `pyproject.toml` or `setup.py` — dependencies declared in `requirements.txt`
- `Flask(__name__)` in `routes.py` resolves templates/static relative to `ytinterface/` package dir
- `/stream/<video_id>` with a truncated/invalid ID returns 404 (caught exception)
- `/watch?v=<id>` shows the video title/channel; if yt-dlp fails it shows an error message

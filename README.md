# emptystream

Multi-service media frontend. Search YouTube via yt-dlp (stream directly) and browse Nyaa torrents.

## Requirements

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) (must be on `PATH`)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional: PORT override
```

## Run

```bash
python app.py
```

Open http://localhost:5000.

## Services

| Service | Route | Status |
|---|---|---|
| **YouTube** | `/youtube/search?q=` | Search, watch, and stream videos via yt-dlp + ffmpeg |
| **Nyaa** | `/nyaa/search?q=&category=&sort=` | Browse torrents (stub data; backend not yet implemented) |

## Deploy as a systemd service

```bash
sudo useradd -r -s /usr/bin/nologin emptystream
sudo mkdir -p /opt/emptystream
sudo cp -r . .venv /opt/emptystream
sudo chown -R emptystream:emptystream /opt/emptystream
sudo cp emptystream.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now emptystream
```

Logs: `journalctl -u emptystream -f`.

## How YouTube works

1. **Search** — queries YouTube via yt-dlp (`extract_flat='in_playlist'`), returns thumbnail/title/channel/duration
2. **Watch** — shows video metadata and a `<video>` player; fetches SponsorBlock segments in parallel
3. **Stream** — yt-dlp extracts DASH video+audio URLs, ffmpeg merges them into a fragmented MP4 on-the-fly (`-c copy -movflags frag_keyframe+empty_moov -f mp4 pipe:1`)

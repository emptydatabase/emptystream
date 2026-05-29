# emptystream

Multi-service media frontend. Search for videos from supported services and stream them directly.

## Requirements

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) (must be on `PATH`)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Open http://localhost:5000.

## Deploy as a systemd service

```bash
# Create unprivileged system user
sudo useradd -r -s /usr/bin/nologin emptystream

# Install app to /opt/emptystream
sudo mkdir -p /opt/emptystream
sudo cp -r . .venv /opt/emptystream
sudo chown -R emptystream:emptystream /opt/emptystream

# Install and start the service
sudo cp emptystream.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now emptystream
```

The service runs on `http://localhost:5000`. Check logs with `journalctl -u emptystream -f`.

## How it works

1. **Search** — queries the media service via yt-dlp, returns thumbnail/title/channel/duration
2. **Watch** — shows video metadata and a `<video>` player
3. **Stream** — yt-dlp fetches DASH video+audio URLs, ffmpeg merges them into a fragmented MP4 on-the-fly
4. **SponsorBlock** — skip segments (sponsors, intros, etc.) are fetched from sponsor.ajay.app and applied client-side

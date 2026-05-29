# ytinterface

YouTube frontend. Search for videos and stream them directly.

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
sudo useradd -r -s /usr/bin/nologin ytinterface

# Install app to /opt/ytinterface
sudo mkdir -p /opt/ytinterface
sudo cp -r . .venv /opt/ytinterface
sudo chown -R ytinterface:ytinterface /opt/ytinterface

# Install and start the service
sudo cp ytinterface.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now ytinterface
```

The service runs on `http://localhost:5000`. Check logs with `journalctl -u ytinterface -f`.

## How it works

1. **Search** — queries YouTube via yt-dlp, returns thumbnail/title/channel/duration
2. **Watch** — shows video metadata and a `<video>` player
3. **Stream** — yt-dlp fetches DASH video+audio URLs, ffmpeg merges them into a fragmented MP4 on-the-fly
4. **SponsorBlock** — skip segments (sponsors, intros, etc.) are fetched from sponsor.ajay.app and applied client-side

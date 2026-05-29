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

## How it works

1. **Search** — queries YouTube via yt-dlp, returns thumbnail/title/channel/duration
2. **Watch** — shows video metadata and a `<video>` player
3. **Stream** — yt-dlp fetches DASH video+audio URLs, ffmpeg merges them into a fragmented MP4 on-the-fly

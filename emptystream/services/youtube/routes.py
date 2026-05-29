import json
import logging
import subprocess
from concurrent.futures.thread import ThreadPoolExecutor

from flask import (
    Blueprint,
    render_template,
    request,
    abort,
    Response,
    stream_with_context,
)

from .functions import (
    youtube_search_videos,
    youtube_get_stream_urls,
    youtube_get_info,
    sponsorblock_get_segments,
)

youtube_bp = Blueprint("youtube", __name__, template_folder="templates", static_folder="static", url_prefix="/youtube")

PER_PAGE = 9


@youtube_bp.route("/search")
def search():
    query = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    if not query:
        return render_template("youtube/search.html")
    else:
        try:
            results = youtube_search_videos(query, (page - 1) * PER_PAGE, page * PER_PAGE)
        except Exception as exc:
            return render_template(
                "youtube/search.html",
                query=query,
                error=str(exc),
            )
        else:
            return render_template(
                "youtube/search.html",
                query=query,
                results=results,
                page=page,
            )


@youtube_bp.route("/watch")
def watch():
    video_id = request.args.get("v", "")
    if not video_id:
        return render_template("youtube/watch.html")
    with ThreadPoolExecutor() as executor:
        info_future = executor.submit(youtube_get_info, video_id)
        sb_segments_future = executor.submit(sponsorblock_get_segments, video_id)
    try:
        info = info_future.result()
        sb_segments = sb_segments_future.result()
    except Exception as exc:
        return render_template(
            "youtube/watch.html",
            video_id=video_id,
            error=str(exc),
        )
    else:
        return render_template(
            "youtube/watch.html",
            video_id=video_id,
            title=info.get("title"),
            channel=info.get("channel"),
            duration=info.get("duration"),
            sponsorblock_segments=json.dumps(sb_segments),
        )


@youtube_bp.route("/stream/<video_id>")
def stream(video_id):
    try:
        video_url, audio_url = youtube_get_stream_urls(video_id)
    except Exception as exc:
        logging.exception("", exc_info=exc)
        abort(404)

    def generate():
        cmd = [
            "ffmpeg",
            "-i", video_url,
            "-i", audio_url,
            "-c", "copy",
            "-movflags", "frag_keyframe+empty_moov",
            "-f", "mp4",
            "-loglevel", "quiet",
            "pipe:1",
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        try:
            while True:
                chunk = proc.stdout.read(1024)
                if not chunk:
                    break
                yield chunk
        finally:
            proc.kill()
            proc.wait()

    return Response(
        stream_with_context(generate()),
        mimetype="video/mp4",
    )

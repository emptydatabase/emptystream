import logging
import subprocess

from flask import (
    render_template,
    request,
    abort,
    Response,
    stream_with_context, Flask,
)

from .core import search_videos, get_stream_urls, get_video_info

PER_PAGE = 9


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/search")
    def search():
        query = request.args.get("q", "")
        page = request.args.get("page", 1, type=int)
        if not query:
            return render_template("search.html")
        else:
            try:
                results = search_videos(query, (page - 1) * PER_PAGE, page * PER_PAGE)
            except Exception as exc:
                return render_template(
                    "search.html",
                    query=query,
                    error=str(exc),
                )
            else:
                return render_template(
                    "search.html",
                    query=query,
                    results=results,
                    page=page,
                )

    @app.route("/watch")
    def watch():
        video_id = request.args.get("v", "")
        if not video_id:
            return render_template("watch.html")
        else:
            try:
                info = get_video_info(video_id)
            except Exception as exc:
                return render_template(
                    "watch.html",
                    video_id=video_id,
                    error=str(exc),
                )
            else:
                return render_template(
                    "watch.html",
                    video_id=video_id,
                    title=info.get("title"),
                    channel=info.get("channel"),
                    duration=info.get("duration"),
                )

    @app.route("/stream/<video_id>")
    def stream(video_id):
        try:
            video_url, audio_url = get_stream_urls(video_id)
        except Exception:
            logging.exception("")
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
                    chunk = proc.stdout.read(65536)
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

    return app

from flask import Flask, abort, redirect, render_template, request, url_for

from .youtube import youtube_bp

app = Flask(__name__)
app.register_blueprint(youtube_bp)

SERVICE_NAMES = {"youtube": "YouTube"}
SERVICE_ROUTES = {"youtube": "youtube.search"}


@app.context_processor
def inject_globals():
    return dict(services=SERVICE_NAMES, current_service="youtube")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
def search():
    query = request.args.get("q", "")
    service = request.args.get("service", "youtube")
    if not query:
        return redirect(url_for("index"))
    service_route = SERVICE_ROUTES.get(service)
    if service_route is None:
        abort(404)
    return redirect(url_for(service_route, q=query))

from flask import Flask, abort, redirect, render_template, request, url_for

from .youtube import YoutubeService
from .nyaa import NyaaService

app = Flask(__name__)

services = [
    YoutubeService,
    NyaaService,
]

for s in services:
    s.register_app(app)

SERVICE_NAMES = {service.id: service.name for service in services}
SERVICE_ROUTES = {service.id: service.search_route for service in services}


@app.context_processor
def inject_globals():
    return dict(services=SERVICE_NAMES)


@app.context_processor
def inject_current_service():
    endpoint = request.endpoint or ""
    parts = endpoint.split(".")
    if len(parts) == 0:
        return {"current_service": "youtube"}
    service_id = parts[0]
    if service_id in SERVICE_NAMES:
        return {"current_service": service_id}
    else:
        return {"current_service": "youtube"}


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
    kwargs = {"q": query}
    if service == "nyaa":
        category = request.args.get("category")
        if category:
            kwargs["category"] = category
        kwargs["sort"] = request.args.get("sort", "seeders")
    return redirect(url_for(service_route, **kwargs))

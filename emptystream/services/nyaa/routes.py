import logging

from flask import Blueprint, redirect, render_template, request

from .functions import (
    CATEGORY_GROUPS,
    CATEGORY_ICONS,
    CATEGORY_LABELS,
    SORT_OPTIONS,
    nyaa_get_download_url,
    nyaa_search_videos,
)

nyaa_bp = Blueprint("nyaa", __name__, template_folder="templates", static_folder="static", url_prefix="/nyaa")

PER_PAGE = 25


@nyaa_bp.route("/search")
def search():
    query = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    category = request.args.get("category", "0_0")
    sort = request.args.get("sort", "seeders")

    template_args = dict(
        query=query,
        page=page,
        category=category,
        sort=sort,
        category_groups=CATEGORY_GROUPS,
        category_icons=CATEGORY_ICONS,
        sort_options=SORT_OPTIONS,
        category_label=CATEGORY_LABELS.get(category, ""),
    )

    if not query:
        return render_template("nyaa/search.html", results=[], **template_args)

    try:
        results = nyaa_search_videos(query, category, sort)
    except Exception as exc:
        logging.exception("nyaa search failed")
        return render_template(
            "nyaa/search.html", results=[], error=str(exc), **template_args
        )

    return render_template("nyaa/search.html", results=results, **template_args)


@nyaa_bp.route("/download/<int:torrent_id>")
def download(torrent_id):
    return redirect(nyaa_get_download_url(torrent_id))

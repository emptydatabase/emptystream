from flask import Blueprint, render_template, request, abort

from .functions import CATEGORY_GROUPS, CATEGORY_ICONS, CATEGORY_LABELS, SORT_OPTIONS

nyaa_bp = Blueprint("nyaa", __name__, template_folder="templates", static_folder="static", url_prefix="/nyaa")

PER_PAGE = 25

STUB_RESULTS = [
    {
        "id": i,
        "name": f"Example Torrent {i} — " + ("Long Name " * 5 if i % 3 == 0 else "Short"),
        "category": ["1_2", "2_1", "3_1", "4_1", "5_2", "6_2"][i % 6],
        "size": f"{50 + i * 37} MiB",
        "date": f"2026-0{1 + (i % 9):02d}-{10 + i:02d}",
        "seeders": 300 - i * 17,
        "leechers": i * 3,
    }
    for i in range(1, 26)
]

STUB_INFO = {
    "id": 12345,
    "name": "Example Torrent — Full Detail View",
    "category": "1_2",
    "size": "1.2 GiB",
    "date": "2026-03-15",
    "seeders": 142,
    "leechers": 7,
    "downloads": 8901,
    "info_hash": "0123456789ABCDEF0123456789ABCDEF01234567",
    "description": "This is a placeholder description for the torrent detail page.\n\nThe actual description will be fetched from nyaa.si once the backend logic is implemented.\n\nFile list, comments, and other metadata will appear here.",
}


@nyaa_bp.route("/search")
def search():
    query = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    category = request.args.get("category", "0_0")
    sort = request.args.get("sort", "seeders")

    if not query:
        return render_template(
            "nyaa/search.html",
            query="",
            page=1,
            category=category,
            sort=sort,
            results=[],
            category_groups=CATEGORY_GROUPS,
            category_icons=CATEGORY_ICONS,
            sort_options=SORT_OPTIONS,
        )

    return render_template(
        "nyaa/search.html",
        query=query,
        page=page,
        category=category,
        sort=sort,
        results=STUB_RESULTS,
        category_groups=CATEGORY_GROUPS,
        category_icons=CATEGORY_ICONS,
        sort_options=SORT_OPTIONS,
        category_label=CATEGORY_LABELS.get(category, ""),
    )


@nyaa_bp.route("/view/<int:torrent_id>")
def view(torrent_id):
    return render_template(
        "nyaa/view.html",
        torrent=STUB_INFO,
        category_label=CATEGORY_LABELS.get(STUB_INFO["category"], ""),
    )


@nyaa_bp.route("/download/<int:torrent_id>")
def download(torrent_id):
    return render_template(
        "nyaa/view.html",
        torrent=STUB_INFO,
        category_label=CATEGORY_LABELS.get(STUB_INFO["category"], ""),
        download_notice="Torrent download is not yet implemented.",
    )

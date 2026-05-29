from flask import Flask

from .functions import CATEGORY_GROUPS
from .routes import nyaa_bp
from ..service import Service


class NyaaService(Service):
    id = "nyaa"
    name = "Nyaa"
    search_route = "nyaa.search"
    blueprint = nyaa_bp

    @classmethod
    def register_app(cls, app: Flask):
        super().register_app(app)

        @app.context_processor
        def inject_globals():
            return dict(category_groups=CATEGORY_GROUPS)

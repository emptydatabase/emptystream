from typing import ClassVar

from flask import Blueprint, Flask


class Service:
    id: ClassVar[str]
    name: ClassVar[str]
    search_route: ClassVar[str]
    blueprint: ClassVar[Blueprint]

    @classmethod
    def register_app(cls, app: Flask):
        app.register_blueprint(cls.blueprint)

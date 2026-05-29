from .routes import youtube_bp
from ..service import Service


class YoutubeService(Service):
    id = "youtube"
    name = "Youtube"
    search_route = "youtube.search"
    blueprint = youtube_bp

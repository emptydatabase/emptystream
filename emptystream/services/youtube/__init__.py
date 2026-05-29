from .functions import (
    sponsorblock_get_segments,
    youtube_get_info,
    youtube_get_stream_urls,
    youtube_search_videos,
)
from .routes import youtube_bp
from ..service import Service


class YoutubeService(Service):
    id = "youtube"
    name = "Youtube"
    search_route = "youtube.search"
    blueprint = youtube_bp

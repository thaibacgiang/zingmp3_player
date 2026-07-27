"""Constants for Zing MP3 Player integration."""

DOMAIN = "zingmp3_player"
DEFAULT_NAME = "Zing MP3 Player"
DEFAULT_SPEAKERS = []
VERSION = "2026.2.9"

# Configuration
CONF_SPEAKERS = "speakers"
CONF_EXTRA_SENSOR = "extra_sensor"
CONF_DROPDOWNS = "dropdowns"
CONF_UPDATE_INTERVAL = "update_interval"

# Attributes
ATTR_SEARCH_RESULTS = "search"
ATTR_TRACKS = "tracks"
ATTR_TOTAL_TRACKS = "total_tracks"
ATTR_PLAYLIST_NAME = "playlist_name"
ATTR_IS_PLAYLIST = "is_playlist"

# Services
SERVICE_SEARCH = "search"
SERVICE_CALL_METHOD = "call_method"
SERVICE_PLAY_PLAYLIST = "play_playlist"

# Media types
MEDIA_TYPE_SONG = "song"
MEDIA_TYPE_PLAYLIST = "playlist"
MEDIA_TYPE_ALBUM = "album"

# Default values
DEFAULT_UPDATE_INTERVAL = 30  # seconds
DEFAULT_SEARCH_LIMIT = 20

# API endpoints
API_BASE_URL = "https://zingmp3.vn"
API_SEARCH_URL = "https://ac.zingmp3.vn/api/v2/search"
API_STREAM_URL = "https://zingmp3.vn/api/v2/streaming"
API_PLAYLIST_URL = "https://zingmp3.vn/api/v2/playlist"

# Error messages
ERROR_CANNOT_CONNECT = "cannot_connect"
ERROR_UNKNOWN = "unknown"
ERROR_NOT_FOUND = "not_found"
ERROR_AUTH = "authentication_error"

# Icons
ICON_MUSIC = "mdi:music"
ICON_PLAY = "mdi:play"
ICON_PAUSE = "mdi:pause"
ICON_STOP = "mdi:stop"
ICON_NEXT = "mdi:skip-next"
ICON_PREVIOUS = "mdi:skip-previous"
ICON_SHUFFLE = "mdi:shuffle"
ICON_REPEAT = "mdi:repeat"

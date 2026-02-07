"""Constants cho Zing MP3 integration."""
import homeassistant.helpers.config_validation as cv
from homeassistant.components.media_player import MediaPlayerEntityFeature
from homeassistant.components.media_player.const import MediaType
import voluptuous as vol
import logging

from homeassistant.const import (
	ATTR_ENTITY_ID,
	CONF_NAME,
	STATE_PLAYING,
	STATE_PAUSED,
	STATE_ON,
	STATE_OFF,
	STATE_IDLE,
)

from homeassistant.components.media_player import (
	DOMAIN as DOMAIN_MP,
)

import homeassistant.components.select as select

# Domain và platforms
PLATFORMS = {"sensor", "select", "media_player"}
DOMAIN = "zingmp3_player"

# Supported features cho media player
SUPPORT_ZINGMP3_PLAYER = (
	MediaPlayerEntityFeature.TURN_ON
	| MediaPlayerEntityFeature.TURN_OFF
	| MediaPlayerEntityFeature.PLAY
	| MediaPlayerEntityFeature.PLAY_MEDIA
	| MediaPlayerEntityFeature.PAUSE
	| MediaPlayerEntityFeature.STOP
	| MediaPlayerEntityFeature.VOLUME_SET
	| MediaPlayerEntityFeature.VOLUME_STEP
	| MediaPlayerEntityFeature.VOLUME_MUTE
	| MediaPlayerEntityFeature.PREVIOUS_TRACK
	| MediaPlayerEntityFeature.NEXT_TRACK
	| MediaPlayerEntityFeature.SHUFFLE_SET
	| MediaPlayerEntityFeature.REPEAT_SET
	| MediaPlayerEntityFeature.BROWSE_MEDIA
	| MediaPlayerEntityFeature.SELECT_SOURCE
	| MediaPlayerEntityFeature.SEEK
)

# Service names
SERVICE_SEARCH = "search"
SERVICE_SEARCH_PLAY = "search_play"
SERVICE_CALL_METHOD = "call_method"
SERVICE_CALL_GOTO_TRACK = "goto_track"
ATTR_QUERY = "query"
ATTR_FILTER = "filter"
ATTR_LIMIT = "limit"
ATTR_COMMAND = "command"
ATTR_PARAMETERS = "parameters"

# Configuration keys
CONF_RECEIVERS = 'speakers'  # list of speakers (media_players)
CONF_INIT_DROPDOWNS = 'dropdowns'
CONF_INIT_EXTRA_SENSOR = 'extra_sensor'
CONF_DEBUG_AS_ERROR = 'debug_as_error'

# Dropdowns
ALL_DROPDOWNS = ["speakers", "playmode", "repeatmode"]
DEFAULT_INIT_DROPDOWNS = ["speakers"]

# Defaults
DEFAULT_DEBUG_AS_ERROR = False
DEFAULT_INIT_EXTRA_SENSOR = False

# Errors (simplified)
ERROR_GENERIC = 'ERROR_GENERIC'
ERROR_NO_SONG_FOUND = 'ERROR_NO_SONG_FOUND'
ERROR_NO_STREAM_LINK = 'ERROR_NO_STREAM_LINK'
ERROR_NO_PLAYER_SELECTED = 'ERROR_NO_PLAYER_SELECTED'

# Logger
_LOGGER = logging.getLogger(__name__)


def ensure_config(user_input):
	"""Đảm bảo các tham số cần thiết tồn tại và điền giá trị mặc định nếu thiếu."""
	out = {}
	out[CONF_NAME] = DOMAIN
	out[CONF_RECEIVERS] = ''
	out[CONF_INIT_DROPDOWNS] = DEFAULT_INIT_DROPDOWNS
	out[CONF_INIT_EXTRA_SENSOR] = DEFAULT_INIT_EXTRA_SENSOR
	out[CONF_DEBUG_AS_ERROR] = DEFAULT_DEBUG_AS_ERROR

	if user_input is not None:
		out.update(user_input)
	return out


def find_thumbnail(item):
	"""Tìm thumbnail từ item (tương thích với Zing MP3 format)."""
	item_thumbnail = ""
	try:
		# Zing MP3 trả về 'thumb' trực tiếp
		if 'thumb' in item:
			item_thumbnail = item['thumb']
		# Hoặc có thể có 'thumbnails' như YouTube format
		elif 'thumbnails' in item:
			if isinstance(item['thumbnails'], list) and len(item['thumbnails']) > 0:
				if isinstance(item['thumbnails'][-1], dict) and 'url' in item['thumbnails'][-1]:
					item_thumbnail = item['thumbnails'][-1]['url']
				elif isinstance(item['thumbnails'][-1], str):
					item_thumbnail = item['thumbnails'][-1]
	except:
		pass
	return item_thumbnail

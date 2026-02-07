"""Media player entity cho Zing MP3."""
import logging
import random
from typing import Any
from datetime import datetime, timezone

from homeassistant.components.media_player import (
	MediaPlayerEntity,
	MediaPlayerEntityFeature,
	ATTR_MEDIA_CONTENT_ID,
	ATTR_MEDIA_CONTENT_TYPE,
	SERVICE_PLAY_MEDIA,
	SERVICE_TURN_ON,
	SERVICE_TURN_OFF,
	SERVICE_MEDIA_PLAY,
	SERVICE_MEDIA_PAUSE,
	SERVICE_MEDIA_STOP,
	SERVICE_VOLUME_SET,
	SERVICE_VOLUME_UP,
	SERVICE_VOLUME_DOWN,
	SERVICE_VOLUME_MUTE,
	SERVICE_MEDIA_SEEK,
	SERVICE_SHUFFLE_SET,
	SERVICE_REPEAT_SET,
	ATTR_MEDIA_VOLUME_LEVEL,
	ATTR_MEDIA_VOLUME_MUTED,
	DOMAIN as DOMAIN_MP,
)
from homeassistant.components.media_player.const import MediaType, RepeatMode
from homeassistant.const import (
	ATTR_ENTITY_ID,
	STATE_OFF,
	STATE_IDLE,
	STATE_PLAYING,
	STATE_PAUSED,
)
from homeassistant.helpers import entity_platform
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.core import Event
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from .const import (
	DOMAIN, CONF_RECEIVERS, SUPPORT_ZINGMP3_PLAYER, 
	SERVICE_SEARCH, ATTR_QUERY, ATTR_FILTER, ATTR_LIMIT,
	SERVICE_CALL_METHOD, SERVICE_CALL_GOTO_TRACK, ATTR_COMMAND, ATTR_PARAMETERS
)
from .utils import get_featured_items, get_zmp3_cookie, get_stream_link_by_id, get_playlist_items

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
	"""Không hỗ trợ YAML setup cho Zing MP3."""
	_LOGGER.debug("Zing MP3 does not support YAML setup, use config_flow instead.")


async def async_setup_entry(hass, config, async_add_entities):
	"""Set up từ config entry."""
	_LOGGER.debug("Config via Storage/UI")
	if len(config.data) > 0 or len(config.options) > 0:
		async_add_entities([ZingMp3Player(hass, config)], update_before_add=True)


class ZingMp3Player(MediaPlayerEntity):
	"""MediaPlayerEntity cho Zing MP3."""

	_should_poll = False

	def __init__(self, hass, config_entry):
		"""Initialize Zing MP3 player."""
		self.hass = hass
		self._attr_unique_id = config_entry.entry_id
		configuration = dict(config_entry.options or config_entry.data)

		self._org_name = configuration.get("name") or "Zing MP3"
		self._attr_name = self._org_name

		self._state = STATE_OFF
		self._playing = False
		self._volume = 0.0
		self._is_mute = False
		self._attr_shuffle = False
		self._attr_repeat = RepeatMode.OFF

		# Track info
		self._track_title: str | None = None
		self._track_artist: str | None = None
		self._track_album_name: str | None = None
		self._track_album_cover: str | None = None
		self._media_duration: int | None = None
		self._media_position: float | None = None
		self._media_position_updated: datetime | None = None
		self._current_song_id: str | None = None
		self._audio_url: str | None = None
		
		# Tracks list (để hiển thị trong cur_playlists)
		self._tracks: list[dict[str, Any]] = []
		self._next_track_no = 0
		self._last_auto_advance: datetime | None = None
		self._allow_next = False

		self._attributes: dict[str, Any] = {}
		
		# Search state (để browse_media có thể lấy kết quả)
		self._search = {"query": "", "filter": None, "limit": 20}
		# Lưu kết quả search để có thể tìm lại thông tin bài hát
		self._search_results: list[dict[str, Any]] = []
		# Lưu danh sách bài hát của playlist đang browse (để khi click bài trong playlist có thể load đúng)
		self._current_playlist_songs: list[dict[str, Any]] = []
		self._current_playlist_id: str | None = None
		
		# Track remote player state changes
		self._untrack_remote_player = None

		# Speakers configuration
		self._speakers_list = configuration.get(CONF_RECEIVERS) or []
		if isinstance(self._speakers_list, str):
			self._speakers_list = [s.strip() for s in self._speakers_list.split(",") if s.strip()]

		self._remote_player: str | None = None

		# Đảm bảo vùng dữ liệu cho integration
		hass.data.setdefault(DOMAIN, {})
		hass.data[DOMAIN].setdefault(self._attr_unique_id, {})
		hass.data[DOMAIN][self._attr_unique_id]["media_player"] = self
		hass.data[DOMAIN][self._attr_unique_id]['total_tracks'] = 0

		# Register services
		platform = entity_platform.current_platform.get()
		platform.async_register_entity_service(
			SERVICE_CALL_METHOD,
			{
				vol.Required(ATTR_COMMAND): cv.string,
				vol.Optional(ATTR_PARAMETERS): vol.All(
					cv.ensure_list, vol.Length(min=1), [cv.string]
				),
			},
			"async_call_method",
		)
		platform.async_register_entity_service(
			SERVICE_SEARCH,
			{
				vol.Required(ATTR_QUERY): cv.string,
				vol.Optional(ATTR_FILTER): cv.string,
				vol.Optional(ATTR_LIMIT): vol.Coerce(int)
			},
			"async_search",
		)

	@property
	def device_info(self):
		"""Return device info để entity thuộc về device Zing MP3."""
		return {
			'identifiers': {(DOMAIN, self._attr_unique_id)},
			'name': self._attr_name,
			'manufacturer': "smarthomeblack",
			'model': "Zing MP3 Player"
		}

	@property
	def should_poll(self) -> bool:
		"""Return False vì không cần polling."""
		return False

	@property
	def name(self):
		"""Return tên của entity."""
		return self._attr_name

	@property
	def icon(self):
		"""Return icon."""
		return "mdi:music-circle"

	@property
	def state(self):
		"""Return state của player."""
		return self._state

	@property
	def supported_features(self) -> MediaPlayerEntityFeature:
		"""Return supported features."""
		return SUPPORT_ZINGMP3_PLAYER

	@property
	def media_content_type(self):
		"""Return media content type."""
		return MediaType.MUSIC

	@property
	def media_title(self):
		"""Return title của bài hát hiện tại."""
		return self._track_title

	@property
	def media_artist(self):
		"""Return artist của bài hát hiện tại."""
		return self._track_artist

	@property
	def media_image_url(self):
		"""Return URL của album cover."""
		return self._track_album_cover
	
	@property
	def media_album_name(self):
		"""Return album name của bài hát."""
		return self._track_album_name

	@property
	def media_duration(self):
		"""Return duration của bài hát."""
		return self._media_duration
	
	@property
	def media_position(self):
		"""Return position của bài hát đang phát (seconds)."""
		return self._media_position
	
	@property
	def media_position_updated_at(self):
		"""Return thời gian cập nhật position."""
		return self._media_position_updated

	@property
	def extra_state_attributes(self):
		"""Return extra state attributes."""
		return self._attributes

	@property
	def volume_level(self):
		"""Return volume level."""
		return self._volume

	@property
	def is_volume_muted(self):
		"""Return True nếu đang mute."""
		return self._is_mute

	@property
	def is_on(self):
		"""Return True nếu player đang on."""
		return self._state not in (STATE_OFF,)

	async def _async_ensure_remote_player(self) -> bool:
		"""Đảm bảo đã chọn được media_player đích để phát nhạc."""
		if self._remote_player and self.hass.states.get(self._remote_player):
			# Track state changes của remote player
			if self._untrack_remote_player is None:
				self._untrack_remote_player = async_track_state_change_event(
					self.hass, self._remote_player, self.async_sync_player
				)
			return True

		# Ưu tiên dùng danh sách speakers cấu hình
		for cand in self._speakers_list:
			entity_id = cand
			if not entity_id.startswith(DOMAIN_MP + "."):
				entity_id = f"{DOMAIN_MP}.{entity_id}"
			# Tránh chọn chính nó làm remote player
			if entity_id != self.entity_id and self.hass.states.get(entity_id):
				self._remote_player = entity_id
				_LOGGER.debug("Selected %s as Zing MP3 output player", entity_id)
				# Track state changes của remote player
				if self._untrack_remote_player is None:
					self._untrack_remote_player = async_track_state_change_event(
						self.hass, self._remote_player, self.async_sync_player
					)
				return True

		# Fallback: tìm bất kỳ media_player nào khác trong hệ thống (tránh chính nó)
		for s in self.hass.states.async_all(DOMAIN_MP):
			if s.entity_id != self.entity_id:
				self._remote_player = s.entity_id
				_LOGGER.debug("Auto-selected %s as Zing MP3 output player", s.entity_id)
				# Track state changes của remote player
				if self._untrack_remote_player is None:
					self._untrack_remote_player = async_track_state_change_event(
						self.hass, self._remote_player, self.async_sync_player
					)
				return True

		_LOGGER.error("No valid media_player found for Zing MP3 output")
		self._track_title = "No output player configured"
		self.async_schedule_update_ha_state()
		return False
	
	async def async_sync_player(self, event: Event):
		"""Sync state từ remote player (duration, position, etc) và xử lý auto-advance."""
		if not self._playing or not self._remote_player:
			return
		
		event_data = event.data
		entity_id = event_data.get('entity_id')
		old_state = event_data.get('old_state')
		new_state = event_data.get('new_state')
		
		if entity_id != self._remote_player or not new_state:
			return
		
		_player = new_state
		
		# Unlock allow_next khi có media_position
		try:
			if 'media_position' in _player.attributes:
				if isinstance(_player.attributes['media_position'], (int, float)):
					if _player.state == STATE_PLAYING and _player.attributes['media_position'] > 0:
						self._allow_next = True
		except:
			pass
		if not self._allow_next and _player.state == STATE_PLAYING:
			self._allow_next = True
		
		# Chỉ cập nhật duration và position nếu không đang pause
		# Giống như dự án gốc: "Only update the duration and especially the position if we're not in pause
		# else the mini-media-player will advance during our pause state"
		if self._state != STATE_PAUSED:
			if 'media_duration' in _player.attributes:
				self._media_duration = _player.attributes['media_duration']
			if 'media_position' in _player.attributes:
				self._media_position = _player.attributes['media_position']
			if 'media_position_updated_at' in _player.attributes:
				if isinstance(_player.attributes['media_position_updated_at'], datetime):
					self._media_position_updated = _player.attributes['media_position_updated_at']
				else:
					self._media_position_updated = datetime.now(timezone.utc)
			else:
				self._media_position_updated = datetime.now(timezone.utc)
		
		# Sync remote player state
		self._attributes['remote_player_state'] = _player.state
		
		# Auto-advance khi bài hát kết thúc
		if old_state is not None and new_state is not None:
			# Detect khi remote player chuyển từ PLAYING sang IDLE (bài hát kết thúc)
			if (old_state.state == STATE_PLAYING and new_state.state == STATE_IDLE and 
				self._allow_next and 
				(self._last_auto_advance is None or 
				 (datetime.now(timezone.utc) - self._last_auto_advance).total_seconds() > 10)):
				_LOGGER.debug("Track ended, auto-advancing...")
				self._allow_next = False
				self._last_auto_advance = datetime.now(timezone.utc)
				await self.async_get_next_track()
		
		self.async_schedule_update_ha_state()

	async def async_turn_on(self, **kwargs):
		"""Turn on player."""
		if not await self._async_ensure_remote_player():
			return
		data = {ATTR_ENTITY_ID: self._remote_player}
		await self.hass.services.async_call(DOMAIN_MP, SERVICE_TURN_ON, data)
		self._state = STATE_IDLE
		self.async_schedule_update_ha_state()

	async def async_turn_off(self, **kwargs):
		"""Turn off player."""
		if self._remote_player:
			data = {ATTR_ENTITY_ID: self._remote_player}
			await self.hass.services.async_call(DOMAIN_MP, SERVICE_MEDIA_STOP, data)
			await self.hass.services.async_call(DOMAIN_MP, SERVICE_TURN_OFF, data)
		self._playing = False
		self._state = STATE_OFF
		self.async_schedule_update_ha_state()

	async def _async_play_keyword(self, keyword: str):
		"""Tìm kiếm và phát bài hát theo keyword."""
		_LOGGER.debug(f"[S] _async_play_keyword for: {keyword}")
		self._state = STATE_PLAYING  # Optimistic update
		self.async_schedule_update_ha_state()

		try:
			# 1. Search for the song (chỉ lấy songs, không lấy playlists/albums)
			items = await self.hass.async_add_executor_job(get_featured_items, keyword, 10, "songs")
			if not items:
				_LOGGER.error(f"No songs found for keyword: {keyword}")
				await self.async_turn_off()
				return

			# Lưu kết quả search để có thể tìm lại sau
			self._search_results = items
			
			# Lưu tất cả kết quả vào tracks list để hỗ trợ shuffle/repeat
			self._tracks = items
			self._next_track_no = 0
			await self._tracks_to_attribute()
			# Clear playlist context khi search (không phải playlist)
			self._current_playlist_songs = []
			self._current_playlist_id = None
			
			# Nếu shuffle được bật, chọn bài ngẫu nhiên
			if self._attr_shuffle and len(items) > 1:
				self._next_track_no = random.randrange(len(items))

			# Take the selected result
			song_info = items[self._next_track_no]
			song_id = song_info.get('id')
			title = song_info.get('title', 'Unknown Title')
			artist = song_info.get('artist_name', 'Unknown Artist')
			thumbnail = song_info.get('thumb', '')
			duration = song_info.get('duration', 0)

			self._current_song_id = song_id
			self._track_title = title
			self._track_artist = artist
			self._track_album_cover = thumbnail
			self._media_duration = duration
			self._attributes['videoId'] = song_id  # Using videoId for consistency
			self._attributes['current_playlist_title'] = "Search Result"
			self._attributes['_media_type'] = MediaType.MUSIC
			self._attributes['_media_id'] = song_id
			self._attributes['current_track'] = self._next_track_no

			self.async_schedule_update_ha_state()

			# 2. Get Zing MP3 cookie
			zmp3_cookie = await self.hass.async_add_executor_job(get_zmp3_cookie)
			if not zmp3_cookie:
				_LOGGER.error("Failed to get Zing MP3 cookie.")
				await self.async_turn_off()
				return

			# 3. Get stream link
			audio_url = await self.hass.async_add_executor_job(get_stream_link_by_id, song_id, zmp3_cookie)
			if not audio_url:
				_LOGGER.error(f"Failed to get stream link for song ID: {song_id}")
				await self.async_turn_off()
				return

			self._audio_url = audio_url

			# Ensure remote player is ready
			if not await self._async_ensure_remote_player():
				_LOGGER.error("Remote player not ready.")
				return

			# 4. Play media on the remote player
			self._state = STATE_PLAYING
			self._playing = True

			# Gửi metadata đầy đủ như ytube_music_player
			data = {
				ATTR_MEDIA_CONTENT_ID: audio_url,
				ATTR_MEDIA_CONTENT_TYPE: MediaType.MUSIC,
				ATTR_ENTITY_ID: self._remote_player,
				"extra": {
					"metadata": {
						"metadataType": 3,  # Music metadata type
						"title": self._track_title or "Unknown Title",
						"artist": self._track_artist or "Unknown Artist",
						"albumName": self._attributes.get('current_playlist_title', ''),
						"images": [
							{
								"url": self._track_album_cover or ""
							}
						] if self._track_album_cover else []
					}
				}
			}
			_LOGGER.debug(f"- forwarding url to player {self._remote_player}: {audio_url} with metadata: title={self._track_title}, artist={self._track_artist}")
			await self.hass.services.async_call(DOMAIN_MP, SERVICE_PLAY_MEDIA, data)
			self.async_schedule_update_ha_state()

		except Exception as e:
			_LOGGER.error(f"Error playing Zing MP3 track: {e}", exc_info=True)
			await self.async_turn_off()

		_LOGGER.debug("[E] _async_play_keyword")

	async def async_play_media(self, media_type, media_id, **kwargs):
		"""Play media từ media_id.
		
		Nếu media_id là song_id (format Zing MP3), sẽ lấy stream link trực tiếp.
		Nếu không, sẽ search như keyword.
		"""
		_LOGGER.debug(f"[S] async_play_media, media_type: {media_type}, media_id: {media_id}")
		
		# Tránh vòng lặp: nếu media_id là URL (đã được forward từ chính nó), bỏ qua
		if media_id and ('http://' in media_id or 'https://' in media_id):
			_LOGGER.debug(f"Ignoring URL media_id to prevent loop: {media_id}")
			return
		
		# Xử lý playlist/album (hỗ trợ cả enum và string)
		# Zing MP3 không thể phát playlist trực tiếp bằng ID, phải lấy danh sách bài hát trước
		if media_type == MediaType.PLAYLIST or media_type == "playlist":
			await self._async_play_playlist(media_id)
			return
		
		# Kiểm tra xem media_id có phải là song_id không (format Zing MP3: chữ và số, thường dài)
		# Song_id thường có format như: ZW69BZOF, ZW6BZOF, etc.
		if media_id and len(media_id) >= 6 and media_id.isalnum() and not ' ' in media_id:
			# Có thể là song_id, thử play trực tiếp
			await self._async_play_song_id(media_id)
		else:
			# Không phải song_id, search như keyword
			await self._async_play_keyword(media_id)
		
		_LOGGER.debug("[E] async_play_media")

	async def _async_play_playlist(self, playlist_id: str):
		"""Phát playlist/album từ playlist_id."""
		_LOGGER.debug(f"[S] _async_play_playlist for: {playlist_id}")
		self._state = STATE_PLAYING  # Optimistic update
		self.async_schedule_update_ha_state()

		try:
			# 1. Get Zing MP3 cookie
			zmp3_cookie = await self.hass.async_add_executor_job(get_zmp3_cookie)
			if not zmp3_cookie:
				_LOGGER.error("Failed to get Zing MP3 cookie.")
				await self.async_turn_off()
				return

			# 2. Get playlist items
			playlist_data = await self.hass.async_add_executor_job(
				get_playlist_items, playlist_id, zmp3_cookie
			)
			if not playlist_data or not playlist_data.get("songs"):
				_LOGGER.error(f"No songs found in playlist: {playlist_id}")
				await self.async_turn_off()
				return

			# 3. Lưu danh sách bài hát vào tracks
			self._tracks = playlist_data["songs"]
			self._next_track_no = 0
			self._search_results = playlist_data["songs"]
			await self._tracks_to_attribute()
			# Lưu playlist context để khi click bài trong playlist có thể load đúng
			self._current_playlist_songs = playlist_data["songs"]
			self._current_playlist_id = playlist_id
			
			# Cập nhật attributes
			self._attributes['current_playlist_title'] = playlist_data.get("title", "Playlist")
			self._track_album_cover = playlist_data.get("thumb", "")
			
			# Nếu shuffle được bật, chọn bài ngẫu nhiên
			if self._attr_shuffle and len(self._tracks) > 1:
				self._next_track_no = random.randrange(len(self._tracks))

			# 4. Phát bài đầu tiên
			first_song = self._tracks[self._next_track_no]
			await self._async_play_song_id(first_song.get("id"))

		except Exception as e:
			_LOGGER.error(f"Error playing playlist: {e}", exc_info=True)
			await self.async_turn_off()

	async def _async_play_song_id(self, song_id: str):
		"""Phát bài hát trực tiếp từ song_id (không cần search)."""
		_LOGGER.debug(f"[S] _async_play_song_id for: {song_id}")
		
		try:
			# Ensure remote player is ready
			if not await self._async_ensure_remote_player():
				_LOGGER.error("Remote player not ready.")
				return
			
			# 1. Get Zing MP3 cookie
			zmp3_cookie = await self.hass.async_add_executor_job(get_zmp3_cookie)
			if not zmp3_cookie:
				_LOGGER.error("Failed to get Zing MP3 cookie.")
				await self.async_turn_off()
				return
			
			# 2. Get stream link
			audio_url = await self.hass.async_add_executor_job(get_stream_link_by_id, song_id, zmp3_cookie)
			if not audio_url:
				_LOGGER.error(f"Failed to get stream link for song ID: {song_id}")
				await self.async_turn_off()
				return
			
			self._current_song_id = song_id
			self._audio_url = audio_url
			
			# Update attributes (có thể lấy thêm thông tin từ API nếu cần)
			self._attributes['videoId'] = song_id
			self._attributes['_media_type'] = MediaType.MUSIC
			self._attributes['_media_id'] = song_id
			
			# Kiểm tra xem bài này có thuộc playlist đang browse không
			# Nếu có, dùng danh sách bài hát của playlist đó
			track_info = None
			track_index = -1
			use_playlist_tracks = False
			
			# Ưu tiên tìm trong playlist đang browse (nếu có)
			if self._current_playlist_songs:
				for idx, track in enumerate(self._current_playlist_songs):
					if track.get('id') == song_id:
						track_info = track
						track_index = idx
						use_playlist_tracks = True
						break
			
			# Nếu không tìm thấy trong playlist, tìm trong search_results
			if not track_info and self._search_results:
				for idx, track in enumerate(self._search_results):
					if track.get('id') == song_id:
						track_info = track
						track_index = idx
						break
			
			# Nếu vẫn không tìm thấy, tạo track info từ thông tin hiện tại
			if not track_info:
				track_info = {
					'id': song_id,
					'title': self._track_title or 'Unknown Title',
					'artist_name': self._track_artist or 'Unknown Artist',
					'thumb': self._track_album_cover or '',
					'duration': self._media_duration or 0
				}
				# Nếu có _tracks, tìm index trong đó
				for idx, track in enumerate(self._tracks):
					if track.get('id') == song_id:
						track_index = idx
						break
			else:
				# Cập nhật thông tin từ track_info tìm được
				self._track_title = track_info.get('title', self._track_title)
				self._track_artist = track_info.get('artist_name', self._track_artist)
				self._track_album_cover = track_info.get('thumb', self._track_album_cover)
				self._media_duration = track_info.get('duration', self._media_duration)
			
			# Set tracks list: ưu tiên playlist đang browse, sau đó là search_results
			if use_playlist_tracks and self._current_playlist_songs:
				# Dùng danh sách bài hát của playlist đang browse
				self._tracks = self._current_playlist_songs
				self._search_results = self._current_playlist_songs
				if self._current_playlist_id:
					self._attributes['current_playlist_title'] = f"Playlist {self._current_playlist_id}"
				if track_index >= 0:
					self._next_track_no = track_index
				else:
					self._next_track_no = 0
			elif self._search_results:
				# Dùng search_results (danh sách từ search)
				self._tracks = self._search_results
				if track_index >= 0:
					self._next_track_no = track_index
				else:
					self._next_track_no = 0
			else:
				# Nếu không có gì, chỉ lưu bài hiện tại
				self._tracks = [track_info]
				self._next_track_no = 0
			
			self._attributes['current_track'] = self._next_track_no
			await self._tracks_to_attribute()
			
			# 3. Play media on the remote player
			self._state = STATE_PLAYING
			self._playing = True
			
			# Gửi metadata đầy đủ như ytube_music_player
			data = {
				ATTR_MEDIA_CONTENT_ID: audio_url,
				ATTR_MEDIA_CONTENT_TYPE: MediaType.MUSIC,
				ATTR_ENTITY_ID: self._remote_player,
				"extra": {
					"metadata": {
						"metadataType": 3,  # Music metadata type
						"title": self._track_title or "Unknown Title",
						"artist": self._track_artist or "Unknown Artist",
						"albumName": self._attributes.get('current_playlist_title', ''),
						"images": [
							{
								"url": self._track_album_cover or ""
							}
						] if self._track_album_cover else []
					}
				}
			}
			_LOGGER.debug(f"- forwarding url to player {self._remote_player}: {audio_url} with metadata: title={self._track_title}, artist={self._track_artist}")
			await self.hass.services.async_call(DOMAIN_MP, SERVICE_PLAY_MEDIA, data)
			self.async_schedule_update_ha_state()
			
		except Exception as e:
			_LOGGER.error(f"Error playing Zing MP3 track by ID: {e}", exc_info=True)
			await self.async_turn_off()
		
		_LOGGER.debug("[E] _async_play_song_id")

	async def async_search(self, query: str, filter: str = None, limit: int = None):
		"""Search và lưu query để browse_media có thể hiển thị kết quả.
		
		Thực hiện search ngay khi được gọi và lưu kết quả vào _search_results.
		
		Args:
			query: Từ khóa tìm kiếm
			filter: Filter (tương thích với code cũ, không sử dụng cho Zing MP3)
			limit: Limit số lượng kết quả (mặc định 20)
		"""
		_LOGGER.debug(f"[S] async_search, query: {query}, filter: {filter}, limit: {limit}")
		
		# Lưu query vào _search để browse_media có thể lấy kết quả
		self._search['query'] = query
		self._search['filter'] = filter
		self._search['limit'] = limit or 20
		
		# Thực hiện search ngay và lưu kết quả vào _search_results
		try:
			# Map filter từ JS: "songs" -> "songs", "playlists" -> "playlists", "albums" -> "albums", "all" -> None
			filter_type = filter
			if filter_type == "all":
				filter_type = None
			
			# Lấy kết quả search từ Zing MP3 với filter
			_LOGGER.debug(f"Calling get_featured_items with query='{query}', limit={self._search['limit']}, filter_type='{filter_type}'")
			search_results = await self.hass.async_add_executor_job(
				get_featured_items, query, self._search['limit'], filter_type
			)
			_LOGGER.debug(f"get_featured_items returned {len(search_results)} results")
			
			# Lưu kết quả search vào player để có thể tìm lại sau
			self._search_results = search_results
			
			# Format search results để lưu vào extra_sensor (giống ytube_music_player)
			formatted_search_results = []
			for item in search_results:
				item_type = item.get("type", "songs")
				formatted_item = {
					'type': item_type,
					'title': item.get("title", ""),
					'id': item.get("id", ""),
					'thumbnail': item.get("thumb", ""),
					'artist_name': item.get("artist_name", "")
				}
				formatted_search_results.append(formatted_item)
			
			# Lưu vào extra_sensor để dùng trong automation
			await self.async_update_extra_sensor('search', formatted_search_results)
			
			_LOGGER.debug(f"Search completed, found {len(search_results)} results")
			
		except Exception as e:
			_LOGGER.error(f"Error during search: {e}", exc_info=True)
			self._search_results = []
			await self.async_update_extra_sensor('search', [])
		
		_LOGGER.debug("[E] async_search")

	async def async_media_play(self):
		"""Play media."""
		_LOGGER.debug("media_play")
		if self._remote_player:
			data = {ATTR_ENTITY_ID: self._remote_player}
			await self.hass.services.async_call(DOMAIN_MP, SERVICE_MEDIA_PLAY, data)
			self._state = STATE_PLAYING
			self._playing = True
			# Khi play lại, cần lấy lại position từ remote player
			# async_sync_player sẽ tự động cập nhật khi remote player state thay đổi
			self.async_schedule_update_ha_state()

	async def async_media_pause(self):
		"""Pause media."""
		_LOGGER.debug("media_pause")
		# Set state to PAUSED first
		self._state = STATE_PAUSED
		# Set media_position to None để JS không tính toán progress khi pause
		# Giống như dự án gốc: "set it to none, otherwise player like mini-media-player will continue"
		self._media_position = None
		self.async_schedule_update_ha_state()
		
		if self._remote_player:
			data = {ATTR_ENTITY_ID: self._remote_player}
			await self.hass.services.async_call(DOMAIN_MP, SERVICE_MEDIA_PAUSE, data)

	async def async_media_stop(self):
		"""Stop media."""
		if self._remote_player and self._remote_player != self.entity_id:
			data = {ATTR_ENTITY_ID: self._remote_player}
			await self.hass.services.async_call(DOMAIN_MP, SERVICE_MEDIA_STOP, data)
		self._playing = False
		self._state = STATE_IDLE
		self.async_schedule_update_ha_state()

	async def async_set_volume_level(self, volume):
		"""Set volume level."""
		if self._remote_player:
			data = {
				ATTR_ENTITY_ID: self._remote_player,
				ATTR_MEDIA_VOLUME_LEVEL: volume
			}
			await self.hass.services.async_call(DOMAIN_MP, SERVICE_VOLUME_SET, data)
			self._volume = volume
			self.async_schedule_update_ha_state()

	async def async_volume_up(self):
		"""Volume up."""
		if self._remote_player:
			data = {ATTR_ENTITY_ID: self._remote_player}
			await self.hass.services.async_call(DOMAIN_MP, SERVICE_VOLUME_UP, data)
			self.async_schedule_update_ha_state()

	async def async_volume_down(self):
		"""Volume down."""
		if self._remote_player:
			data = {ATTR_ENTITY_ID: self._remote_player}
			await self.hass.services.async_call(DOMAIN_MP, SERVICE_VOLUME_DOWN, data)
			self.async_schedule_update_ha_state()

	async def async_mute_volume(self, mute):
		"""Mute/unmute volume."""
		if self._remote_player:
			data = {ATTR_ENTITY_ID: self._remote_player}
			data[ATTR_MEDIA_VOLUME_MUTED] = mute
			await self.hass.services.async_call(DOMAIN_MP, SERVICE_VOLUME_MUTE, data)
			self._is_mute = mute
			self.async_schedule_update_ha_state()

	async def async_media_previous_track(self):
		"""Previous track."""
		if not self._playing or not self._tracks:
			return
		
		_LOGGER.debug(f"[S] async_media_previous_track, current={self._next_track_no}, shuffle={self._attr_shuffle}")
		self._allow_next = False
		
		if self._attr_shuffle:
			# Shuffle mode: chọn bài ngẫu nhiên
			self._next_track_no = random.randrange(len(self._tracks))
			_LOGGER.debug(f"Shuffle: selected track {self._next_track_no}")
		else:
			# Normal mode: quay lại bài trước
			self._next_track_no = max(self._next_track_no - 1, 0)
			_LOGGER.debug(f"Normal: previous track {self._next_track_no}")
		
		# Lấy bài hát từ tracks list
		try:
			track = self._tracks[self._next_track_no]
			song_id = track.get('id')
			if not song_id:
				_LOGGER.error(f"Track {self._next_track_no} has no ID")
				return
			
			self._attributes['current_track'] = self._next_track_no
			await self._async_play_song_id(song_id)
		except IndexError:
			_LOGGER.error(f"Track index {self._next_track_no} out of range")
		except Exception as e:
			_LOGGER.error(f"Error playing previous track: {e}", exc_info=True)
		
		_LOGGER.debug("[E] async_media_previous_track")

	async def async_media_next_track(self):
		"""Next track."""
		if not self._playing or not self._tracks:
			return
		
		_LOGGER.debug(f"[S] async_media_next_track, current={self._next_track_no}, shuffle={self._attr_shuffle}")
		self._allow_next = False
		
		if self._attr_shuffle:
			# Shuffle mode: chọn bài ngẫu nhiên
			self._next_track_no = random.randrange(len(self._tracks))
			_LOGGER.debug(f"Shuffle: selected track {self._next_track_no}")
		else:
			# Normal mode: chọn bài tiếp theo
			self._next_track_no = self._next_track_no + 1
			if self._next_track_no >= len(self._tracks):
				# Nếu hết danh sách và repeat ALL, quay lại đầu
				if self._attr_repeat == RepeatMode.ALL:
					self._next_track_no = 0
				else:
					_LOGGER.info("End of playlist")
					return
			_LOGGER.debug(f"Normal: next track {self._next_track_no}")
		
		# Lấy bài hát từ tracks list
		try:
			track = self._tracks[self._next_track_no]
			song_id = track.get('id')
			if not song_id:
				_LOGGER.error(f"Track {self._next_track_no} has no ID")
				return
			
			self._attributes['current_track'] = self._next_track_no
			await self._async_play_song_id(song_id)
		except IndexError:
			_LOGGER.error(f"Track index {self._next_track_no} out of range")
		except Exception as e:
			_LOGGER.error(f"Error playing next track: {e}", exc_info=True)
		
		_LOGGER.debug("[E] async_media_next_track")

	async def async_media_seek(self, position):
		"""Seek to position."""
		if self._remote_player:
			data = {
				ATTR_ENTITY_ID: self._remote_player,
				"seek_position": position
			}
			await self.hass.services.async_call(DOMAIN_MP, SERVICE_MEDIA_SEEK, data)
			self.async_schedule_update_ha_state()

	async def async_set_shuffle(self, shuffle):
		"""Set shuffle mode."""
		_LOGGER.debug(f"Setting shuffle: {shuffle}")
		self._attr_shuffle = shuffle
		self.async_schedule_update_ha_state()

	async def async_set_repeat(self, repeat):
		"""Set repeat mode."""
		_LOGGER.debug(f"Setting repeat: {repeat}")
		self._attr_repeat = repeat
		self.async_schedule_update_ha_state()
	
	@property
	def shuffle(self):
		"""Return shuffle state."""
		return self._attr_shuffle
	
	@property
	def repeat(self):
		"""Return repeat mode."""
		return self._attr_repeat
	
	async def async_get_next_track(self):
		"""Lấy bài hát tiếp theo dựa trên shuffle/repeat mode."""
		_LOGGER.debug(f"[S] async_get_next_track, shuffle={self._attr_shuffle}, repeat={self._attr_repeat}, tracks={len(self._tracks)}")
		
		if not self._tracks:
			_LOGGER.warning("No tracks available for next track")
			await self.async_turn_off()
			return
		
		# Xử lý repeat mode ONE - lặp lại bài hiện tại
		if self._attr_repeat == RepeatMode.ONE:
			_LOGGER.debug("Repeat ONE: playing same track")
			await self._async_play_song_id(self._current_song_id)
			return
		
		# Xử lý shuffle mode
		if self._attr_shuffle:
			self._next_track_no = random.randrange(len(self._tracks))
			_LOGGER.debug(f"Shuffle: selected track {self._next_track_no}")
		else:
			# Normal mode: chọn bài tiếp theo
			self._next_track_no = self._next_track_no + 1
			_LOGGER.debug(f"Normal: next track {self._next_track_no}")
			
			# Kiểm tra nếu đã hết danh sách
			if self._next_track_no >= len(self._tracks):
				if self._attr_repeat == RepeatMode.ALL:
					# Repeat ALL: quay lại đầu danh sách
					self._next_track_no = 0
					_LOGGER.debug("Repeat ALL: restarting from beginning")
				else:
					# Không repeat: tắt player
					_LOGGER.info("End of playlist, turning off")
					await self.async_turn_off()
					return
		
		# Lấy bài hát từ tracks list
		try:
			track = self._tracks[self._next_track_no]
			song_id = track.get('id')
			if not song_id:
				_LOGGER.error(f"Track {self._next_track_no} has no ID")
				await self.async_turn_off()
				return
			
			self._attributes['current_track'] = self._next_track_no
			await self._async_play_song_id(song_id)
		except IndexError:
			_LOGGER.error(f"Track index {self._next_track_no} out of range")
			await self.async_turn_off()
		except Exception as e:
			_LOGGER.error(f"Error getting next track: {e}", exc_info=True)
			await self.async_turn_off()

	async def async_select_source(self, source):
		"""Select source (speaker)."""
		entity_id = source
		if not entity_id.startswith(DOMAIN_MP + "."):
			entity_id = f"{DOMAIN_MP}.{entity_id}"
		if self.hass.states.get(entity_id):
			self._remote_player = entity_id
			_LOGGER.debug("Selected %s as Zing MP3 output player", entity_id)
			self.async_schedule_update_ha_state()

	@property
	def source_list(self):
		"""Return list of available sources."""
		sources = []
		for s in self.hass.states.async_all(DOMAIN_MP):
			if s.entity_id != self.entity_id:
				sources.append(s.entity_id)
		return sources

	@property
	def source(self):
		"""Return current source."""
		return self._remote_player

	async def async_update_extra_sensor(self, attribute, value):
		"""Update extra sensor attribute (giống ytube_music_player).
		
		Args:
			attribute: Tên attribute (e.g., 'search', 'tracks', 'total_tracks')
			value: Giá trị để lưu
		"""
		_LOGGER.debug(f"[S] async_update_extra_sensor, attribute: {attribute}, value type: {type(value)}")
		self.hass.data[DOMAIN][self._attr_unique_id][attribute] = value
		
		# Luôn lưu vào hass.data, dù có extra_sensor hay không
		_LOGGER.debug(f"Saved to hass.data[{DOMAIN}][{self._attr_unique_id}][{attribute}]")
		
		if self.hass.data[DOMAIN][self._attr_unique_id].get('extra_sensor'):
			try:
				_LOGGER.debug("Extra sensor exists, calling async_update")
				await self.hass.data[DOMAIN][self._attr_unique_id]['extra_sensor'].async_update()
			except Exception as e:
				_LOGGER.error(f"Update extra_sensor failed: {e}", exc_info=True)
		else:
			_LOGGER.debug("Extra sensor not found or not enabled")
		_LOGGER.debug("[E] async_update_extra_sensor")

	async def _tracks_to_attribute(self):
		"""Convert tracks list thành attributes để expose qua extra_sensor (giống ytube_music_player)."""
		_LOGGER.debug("[S] _tracks_to_attribute")
		await self.async_update_extra_sensor('total_tracks', len(self._tracks))
		
		track_attributes = []
		for track in self._tracks:
			title = track.get("title", "Unknown Title")
			artist = track.get("artist_name", "Unknown Artist")
			track_attributes.append(f"{artist} - {title}")
		
		await self.async_update_extra_sensor('tracks', track_attributes)
		_LOGGER.debug("[E] _tracks_to_attribute")

	async def async_call_method(self, command=None, parameters=None):
		"""Handle call_method service calls.
		
		Args:
			command: Command name (e.g., "goto_track")
			parameters: List of parameters for the command
		"""
		_LOGGER.debug(f"[S] async_call_method, command: {command}, parameters: {parameters}")
		
		if not command:
			_LOGGER.error("No command provided to async_call_method")
			return
		
		# Convert parameters to list if it's a single value
		all_params = []
		if parameters:
			if isinstance(parameters, str):
				all_params = [parameters]
			elif isinstance(parameters, list):
				all_params = parameters
			else:
				all_params = [str(parameters)]
		
		if command == SERVICE_CALL_GOTO_TRACK:
			if not all_params or len(all_params) == 0:
				_LOGGER.error("goto_track requires a track number parameter")
				return
			
			try:
				# Parameters[0] should be the track number (1-based index from frontend)
				track_num = int(all_params[0])
				_LOGGER.debug(f"Going to Track {track_num} (1-based)")
				
				if not self._tracks or len(self._tracks) == 0:
					_LOGGER.warning("No tracks available to goto")
					return
				
				# Convert to 0-based index and clamp to valid range
				self._next_track_no = min(max(track_num - 1, 0), len(self._tracks) - 1)
				_LOGGER.debug(f"Set next_track_no to {self._next_track_no} (0-based)")
				
				# Store current shuffle setting and temporarily disable it
				# (otherwise async_get_next_track might override next_track_no)
				prev_shuffle = self._attr_shuffle
				self._attr_shuffle = False
				
				# Get and play the track
				track = self._tracks[self._next_track_no]
				song_id = track.get('id')
				if not song_id:
					_LOGGER.error(f"Track {self._next_track_no} has no ID")
					self._attr_shuffle = prev_shuffle
					return
				
				self._attributes['current_track'] = self._next_track_no
				await self._async_play_song_id(song_id)
				
				# Restore shuffle setting
				self._attr_shuffle = prev_shuffle
				
			except (ValueError, IndexError) as e:
				_LOGGER.error(f"Error in goto_track: {e}")
		else:
			_LOGGER.warning(f"Command '{command}' not implemented in async_call_method")
		
		_LOGGER.debug("[E] async_call_method")

	async def async_browse_media(self, media_content_type=None, media_content_id=None):
		"""Browse media - delegate to browse_media module."""
		from .browse_media import async_browse_media
		return await async_browse_media(self, media_content_type, media_content_id)

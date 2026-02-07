"""Support cho media browsing của Zing MP3."""
import logging
from homeassistant.components.media_player import BrowseError, BrowseMedia
from homeassistant.components.media_player.const import MediaType, MediaClass
from .utils import get_featured_items, get_playlist_items

_LOGGER = logging.getLogger(__name__)

SEARCH = 'search'
SEARCH_TITLE = "Kết quả tìm kiếm"
CUR_PLAYLIST = 'cur_playlists'
CUR_PLAYLIST_TITLE = "Bài đang phát"
CUR_PLAYLIST_COMMAND = "PLAYLIST_GOTO_TRACK"


async def async_browse_media(player, media_content_type=None, media_content_id=None):
	"""Browse media cho Zing MP3.
	
	Hỗ trợ tìm kiếm và hiển thị kết quả.
	Media browser sẽ được mở rộng trong tương lai để hỗ trợ playlists và albums của Zing MP3.
	"""
	_LOGGER.debug(f"Browse media called: type={media_content_type}, id={media_content_id}")
	
	# Root level
	if media_content_type is None:
		title = "Zing MP3"
		children = []
		
		# Thêm search results nếu có query
		if player._search.get("query", ""):
			children.append(
				BrowseMedia(
					title=f'Kết quả tìm kiếm: "{player._search.get("query", "")}"',
					media_class=MediaClass.DIRECTORY,
					media_content_type=SEARCH,
					media_content_id="",
					can_play=False,
					can_expand=True,
					thumbnail=""
				)
			)
		
		return BrowseMedia(
			title=title,
			media_class=MediaClass.DIRECTORY,
			media_content_id="",
			media_content_type="",
			can_play=False,
			can_expand=True,
			children=children
		)
	
	# Xử lý search results
	if media_content_type == SEARCH:
		query = player._search.get("query", "")
		limit = player._search.get("limit", 20)
		
		if not query:
			raise BrowseError("Không có query để tìm kiếm")
		
		# Lấy filter từ search state
		filter_type = player._search.get("filter")
		# Map filter từ JS: "songs" -> "songs", "playlists" -> "playlists", "albums" -> "albums", "all" -> None
		if filter_type == "all":
			filter_type = None
		
		# Lấy kết quả search từ Zing MP3 với filter
		search_results = await player.hass.async_add_executor_job(
			get_featured_items, query, limit, filter_type
		)
		
		# Lưu kết quả search vào player để có thể tìm lại sau
		player._search_results = search_results
		
		children = []
		for item in search_results:
			title = item.get("title", "")
			item_type = item.get("type", "songs")
			
			# Xác định media_class và media_content_type dựa vào loại item
			if item_type == "songs":
				media_class = MediaClass.TRACK
				media_content_type_result = MediaType.MUSIC
				can_expand = False
				if item.get("artist_name"):
					title = f"{item['artist_name']} - {title}"
			elif item_type in ["playlists", "albums"]:
				media_class = MediaClass.PLAYLIST
				media_content_type_result = MediaType.PLAYLIST
				can_expand = True
			else:
				media_class = MediaClass.TRACK
				media_content_type_result = MediaType.MUSIC
				can_expand = False
			
			children.append(
				BrowseMedia(
					title=title,
					media_class=media_class,
					media_content_type=media_content_type_result,
					media_content_id=item.get("id", ""),
					can_play=True,
					can_expand=can_expand,
					thumbnail=item.get("thumb", "")
				)
			)
		
		return BrowseMedia(
			title=f'{SEARCH_TITLE}: "{query}"',
			media_class=MediaClass.DIRECTORY,
			media_content_id="",
			media_content_type=SEARCH,
			can_play=False,
			can_expand=True,
			children=children,
			thumbnail=""
		)
	
	# Xử lý playlist/album (hiển thị danh sách bài hát trong playlist)
	if media_content_type == MediaType.PLAYLIST:
		playlist_id = media_content_id
		if not playlist_id:
			raise BrowseError("Không có playlist ID")
		
		# Lấy danh sách bài hát từ playlist
		playlist_data = await player.hass.async_add_executor_job(
			get_playlist_items, playlist_id
		)
		
		if not playlist_data or not playlist_data.get("songs"):
			raise BrowseError(f"Không lấy được danh sách bài hát từ playlist {playlist_id}")
		
		# Lưu danh sách bài hát vào player để khi click bài có thể load đúng playlist
		player._current_playlist_songs = playlist_data["songs"]
		player._current_playlist_id = playlist_id
		
		children = []
		for song in playlist_data["songs"]:
			title = song.get("title", "")
			if song.get("artist_name"):
				title = f"{song['artist_name']} - {title}"
			
			children.append(
				BrowseMedia(
					title=title,
					media_class=MediaClass.TRACK,
					media_content_type=MediaType.MUSIC,
					media_content_id=song.get("id", ""),
					can_play=True,
					can_expand=False,
					thumbnail=song.get("thumb", "")
				)
			)
		
		return BrowseMedia(
			title=playlist_data.get("title", "Playlist"),
			media_class=MediaClass.PLAYLIST,
			media_content_id=playlist_id,
			media_content_type=MediaType.PLAYLIST,
			can_play=False,
			can_expand=True,
			children=children,
			thumbnail=playlist_data.get("thumb", "")
		)
	
	# Xử lý cur_playlists (danh sách bài đang phát)
	if media_content_type == CUR_PLAYLIST:
		children = []
		for i, track in enumerate(player._tracks, 1):
			title = track.get("title", "")
			if track.get("artist_name"):
				title = f"{track['artist_name']} - {title}"
			
			children.append(
				BrowseMedia(
					title=title,
					media_class=MediaClass.TRACK,
					media_content_type=CUR_PLAYLIST_COMMAND,
					media_content_id=str(i),
					can_play=True,
					can_expand=False,
					thumbnail=track.get("thumb", "")
				)
			)
		
		return BrowseMedia(
			title=CUR_PLAYLIST_TITLE,
			media_class=MediaClass.DIRECTORY,
			media_content_id="",
			media_content_type=CUR_PLAYLIST,
			can_play=False,
			can_expand=True,
			children=children,
			thumbnail=""
		)
	
	# Chưa hỗ trợ các loại khác
	raise BrowseError(f"Media browsing chưa được hỗ trợ cho type: {media_content_type}")

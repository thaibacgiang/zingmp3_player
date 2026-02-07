"""Utilities cho Zing MP3 API integration."""
import time
import requests
import hashlib
import hmac
import re

# Headers cho Zing MP3 API requests
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Referer": "https://zingmp3.vn/",
    "Origin": "https://zingmp3.vn",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Connection": "keep-alive",
    "Priority": "u=4",
    "TE": "trailers"
}

BASE_URL = "https://zingmp3.vn"
URL_SEARCH = "https://ac.zingmp3.vn/v1/web/featured"
API_KEY = "88265e23d4284f25963e6eedac8fbfa3"
SECRET_KEY = "2aa2d1c561e809b267f3638c4a307aab"
VERSION = "1.6.34"


def get_hash256(s: str) -> str:
    """Tính SHA256 hash."""
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def get_hmac512(s: str, key: str) -> str:
    """Tính HMAC-SHA512."""
    return hmac.new(key.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()


def hash_param(path: str, song_id: str, ctime: str) -> str:
    """Tính signature cho Zing MP3 API request."""
    raw = f"ctime={ctime}id={song_id}version={VERSION}"
    return get_hmac512(path + get_hash256(raw), SECRET_KEY)


def get_zmp3_cookie() -> str:
    """Lấy cookie zmp3_rqid từ trang chủ Zing MP3."""
    resp = requests.get(BASE_URL, headers=headers)
    set_cookie = resp.headers.get('Set-Cookie') or resp.headers.get('set-cookie', '')
    zmp3_cookie = ''
    match = re.search(r'zmp3_rqid=[^;]+', set_cookie)
    if match:
        zmp3_cookie = match.group(0)
    return zmp3_cookie


def get_featured_items(keyword: str, limit: int = 10, filter_type: str = None) -> list:
	"""Tìm kiếm trên Zing MP3 theo keyword và filter type.
	
	Args:
		keyword: Từ khóa tìm kiếm
		limit: Số lượng kết quả tối đa cần lấy (mặc định 10)
		filter_type: Loại filter - "songs", "playlists", "albums", "artists", hoặc None (tất cả)
	
	Returns:
		List các dict chứa: id, title, thumb, link, lyricLink, artist_name, duration, type
		(tối đa `limit` kết quả)
	"""
	params = {
		"query": keyword,
		"allowCorrect": "1",
		"ctime": str(int(time.time())),
		"version": "1.17.2"
	}
	response = requests.get(URL_SEARCH, headers=headers, params=params)
	try:
		data = response.json()
	except Exception as e:
		print(f"[DEBUG] Không parse được JSON từ response: {e}")
		print(f"[DEBUG] Response status: {response.status_code}")
		print(f"[DEBUG] Response text: {response.text[:500]}")
		return []
	
	if "data" not in data or "items" not in data["data"]:
		print(f"[DEBUG] Response không có data.items: {data}")
		return []
	
	try:
		items_list = data["data"]["items"]
		result = []
		# Duyệt qua tất cả các groups, lấy items hợp lệ cho đến khi đủ limit hoặc hết groups
		for group in items_list:
			if len(result) >= limit:
				break
			group_items = group.get("items", [])
			for item in group_items:
				if len(result) >= limit:
					break
				link = item.get("link", "")
				item_type = None
				
				# Xác định loại item dựa vào link pattern
				if link.startswith("/bai-hat/") or "zingmp3.vn/bai-hat/" in link:
					item_type = "songs"
				elif link.startswith("/playlist/") or "zingmp3.vn/playlist/" in link:
					item_type = "playlists"
				elif link.startswith("/album/") or "zingmp3.vn/album/" in link:
					item_type = "albums"
				elif link.startswith("/nghe-si/") or "zingmp3.vn/nghe-si/" in link:
					item_type = "artists"
				
				# Nếu có filter_type, chỉ lấy items khớp với filter
				# Lưu ý: trong Zing MP3, playlist và album là 1, nên filter "playlists" hoặc "albums" sẽ lấy cả hai
				if filter_type:
					if filter_type == "playlists" or filter_type == "albums":
						# Lấy cả playlist và album
						if item_type not in ["playlists", "albums"]:
							continue
					elif item_type != filter_type:
						continue
				
				# Nếu không có filter_type, chỉ lấy songs (mặc định)
				if not filter_type and item_type != "songs":
					continue
				
				# Xử lý theo từng loại
				if item_type == "songs":
					artist_name = item['artists'][0]['name'] if item.get('artists') else None
					song_id = item.get('id')
					result.append({
						"id": song_id,
						"title": item.get("title"),
						"thumb": item.get("thumb"),
						"link": link,
						"lyricLink": item.get("lyricLink"),
						"artist_name": artist_name,
						"duration": item.get("duration", 0),
						"type": item_type
					})
				elif item_type in ["playlists", "albums"]:
					item_id = item.get('id')
					result.append({
						"id": item_id,
						"title": item.get("title"),
						"thumb": item.get("thumb"),
						"link": link,
						"artist_name": item.get("artists", [{}])[0].get("name") if item.get("artists") else None,
						"duration": 0,
						"type": item_type
					})
				elif item_type == "artists":
					item_id = item.get('id')
					result.append({
						"id": item_id,
						"title": item.get("title"),
						"thumb": item.get("thumb"),
						"link": link,
						"artist_name": None,
						"duration": 0,
						"type": item_type
					})
		print(f"[DEBUG] get_featured_items: found {len(result)} results for keyword '{keyword}' with filter '{filter_type}'")
		return result
	except Exception as e:
		print(f"[DEBUG] Lỗi khi phân tích dữ liệu: {e}")
		import traceback
		traceback.print_exc()
		return []


def get_playlist_items(playlist_id: str, cookie: str = None) -> dict:
	"""Lấy danh sách bài hát từ playlist/album ID.
	
	Args:
		playlist_id: ID của playlist/album trên Zing MP3
		cookie: Cookie zmp3_rqid (optional, sẽ tự lấy nếu None)
	
	Returns:
		Dict chứa thông tin playlist và danh sách bài hát:
		{
			"id": playlist_id,
			"title": title,
			"thumb": thumbnail,
			"songs": [list các bài hát với id, title, artist_name, thumb, duration]
		}
		hoặc None nếu lỗi
	"""
	if cookie is None:
		cookie = get_zmp3_cookie()
	
	ctime = str(int(time.time()))
	path = "/api/v2/page/get/playlist"
	# Tính sig cho playlist API (giống như stream API nhưng path khác)
	raw = f"ctime={ctime}id={playlist_id}version={VERSION}"
	sig = get_hmac512(path + get_hash256(raw), SECRET_KEY)
	
	params = {
		"id": playlist_id,
		"thumbSize": "600_600",
		"ctime": ctime,
		"version": VERSION,
		"sig": sig,
		"apiKey": API_KEY
	}
	
	req_headers = headers.copy()
	if cookie:
		req_headers["Cookie"] = cookie
	
	url = BASE_URL + path
	resp = requests.get(url, params=params, headers=req_headers)
	try:
		data = resp.json()
	except Exception as e:
		print(f"[DEBUG] Không parse được JSON từ response: {e}")
		print(f"[DEBUG] Response text: {resp.text}")
		return None
	
	if "err" in data and data["err"] == 0 and "data" in data:
		playlist_data = data["data"]
		songs = []
		
		# Lấy danh sách bài hát từ data.song.items
		if "song" in playlist_data and "items" in playlist_data["song"]:
			for item in playlist_data["song"]["items"]:
				artist_name = None
				if item.get("artists") and len(item["artists"]) > 0:
					artist_name = item["artists"][0].get("name")
				
				songs.append({
					"id": item.get("encodeId"),
					"title": item.get("title"),
					"thumb": item.get("thumbnailM") or item.get("thumbnail"),
					"link": item.get("link"),
					"artist_name": artist_name,
					"duration": item.get("duration", 0)
				})
		
		return {
			"id": playlist_data.get("encodeId", playlist_id),
			"title": playlist_data.get("title"),
			"thumb": playlist_data.get("thumbnailM") or playlist_data.get("thumbnail"),
			"songs": songs
		}
	else:
		print(f"Không lấy được playlist: {data}")
		return None


def get_stream_link_by_id(song_id: str, cookie: str = None) -> str:
    """Lấy link stream 128kbps cho bài hát theo song_id.
    
    Args:
        song_id: ID bài hát trên Zing MP3
        cookie: Cookie zmp3_rqid (optional, sẽ tự lấy nếu None)
    
    Returns:
        URL stream 128kbps hoặc None nếu lỗi
    """
    ctime = str(int(time.time()))
    path = "/api/v2/song/get/streaming"
    sig = hash_param(path, song_id, ctime)
    params = {
        "id": song_id,
        "ctime": ctime,
        "version": VERSION,
        "apiKey": API_KEY,
        "sig": sig
    }
    req_headers = headers.copy()
    if cookie:
        req_headers["Cookie"] = cookie
    url = BASE_URL + path
    resp = requests.get(url, params=params, headers=req_headers)
    try:
        data = resp.json()
    except Exception as e:
        print(f"[DEBUG] Không parse được JSON từ response: {e}")
        print(f"[DEBUG] Response text: {resp.text}")
        return None
    if "data" in data and "128" in data["data"]:
        stream_link = data["data"]["128"]
        # Thay host để bypass (nếu cần)
        if stream_link and 'a128-z3.zmdcdn.me' in stream_link:
            stream_link = stream_link.replace('a128-z3.zmdcdn.me', 'vnno-ne-2-tf-a128-z3.zmdcdn.me')
        return stream_link
    else:
        print("Không lấy được link 128kbps:", data)
        return None


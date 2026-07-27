"""Utilities for Zing MP3 Player integration."""

import asyncio
import hashlib
import hmac
import json
import logging
import time
from typing import Any, Dict, List, Optional

import aiohttp
from homeassistant.core import HomeAssistant

from .const import (
    API_BASE_URL,
    API_PLAYLIST_URL,
    API_SEARCH_URL,
    API_STREAM_URL,
)

_LOGGER = logging.getLogger(__name__)


class ZingMP3API:
    """API handler for Zing MP3."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the API handler."""
        self.hass = hass
        self._session = None
        self._api_key = "M5dDSHbuuhpxtUbOxMWR3XQQjE2OjIlS"  # Default API key
        self._secret_key = "RmVytXdnqIx2UgGYB1jfGqCznJlA9kDn"  # Default secret

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to Zing MP3 API."""
        try:
            session = await self._get_session()
            
            # Generate signature
            timestamp = str(int(time.time() * 1000))
            params["ctime"] = timestamp
            
            # Sort params and generate signature
            sorted_params = " ".join(
                f"{k}={v}" for k, v in sorted(params.items()) if k != "sig"
            )
            signature = hmac.new(
                self._secret_key.encode("utf-8"),
                sorted_params.encode("utf-8"),
                hashlib.sha256
            ).hexdigest()
            params["sig"] = signature
            
            # Make request
            async with session.get(endpoint, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("err") == 0:
                        return data.get("data", {})
                    else:
                        _LOGGER.error("API returned error: %s", data.get("msg"))
                        return {}
                else:
                    _LOGGER.error("API request failed with status: %s", response.status)
                    return {}
                    
        except Exception as e:
            _LOGGER.error("Error making API request: %s", e)
            return {}

    async def search(self, query: str, filter_type: str = "songs", limit: int = 20) -> List[Dict]:
        """Search for music."""
        params = {
            "keyword": query,
            "type": filter_type,
            "count": limit,
        }
        
        data = await self._request(API_SEARCH_URL, params)
        results = []
        
        if data and "items" in data:
            for item in data["items"]:
                if filter_type == "songs":
                    results.append({
                        "media_content_id": item.get("encodeId"),
                        "media_content_type": "song",
                        "title": item.get("title"),
                        "artist": item.get("artists_names", ""),
                        "albumName": item.get("album", {}).get("title", ""),
                        "images": item.get("thumbnail", ""),
                        "duration": item.get("duration", 0),
                    })
                elif filter_type == "playlists":
                    results.append({
                        "media_content_id": item.get("encodeId"),
                        "media_content_type": "playlist",
                        "title": item.get("title"),
                        "artist": item.get("artists_names", ""),
                        "images": item.get("thumbnail", ""),
                    })
                    
        return results

    async def get_track_info(self, track_id: str) -> Optional[Dict]:
        """Get track information."""
        params = {
            "id": track_id,
            "type": "song",
        }
        
        data = await self._request(API_STREAM_URL, params)
        if data:
            return {
                "media_content_id": data.get("encodeId"),
                "media_content_type": "song",
                "title": data.get("title"),
                "artist": data.get("artists_names", ""),
                "albumName": data.get("album", {}).get("title", ""),
                "images": data.get("thumbnail", ""),
                "duration": data.get("duration", 0),
            }
        return None

    async def get_stream_url(self, track_id: str) -> Optional[str]:
        """Get streaming URL for a track."""
        params = {
            "id": track_id,
            "type": "song",
        }
        
        data = await self._request(API_STREAM_URL, params)
        if data and "data" in data:
            # Get the highest quality available
            stream_data = data["data"]
            for quality in ["320", "128", "64"]:
                if quality in stream_data:
                    return stream_data[quality]
        return None

    async def get_playlist_tracks(self, playlist_id: str) -> List[Dict]:
        """Get tracks from a playlist."""
        params = {
            "id": playlist_id,
            "type": "playlist",
        }
        
        data = await self._request(API_PLAYLIST_URL, params)
        tracks = []
        
        if data and "items" in data:
            for item in data["items"]:
                tracks.append({
                    "media_content_id": item.get("encodeId"),
                    "media_content_type": "song",
                    "title": item.get("title"),
                    "artist": item.get("artists_names", ""),
                    "albumName": item.get("album", {}).get("title", ""),
                    "images": item.get("thumbnail", ""),
                    "duration": item.get("duration", 0),
                })
                
        return tracks

    async def close(self):
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()

"""Support for Zing MP3 Player media player."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional

import aiohttp
import voluptuous as vol
from homeassistant.components import media_source
from homeassistant.components.media_player import (
    BrowseMedia,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
    RepeatMode,
    async_process_play_media_url,
)
from homeassistant.components.media_player.browse_media import (
    async_browse_media,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.typing import ConfigType

from .const import (
    API_BASE_URL,
    API_PLAYLIST_URL,
    API_SEARCH_URL,
    API_STREAM_URL,
    ATTR_TRACKS,
    CONF_EXTRA_SENSOR,
    CONF_SPEAKERS,
    DEFAULT_NAME,
    DOMAIN,
    MEDIA_TYPE_PLAYLIST,
    MEDIA_TYPE_SONG,
    SERVICE_CALL_METHOD,
    SERVICE_SEARCH,
)
from .utils import ZingMP3API

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)

SUPPORT_ZINGMP3 = (
    MediaPlayerEntityFeature.PLAY
    | MediaPlayerEntityFeature.PAUSE
    | MediaPlayerEntityFeature.STOP
    | MediaPlayerEntityFeature.NEXT_TRACK
    | MediaPlayerEntityFeature.PREVIOUS_TRACK
    | MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.SHUFFLE_SET
    | MediaPlayerEntityFeature.REPEAT_SET
    | MediaPlayerEntityFeature.SELECT_SOURCE
    | MediaPlayerEntityFeature.PLAY_MEDIA
    | MediaPlayerEntityFeature.BROWSE_MEDIA
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zing MP3 Player from a config entry."""
    _LOGGER.debug("Setting up Zing MP3 Player entry: %s", entry.title)
    
    # Get configuration
    name = entry.data.get("name", DEFAULT_NAME)
    speakers = entry.data.get(CONF_SPEAKERS, [])
    extra_sensor = entry.data.get(CONF_EXTRA_SENSOR, False)

    # Create API instance
    api = ZingMP3API(hass)

    # Create entity
    entity = ZingMP3PlayerEntity(
        hass,
        entry,
        name,
        speakers,
        api,
        extra_sensor,
    )

    async_add_entities([entity])

    # Register services
    platform = entity_platform.async_get_current_platform()
    
    platform.async_register_entity_service(
        SERVICE_SEARCH,
        {
            vol.Required("query"): str,
            vol.Optional("filter", default="songs"): vol.In(["songs", "playlists"]),
            vol.Optional("limit", default=20): vol.All(vol.Coerce(int), vol.Range(1, 50)),
        },
        "async_search",
    )

    platform.async_register_entity_service(
        SERVICE_CALL_METHOD,
        {
            vol.Required("command"): str,
            vol.Optional("parameters", default={}): dict,
        },
        "async_call_method",
    )


class ZingMP3PlayerEntity(MediaPlayerEntity):
    """Representation of a Zing MP3 Player."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        name: str,
        speakers: List[str],
        api: ZingMP3API,
        extra_sensor: bool = False,
    ) -> None:
        """Initialize the Zing MP3 Player."""
        self.hass = hass
        self._config_entry = config_entry
        self._name = name
        self._api = api
        self._speakers = speakers
        self._extra_sensor = extra_sensor
        
        # State variables
        self._state = MediaPlayerState.IDLE
        self._current_track = None
        self._playlist = []
        self._current_index = -1
        self._shuffle = False
        self._repeat = RepeatMode.OFF
        self._current_source = None
        self._source_list = []
        self._media_image_url = None
        self._media_duration = 0
        self._media_position = 0
        self._search_results = []
        
        # Update list of available speakers
        self._update_source_list()

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the entity."""
        return f"{DOMAIN}_{self._name}"

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def state(self) -> MediaPlayerState:
        """Return the current state."""
        return self._state

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        """Return the supported features."""
        return SUPPORT_ZINGMP3

    @property
    def source(self) -> str:
        """Return the current source."""
        return self._current_source

    @property
    def source_list(self) -> List[str]:
        """Return the list of available sources."""
        return self._source_list

    @property
    def shuffle(self) -> bool:
        """Return if shuffle is enabled."""
        return self._shuffle

    @property
    def repeat(self) -> RepeatMode:
        """Return the repeat mode."""
        return self._repeat

    @property
    def media_title(self) -> str | None:
        """Return the title of the current media."""
        return self._current_track.get("title") if self._current_track else None

    @property
    def media_artist(self) -> str | None:
        """Return the artist of the current media."""
        return self._current_track.get("artist") if self._current_track else None

    @property
    def media_album_name(self) -> str | None:
        """Return the album name of the current media."""
        return self._current_track.get("albumName") if self._current_track else None

    @property
    def media_image_url(self) -> str | None:
        """Return the image URL of the current media."""
        return self._media_image_url

    @property
    def media_duration(self) -> int | None:
        """Return the duration of the current media in seconds."""
        return self._media_duration

    @property
    def media_position(self) -> int | None:
        """Return the position of the current media in seconds."""
        return self._media_position

    def _update_source_list(self):
        """Update the list of available speakers."""
        speakers = []
        for entity_id in self._speakers:
            if entity_id and entity_id in self.hass.states.async_entity_ids("media_player"):
                state = self.hass.states.get(entity_id)
                if state:
                    speakers.append(state.name or entity_id)
        self._source_list = speakers

    async def async_select_source(self, source: str) -> None:
        """Select a source."""
        # Find the entity_id from the source name
        for entity_id in self._speakers:
            state = self.hass.states.get(entity_id)
            if state and state.name == source:
                self._current_source = source
                self.async_write_ha_state()
                return
        _LOGGER.error("Source %s not found", source)

    async def async_play_media(
        self, media_type: str, media_id: str, **kwargs: Any
    ) -> None:
        """Play a piece of media."""
        _LOGGER.debug("Playing media: %s (type: %s)", media_id, media_type)
        
        if media_source.is_media_source_id(media_id):
            # Handle media source
            play_media = await media_source.async_resolve_media(
                self.hass, media_id, self.entity_id
            )
            media_id = play_media.url
            media_id = async_process_play_media_url(self.hass, media_id)

        try:
            # If it's a playlist ID
            if media_type == MEDIA_TYPE_PLAYLIST or media_id.startswith("PL"):
                tracks = await self._api.get_playlist_tracks(media_id)
                if tracks:
                    self._playlist = tracks
                    self._current_index = 0
                    await self._play_track(0)
            else:
                # Single track
                track = await self._api.get_track_info(media_id)
                if track:
                    self._playlist = [track]
                    self._current_index = 0
                    await self._play_track(0)
                    
        except Exception as e:
            _LOGGER.error("Error playing media: %s", e)
            self._state = MediaPlayerState.IDLE
            self.async_write_ha_state()

    async def _play_track(self, index: int):
        """Play a track at the given index."""
        if index < 0 or index >= len(self._playlist):
            _LOGGER.warning("Invalid track index: %s", index)
            return

        self._current_index = index
        self._current_track = self._playlist[index]
        
        # Get streaming URL
        stream_url = await self._api.get_stream_url(
            self._current_track.get("media_content_id")
        )
        
        if stream_url:
            self._state = MediaPlayerState.PLAYING
            self._media_duration = self._current_track.get("duration", 0)
            self._media_image_url = self._current_track.get("images")
            
            # Play on selected speaker
            if self._current_source:
                await self._play_on_speaker(stream_url)
            
            self.async_write_ha_state()
        else:
            _LOGGER.error("Failed to get stream URL for track: %s", 
                          self._current_track.get("title"))

    async def _play_on_speaker(self, stream_url: str):
        """Play the stream on the selected speaker."""
        # Find the speaker entity
        for entity_id in self._speakers:
            state = self.hass.states.get(entity_id)
            if state and state.name == self._current_source:
                # Call play_media on the speaker
                await self.hass.services.async_call(
                    "media_player",
                    "play_media",
                    {
                        "entity_id": entity_id,
                        "media_content_id": stream_url,
                        "media_content_type": "audio/mpeg",
                    },
                )
                return

    async def async_media_play(self) -> None:
        """Play media."""
        if self._state == MediaPlayerState.PAUSED and self._current_track:
            self._state = MediaPlayerState.PLAYING
            # Resume on speaker
            if self._current_source:
                await self._play_on_speaker(
                    await self._api.get_stream_url(
                        self._current_track.get("media_content_id")
                    )
                )
            self.async_write_ha_state()

    async def async_media_pause(self) -> None:
        """Pause media."""
        if self._state == MediaPlayerState.PLAYING:
            self._state = MediaPlayerState.PAUSED
            # Pause on speaker
            if self._current_source:
                for entity_id in self._speakers:
                    state = self.hass.states.get(entity_id)
                    if state and state.name == self._current_source:
                        await self.hass.services.async_call(
                            "media_player",
                            "media_pause",
                            {"entity_id": entity_id},
                        )
                        break
            self.async_write_ha_state()

    async def async_media_stop(self) -> None:
        """Stop media."""
        self._state = MediaPlayerState.IDLE
        if self._current_source:
            for entity_id in self._speakers:
                state = self.hass.states.get(entity_id)
                if state and state.name == self._current_source:
                    await self.hass.services.async_call(
                        "media_player",
                        "media_stop",
                        {"entity_id": entity_id},
                    )
                    break
        self.async_write_ha_state()

    async def async_media_next_track(self) -> None:
        """Go to the next track."""
        if not self._playlist:
            return
            
        if self._shuffle:
            # Random track
            import random
            next_index = random.randint(0, len(self._playlist) - 1)
        else:
            next_index = self._current_index + 1
            if next_index >= len(self._playlist):
                if self._repeat == RepeatMode.ALL:
                    next_index = 0
                else:
                    return
                    
        await self._play_track(next_index)

    async def async_media_previous_track(self) -> None:
        """Go to the previous track."""
        if not self._playlist:
            return
            
        if self._shuffle:
            import random
            prev_index = random.randint(0, len(self._playlist) - 1)
        else:
            prev_index = self._current_index - 1
            if prev_index < 0:
                if self._repeat == RepeatMode.ALL:
                    prev_index = len(self._playlist) - 1
                else:
                    return
                    
        await self._play_track(prev_index)

    async def async_set_shuffle(self, shuffle: bool) -> None:
        """Set shuffle mode."""
        self._shuffle = shuffle
        self.async_write_ha_state()

    async def async_set_repeat(self, repeat: RepeatMode) -> None:
        """Set repeat mode."""
        self._repeat = repeat
        self.async_write_ha_state()

    async def async_browse_media(
        self,
        media_content_type: str | None = None,
        media_content_id: str | None = None,
    ) -> BrowseMedia:
        """Browse media."""
        return await async_browse_media(
            self.hass,
            media_content_type,
            media_content_id,
            content_filter=lambda item: item.media_content_type.startswith("audio/"),
        )

    async def async_search(self, query: str, filter_type: str = "songs", limit: int = 20):
        """Search for music."""
        _LOGGER.debug("Searching for: %s (filter: %s)", query, filter_type)
        results = await self._api.search(query, filter_type, limit)
        # Store results for sensor
        self._search_results = results
        self.async_write_ha_state()
        return results

    async def async_call_method(self, command: str, parameters: dict = None):
        """Call a custom method."""
        _LOGGER.debug("Calling method: %s with params: %s", command, parameters)
        if command == "goto_track" and parameters:
            track_no = parameters.get("track_no")
            if track_no is not None and 0 <= track_no < len(self._playlist):
                await self._play_track(track_no)

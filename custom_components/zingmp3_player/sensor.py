"""Sensor for Zing MP3 Player integration."""

from __future__ import annotations

import json
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_SEARCH_RESULTS, ATTR_TRACKS, DOMAIN
from .media_player import ZingMP3PlayerEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zing MP3 Player sensor from a config entry."""
    # Find the media player entity
    for entity in hass.data[DOMAIN].values():
        if isinstance(entity, ZingMP3PlayerEntity):
            async_add_entities([ZingMP3SensorEntity(entity)])
            break


class ZingMP3SensorEntity(SensorEntity):
    """Sensor entity for Zing MP3 Player."""

    def __init__(self, player: ZingMP3PlayerEntity) -> None:
        """Initialize the sensor."""
        self._player = player
        self._attr_name = f"{player.name} Extra"
        self._attr_unique_id = f"{player.unique_id}_extra"
        self._attr_native_unit_of_measurement = "tracks"
        self._attr_icon = "mdi:music-box"

    @property
    def native_value(self) -> int:
        """Return the number of tracks."""
        return len(self._player._playlist) if self._player._playlist else 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        attrs = {}
        
        # Current track info
        if self._player._current_track:
            attrs["current_track"] = self._player._current_track
            
        # Playlist info
        if self._player._playlist:
            attrs[ATTR_TRACKS] = json.dumps(self._player._playlist)
            attrs["total_tracks"] = len(self._player._playlist)
            attrs["current_index"] = self._player._current_index
            
        # Search results (if any)
        if hasattr(self._player, "_search_results"):
            attrs[ATTR_SEARCH_RESULTS] = json.dumps(self._player._search_results)
            
        return attrs

    async def async_update(self) -> None:
        """Update the sensor."""
        # State is updated via the player
        self.async_write_ha_state()

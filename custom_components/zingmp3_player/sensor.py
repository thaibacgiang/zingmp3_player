"""Platform cho sensor integration của Zing MP3."""
import logging
from homeassistant.helpers.entity import Entity
from . import DOMAIN
from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config, async_add_entities):
	"""Set up sensor từ config entry."""
	_LOGGER.debug("Init Zing MP3 sensor")
	if config.data.get(CONF_INIT_EXTRA_SENSOR, DEFAULT_INIT_EXTRA_SENSOR):
		async_add_entities([ZingMp3Sensor(hass, config)], update_before_add=True)


class ZingMp3Sensor(Entity):
	"""Extra Sensor cho Zing MP3 integration."""

	def __init__(self, hass, config):
		"""Initialize sensor."""
		self.hass = hass
		self._state = STATE_OFF
		self._device_id = config.entry_id
		self._device_name = config.data.get(CONF_NAME)
		self._attr_unique_id = config.entry_id + "_extra"
		self._attr_has_entity_name = True
		self._attr_name = "Extra"
		self._attr_icon = 'mdi:information-outline'
		self.hass.data[DOMAIN][self._device_id]['extra_sensor'] = self
		self._attr = {'current_song_id', 'current_song_title', 'current_song_artist', 'search', 'tracks', 'total_tracks'}
		self._attributes = {}
		for attr in self._attr:
			self._attributes[attr] = ""

		_LOGGER.debug("Init Zing MP3 sensor done")

	@property
	def device_info(self):
		"""Return device info."""
		return {
			'identifiers': {(DOMAIN, self._device_id)},
			'name': self._device_name,
			'manufacturer': "smarthomeblack",
			'model': "Zing MP3 Player"
		}

	@property
	def name(self):
		"""Return name."""
		return self._attr_name

	@property
	def state(self):
		"""Return state."""
		return self._state

	@property
	def extra_state_attributes(self):
		"""Return extra state attributes."""
		return self._attributes

	@property
	def icon(self):
		"""Return icon."""
		return self._attr_icon

	async def async_update(self):
		"""Update sensor state từ media player."""
		if DOMAIN in self.hass.data and self._device_id in self.hass.data[DOMAIN]:
			media_player_entity = self.hass.data[DOMAIN][self._device_id].get("media_player")
			if media_player_entity:
				self._state = media_player_entity.state
				self._attributes['current_song_id'] = getattr(media_player_entity, '_current_song_id', '')
				self._attributes['current_song_title'] = getattr(media_player_entity, '_track_title', '')
				self._attributes['current_song_artist'] = getattr(media_player_entity, '_track_artist', '')
			
			# Update all attributes from the data var (giống ytube_music_player)
			for attr in self._attr:
				if attr in self.hass.data[DOMAIN][self._device_id]:
					self._attributes[attr] = self.hass.data[DOMAIN][self._device_id][attr]
		
		# Write state ngay lập tức và đợi xong (không schedule)
		try:
			self.async_write_ha_state()
		except Exception:
			pass  # ignore errors during startup
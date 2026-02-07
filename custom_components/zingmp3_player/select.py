"""Platform cho select integration của Zing MP3."""
import logging
from homeassistant.components.select import SelectEntity
from . import DOMAIN
from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config, async_add_entities):
	"""Set up select entities từ config entry."""
	_LOGGER.debug("Init Zing MP3 dropdowns")
	init_dropdowns = config.data.get(CONF_INIT_DROPDOWNS, DEFAULT_INIT_DROPDOWNS)
	select_entities = {
		"speakers": ZingMp3SpeakerSelect(hass, config),
	}
	entities = []
	for dropdown, entity in select_entities.items():
		if dropdown in init_dropdowns:
			entities.append(entity)
	async_add_entities(entities, update_before_add=True)


class ZingMp3SelectEntity(SelectEntity):
	"""Base class cho Zing MP3 select entities."""

	def __init__(self, hass, config):
		"""Initialize select entity."""
		self.hass = hass
		self._device_id = config.entry_id
		self._device_name = config.data.get(CONF_NAME)
		self._attr_has_entity_name = True

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
	def should_poll(self):
		"""Return False vì không cần polling."""
		return False


class ZingMp3SpeakerSelect(ZingMp3SelectEntity):
	"""Select entity cho chọn speaker/output player."""

	def __init__(self, hass, config):
		"""Initialize speaker select."""
		super().__init__(hass, config)
		self._attr_unique_id = config.entry_id + "_speakers"
		self._attr_name = "Speakers"
		self._attr_icon = 'mdi:speaker'
		self._attr_current_option = None
		self._options = []
		self.hass.data[DOMAIN][self._device_id]['select_speakers'] = self
		self._update_options()

	def _update_options(self):
		"""Update danh sách speakers có sẵn."""
		from homeassistant.components.media_player import DOMAIN as DOMAIN_MP
		self._options = []
		for state in self.hass.states.async_all(DOMAIN_MP):
			if state.entity_id != f"{DOMAIN_MP}.{DOMAIN}_{self._device_name}":
				friendly_name = state.attributes.get('friendly_name', state.entity_id)
				self._options.append(friendly_name)
		if not self._options:
			self._options = ["No speakers available"]

	@property
	def options(self):
		"""Return list of options."""
		return self._options

	async def async_select_option(self, option):
		"""Select option."""
		from homeassistant.components.media_player import DOMAIN as DOMAIN_MP
		# Tìm entity_id từ friendly_name
		for state in self.hass.states.async_all(DOMAIN_MP):
			if state.attributes.get('friendly_name') == option:
				media_player_entity = self.hass.data[DOMAIN][self._device_id].get("media_player")
				if media_player_entity:
					await media_player_entity.async_select_source(state.entity_id.replace(f"{DOMAIN_MP}.", ""))
				break
		self._attr_current_option = option
		self.async_schedule_update_ha_state()

	async def async_update(self):
		"""Update current option từ media player."""
		media_player_entity = self.hass.data[DOMAIN][self._device_id].get("media_player")
		if media_player_entity and hasattr(media_player_entity, '_remote_player'):
			if media_player_entity._remote_player:
				from homeassistant.components.media_player import DOMAIN as DOMAIN_MP
				state = self.hass.states.get(media_player_entity._remote_player)
				if state:
					friendly_name = state.attributes.get('friendly_name', media_player_entity._remote_player)
					if friendly_name in self._options:
						self._attr_current_option = friendly_name
		self._update_options()

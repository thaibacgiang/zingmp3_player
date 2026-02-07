"""Provide the initial setup."""
import logging
import voluptuous as vol
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.service import async_extract_entity_ids
from .const import *

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass, config):
	"""Provide Setup of platform."""
	return True


async def async_setup_entry(hass, config_entry):
	"""Set up this integration using UI/YAML."""
	hass.data.setdefault(DOMAIN, {})
	hass.data[DOMAIN][config_entry.entry_id] = {}
	hass.config_entries.async_update_entry(config_entry, data=ensure_config(config_entry.data))

	if not config_entry.update_listeners:
		config_entry.add_update_listener(async_update_options)

	# Add entities to HA
	await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
	return True



async def async_remove_entry(hass, config_entry):
	"""Handle removal of an entry."""
	for platform in PLATFORMS:
		try:
			await hass.config_entries.async_forward_entry_unload(config_entry, platform)
			_LOGGER.info(
				"Successfully removed entities from the Zing MP3 integration"
			)
		except ValueError:
			pass


async def async_update_options(hass, config_entry):
	_LOGGER.debug("Config updated, reload the Zing MP3 entities.")
	for platform in PLATFORMS:
		await hass.config_entries.async_forward_entry_unload(config_entry, platform)
	await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

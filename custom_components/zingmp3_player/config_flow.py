"""Config flow cho Zing MP3 integration."""
from homeassistant.core import callback
from homeassistant import config_entries
from homeassistant.helpers.selector import selector
import voluptuous as vol
import logging
from .const import (
	DOMAIN, CONF_NAME, CONF_RECEIVERS, ensure_config, DOMAIN_MP,
	CONF_INIT_EXTRA_SENSOR, DEFAULT_INIT_EXTRA_SENSOR
)

_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class ZingMp3FlowHandler(config_entries.ConfigFlow):
	"""Config flow handler cho Zing MP3."""

	CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL
	VERSION = 1

	def __init__(self):
		"""Initialize config flow."""
		self._errors = {}

	async def async_step_user(self, user_input=None):
		"""Bước đầu tiên: nhập tên và chọn speakers."""
		self._errors = {}
		
		if user_input is not None:
			self.data = user_input
			# Đảm bảo name không có domain prefix
			if CONF_NAME in self.data:
				self.data[CONF_NAME] = self.data[CONF_NAME].replace(DOMAIN_MP + ".", "")
			return self.async_create_entry(
				title=f"Zing MP3 {self.data[CONF_NAME]}", 
				data=self.data
			)
		
		# Tạo form ban đầu
		_exclude_entities = []
		if (_zm := self.hass.data.get(DOMAIN)) is not None:
			for _zm_player in _zm.values():
				if DOMAIN_MP in _zm_player:
					_exclude_entities.append(_zm_player[DOMAIN_MP].entity_id)
		
		data_schema = vol.Schema({
			vol.Required(CONF_NAME, default=DOMAIN): str,
			vol.Optional(CONF_RECEIVERS): selector({
				"entity": {
					"multiple": True,
					"filter": [{"domain": DOMAIN_MP}],
					"exclude_entities": _exclude_entities
				}
			}),
			vol.Optional(CONF_INIT_EXTRA_SENSOR, default=DEFAULT_INIT_EXTRA_SENSOR): selector({
				"boolean": {}
			})
		})
		
		return self.async_show_form(
			step_id="user", 
			data_schema=data_schema, 
			errors=self._errors
		)

	@staticmethod
	@callback
	def async_get_options_flow(config_entry):
		"""Return options flow handler."""
		return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
	"""Options flow handler để cập nhật config."""

	def __init__(self, config_entry):
		"""Initialize options flow."""
		self.data = dict(config_entry.options or config_entry.data)

	async def async_step_init(self, user_input=None):
		"""Bước đầu tiên của options flow."""
		self._errors = {}
		
		if user_input is not None:
			self.data.update(user_input)
			# Đảm bảo name không có domain prefix
			if CONF_NAME in self.data:
				self.data[CONF_NAME] = self.data[CONF_NAME].replace(DOMAIN_MP + ".", "")
			return self.async_create_entry(data=self.data)
		
		# Tạo form options
		_exclude_entities = []
		if (_zm := self.hass.data.get(DOMAIN)) is not None:
			for _zm_player in _zm.values():
				if DOMAIN_MP in _zm_player:
					_exclude_entities.append(_zm_player[DOMAIN_MP].entity_id)
		
		data_schema = vol.Schema({
			vol.Required(CONF_NAME, default=self.data.get(CONF_NAME, DOMAIN)): str,
			vol.Optional(CONF_RECEIVERS, default=self.data.get(CONF_RECEIVERS, [])): selector({
				"entity": {
					"multiple": True,
					"filter": [{"domain": DOMAIN_MP}],
					"exclude_entities": _exclude_entities
				}
			}),
			vol.Optional(CONF_INIT_EXTRA_SENSOR, default=self.data.get(CONF_INIT_EXTRA_SENSOR, DEFAULT_INIT_EXTRA_SENSOR)): selector({
				"boolean": {}
			})
		})
		
		return self.async_show_form(
			step_id="init", 
			data_schema=data_schema, 
			errors=self._errors
		)

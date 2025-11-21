"""Config flow for Zendure Tempo integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_TEMPO_COLOR,
    CONF_TEMPO_NEXT_COLOR,
    CONF_TEMPO_HC,
    CONF_HYPER_INPUT_LIMIT,
    CONF_HYPER_OUTPUT_LIMIT,
    CONF_HYPER_SOC_SET,
    DEFAULT_SOC_ROUGE,
    DEFAULT_SOC_NORMAL,
    DEFAULT_INPUT_LIMIT,
    DEFAULT_OUTPUT_LIMIT,
)


class ZendureTempoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Zendure Tempo."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate that entities exist
            valid = True
            for key in [CONF_TEMPO_COLOR, CONF_TEMPO_NEXT_COLOR, CONF_TEMPO_HC,
                       CONF_HYPER_INPUT_LIMIT, CONF_HYPER_OUTPUT_LIMIT, CONF_HYPER_SOC_SET]:
                if not self.hass.states.get(user_input[key]):
                    errors[key] = "entity_not_found"
                    valid = False

            if valid:
                return self.async_create_entry(
                    title="Zendure Tempo",
                    data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_TEMPO_COLOR, default="sensor.rte_tempo_couleur_actuelle"): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
                vol.Required(CONF_TEMPO_NEXT_COLOR, default="sensor.rte_tempo_prochaine_couleur"): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
                vol.Required(CONF_TEMPO_HC, default="binary_sensor.rte_tempo_heures_creuses"): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="binary_sensor")
                ),
                vol.Required(CONF_HYPER_INPUT_LIMIT, default="number.hyper_2000_input_limit"): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="number")
                ),
                vol.Required(CONF_HYPER_OUTPUT_LIMIT, default="number.hyper_2000_output_limit"): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="number")
                ),
                vol.Required(CONF_HYPER_SOC_SET, default="number.hyper_2000_soc_set"): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="number")
                ),
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return ZendureTempoOptionsFlow(config_entry)


class ZendureTempoOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Zendure Tempo."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    "soc_rouge",
                    default=self.config_entry.options.get("soc_rouge", DEFAULT_SOC_ROUGE)
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=80, max=100, step=5, unit_of_measurement="%")
                ),
                vol.Required(
                    "soc_normal",
                    default=self.config_entry.options.get("soc_normal", DEFAULT_SOC_NORMAL)
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=70, max=100, step=5, unit_of_measurement="%")
                ),
                vol.Required(
                    "input_limit_max",
                    default=self.config_entry.options.get("input_limit_max", DEFAULT_INPUT_LIMIT)
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=0, max=1200, step=100, unit_of_measurement="W")
                ),
                vol.Required(
                    "output_limit_max",
                    default=self.config_entry.options.get("output_limit_max", DEFAULT_OUTPUT_LIMIT)
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=0, max=1200, step=100, unit_of_measurement="W")
                ),
            }),
        )

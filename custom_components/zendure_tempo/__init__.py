"""Zendure Tempo integration for Home Assistant."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN,
    CONF_TEMPO_COLOR,
    CONF_TEMPO_NEXT_COLOR,
    CONF_TEMPO_HC,
    CONF_TEMPO_JOURS_ROUGE,
    CONF_TEMPO_JOURS_BLANC,
    CONF_SOLAR_FORECAST,
    CONF_HYPER_INPUT_LIMIT,
    CONF_HYPER_OUTPUT_LIMIT,
    CONF_HYPER_SOC_SET,
    DEFAULT_SOC_ROUGE,
    DEFAULT_SOC_ROUGE_SOLEIL,
    DEFAULT_SOC_NORMAL,
    DEFAULT_INPUT_LIMIT,
    DEFAULT_OUTPUT_LIMIT,
    DEFAULT_SOLAR_THRESHOLD,
    DEFAULT_ENABLED_ROUGE,
    DEFAULT_ENABLED_BLANC,
    DEFAULT_ENABLED_BLEU,
    COLOR_ROUGE,
    COLOR_BLANC,
    COLOR_BLEU,
    MODE_ROUGE_HP,
    MODE_ROUGE_HC,
    MODE_BLANC_HP,
    MODE_BLANC_HC,
    MODE_VEILLE_ROUGE,
    MODE_BLEU,
    MODE_DISABLED,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SWITCH, Platform.SENSOR, Platform.BUTTON]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Zendure Tempo from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = ZendureTempoCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Listen for state changes on tempo entities
    @callback
    def async_state_changed(event):
        """Handle state changes."""
        coordinator.async_request_refresh()

    entry.async_on_unload(
        async_track_state_change_event(
            hass,
            [
                entry.data[CONF_TEMPO_COLOR],
                entry.data[CONF_TEMPO_NEXT_COLOR],
                entry.data[CONF_TEMPO_HC],
            ],
            async_state_changed,
        )
    )

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


class ZendureTempoCoordinator(DataUpdateCoordinator):
    """Coordinator for Zendure Tempo."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self.entry = entry
        # Restore enabled state from options (default: enabled)
        self.enabled = self._options.get("enabled", True)
        self._last_mode = None
        self._test_mode = None  # For manual testing

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this Zendure Tempo instance."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name=self.entry.title,
            manufacturer="Zendure",
            model="Tempo Controller",
            sw_version="0.0.5",
        )

    @property
    def _options(self) -> dict:
        """Get options safely."""
        return getattr(self.entry, 'options', {}) or {}

    @property
    def tempo_color(self) -> str | None:
        """Get current tempo color."""
        state = self.hass.states.get(self.entry.data[CONF_TEMPO_COLOR])
        return state.state if state else None

    @property
    def tempo_next_color(self) -> str | None:
        """Get next day tempo color."""
        state = self.hass.states.get(self.entry.data[CONF_TEMPO_NEXT_COLOR])
        return state.state if state else None

    @property
    def is_heures_creuses(self) -> bool:
        """Check if currently in off-peak hours."""
        state = self.hass.states.get(self.entry.data[CONF_TEMPO_HC])
        return state.state == "on" if state else False

    @property
    def jours_restants_rouge(self) -> int:
        """Get remaining red days in cycle."""
        entity_id = self.entry.data.get(CONF_TEMPO_JOURS_ROUGE)
        if not entity_id:
            return 0
        state = self.hass.states.get(entity_id)
        try:
            return int(float(state.state)) if state else 0
        except (ValueError, TypeError):
            return 0

    @property
    def jours_restants_blanc(self) -> int:
        """Get remaining white days in cycle."""
        entity_id = self.entry.data.get(CONF_TEMPO_JOURS_BLANC)
        if not entity_id:
            return 0
        state = self.hass.states.get(entity_id)
        try:
            return int(float(state.state)) if state else 0
        except (ValueError, TypeError):
            return 0

    @property
    def has_tempo_days_remaining(self) -> bool:
        """Check if there are red or white days remaining."""
        return self.jours_restants_rouge > 0 or self.jours_restants_blanc > 0

    @property
    def soc_rouge(self) -> int:
        """Get SOC target for red days."""
        return self._options.get("soc_rouge", DEFAULT_SOC_ROUGE)

    @property
    def soc_normal(self) -> int:
        """Get SOC target for normal days."""
        return self._options.get("soc_normal", DEFAULT_SOC_NORMAL)

    @property
    def input_limit_max(self) -> int:
        """Get max input limit."""
        return self._options.get("input_limit_max", DEFAULT_INPUT_LIMIT)

    @property
    def output_limit_max(self) -> int:
        """Get max output limit."""
        return self._options.get("output_limit_max", DEFAULT_OUTPUT_LIMIT)

    @property
    def soc_rouge_soleil(self) -> int:
        """Get SOC target for red days with solar forecast."""
        return self._options.get("soc_rouge_soleil", DEFAULT_SOC_ROUGE_SOLEIL)

    @property
    def solar_threshold(self) -> float:
        """Get minimum solar production to reduce charge."""
        return self._options.get("solar_threshold", DEFAULT_SOLAR_THRESHOLD)

    @property
    def enabled_rouge(self) -> bool:
        """Check if automation is enabled for red days."""
        return self._options.get("enabled_rouge", DEFAULT_ENABLED_ROUGE)

    @property
    def enabled_blanc(self) -> bool:
        """Check if automation is enabled for white days."""
        return self._options.get("enabled_blanc", DEFAULT_ENABLED_BLANC)

    @property
    def enabled_bleu(self) -> bool:
        """Check if automation is enabled for blue days."""
        return self._options.get("enabled_bleu", DEFAULT_ENABLED_BLEU)

    @property
    def solar_forecast_tomorrow(self) -> float:
        """Get solar production forecast for tomorrow in kWh."""
        solar_entity = self.entry.data.get(CONF_SOLAR_FORECAST)
        if not solar_entity:
            return 0.0
        state = self.hass.states.get(solar_entity)
        try:
            return float(state.state) if state else 0.0
        except (ValueError, TypeError):
            return 0.0

    @property
    def has_good_solar_forecast(self) -> bool:
        """Check if solar forecast is good enough to reduce charge."""
        return self.solar_forecast_tomorrow >= self.solar_threshold

    def get_current_mode(self) -> str:
        """Determine current mode based on tempo state."""
        # If in test mode, return test mode
        if self._test_mode:
            return self._test_mode

        if not self.enabled:
            return MODE_DISABLED

        # If no red/white days remaining, just use normal mode
        if not self.has_tempo_days_remaining:
            return MODE_BLEU

        color = self.tempo_color
        next_color = self.tempo_next_color
        hc = self.is_heures_creuses

        if color == COLOR_ROUGE:
            # If red day automation is disabled, use normal mode
            if not self.enabled_rouge:
                return MODE_BLEU
            return MODE_ROUGE_HC if hc else MODE_ROUGE_HP
        elif color == COLOR_BLANC:
            # If white day automation is disabled, use normal mode
            if not self.enabled_blanc:
                return MODE_BLEU
            if hc:
                # If tomorrow is red and red automation is enabled, prepare
                if next_color == COLOR_ROUGE and self.enabled_rouge:
                    return MODE_VEILLE_ROUGE
                return MODE_BLANC_HC
            return MODE_BLANC_HP
        elif color == COLOR_BLEU:
            # If tomorrow is red and we're in HC and red automation is enabled, prepare
            if next_color == COLOR_ROUGE and hc and self.enabled_rouge:
                return MODE_VEILLE_ROUGE
            # If blue day automation is disabled, use normal mode
            if not self.enabled_bleu:
                return MODE_BLEU
            return MODE_BLEU

        return MODE_BLEU

    async def _async_update_data(self):
        """Update data and apply battery settings."""
        mode = self.get_current_mode()

        # Only apply if mode changed or first run
        if mode != self._last_mode and self.enabled:
            await self._apply_mode(mode)
            self._last_mode = mode

        return {"mode": mode}

    async def _apply_mode(self, mode: str) -> None:
        """Apply battery settings based on mode."""
        _LOGGER.info("Applying Zendure Tempo mode: %s", mode)

        input_limit_entity = self.entry.data[CONF_HYPER_INPUT_LIMIT]
        output_limit_entity = self.entry.data[CONF_HYPER_OUTPUT_LIMIT]
        soc_set_entity = self.entry.data[CONF_HYPER_SOC_SET]

        if mode == MODE_ROUGE_HP:
            # Red peak: discharge max, no grid charging
            await self._set_number(input_limit_entity, 0)
            await self._set_number(output_limit_entity, self.output_limit_max)

        elif mode == MODE_ROUGE_HC:
            # Red off-peak: charge max
            await self._set_number(input_limit_entity, self.input_limit_max)
            await self._set_number(output_limit_entity, 0)
            await self._set_number(soc_set_entity, self.soc_rouge)

        elif mode == MODE_BLANC_HP:
            # White peak: discharge
            await self._set_number(input_limit_entity, 0)
            await self._set_number(output_limit_entity, self.output_limit_max)

        elif mode == MODE_BLANC_HC:
            # White off-peak: normal
            await self._set_number(input_limit_entity, self.input_limit_max)
            await self._set_number(output_limit_entity, self.output_limit_max)
            await self._set_number(soc_set_entity, self.soc_normal)

        elif mode == MODE_VEILLE_ROUGE:
            # Pre-red: charge based on solar forecast
            await self._set_number(input_limit_entity, self.input_limit_max)
            await self._set_number(output_limit_entity, 0)

            # Adjust SOC based on solar forecast
            if self.has_good_solar_forecast:
                target_soc = self.soc_rouge_soleil
                solar_msg = f" Solaire prévu: {self.solar_forecast_tomorrow:.1f} kWh → charge réduite à {target_soc}%."
            else:
                target_soc = self.soc_rouge
                solar_msg = ""

            await self._set_number(soc_set_entity, target_soc)

            # Send notification (with fixed ID to avoid duplicates on restart)
            await self.hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Tempo - Jour Rouge demain",
                    "message": f"Demain est un jour ROUGE. Charge de la batterie en cours (cible: {target_soc}%).{solar_msg}",
                    "notification_id": "zendure_tempo_veille_rouge",
                },
            )

        elif mode == MODE_BLEU:
            # Blue: normal
            await self._set_number(input_limit_entity, self.input_limit_max)
            await self._set_number(output_limit_entity, self.output_limit_max)
            await self._set_number(soc_set_entity, self.soc_normal)

    async def _set_number(self, entity_id: str, value: int) -> None:
        """Set a number entity value."""
        try:
            await self.hass.services.async_call(
                "number",
                "set_value",
                {"entity_id": entity_id, "value": value},
            )
        except Exception as err:
            _LOGGER.error("Failed to set %s to %s: %s", entity_id, value, err)

    async def async_set_enabled(self, enabled: bool) -> None:
        """Enable or disable the tempo control."""
        self.enabled = enabled
        # Persist the state in options
        new_options = {**self._options, "enabled": enabled}
        self.hass.config_entries.async_update_entry(self.entry, options=new_options)
        if enabled:
            self._last_mode = None  # Force reapply
            await self.async_request_refresh()
        else:
            # Reset to normal values
            await self._set_number(
                self.entry.data[CONF_HYPER_INPUT_LIMIT], self.input_limit_max
            )
            await self._set_number(
                self.entry.data[CONF_HYPER_OUTPUT_LIMIT], self.output_limit_max
            )
            await self._set_number(
                self.entry.data[CONF_HYPER_SOC_SET], self.soc_normal
            )

    async def async_apply_test_mode(self, mode: str) -> None:
        """Apply a specific mode for testing purposes."""
        _LOGGER.info("Applying test mode: %s", mode)
        self._test_mode = mode
        self._last_mode = None  # Force reapply
        await self.async_request_refresh()

    async def async_reset_to_auto(self) -> None:
        """Reset to automatic mode."""
        _LOGGER.info("Resetting to automatic mode")
        self._test_mode = None
        self._last_mode = None  # Force reapply
        await self.async_request_refresh()

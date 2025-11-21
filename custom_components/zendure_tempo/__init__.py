"""Zendure Tempo integration for Home Assistant."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN,
    CONF_TEMPO_COLOR,
    CONF_TEMPO_NEXT_COLOR,
    CONF_TEMPO_HC,
    CONF_TEMPO_JOURS_ROUGE,
    CONF_TEMPO_JOURS_BLANC,
    CONF_HYPER_INPUT_LIMIT,
    CONF_HYPER_OUTPUT_LIMIT,
    CONF_HYPER_SOC_SET,
    DEFAULT_SOC_ROUGE,
    DEFAULT_SOC_NORMAL,
    DEFAULT_INPUT_LIMIT,
    DEFAULT_OUTPUT_LIMIT,
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

PLATFORMS = [Platform.SWITCH, Platform.SENSOR]


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
        self.enabled = entry.options.get("enabled", True)
        self._last_mode = None

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
        state = self.hass.states.get(self.entry.data[CONF_TEMPO_JOURS_ROUGE])
        try:
            return int(float(state.state)) if state else 0
        except (ValueError, TypeError):
            return 0

    @property
    def jours_restants_blanc(self) -> int:
        """Get remaining white days in cycle."""
        state = self.hass.states.get(self.entry.data[CONF_TEMPO_JOURS_BLANC])
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
        return self.entry.options.get("soc_rouge", DEFAULT_SOC_ROUGE)

    @property
    def soc_normal(self) -> int:
        """Get SOC target for normal days."""
        return self.entry.options.get("soc_normal", DEFAULT_SOC_NORMAL)

    @property
    def input_limit_max(self) -> int:
        """Get max input limit."""
        return self.entry.options.get("input_limit_max", DEFAULT_INPUT_LIMIT)

    @property
    def output_limit_max(self) -> int:
        """Get max output limit."""
        return self.entry.options.get("output_limit_max", DEFAULT_OUTPUT_LIMIT)

    def get_current_mode(self) -> str:
        """Determine current mode based on tempo state."""
        if not self.enabled:
            return MODE_DISABLED

        # If no red/white days remaining, just use normal mode
        if not self.has_tempo_days_remaining:
            return MODE_BLEU

        color = self.tempo_color
        next_color = self.tempo_next_color
        hc = self.is_heures_creuses

        if color == COLOR_ROUGE:
            return MODE_ROUGE_HC if hc else MODE_ROUGE_HP
        elif color == COLOR_BLANC:
            if hc:
                # If tomorrow is red, prepare
                if next_color == COLOR_ROUGE:
                    return MODE_VEILLE_ROUGE
                return MODE_BLANC_HC
            return MODE_BLANC_HP
        elif color == COLOR_BLEU:
            # If tomorrow is red and we're in HC, prepare
            if next_color == COLOR_ROUGE and hc:
                return MODE_VEILLE_ROUGE
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
            # Pre-red: charge max
            await self._set_number(input_limit_entity, self.input_limit_max)
            await self._set_number(output_limit_entity, 0)
            await self._set_number(soc_set_entity, self.soc_rouge)
            # Send notification
            await self.hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Tempo - Jour Rouge demain",
                    "message": "Demain est un jour ROUGE. Charge de la batterie en cours.",
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
        new_options = {**self.entry.options, "enabled": enabled}
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

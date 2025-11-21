"""Switch platform for Zendure Tempo."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ZendureTempoSwitch(coordinator, entry)])


class ZendureTempoSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to enable/disable Zendure Tempo control."""

    _attr_has_entity_name = True
    _attr_name = "Pilotage Tempo"
    _attr_icon = "mdi:battery-clock"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_enabled"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Zendure Tempo",
            "manufacturer": "Community",
            "model": "Tempo Battery Controller",
        }

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self.coordinator.enabled

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        await self.coordinator.async_set_enabled(True)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        await self.coordinator.async_set_enabled(False)
        self.async_write_ha_state()

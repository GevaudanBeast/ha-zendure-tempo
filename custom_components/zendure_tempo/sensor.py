"""Sensor platform for Zendure Tempo."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MODE_DISABLED


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ZendureTempoModeSensor(coordinator, entry)])


class ZendureTempoModeSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing current Tempo mode."""

    _attr_has_entity_name = True
    _attr_name = "Mode actuel"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_mode"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> str:
        """Return the current mode."""
        return self.coordinator.get_current_mode()

    @property
    def icon(self) -> str:
        """Return the icon based on mode."""
        mode = self.native_value
        if mode == MODE_DISABLED:
            return "mdi:battery-off"
        elif "Décharge" in mode:
            return "mdi:battery-arrow-down"
        elif "Charge" in mode:
            return "mdi:battery-arrow-up"
        return "mdi:battery"

"""Button entities for Zendure Tempo integration."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    MODE_ROUGE_HP,
    MODE_ROUGE_HC,
    MODE_BLANC_HP,
    MODE_BLANC_HC,
    MODE_VEILLE_ROUGE,
    MODE_BLEU,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zendure Tempo button entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    buttons = [
        ZendureTempoTestButton(coordinator, entry, MODE_ROUGE_HP, "test_rouge_hp"),
        ZendureTempoTestButton(coordinator, entry, MODE_ROUGE_HC, "test_rouge_hc"),
        ZendureTempoTestButton(coordinator, entry, MODE_BLANC_HP, "test_blanc_hp"),
        ZendureTempoTestButton(coordinator, entry, MODE_BLANC_HC, "test_blanc_hc"),
        ZendureTempoTestButton(coordinator, entry, MODE_VEILLE_ROUGE, "test_veille_rouge"),
        ZendureTempoTestButton(coordinator, entry, MODE_BLEU, "test_bleu"),
        ZendureTempoResetButton(coordinator, entry),
    ]

    async_add_entities(buttons)


class ZendureTempoTestButton(CoordinatorEntity, ButtonEntity):
    """Button to test a specific Tempo mode."""

    def __init__(self, coordinator, entry: ConfigEntry, mode: str, button_id: str) -> None:
        """Initialize the test button."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._mode = mode
        self._attr_name = f"Test {mode}"
        self._attr_unique_id = f"{entry.entry_id}_{button_id}"
        self._attr_icon = self._get_icon_for_mode(mode)
        self._attr_device_info = coordinator.device_info

    def _get_icon_for_mode(self, mode: str) -> str:
        """Get icon based on mode."""
        if "Rouge HP" in mode:
            return "mdi:battery-arrow-down"
        elif "Rouge HC" in mode or "Veille Rouge" in mode:
            return "mdi:battery-arrow-up"
        elif "Blanc HP" in mode:
            return "mdi:battery-minus"
        elif "Blanc HC" in mode:
            return "mdi:battery-sync"
        elif "Bleu" in mode:
            return "mdi:battery"
        return "mdi:battery-check"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_apply_test_mode(self._mode)


class ZendureTempoResetButton(CoordinatorEntity, ButtonEntity):
    """Button to reset to automatic mode."""

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize the reset button."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._attr_name = "Réinitialiser mode automatique"
        self._attr_unique_id = f"{entry.entry_id}_reset_auto"
        self._attr_icon = "mdi:refresh"
        self._attr_device_info = coordinator.device_info

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_reset_to_auto()

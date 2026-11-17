"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import HomeAssistantError

from .base import XiaowoEntity
from .const import (
    DOMAIN,
    XiaowoBoiler, XiaowoExtBoiler
)

OPTIONS = {
    "heating_trg_temp": ["Boiler_heating_trg_temp", "采暖水目标温度", "mdi:sun-thermometer-outline", '°C', 30,
                         80, 33],
    "ch_setpoint": ["Ext_boiler_ch_setpoint", "采暖水目标温度", "mdi:sun-thermometer-outline", '°C', 30, 80,
                    162],
    "dhw_setpoint": ["Ext_boiler_dhw_setpoint", "卫浴水目标温度", "mdi:water-thermometer-outline", '°C', 30, 60,
                     163],
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    device_list = data["devices"]
    entities: list[XiaowoNumber] = []
    for device in device_list:
        if isinstance(device, XiaowoBoiler):
            device_id = "b" + str(device.boiler_id)
            entities.append(XiaowoNumber(hass, coordinator, device, 'heating_trg_temp', device_id))
        if isinstance(device, XiaowoExtBoiler):
            device_id = "e" + str(device.gateway_id)
            entities.append(XiaowoNumber(hass, coordinator, device, 'ch_setpoint', device_id))
            entities.append(XiaowoNumber(hass, coordinator, device, 'dhw_setpoint', device_id))

    async_add_entities(entities)


class XiaowoNumber(XiaowoEntity, NumberEntity):

    def __init__(self, hass, coordinator, device, option, device_id):
        """初始化."""
        super().__init__(hass, coordinator, device, device_id)
        self._object_id = OPTIONS[option][0]
        self._name = OPTIONS[option][1]
        self._icon = OPTIONS[option][2]
        self._attr_native_unit_of_measurement = OPTIONS[option][3]
        self._attr_native_min_value = OPTIONS[option][4]
        self._attr_native_max_value = OPTIONS[option][5]
        self._type = option
        self._attr_unique_id = f"{super().unique_id}{OPTIONS[option][0]}"
        self.option_key = OPTIONS[option][6]

    @property
    def name(self):
        """返回实体的名字."""
        return self._name

    @property
    def unique_id(self) -> str | None:
        """Return a unique ID."""
        return self._attr_unique_id

    @property
    def icon(self):
        """返回icon属性."""
        return self._icon

    @property
    def native_value(self) -> float | None:
        """Return the value reported by the number."""
        if self._type == "heating_trg_temp":
            return self._device.heating_trg_temp
        if self._type == "ch_setpoint":
            return self._device.ch_setpoint
        if self._type == "dhw_setpoint":
            return self._device.dhw_setpoint
        return None

    async def async_set_native_value(self, value: float):
        """Set the value."""
        if self.option_key == 33:
            if self._device.auto_ctrl:
                raise HomeAssistantError("自动控制采暖水目标温度为允许状态，无法设置采暖水目标温度！")
        if self.option_key == 162:
            if self._device.ext_auto_ctrl:
                raise HomeAssistantError("自动控制为允许状态，无法设置采暖水目标温度！")
        await self._send_command(self.option_key, int(value))
        if self.option_key == 33:
            self._device.heating_trg_temp = value
        elif self.option_key == 162:
            self._device.ch_setpoint = value
        elif self.option_key == 163:
            self._device.dhw_setpoint = value
        self.async_write_ha_state()

"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from homeassistant.const import (
    TEMP_CELSIUS,
)

from . import HomeAssistantXiaowoData
from .base import XiaowoEntity
from .const import (
    DOMAIN,
    LOGGER,
    XiaowoThermostat, XiaowoBoiler, XiaowoExtBoiler
)

OPTIONS = {
    "trg_temp_leave": ["Thermostat_trg_temp_leave", "离家模式目标温度", "mdi:temperature-celsius", TEMP_CELSIUS, 5, 35,
                       14],
    "trg_temp_home": ["Thermostat_trg_temp_home", "居家模式目标温度", "mdi:temperature-celsius", TEMP_CELSIUS, 5, 35,
                      15],
    "trg_temp_sleep": ["Thermostat_trg_temp_sleep", "睡眠模式目标温度", "mdi:temperature-celsius", TEMP_CELSIUS, 5, 35,
                       16],

    "heating_trg_temp": ["Boiler_heating_trg_temp", "采暖水目标温度", "mdi:sun-thermometer-outline", TEMP_CELSIUS, 30,
                         80, 33],
    "dhw_trg_temp": ["Boiler_dhw_trg_temp", "卫浴水目标温度", "mdi:water-thermometer-outline", TEMP_CELSIUS, 30, 60, 7],

    "ch_setpoint": ["Ext_boiler_ch_setpoint", "采暖水目标温度", "mdi:sun-thermometer-outline", TEMP_CELSIUS, 30, 80,
                    162],
    "dhw_setpoint": ["Ext_boiler_dhw_setpoint", "卫浴水目标温度", "mdi:water-thermometer-outline", TEMP_CELSIUS, 30, 60,
                     163],
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    hass_data: HomeAssistantXiaowoData = hass.data[DOMAIN][entry.entry_id]
    device_list = hass_data.device_list
    entities: list[XiaowoNumber] = []
    for device in device_list:
        if isinstance(device, XiaowoThermostat):
            device_id = "t" + str(device.thermostat_id)
            entities.append(XiaowoNumber(device, 'trg_temp_leave', device.trg_temp_leave, device_id))
            entities.append(XiaowoNumber(device, 'trg_temp_home', device.trg_temp_home, device_id))
            entities.append(XiaowoNumber(device, 'trg_temp_sleep', device.trg_temp_sleep, device_id))
        if isinstance(device, XiaowoBoiler):
            device_id = "b" + str(device.boiler_id)
            entities.append(XiaowoNumber(device, 'heating_trg_temp', device.heating_trg_temp, device_id))
            entities.append(XiaowoNumber(device, 'dhw_trg_temp', device.dhw_trg_temp, device_id))
        if isinstance(device, XiaowoExtBoiler):
            device_id = "e" + str(device.gateway_id)
            entities.append(XiaowoNumber(device, 'ch_setpoint', device.ch_setpoint, device_id))
            entities.append(XiaowoNumber(device, 'dhw_setpoint', device.dhw_setpoint, device_id))

    async_add_entities(entities)


class XiaowoNumber(XiaowoEntity, NumberEntity):

    def __init__(self, device, option, option_value, device_id):
        """初始化."""
        super().__init__(device_id)
        self._device = device
        self._object_id = OPTIONS[option][0]
        self._name = OPTIONS[option][1]
        self._icon = OPTIONS[option][2]
        self._unit_of_measurement = OPTIONS[option][3]
        self._attr_native_min_value = OPTIONS[option][4]
        self._attr_native_max_value = OPTIONS[option][5]
        self._type = option
        self._state = None
        self._attributes = {"states": "null"}
        self._attr_unique_id = f"{super().unique_id}{OPTIONS[option][0]}"
        self._attr_native_value = option_value
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
    def unit_of_measurement(self):
        """返回unit_of_measuremeng属性."""
        return self._unit_of_measurement

    @property
    def native_value(self) -> float | None:
        """Return the value reported by the number."""
        return self._attr_native_value

    async def async_update(self) -> None:
        if self._type == 'trg_temp_leave':
            self._attr_native_value = self._device.trg_temp_leave
        elif self._type == 'trg_temp_home':
            self._attr_native_value = self._device.trg_temp_home
        elif self._type == 'trg_temp_sleep':
            self._attr_native_value = self._device.trg_temp_sleep
        elif self._type == "heating_trg_temp":
            self._attr_native_value = self._device.heating_trg_temp
        elif self._type == "dhw_trg_temp":
            self._attr_native_value = self._device.dhw_trg_temp
        elif self._type == "ch_setpoint":
            self._attr_native_value = self._device.ch_setpoint
        elif self._type == "dhw_setpoint":
            self._attr_native_value = self._device.dhw_setpoint

    async def async_set_native_value(self, value: float):
        """Set the value."""
        if self.option_key == 33:
            if self._device.auto_ctrl:
                LOGGER.error("自动控制采暖水目标温度为允许状态，无法设置采暖水目标温度！")
                errors = {}
                errors["base"] = "自动控制采暖水目标温度为允许状态，无法设置采暖水目标温度！"
                # return self.async_show_form(step_id="init", data_schema=vol.Schema({"user_title": str}), errors=errors)
                return
        if self.option_key == 162:
            if self._device.ext_auto_ctrl:
                LOGGER.error("自动控制为允许状态，无法设置采暖水目标温度！")
                return
        if await self._send_command(self._device, self.option_key, int(value)):
            if self.option_key == 14:
                self._device.trg_temp_leave = value
                self._attr_native_value = value
            elif self.option_key == 15:
                self._device.trg_temp_home = value
                self._attr_native_value = value
            elif self.option_key == 16:
                self._device.trg_temp_sleep = value
                self._attr_native_value = value
            elif self.option_key == 33:
                self._device.heating_trg_temp = value
                self._attr_native_value = value
            elif self.option_key == 7:
                self._device.dhw_trg_temp = value
                self._attr_native_value = value
            elif self.option_key == 162:
                self._device.ch_setpoint = value
                self._attr_native_value = value
            elif self.option_key == 163:
                self._device.dhw_setpoint = value
                self._attr_native_value = value

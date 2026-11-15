"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .base import XiaowoEntity
from .const import (
    DOMAIN,
    XiaowoBoiler, XiaowoExtBoiler
)

OPTIONS = {
    "auto_ctrl": ["Boiler_auto_ctrl", "自动控制采暖水目标温度", "mdi:thermometer-auto", None, ['禁止', '允许'], 27],
    "dhw_preheat_status": ["Boiler_dhw_preheat_status", "卫浴水短时预热开关", "mdi:heating-coil", None, ['关闭', '开启'],
                           10],
    "ext_auto_ctrl": ["Ext_boiler_auto_ctrl", "自动控制", "mdi:thermostat-auto", None, ['禁止', '允许'], 157],
    "ch_enable": ["Ext_boiler_ch_enable", "采暖允许", "mdi:heat-wave", None, ['禁止', '允许'], 160],
    "dhw_enable": ["Ext_boiler_dhw_enable", "卫浴允许", "mdi:shower", None, ['禁止', '允许'], 161],
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    device_list = data["devices"]
    entities: list[XiaowoSelectSensor] = []
    for device in device_list:
        if isinstance(device, XiaowoBoiler):
            device_id = "b" + str(device.boiler_id)
            entities.append(XiaowoSelectSensor(hass, coordinator, device, 'auto_ctrl', device_id))
            if device.dhw_preheat_enable:
                entities.append(
                    XiaowoSelectSensor(hass, coordinator, device, 'dhw_preheat_status', device_id))
        if isinstance(device, XiaowoExtBoiler):
            device_id = "e" + str(device.gateway_id)
            entities.append(XiaowoSelectSensor(hass, coordinator, device, 'ext_auto_ctrl', device_id))
            entities.append(XiaowoSelectSensor(hass, coordinator, device, 'ch_enable', device_id))
            entities.append(XiaowoSelectSensor(hass, coordinator, device, 'dhw_enable', device_id))

    async_add_entities(entities)


class XiaowoSelectSensor(XiaowoEntity, SelectEntity):

    def __init__(self, hass, coordinator, device, option, device_id):
        """初始化."""
        super().__init__(hass, coordinator, device, device_id)
        self._object_id = OPTIONS[option][0]
        self._name = OPTIONS[option][1]
        self._icon = OPTIONS[option][2]
        self._unit_of_measurement = OPTIONS[option][3]
        self._type = option
        self._attr_unique_id = f"{super().unique_id}{OPTIONS[option][0]}"
        self._attr_options: list[str] = OPTIONS[option][4]
        self.option_key = OPTIONS[option][5]

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
    def options(self) -> list[str]:
        return self._attr_options

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        if self._type == 'auto_ctrl':
            return self._attr_options[1] if self._device.auto_ctrl else self._attr_options[0]
        if self._type == 'dhw_preheat_status':
            return self._attr_options[1] if self._device.dhw_preheat_status else self._attr_options[0]
        if self._type == 'ext_auto_ctrl':
            return self._attr_options[1] if self._device.ext_auto_ctrl == 1 else self._attr_options[0]
        if self._type == 'ch_enable':
            return self._attr_options[1] if self._device.ch_enable == 1 else self._attr_options[0]
        if self._type == 'dhw_enable':
            return self._attr_options[1] if self._device.dhw_enable == 1 else self._attr_options[0]
        return None

    async def async_select_option(self, option: str) -> None:
        if self._type == 'auto_ctrl':
            value = option == '允许'
        elif self._type == 'dhw_preheat_status':
            value = option == '开启'
        elif self._type == 'ext_auto_ctrl':
            value = 1 if option == '允许' else 0
        elif self._type == 'ch_enable':
            value = 1 if option == '允许' else 0
        elif self._type == 'dhw_enable':
            value = 1 if option == '允许' else 0
        else:
            return
        await self._send_command(self.option_key, value)
        if self.option_key == 27:
            self._device.auto_ctrl = value
        elif self.option_key == 10:
            self._device.dhw_preheat_status = value
        elif self.option_key == 157:
            self._device.ext_auto_ctrl = value
        elif self.option_key == 160:
            self._device.ch_enable = value
        elif self.option_key == 161:
            self._device.dhw_enable = value

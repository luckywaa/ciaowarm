"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from . import HomeAssistantXiaowoData
from .base import XiaowoEntity
from .const import (
    DOMAIN,
    LOGGER,
    XiaowoThermostat, XiaowoBoiler, XiaowoExtBoiler
)

OPTIONS = {
    "work_mode": ["Thermostat_work_mode", "模式", "mdi:alpha-m-box-outline", ' ', ['离家模式', '居家模式', '睡眠模式'],
                  17],
    "switch_ctrl": ["Boiler_switch_ctrl", "开关机", "mdi:toggle-switch-outline", ' ', ['关机', '开机'], 23],
    "season_ctrl": ["Boiler_season_ctrl", "冬夏模式", "mdi:sun-snowflake", ' ', ['夏季', '冬季'], 22],
    "auto_ctrl": ["Boiler_auto_ctrl", "自动控制采暖水目标温度", "mdi:thermometer-auto", ' ', ['禁止', '允许'], 27],
    "dhw_preheat_status": ["Boiler_dhw_preheat_status", "卫浴水短时预热开关", "mdi:heating-coil", ' ', ['关闭', '开启'],
                           10],
    "ext_auto_ctrl": ["Ext_boiler_auto_ctrl", "自动控制", "mdi:thermostat-auto", ' ', ['禁止', '允许'], 157],
    "ch_enable": ["Ext_boiler_ch_enable", "采暖允许", "mdi:heat-wave", ' ', ['禁止', '允许'], 160],
    "dhw_enable": ["Ext_boiler_dhw_enable", "卫浴允许", "mdi:shower", ' ', ['禁止', '允许'], 161],
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    hass_data: HomeAssistantXiaowoData = hass.data[DOMAIN][entry.entry_id]
    device_list = hass_data.device_list
    entities: list[XiaowoSelectSensor] = []
    for device in device_list:
        if isinstance(device, XiaowoThermostat):
            device_id = "t" + str(device.thermostat_id)
            entities.append(XiaowoSelectSensor(hass, entry, device, 'work_mode', device.work_mode, device_id))
        if isinstance(device, XiaowoBoiler):
            device_id = "b" + str(device.boiler_id)
            entities.append(XiaowoSelectSensor(hass, entry, device, 'switch_ctrl', device.switch_ctrl, device_id))
            entities.append(XiaowoSelectSensor(hass, entry, device, 'season_ctrl', device.season_ctrl, device_id))
            entities.append(XiaowoSelectSensor(hass, entry, device, 'auto_ctrl', device.auto_ctrl, device_id))
            if device.dhw_preheat_enable:
                entities.append(
                    XiaowoSelectSensor(hass, entry, device, 'dhw_preheat_status', device.dhw_preheat_status, device_id))
        if isinstance(device, XiaowoExtBoiler):
            device_id = "e" + str(device.gateway_id)
            entities.append(XiaowoSelectSensor(hass, entry, device, 'ext_auto_ctrl', device.ext_auto_ctrl, device_id))
            entities.append(XiaowoSelectSensor(hass, entry, device, 'ch_enable', device.ch_enable, device_id))
            entities.append(XiaowoSelectSensor(hass, entry, device, 'dhw_enable', device.dhw_enable, device_id))

    async_add_entities(entities)


class XiaowoSelectSensor(XiaowoEntity, SelectEntity):

    def __init__(self, hass, entry, device, option, option_value, device_id):
        """初始化."""
        super().__init__(device_id)
        self._hass = hass
        self._entry = entry
        self._device = device
        self._object_id = OPTIONS[option][0]
        self._name = OPTIONS[option][1]
        self._icon = OPTIONS[option][2]
        self._unit_of_measurement = OPTIONS[option][3]
        self._type = option
        self._attr_unique_id = f"{super().unique_id}{OPTIONS[option][0]}"
        self._attr_options: list[str] = OPTIONS[option][4]
        self.option_key = OPTIONS[option][5]
        if self._type == 'switch_ctrl':
            if self._device.switch_ctrl:
                self._attr_current_option = self._attr_options[1]
            else:
                self._attr_current_option = self._attr_options[0]
        elif self._type == 'season_ctrl':
            if self._device.season_ctrl:
                self._attr_current_option = self._attr_options[1]
            else:
                self._attr_current_option = self._attr_options[0]
        elif self._type == 'auto_ctrl':
            if self._device.auto_ctrl:
                self._attr_current_option = self._attr_options[1]
            else:
                self._attr_current_option = self._attr_options[0]
        elif self._type == 'dhw_preheat_status':
            if self._device.dhw_preheat_status:
                self._attr_current_option = self._attr_options[1]
            else:
                self._attr_current_option = self._attr_options[0]
        elif self._type == 'ext_auto_ctrl':
            if self._device.ext_auto_ctrl == 1:
                self._attr_current_option = self._attr_options[1]
            else:
                self._attr_current_option = self._attr_options[0]
        elif self._type == 'ch_enable':
            if self._device.ch_enable == 1:
                self._attr_current_option = self._attr_options[1]
            else:
                self._attr_current_option = self._attr_options[0]
        elif self._type == 'dhw_enable':
            if self._device.dhw_enable == 1:
                self._attr_current_option = self._attr_options[1]
            else:
                self._attr_current_option = self._attr_options[0]
        elif self._type == 'work_mode':
            self._attr_current_option = self._attr_options[option_value]

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
        return self._attr_current_option

    async def async_update(self) -> None:
        if self._type == 'switch_ctrl':
            if self._device.switch_ctrl:
                self._attr_current_option = self._attr_options[1]
            else:
                self._attr_current_option = self._attr_options[0]
        elif self._type == 'season_ctrl':
            if self._device.season_ctrl:
                self._attr_current_option = self._attr_options[1]
            else:
                self._attr_current_option = self._attr_options[0]
        elif self._type == 'auto_ctrl':
            if self._device.auto_ctrl:
                self._attr_current_option = self._attr_options[1]
            else:
                self._attr_current_option = self._attr_options[0]
        elif self._type == 'dhw_preheat_status':
            if self._device.dhw_preheat_status:
                self._attr_current_option = self._attr_options[1]
            else:
                self._attr_current_option = self._attr_options[0]
        elif self._type == 'ext_auto_ctrl':
            if self._device.ext_auto_ctrl == 1:
                self._attr_current_option = self._attr_options[1]
            else:
                self._attr_current_option = self._attr_options[0]
        elif self._type == 'ch_enable':
            if self._device.ch_enable == 1:
                self._attr_current_option = self._attr_options[1]
            else:
                self._attr_current_option = self._attr_options[0]
        elif self._type == 'dhw_enable':
            if self._device.dhw_enable == 1:
                self._attr_current_option = self._attr_options[1]
            else:
                self._attr_current_option = self._attr_options[0]
        elif self._type == 'work_mode':
            self._attr_current_option = self._attr_options[self._device.work_mode]

    async def async_select_option(self, option: str) -> None:
        LOGGER.error("option: %s", option)
        if self._type == 'switch_ctrl':
            if option == '开机':
                value = True
            else:
                value = False
        elif self._type == 'season_ctrl':
            if option == '冬季':
                value = True
            else:
                value = False
        elif self._type == 'auto_ctrl':
            if option == '允许':
                value = True
            else:
                value = False
        elif self._type == 'dhw_preheat_status':
            if option == '开启':
                value = True
            else:
                value = False
        elif self._type == 'ext_auto_ctrl':
            if option == '允许':
                value = int(1)
            else:
                value = int(0)
        elif self._type == 'ch_enable':
            if option == '允许':
                value = int(1)
            else:
                value = int(0)
        elif self._type == 'dhw_enable':
            if option == '允许':
                value = int(1)
            else:
                value = int(0)
        elif self._type == 'work_mode':
            if option == '离家模式':
                value = int(0)
            elif option == '居家模式':
                value = int(1)
            else:
                value = int(2)
        if await self._send_command(self._device, self.option_key, value):
            if self.option_key == 23:
                self._device.switch_ctrl = value
            elif self.option_key == 22:
                self._device.season_ctrl = value
            elif self.option_key == 27:
                self._device.auto_ctrl = value
            elif self.option_key == 10:
                self._device.dhw_preheat_status = value
            elif self.option_key == 157:
                self._device.ext_auto_ctrl = value
            elif self.option_key == 160:
                self._device.ch_enable = value
            elif self.option_key == 161:
                self._device.dhw_enable = value
            elif self.option_key == 17:
                self._device.work_mode = value

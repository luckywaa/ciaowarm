"""Switch platform for ciaowarm binary controls."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .base import XiaowoEntity
from .const import (
    DOMAIN,
    XiaowoBoiler, XiaowoExtBoiler
)

# 名称、图标、option_key；锅炉标志位为布尔值，第三方壁挂炉标志位为 1/0
OPTIONS = {
    "auto_ctrl": ["Boiler_auto_ctrl", "自动控制采暖水目标温度", "mdi:thermometer-auto", 27],
    "dhw_preheat_status": ["Boiler_dhw_preheat_status", "卫浴水短时预热开关", "mdi:heating-coil", 10],
    "ext_auto_ctrl": ["Ext_boiler_auto_ctrl", "自动控制", "mdi:thermostat-auto", 157],
    "ch_enable": ["Ext_boiler_ch_enable", "采暖允许", "mdi:heat-wave", 160],
    "dhw_enable": ["Ext_boiler_dhw_enable", "卫浴允许", "mdi:shower", 161],
}

# 各开关对应的设备模型字段（与 OPTIONS 键一致）
BOOL_FIELDS = ("auto_ctrl", "dhw_preheat_status")
INT_FIELDS = ("ext_auto_ctrl", "ch_enable", "dhw_enable")


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    device_list = data["devices"]
    entities: list[XiaowoSwitch] = []
    for device in device_list:
        if isinstance(device, XiaowoBoiler):
            device_id = "b" + str(device.boiler_id)
            entities.append(XiaowoSwitch(hass, coordinator, device, 'auto_ctrl', device_id))
            if device.dhw_preheat_enable:
                entities.append(
                    XiaowoSwitch(hass, coordinator, device, 'dhw_preheat_status', device_id))
        if isinstance(device, XiaowoExtBoiler):
            device_id = "e" + str(device.gateway_id)
            entities.append(XiaowoSwitch(hass, coordinator, device, 'ext_auto_ctrl', device_id))
            entities.append(XiaowoSwitch(hass, coordinator, device, 'ch_enable', device_id))
            entities.append(XiaowoSwitch(hass, coordinator, device, 'dhw_enable', device_id))

    async_add_entities(entities)


class XiaowoSwitch(XiaowoEntity, SwitchEntity):
    """二值控制开关：锅炉标志位为布尔值，第三方壁挂炉标志位为 1/0。"""

    def __init__(self, hass, coordinator, device, option, device_id):
        """初始化."""
        super().__init__(hass, coordinator, device, device_id)
        self._object_id = OPTIONS[option][0]
        self._name = OPTIONS[option][1]
        self._icon = OPTIONS[option][2]
        self._type = option
        self._attr_unique_id = f"{super().unique_id}{OPTIONS[option][0]}"
        self.option_key = OPTIONS[option][3]

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
    def is_on(self) -> bool | None:
        """返回开关状态."""
        if self._type in BOOL_FIELDS:
            return bool(getattr(self._device, self._type))
        if self._type in INT_FIELDS:
            return getattr(self._device, self._type) == 1
        return None

    async def async_turn_on(self, **kwargs):
        """开启."""
        await self._async_set_value(True)

    async def async_turn_off(self, **kwargs):
        """关闭."""
        await self._async_set_value(False)

    async def _async_set_value(self, value: bool):
        """下发指令，失败抛 HomeAssistantError；状态以轮询结果为准."""
        if self._type in INT_FIELDS:
            payload = 1 if value else 0
        else:
            payload = value
        await self._send_command(self.option_key, payload)

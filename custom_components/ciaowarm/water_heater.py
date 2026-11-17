"""Water heater platform for ciaowarm boilers."""
from __future__ import annotations

from homeassistant.components.water_heater import (
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .base import XiaowoEntity
from .const import (
    DOMAIN,
    XiaowoBoiler,
)

# 运行模式：开关机（整机）与冬夏模式的组合
OPERATION_OFF = "关机"
OPERATION_SUMMER = "夏季"
OPERATION_WINTER = "冬季"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    device_list = data["devices"]
    entities: list[XiaowoWaterHeater] = []
    for device in device_list:
        if isinstance(device, XiaowoBoiler):
            device_id = "b" + str(device.boiler_id)
            entities.append(XiaowoWaterHeater(hass, coordinator, device, device_id))

    async_add_entities(entities)


class XiaowoWaterHeater(XiaowoEntity, WaterHeaterEntity):
    """壁挂炉 Water Heater 实体：运行模式为关机/夏季/冬季，可设置卫浴水目标温度。"""

    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_min_temp = 30
    _attr_max_temp = 60
    _attr_operation_list = [OPERATION_OFF, OPERATION_SUMMER, OPERATION_WINTER]
    _attr_supported_features = (
        WaterHeaterEntityFeature.TARGET_TEMPERATURE
        | WaterHeaterEntityFeature.OPERATION_MODE
    )

    def __init__(self, hass, coordinator, device: XiaowoBoiler, device_id):
        """初始化."""
        super().__init__(hass, coordinator, device, device_id)
        self._attr_unique_id = f"{super().unique_id}Boiler_water_heater"
        self._name = "热水器"

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
        return "mdi:water-boiler"

    @property
    def current_operation(self) -> str | None:
        """返回当前运行模式（注意：开关机为整机开关，含采暖）."""
        if not self._device.switch_ctrl:
            return OPERATION_OFF
        if self._device.season_ctrl:
            return OPERATION_WINTER
        return OPERATION_SUMMER

    @property
    def native_current_temperature(self) -> float | None:
        """返回卫浴水当前温度."""
        return self._device.dhw_water_temp

    @property
    def native_target_temperature(self) -> float | None:
        """返回卫浴水目标温度."""
        return self._device.dhw_trg_temp

    async def async_set_temperature(self, **kwargs):
        """设置卫浴水目标温度."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        await self._send_command(7, int(temperature))
        self._device.dhw_trg_temp = int(temperature)
        self.async_write_ha_state()

    async def async_set_operation_mode(self, operation_mode: str):
        """切换运行模式：关机/夏季/冬季."""
        if operation_mode == OPERATION_OFF:
            commands = [(23, False)]
        elif operation_mode == OPERATION_SUMMER:
            commands = [] if self._device.switch_ctrl else [(23, True)]
            commands.append((22, False))
        elif operation_mode == OPERATION_WINTER:
            commands = [] if self._device.switch_ctrl else [(23, True)]
            commands.append((22, True))
        else:
            return
        for option_key, option_value in commands:
            await self._send_command(option_key, option_value)
        self._device.switch_ctrl = operation_mode != OPERATION_OFF
        if operation_mode != OPERATION_OFF:
            self._device.season_ctrl = operation_mode == OPERATION_WINTER
        self.async_write_ha_state()

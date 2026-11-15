"""Climate platform for ciaowarm thermostats."""
from __future__ import annotations

from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACMode
from homeassistant.components.climate.const import (
    PRESET_AWAY,
    PRESET_HOME,
    PRESET_SLEEP,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .base import XiaowoEntity
from .const import (
    DOMAIN,
    XiaowoThermostat,
)

# work_mode 与预设的对应关系
PRESET_TO_WORK_MODE = {
    PRESET_AWAY: 0,
    PRESET_HOME: 1,
    PRESET_SLEEP: 2,
}
WORK_MODE_TO_PRESET = {value: key for key, value in PRESET_TO_WORK_MODE.items()}
PRESET_ORDER = [PRESET_AWAY, PRESET_HOME, PRESET_SLEEP]

# 各 work_mode 的目标温度字段与对应 option_key
WORK_MODE_FIELDS = {
    0: ("trg_temp_leave", 14),
    1: ("trg_temp_home", 15),
    2: ("trg_temp_sleep", 16),
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    device_list = data["devices"]
    entities: list[XiaowoClimate] = []
    for device in device_list:
        if isinstance(device, XiaowoThermostat):
            device_id = "t" + str(device.thermostat_id)
            entities.append(XiaowoClimate(hass, coordinator, device, device_id))

    async_add_entities(entities)


class XiaowoClimate(XiaowoEntity, ClimateEntity):
    """温控器 Climate 实体：目标温度按当前模式写入，预设对应离家/居家/睡眠模式。"""

    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.HEAT]
    _attr_min_temp = 5
    _attr_max_temp = 35
    _attr_target_temperature_step = 1
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE
    )
    _attr_preset_modes = PRESET_ORDER

    def __init__(self, hass, coordinator, device: XiaowoThermostat, device_id):
        """初始化."""
        super().__init__(hass, coordinator, device, device_id)
        self._attr_unique_id = f"{super().unique_id}Thermostat_climate"
        self._name = "温控器"

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
        return "mdi:thermostat"

    @property
    def hvac_mode(self):
        """温控器无独立电源控制，恒为制热模式."""
        return HVACMode.HEAT

    @property
    def native_current_temperature(self) -> float | None:
        """返回当前室内温度."""
        if self._device.room_temp is None:
            return None
        return self._device.room_temp / 10

    @property
    def native_target_temperature(self) -> float | None:
        """返回当前模式的目标温度."""
        field = WORK_MODE_FIELDS.get(self._device.work_mode, (None, None))[0]
        if field is None:
            return None
        return getattr(self._device, field, None)

    @property
    def preset_mode(self) -> str | None:
        """返回当前预设模式."""
        return WORK_MODE_TO_PRESET.get(self._device.work_mode)

    async def async_set_temperature(self, **kwargs):
        """按当前模式写入对应的目标温度."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        work_mode = self._device.work_mode
        field_and_key = WORK_MODE_FIELDS.get(work_mode)
        if field_and_key is None:
            return
        field, option_key = field_and_key
        await self._send_command(option_key, int(temperature))
        setattr(self._device, field, int(temperature))

    async def async_set_preset_mode(self, preset_mode: str):
        """切换离家/居家/睡眠模式."""
        work_mode = PRESET_TO_WORK_MODE.get(preset_mode)
        if work_mode is None:
            return
        await self._send_command(17, work_mode)
        self._device.work_mode = work_mode

    async def async_set_hvac_mode(self, hvac_mode):
        """温控器无独立电源控制，无需处理."""

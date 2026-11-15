"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfPressure, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .base import XiaowoEntity
from .const import (
    DOMAIN,
    XiaowoThermostat, XiaowoBoiler, XiaowoExtBoiler
)

OPTIONS = {
    "thermostat_gateway_id": ["Thermostat_gateway_id", "网关ID", "mdi:identifier", None],
    "thermostat_id": ["Thermostat_thermostat_id", "温控器ID", "mdi:identifier", None],
    "room_temp": ["Thermostat_room_temp", "室内温度", "mdi:home-thermometer-outline", '°C'],
    "room_temp_correct": ["Thermostat_room_temp_correct", "修正后室内温度", "mdi:home-thermometer-outline", '°C'],
    "thermostat_online": ["Thermostat_online", "温控器在线状态", "mdi:signal-variant", None],
    "thermostat_name": ["Thermostat_thermostat_name", "温控器名称", "mdi:subtitles-outline", None],

    "boiler_gateway_id": ["Boiler_gateway_id", "网关ID", "mdi:identifier", None],
    "boiler_id": ["Boiler_boiler_id", "壁挂炉ID", "mdi:identifier", None],
    "boiler_online": ["Boiler_boiler_online", "壁挂炉在线状态", "mdi:signal-variant", None],
    "water_pressure_value": ["Boiler_water_pressure_value", "水压值", "mdi:speedometer", 'bar'],
    "heating_water_temp": ["Boiler_heating_water_temp", "采暖水出水温度", "mdi:sun-thermometer-outline", '°C'],
    "dhw_water_temp": ["Boiler_dhw_water_temp", "卫浴水出水温度", "mdi:water-thermometer-outline", '°C'],
    "heating_return_water_temp": ["Boiler_heating_return_water_temp", "采暖水回水温度", "mdi:sun-thermometer-outline", '°C'],
    "dhw_return_water_temp": ["Boiler_dhw_return_water_temp", "卫浴水回水温度", "mdi:water-thermometer-outline", '°C'],
    "flame_status": ["Boiler_flame_status", "火焰状态", "mdi:fire", None],
    "fault_code": ["Boiler_fault_code", "故障码", "mdi:alert-outline", None],
    "dhw_preheat_mode": ["Boiler_dhw_preheat_mode", "卫浴水工作模式", "mdi:alpha-m-box-outline", None],

    "ext_boiler_gateway_id": ["Ext_boiler_gateway_id", "网关ID", "mdi:identifier", None],
    "ext_boiler_online": ["Ext_boiler_online", "网关在线状态", "mdi:signal-variant", None],
    "ext_ch_water_temp": ["Ext_boiler_ch_water_temp", "采暖水实际温度", "mdi:sun-thermometer-outline", '°C'],
    "ext_dhw_water_temp": ["Ext_boiler_dhw_water_temp", "卫浴水实际温度", "mdi:water-thermometer-outline",
                           '°C'],
    "ext_flame": ["Ext_boiler_flame", "火焰状态", "mdi:fire", None],
    "ext_error_code": ["Ext_boiler_error_code", "故障码", "mdi:alert-outline", None],
}


def _div10(value):
    """云端按 10 倍整数缩放的值转显示值（None 安全）。"""
    return value / 10 if value is not None else None


# 各测点从共享数据模型对象提取原始值
SENSOR_RAW = {
    "thermostat_gateway_id": lambda d: d.gateway_id,
    "thermostat_id": lambda d: d.thermostat_id,
    "room_temp": lambda d: _div10(d.room_temp),
    "room_temp_correct": lambda d: _div10(d.room_temp_correct),
    "thermostat_online": lambda d: d.thermostat_online,
    "thermostat_name": lambda d: d.thermostat_name,
    "boiler_gateway_id": lambda d: d.gateway_id,
    "boiler_id": lambda d: d.boiler_id,
    "boiler_online": lambda d: d.boiler_online,
    "water_pressure_value": lambda d: _div10(d.water_pressure_value),
    "heating_water_temp": lambda d: d.heating_water_temp,
    "dhw_water_temp": lambda d: d.dhw_water_temp,
    "heating_return_water_temp": lambda d: d.heating_return_water_temp,
    "dhw_return_water_temp": lambda d: d.dhw_return_water_temp,
    "flame_status": lambda d: d.flame_status,
    "fault_code": lambda d: d.fault_code,
    "dhw_preheat_mode": lambda d: d.dhw_preheat_mode,
    "ext_boiler_gateway_id": lambda d: d.gateway_id,
    "ext_boiler_online": lambda d: d.ext_boiler_online,
    "ext_ch_water_temp": lambda d: d.ch_water_temp,
    "ext_dhw_water_temp": lambda d: d.dhw_water_temp,
    "ext_flame": lambda d: d.flame,
    "ext_error_code": lambda d: d.error_code,
}

# 枚举类测点的原始值转中文展示；其余测点直接展示原始值
SENSOR_DISPLAY = {
    "thermostat_online": lambda raw: "在线" if raw else "离线",
    "boiler_online": lambda raw: "在线" if raw else "离线",
    # 注意：小沃壁挂炉云端 flame_status 语义为 真=无火（与第三方壁挂炉 ext_flame 的 1=有火 相反），
    # 此映射为厂商既有约定，勿"修复"
    "flame_status": lambda raw: "无火" if raw else "有火",
    "ext_boiler_online": lambda raw: "在线" if raw else "离线",
    "ext_flame": lambda raw: "有火" if raw == 1 else "无火",
    "dhw_preheat_mode": lambda raw: {
        1: "短时预热",
        2: "定时预热",
        3: "水控单次预热",
    }.get(raw, "未启用"),
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    device_list = data["devices"]
    entities: list[XiaowoSensor] = []
    for device in device_list:
        if isinstance(device, XiaowoThermostat):
            device_id = "t" + str(device.thermostat_id)
            entities.append(XiaowoSensor(hass, coordinator, device, 'thermostat_gateway_id', device_id))
            entities.append(XiaowoSensor(hass, coordinator, device, 'thermostat_id', device_id))
            entities.append(XiaowoSensor(hass, coordinator, device, 'room_temp', device_id))
            entities.append(XiaowoSensor(hass, coordinator, device, 'room_temp_correct', device_id))
            entities.append(XiaowoSensor(hass, coordinator, device, 'thermostat_online', device_id))
            entities.append(XiaowoSensor(hass, coordinator, device, 'thermostat_name', device_id))
        if isinstance(device, XiaowoBoiler):
            device_id = "b" + str(device.boiler_id)
            entities.append(XiaowoSensor(hass, coordinator, device, 'boiler_gateway_id', device_id))
            entities.append(XiaowoSensor(hass, coordinator, device, 'boiler_id', device_id))
            entities.append(XiaowoSensor(hass, coordinator, device, 'boiler_online', device_id))
            entities.append(XiaowoSensor(hass, coordinator, device, 'water_pressure_value', device_id))
            entities.append(XiaowoSensor(hass, coordinator, device, 'heating_water_temp', device_id))
            entities.append(XiaowoSensor(hass, coordinator, device, 'dhw_water_temp', device_id))
            entities.append(XiaowoSensor(hass, coordinator, device, 'heating_return_water_temp', device_id))
            entities.append(XiaowoSensor(hass, coordinator, device, 'dhw_return_water_temp', device_id))
            entities.append(XiaowoSensor(hass, coordinator, device, 'flame_status', device_id))
            entities.append(XiaowoSensor(hass, coordinator, device, 'fault_code', device_id))
            entities.append(XiaowoSensor(hass, coordinator, device, 'dhw_preheat_mode', device_id))
        if isinstance(device, XiaowoExtBoiler):
            device_id = "e" + str(device.gateway_id)
            entities.append(XiaowoSensor(hass, coordinator, device, 'ext_boiler_gateway_id', device_id))
            entities.append(XiaowoSensor(hass, coordinator, device, 'ext_boiler_online', device_id))
            entities.append(XiaowoSensor(hass, coordinator, device, 'ext_ch_water_temp', device_id))
            entities.append(XiaowoSensor(hass, coordinator, device, 'ext_dhw_water_temp', device_id))
            entities.append(XiaowoSensor(hass, coordinator, device, 'ext_flame', device_id))
            entities.append(XiaowoSensor(hass, coordinator, device, 'ext_error_code', device_id))

    async_add_entities(entities)


class XiaowoSensor(XiaowoEntity, SensorEntity):
    """定义一个温度传感器的类，继承自HomeAssistant的Entity类."""

    def __init__(self, hass, coordinator, device, option, device_id):
        """初始化."""
        super().__init__(hass, coordinator, device, device_id)
        self._object_id = OPTIONS[option][0]
        self._name = OPTIONS[option][1]
        self._icon = OPTIONS[option][2]
        self._type = option
        self._attr_unique_id = f"{super().unique_id}{OPTIONS[option][0]}"
        unit = OPTIONS[option][3]
        if unit == UnitOfTemperature.CELSIUS:
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_native_unit_of_measurement = unit
            self._attr_suggested_display_precision = 1
        elif unit == UnitOfPressure.BAR:
            self._attr_device_class = SensorDeviceClass.PRESSURE
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_native_unit_of_measurement = unit
            self._attr_suggested_display_precision = 1
        if self._type in ("thermostat_online", "boiler_online", "ext_boiler_online"):
            self._attr_device_class = "enum"
            self._attr_options: list[str] = ['在线', '离线']
        elif self._type == "flame_status":
            self._attr_device_class = "enum"
            self._attr_options: list[str] = ['无火', '有火']
        elif self._type == "ext_flame":
            self._attr_device_class = "enum"
            self._attr_options: list[str] = ['有火', '无火']
        elif self._type == "dhw_preheat_mode":
            self._attr_device_class = "enum"
            self._attr_options: list[str] = ['未启用', '短时预热', '定时预热', '水控单次预热']

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
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        return {"states": SENSOR_RAW[self._type](self._device)}

    @property
    def native_value(self):
        """返回当前的状态."""
        raw = SENSOR_RAW[self._type](self._device)
        display = SENSOR_DISPLAY.get(self._type)
        if display is not None:
            return display(raw)
        return raw

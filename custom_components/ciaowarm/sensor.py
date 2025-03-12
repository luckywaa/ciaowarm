"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
)
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
    "thermostat_gateway_id": ["Thermostat_gateway_id", "网关ID", "mdi:identifier", ' '],
    "thermostat_id": ["Thermostat_thermostat_id", "温控器ID", "mdi:identifier", ' '],
    "room_temp": ["Thermostat_room_temp", "室内温度", "mdi:home-thermometer-outline", '°C'],
    "room_temp_correct": ["Thermostat_room_temp_correct", "修正后室内温度", "mdi:home-thermometer-outline", '°C'],
    "thermostat_online": ["Thermostat_online", "温控器在线状态", "mdi:signal-variant", ' '],
    "thermostat_name": ["Thermostat_thermostat_name", "温控器名称", "mdi:subtitles-outline", ' '],

    "boiler_gateway_id": ["Boiler_gateway_id", "网关ID", "mdi:identifier", ' '],
    "boiler_id": ["Boiler_boiler_id", "壁挂炉ID", "mdi:identifier", ' '],
    "boiler_online": ["Boiler_boiler_online", "壁挂炉在线状态", "mdi:signal-variant", ' '],
    "water_pressure_value": ["Boiler_water_pressure_value", "水压值", "mdi:speedometer", ' '],
    "heating_water_temp": ["Boiler_heating_water_temp", "采暖水出水温度", "mdi:sun-thermometer-outline", '°C'],
    "dhw_water_temp": ["Boiler_dhw_water_temp", "卫浴水出水温度", "mdi:water-thermometer-outline", '°C'],
    "heating_return_water_temp": ["Boiler_heating_return_water_temp", "采暖水回水温度", "mdi:sun-thermometer-outline", '°C'],
    "dhw_return_water_temp": ["Boiler_dhw_return_water_temp", "卫浴水回水温度", "mdi:water-thermometer-outline", '°C'],
    "flame_status": ["Boiler_flame_status", "火焰状态", "mdi:fire", ' '],
    "fault_code": ["Boiler_fault_code", "故障码", "mdi:alert-outline", ' '],
    "dhw_preheat_mode": ["Boiler_dhw_preheat_mode", "卫浴水工作模式", "mdi:alpha-m-box-outline", ' '],

    "ext_boiler_gateway_id": ["Ext_boiler_gateway_id", "网关ID", "mdi:identifier", ' '],
    "ext_boiler_online": ["Ext_boiler_online", "网关在线状态", "mdi:signal-variant", ' '],
    "ext_ch_water_temp": ["Ext_boiler_ch_water_temp", "采暖水实际温度", "mdi:sun-thermometer-outline", '°C'],
    "ext_dhw_water_temp": ["Ext_boiler_dhw_water_temp", "卫浴水实际温度", "mdi:water-thermometer-outline",
                           '°C'],
    "ext_flame": ["Ext_boiler_flame", "火焰状态", "mdi:fire", ' '],
    "ext_error_code": ["Ext_boiler_error_code", "故障码", "mdi:alert-outline", ' '],
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    hass_data: HomeAssistantXiaowoData = hass.data[DOMAIN][entry.entry_id]
    device_list = hass_data.device_list
    entities: list[XiaowoSensor] = []
    for device in device_list:
        if isinstance(device, XiaowoThermostat):
            device_id = "t" + str(device.thermostat_id)
            entities.append(XiaowoSensor(device, 'thermostat_gateway_id', device.gateway_id, device_id))
            entities.append(XiaowoSensor(device, 'thermostat_id', device.thermostat_id, device_id))
            entities.append(XiaowoSensor(device, 'room_temp', device.room_temp, device_id))
            entities.append(XiaowoSensor(device, 'room_temp_correct', device.room_temp_correct, device_id))
            entities.append(XiaowoSensor(device, 'thermostat_online', device.thermostat_online, device_id))
            entities.append(XiaowoSensor(device, 'thermostat_name', device.thermostat_name, device_id))
        if isinstance(device, XiaowoBoiler):
            device_id = "b" + str(device.boiler_id)
            entities.append(XiaowoSensor(device, 'boiler_gateway_id', device.gateway_id, device_id))
            entities.append(XiaowoSensor(device, 'boiler_id', device.boiler_id, device_id))
            entities.append(XiaowoSensor(device, 'boiler_online', device.boiler_online, device_id))
            entities.append(XiaowoSensor(device, 'water_pressure_value', device.water_pressure_value, device_id))
            entities.append(XiaowoSensor(device, 'heating_water_temp', device.heating_water_temp, device_id))
            entities.append(XiaowoSensor(device, 'dhw_water_temp', device.dhw_water_temp, device_id))
            entities.append(XiaowoSensor(device, 'heating_return_water_temp', device.heating_return_water_temp, device_id))
            entities.append(XiaowoSensor(device, 'dhw_return_water_temp', device.dhw_return_water_temp, device_id))
            entities.append(XiaowoSensor(device, 'flame_status', device.flame_status, device_id))
            entities.append(XiaowoSensor(device, 'fault_code', device.fault_code, device_id))
            entities.append(XiaowoSensor(device, 'dhw_preheat_mode', device.dhw_preheat_mode, device_id))
        if isinstance(device, XiaowoExtBoiler):
            device_id = "e" + str(device.gateway_id)
            entities.append(XiaowoSensor(device, 'ext_boiler_gateway_id', device.gateway_id, device_id))
            entities.append(XiaowoSensor(device, 'ext_boiler_online', device.ext_boiler_online, device_id))
            entities.append(XiaowoSensor(device, 'ext_ch_water_temp', device.ch_water_temp, device_id))
            entities.append(XiaowoSensor(device, 'ext_dhw_water_temp', device.dhw_water_temp, device_id))
            entities.append(XiaowoSensor(device, 'ext_flame', device.flame, device_id))
            entities.append(XiaowoSensor(device, 'ext_error_code', device.error_code, device_id))

    async_add_entities(entities)


class XiaowoSensor(XiaowoEntity, SensorEntity):
    """定义一个温度传感器的类，继承自HomeAssistant的Entity类."""

    def __init__(self, device, option, option_value, device_id):
        """初始化."""
        super().__init__(device_id)
        self._device = device
        self._object_id = OPTIONS[option][0]
        self._name = OPTIONS[option][1]
        self._icon = OPTIONS[option][2]
        self._unit_of_measurement = OPTIONS[option][3]
        self._type = option
        self._attr_state = None
        self._attributes = {"states": "null"}
        self._attr_unique_id = f"{super().unique_id}{OPTIONS[option][0]}"
        self._option_value = option_value
        if self._type == "thermostat_online":
            self._attr_device_class = "enum"
            self._attr_options: list[str] = ['在线', '离线']
        elif self._type == "boiler_online":
            self._attr_device_class = "enum"
            self._attr_options: list[str] = ['在线', '离线']
        elif self._type == "flame_status":
            self._attr_device_class = "enum"
            self._attr_options: list[str] = ['无火', '有火']
        elif self._type == "ext_boiler_online":
            self._attr_device_class = "enum"
            self._attr_options: list[str] = ['在线', '离线']
        elif self._type == "ext_flame":
            self._attr_device_class = "enum"
            self._attr_options: list[str] = ['有火', '无火']


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
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        return self._attributes

    @property
    def state(self):
        """返回当前的状态."""
        return self._attr_state

    # @asyncio.coroutine
    async def async_update(self):
        if self._type == 'thermostat_gateway_id':
            self._attr_state = self._device.gateway_id
            self._attributes["states"] = self._device.gateway_id
        elif self._type == "thermostat_id":
            self._attr_state = self._device.thermostat_id
            self._attributes["states"] = self._device.thermostat_id
        elif self._type == "room_temp":
            self._attr_state = self._device.room_temp / 10
            self._attributes["states"] = self._device.room_temp / 10
        elif self._type == "room_temp_correct":
            self._attr_state = self._device.room_temp_correct / 10
            self._attributes["states"] = self._device.room_temp_correct / 10
        elif self._type == "thermostat_online":
            if self._device.thermostat_online:
                self._attr_state = "在线"
            else:
                self._attr_state = "离线"
            self._attributes["states"] = self._device.thermostat_online
        elif self._type == "thermostat_name":
            self._attr_state = self._device.thermostat_name
            self._attributes["states"] = self._device.thermostat_name
        elif self._type == "boiler_gateway_id":
            self._attr_state = self._device.gateway_id
            self._attributes["states"] = self._device.gateway_id
        elif self._type == "boiler_id":
            self._attr_state = self._device.boiler_id
            self._attributes["states"] = self._device.boiler_id
        elif self._type == "boiler_online":
            if self._device.boiler_online:
                self._attr_state = "在线"
            else:
                self._attr_state = "离线"
            self._attributes["states"] = self._device.boiler_online
        elif self._type == "water_pressure_value":
            self._attr_state = self._device.water_pressure_value / 10
            self._attributes["states"] = self._device.water_pressure_value / 10
        elif self._type == "heating_water_temp":
            self._attr_state = self._device.heating_water_temp
            self._attributes["states"] = self._device.heating_water_temp
        elif self._type == "dhw_water_temp":
            self._attr_state = self._device.dhw_water_temp
            self._attributes["states"] = self._device.dhw_water_temp
        elif self._type == "heating_return_water_temp":
            self._attr_state = self._device.heating_return_water_temp
            self._attributes["states"] = self._device.heating_return_water_temp
        elif self._type == "dhw_return_water_temp":
            self._attr_state = self._device.dhw_return_water_temp
            self._attributes["states"] = self._device.dhw_return_water_temp
        elif self._type == "flame_status":
            if self._device.flame_status:
                self._attr_state = "无火"
            else:
                self._attr_state = "有火"
            self._attributes["states"] = self._device.flame_status
        elif self._type == "fault_code":
            self._attr_state = self._device.fault_code
            self._attributes["states"] = self._device.fault_code
        elif self._type == "dhw_preheat_mode":
            if self._device.dhw_preheat_mode == 1:
                self._attr_state = "短时预热"
            elif self._device.dhw_preheat_mode == 2:
                self._attr_state = "定时预热"
            elif self._device.dhw_preheat_mode == 3:
                self._attr_state = "水控单次预热"
            else:
                self._attr_state = "未启用"
            self._attributes["states"] = self._device.dhw_preheat_mode
        elif self._type == "ext_boiler_gateway_id":
            self._attr_state = self._device.gateway_id
            self._attributes["states"] = self._device.gateway_id
        elif self._type == "ext_boiler_online":
            if self._device.ext_boiler_online:
                self._attr_state = "在线"
            else:
                self._attr_state = "离线"
            self._attributes["states"] = self._device.ext_boiler_online
        elif self._type == "ext_ch_water_temp":
            self._attr_state = self._device.ch_water_temp
            self._attributes["states"] = self._device.ch_water_temp
        elif self._type == "ext_dhw_water_temp":
            self._attr_state = self._device.dhw_water_temp
            self._attributes["states"] = self._device.dhw_water_temp
        elif self._type == "ext_flame":
            if self._device.flame == 1:
                self._attr_state = "有火"
            else:
                self._attr_state = "无火"
            self._attributes["states"] = self._device.flame
        elif self._type == "ext_error_code":
            self._attr_state = self._device.error_code
            self._attributes["states"] = self._device.error_code

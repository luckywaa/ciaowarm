import asyncio
from datetime import timedelta

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    DOMAIN,
    LOGGER,
    REQUEST_URL_PREFIX,
    CONF_PHONE,
    CONF_KEY,
    XiaowoApiError,
    XiaowoDevice, XiaowoThermostat, XiaowoBoiler, XiaowoExtBoiler
)

GATEWAY_PLATFORMS = [
    Platform.SENSOR,
    Platform.NUMBER,
    Platform.SWITCH,
    Platform.CLIMATE,
    Platform.WATER_HEATER,
]

UPDATE_INTERVAL = timedelta(seconds=20)

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=10)

# 已被 climate / water_heater 实体接管、不再由本集成提供的旧控件，
# 以及已由 switch 实体取代的旧 select 控件，
# 升级后需从实体注册表移除，避免残留不可用的孤儿实体
STALE_ENTITY_SUFFIXES = (
    "Thermostat_work_mode",
    "Thermostat_trg_temp_leave",
    "Thermostat_trg_temp_home",
    "Thermostat_trg_temp_sleep",
    "Boiler_switch_ctrl",
    "Boiler_season_ctrl",
    "Boiler_dhw_trg_temp",
    "Boiler_auto_ctrl",
    "Boiler_dhw_preheat_status",
    "Ext_boiler_auto_ctrl",
    "Ext_boiler_ch_enable",
    "Ext_boiler_dhw_enable",
)


async def async_fetch_device_info(hass: HomeAssistant, phone: str, token: str) -> list:
    """调用设备信息接口，返回 message_info；接口错误抛 XiaowoApiError，网络错误抛 aiohttp 异常。"""
    _device_info_url = REQUEST_URL_PREFIX + "/ciaowarm/hass/v1/device/info?phone=" + phone
    session = async_get_clientsession(hass)
    async with session.get(_device_info_url, headers={'token': token},
                           timeout=REQUEST_TIMEOUT) as response:
        json_data = await response.json()
    message_code = json_data.get("message_code")
    if message_code != 0:
        raise XiaowoApiError(json_data.get("message_info", "未知错误"))
    return json_data.get("message_info") or []


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ciaowarm from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    phone = entry.data[CONF_PHONE]
    access_token = entry.data[CONF_KEY]

    try:
        message_info = await async_fetch_device_info(hass, phone, access_token)
    except XiaowoApiError as err:
        LOGGER.error("接口返回错误：%s", err)
        return False
    except (asyncio.TimeoutError, aiohttp.ClientError):
        LOGGER.error("访问接口失败：%s", REQUEST_URL_PREFIX)
        return False

    device_registry = dr.async_get(hass)
    device_list: list[XiaowoDevice] = []
    for item in message_info:
        gateway_id = item.get('gateway_id')
        for gateway_item in item:
            if gateway_item == "thermostats":
                thermostats = item[gateway_item]
                for thermostat in thermostats:
                    device_list.append(XiaowoThermostat(phone, access_token, gateway_id, thermostat))
                    thermostat_id = "t" + str(thermostat["thermostat_id"])
                    device_registry.async_get_or_create(
                        config_entry_id=entry.entry_id,
                        identifiers={(DOMAIN, thermostat_id)},
                        manufacturer="IWARM TECH CO., LTD.",
                        name=thermostat["thermostat_name"],
                        model=f"thermostat",
                    )
            if gateway_item == "boilers":
                boilers = item[gateway_item]
                for boiler in boilers:
                    device_list.append(XiaowoBoiler(phone, access_token, gateway_id, boiler))
                    boiler_id = "b" + str(boiler["boiler_id"])
                    device_registry.async_get_or_create(
                        config_entry_id=entry.entry_id,
                        identifiers={(DOMAIN, boiler_id)},
                        manufacturer="IWARM TECH CO., LTD.",
                        name="小沃壁挂炉",
                        model=f"boiler",
                    )
            if gateway_item == "extBoiler":
                ext_boiler = item[gateway_item]
                device_list.append(XiaowoExtBoiler(phone, access_token, gateway_id, ext_boiler))
                ext_boiler_id = "e" + str(gateway_id)
                device_registry.async_get_or_create(
                    config_entry_id=entry.entry_id,
                    identifiers={(DOMAIN, ext_boiler_id)},
                    manufacturer="IWARM TECH CO., LTD.",
                    name="第三方壁挂炉",
                    model=f"extBoiler",
                )

    coordinator = XiaowoCoordinator(hass, phone, access_token, device_list)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "devices": device_list,
    }

    _async_remove_stale_entities(hass, entry)

    await hass.config_entries.async_forward_entry_setups(entry, GATEWAY_PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


def _async_remove_stale_entities(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """移除已被 climate / water_heater 接管、不再提供的旧实体。"""
    entity_registry = er.async_get(hass)
    for registry_entry in list(entity_registry.entities.values()):
        if registry_entry.platform != DOMAIN:
            continue
        if registry_entry.config_entry_id != entry.entry_id:
            continue
        if registry_entry.unique_id.endswith(STALE_ENTITY_SUFFIXES):
            entity_registry.async_remove(registry_entry.entity_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, GATEWAY_PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def update_listener(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


class XiaowoCoordinator(DataUpdateCoordinator[list[XiaowoDevice]]):
    """轮询云端设备信息并更新共享数据模型对象。"""

    def __init__(self, hass: HomeAssistant, phone: str, token: str, device_list: list[XiaowoDevice]):
        """Initialize coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self._phone = phone
        self._token = token
        self.device_list = device_list

    async def _async_update_data(self) -> list[XiaowoDevice]:
        """拉取设备信息并更新数据模型，失败抛 UpdateFailed。"""
        try:
            message_info = await async_fetch_device_info(self.hass, self._phone, self._token)
        except XiaowoApiError as err:
            raise UpdateFailed(f"接口返回错误：{err}") from err
        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            raise UpdateFailed(f"访问云端接口失败：{err}") from err

        for item in message_info:
            gateway_id = item.get('gateway_id')
            for gateway_item in item:
                if gateway_item == "thermostats":
                    for thermostat in item[gateway_item]:
                        for device in self.device_list:
                            if isinstance(device, XiaowoThermostat):
                                if device.thermostat_id == thermostat.get('thermostat_id'):
                                    device.update(thermostat)
                if gateway_item == "boilers":
                    for boiler in item[gateway_item]:
                        for device in self.device_list:
                            if isinstance(device, XiaowoBoiler):
                                if device.boiler_id == boiler.get('boiler_id'):
                                    device.update(boiler)
                if gateway_item == "extBoiler":
                    ext_boiler = item[gateway_item]
                    for device in self.device_list:
                        if isinstance(device, XiaowoExtBoiler):
                            if device.gateway_id == gateway_id:
                                device.update(ext_boiler)
        return self.device_list

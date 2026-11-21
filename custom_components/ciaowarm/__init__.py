import asyncio
from datetime import timedelta

import aiohttp

from homeassistant.components.logbook import async_log_entry
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
    WORK_MODE_LABELS,
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

# climate 预设/目标温度与热水器卫浴水目标温度属于实体属性变化，
# 原生 Logbook 只按状态值渲染、不会显示；开关/数值实体的状态变化原生已有记录。
# 轮询确认这些属性变化后补写中文 Logbook 条目，App 端等外部操作同样生效。
THERMOSTAT_LOG_FIELDS = {
    "trg_temp_leave": "离家模式目标温度",
    "trg_temp_home": "居家模式目标温度",
    "trg_temp_sleep": "睡眠模式目标温度",
}
BOILER_LOG_FIELDS = {
    "dhw_trg_temp": "卫浴水目标温度",
}

# 云端在设备链路抖动时会短暂把目标温度类设定值清零（温控器 5–35℃、卫浴水 30–60℃，0 非合法设定），
# 这类 0 值不采用：轮询时沿用上一轮值，避免实体属性闪变与「调整为 0℃」的假日志
ZERO_GLITCH_FIELDS = (
    "trg_temp_leave",
    "trg_temp_home",
    "trg_temp_sleep",
    "dhw_trg_temp",
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
                                    thermostat = self._drop_zero_glitch(device, thermostat)
                                    self._log_thermostat_changes(device, thermostat)
                                    device.update(thermostat)
                if gateway_item == "boilers":
                    for boiler in item[gateway_item]:
                        for device in self.device_list:
                            if isinstance(device, XiaowoBoiler):
                                if device.boiler_id == boiler.get('boiler_id'):
                                    boiler = self._drop_zero_glitch(device, boiler)
                                    self._log_boiler_changes(device, boiler)
                                    device.update(boiler)
                if gateway_item == "extBoiler":
                    ext_boiler = item[gateway_item]
                    for device in self.device_list:
                        if isinstance(device, XiaowoExtBoiler):
                            if device.gateway_id == gateway_id:
                                device.update(ext_boiler)
        return self.device_list

    @staticmethod
    def _drop_zero_glitch(device: XiaowoDevice, payload: dict) -> dict:
        """云端抖动清零时沿用上一轮值，并以 debug 日志留痕便于定位。"""
        for field in ZERO_GLITCH_FIELDS:
            if payload.get(field) == 0:
                LOGGER.debug("云端将 %s 清零，疑为链路抖动，沿用上一轮值", field)
                payload[field] = getattr(device, field, None)
        return payload

    def _logbook_entry(self, name: str, message: str, platform: Platform, unique_id: str) -> None:
        """写入一条 Logbook 条目并归属到对应实体。"""
        entity_id = er.async_get(self.hass).async_get_entity_id(platform, DOMAIN, unique_id)
        async_log_entry(self.hass, name, message, DOMAIN, entity_id)

    def _log_thermostat_changes(self, device: XiaowoThermostat, thermostat: dict) -> None:
        """轮询确认温控器模式与各模式目标温度变化后补写 Logbook（原生不显示属性变化）。"""
        unique_id = f"xiaowo.t{device.thermostat_id}Thermostat_climate"
        name = device.thermostat_name or "小沃温控器"
        old_mode = device.work_mode
        new_mode = thermostat.get("work_mode")
        if old_mode is not None and new_mode is not None and old_mode != new_mode:
            self._logbook_entry(
                name,
                f"模式由「{WORK_MODE_LABELS.get(old_mode, old_mode)}」"
                f"切换为「{WORK_MODE_LABELS.get(new_mode, new_mode)}」",
                Platform.CLIMATE,
                unique_id,
            )
        for field, label in THERMOSTAT_LOG_FIELDS.items():
            old_value = getattr(device, field, None)
            new_value = thermostat.get(field)
            # 0 值为云端抖动假数据（可能残留于启动初值），双向跳过
            if not old_value or not new_value or old_value == new_value:
                continue
            self._logbook_entry(
                name, f"{label}由 {old_value}℃ 调整为 {new_value}℃", Platform.CLIMATE, unique_id)

    def _log_boiler_changes(self, device: XiaowoBoiler, boiler: dict) -> None:
        """轮询确认壁挂炉属性变化后补写 Logbook（原生不显示属性变化）。"""
        unique_id = f"xiaowo.b{device.boiler_id}Boiler_water_heater"
        for field, label in BOILER_LOG_FIELDS.items():
            old_value = getattr(device, field, None)
            new_value = boiler.get(field)
            # 0 值为云端抖动假数据（可能残留于启动初值），双向跳过
            if not old_value or not new_value or old_value == new_value:
                continue
            self._logbook_entry(
                "小沃壁挂炉", f"{label}由 {old_value}℃ 调整为 {new_value}℃",
                Platform.WATER_HEATER, unique_id)

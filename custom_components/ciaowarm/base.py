import asyncio

import aiohttp

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    LOGGER,
    REQUEST_URL_PREFIX,
)

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=10)


class XiaowoEntity(CoordinatorEntity):
    """小沃实体基类：状态由 coordinator 推送，短暂轮询失败保持可用并沿用最后一轮数据。"""

    _attr_should_poll = False

    def __init__(self, hass, coordinator, device, device_id) -> None:
        """初始化."""
        # CoordinatorEntity 首个参数即 coordinator，无 hass 参数
        super().__init__(coordinator)
        self._hass = hass
        self._device = device
        self._device_id = device_id
        self._attr_unique_id = f"xiaowo.{device_id}"

    @property
    def available(self) -> bool:
        """连续失败超过宽限阈值（约 5 分钟）或设备离线时不可用."""
        return (self.coordinator.last_update_success or not self.coordinator.degraded) and self._device.online

    @property
    def device_info(self) -> DeviceInfo:
        """Return a device description for device registry."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
        )

    async def _send_command(self, option_key, option_value) -> None:
        """下发控制指令，失败抛 HomeAssistantError 由前端展示。"""
        _device_info_url = REQUEST_URL_PREFIX + "/ciaowarm/hass/v1/device/info"
        data = {
            'phone': self._device.phone,
            'gateway_id': self._device.gateway_id,
            'thermostat_id': self._device.thermostat_id,
            'boiler_id': self._device.boiler_id,
            'option_key': option_key,
            'option_value': option_value
        }
        session = async_get_clientsession(self._hass)
        try:
            async with session.put(_device_info_url, data=data, headers={'token': self._device.token},
                                   timeout=REQUEST_TIMEOUT) as response:
                json_data = await response.json()
        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            LOGGER.error("访问接口失败：%s", _device_info_url)
            raise HomeAssistantError("设备指令发送失败，请检查网络后重试") from err
        if json_data is None or json_data.get("message_code") != 0:
            message_info = json_data.get("message_info") if json_data else None
            LOGGER.error("指令下发失败：%s", message_info)
            raise HomeAssistantError(f"指令下发失败：{message_info}")

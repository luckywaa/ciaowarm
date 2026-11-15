import logging

DOMAIN = "ciaowarm"
LOGGER = logging.getLogger(__package__)
REQUEST_URL_PREFIX = "https://api.iwarm.com"
CONF_PHONE = "phone"
CONF_KEY = "key"


class XiaowoApiError(Exception):
    """小沃云端接口返回错误。"""


class XiaowoDevice:
    def __init__(self, phone, token, gateway_id, thermostat_id, boiler_id):
        self.phone = phone
        self.token = token
        self.gateway_id = gateway_id
        self.thermostat_id = thermostat_id
        self.boiler_id = boiler_id


class XiaowoThermostat(XiaowoDevice):
    def __init__(self, phone, token, gateway_id, thermostat):
        self.phone = phone
        self.token = token
        self.gateway_id = gateway_id
        self.thermostat_id = thermostat.get('thermostat_id')
        self.boiler_id = 0
        self.work_mode = thermostat.get('work_mode')
        self.trg_temp = thermostat.get('trg_temp')
        self.room_temp = thermostat.get('room_temp')
        self.room_temp_correct = thermostat.get('room_temp_correct')
        self.trg_temp_home = thermostat.get('trg_temp_home')
        self.trg_temp_leave = thermostat.get('trg_temp_leave')
        self.trg_temp_sleep = thermostat.get('trg_temp_sleep')
        self.thermostat_online = thermostat.get('thermostat_online')
        self.thermostat_name = thermostat.get('thermostat_name')

    @property
    def online(self) -> bool:
        """设备是否在线."""
        return bool(self.thermostat_online)

    def update(self, thermostat):
        self.work_mode = thermostat.get('work_mode')
        self.trg_temp = thermostat.get('trg_temp')
        self.room_temp = thermostat.get('room_temp')
        self.room_temp_correct = thermostat.get('room_temp_correct')
        self.trg_temp_home = thermostat.get('trg_temp_home')
        self.trg_temp_leave = thermostat.get('trg_temp_leave')
        self.trg_temp_sleep = thermostat.get('trg_temp_sleep')
        self.thermostat_online = thermostat.get('thermostat_online')
        self.thermostat_name = thermostat.get('thermostat_name')


class XiaowoBoiler(XiaowoDevice):
    def __init__(self, phone, token, gateway_id, boiler):
        self.phone = phone
        self.token = token
        self.gateway_id = gateway_id
        self.thermostat_id = 0
        self.boiler_id = boiler.get('boiler_id')
        self.heating_trg_temp = boiler.get('heating_trg_temp')
        self.dhw_trg_temp = boiler.get('dhw_trg_temp')
        self.auto_ctrl = boiler.get('auto_ctrl')
        self.season_ctrl = boiler.get('season_ctrl')
        self.switch_ctrl = boiler.get('switch_ctrl')
        self.dhw_preheat_enable = boiler.get('dhw_preheat_enable')
        self.dhw_preheat_status = boiler.get('dhw_preheat_status')
        self.boiler_online = boiler.get('boiler_online')
        self.water_pressure_value = boiler.get('water_pressure_value')
        self.heating_water_temp = boiler.get('heating_water_temp')
        self.dhw_water_temp = boiler.get('dhw_water_temp')
        self.heating_return_water_temp = boiler.get('heating_return_water_temp')
        self.dhw_return_water_temp = boiler.get('dhw_return_water_temp')
        self.flame_status = boiler.get('flame_status')
        self.fault_code = boiler.get('fault_code')
        self.dhw_preheat_mode = boiler.get('dhw_preheat_mode')

    @property
    def online(self) -> bool:
        """设备是否在线."""
        return bool(self.boiler_online)

    def update(self, boiler):
        self.heating_trg_temp = boiler.get('heating_trg_temp')
        self.dhw_trg_temp = boiler.get('dhw_trg_temp')
        self.auto_ctrl = boiler.get('auto_ctrl')
        self.season_ctrl = boiler.get('season_ctrl')
        self.switch_ctrl = boiler.get('switch_ctrl')
        self.dhw_preheat_enable = boiler.get('dhw_preheat_enable')
        self.dhw_preheat_status = boiler.get('dhw_preheat_status')
        self.boiler_online = boiler.get('boiler_online')
        self.water_pressure_value = boiler.get('water_pressure_value')
        self.heating_water_temp = boiler.get('heating_water_temp')
        self.dhw_water_temp = boiler.get('dhw_water_temp')
        self.heating_return_water_temp = boiler.get('heating_return_water_temp')
        self.dhw_return_water_temp = boiler.get('dhw_return_water_temp')
        self.flame_status = boiler.get('flame_status')
        self.fault_code = boiler.get('fault_code')
        self.dhw_preheat_mode = boiler.get('dhw_preheat_mode')


class XiaowoExtBoiler(XiaowoDevice):
    def __init__(self, phone, token, gateway_id, ext_boiler):
        self.phone = phone
        self.token = token
        self.gateway_id = gateway_id
        self.thermostat_id = 0
        self.boiler_id = 0
        self.ch_setpoint = ext_boiler.get('ch_setpoint')
        self.dhw_setpoint = ext_boiler.get('dhw_setpoint')
        self.ext_auto_ctrl = ext_boiler.get('ext_auto_ctrl')
        self.ch_enable = ext_boiler.get('ch_enable')
        self.dhw_enable = ext_boiler.get('dhw_enable')
        self.ext_boiler_online = ext_boiler.get('ext_boiler_online')
        self.ch_water_temp = ext_boiler.get('ch_water_temp')
        self.dhw_water_temp = ext_boiler.get('dhw_water_temp')
        self.flame = ext_boiler.get('flame')
        self.error_code = ext_boiler.get('error_code')

    @property
    def online(self) -> bool:
        """设备是否在线."""
        return bool(self.ext_boiler_online)

    def update(self, ext_boiler):
        self.ch_setpoint = ext_boiler.get('ch_setpoint')
        self.dhw_setpoint = ext_boiler.get('dhw_setpoint')
        self.ext_auto_ctrl = ext_boiler.get('ext_auto_ctrl')
        self.ch_enable = ext_boiler.get('ch_enable')
        self.dhw_enable = ext_boiler.get('dhw_enable')
        self.ext_boiler_online = ext_boiler.get('ext_boiler_online')
        self.ch_water_temp = ext_boiler.get('ch_water_temp')
        self.dhw_water_temp = ext_boiler.get('dhw_water_temp')
        self.flame = ext_boiler.get('flame')
        self.error_code = ext_boiler.get('error_code')

import logging

DOMAIN = "ciaowarm"
LOGGER = logging.getLogger(__package__)
REQUEST_URL_PREFIX = "https://api.iwarm.com"
CONF_PHONE = "phone"
CONF_KEY = "key"


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
        self.thermostat_id = thermostat['thermostat_id']
        self.boiler_id = 0
        self.work_mode = thermostat['work_mode']
        self.trg_temp = thermostat['trg_temp']
        self.room_temp = thermostat['room_temp']
        self.room_temp_correct = thermostat['room_temp_correct']
        self.trg_temp_home = thermostat['trg_temp_home']
        self.trg_temp_leave = thermostat['trg_temp_leave']
        self.trg_temp_sleep = thermostat['trg_temp_sleep']
        self.thermostat_online = thermostat['thermostat_online']
        self.thermostat_name = thermostat['thermostat_name']

    def update(self, thermostat):
        self.work_mode = thermostat['work_mode']
        self.trg_temp = thermostat['trg_temp']
        self.room_temp = thermostat['room_temp']
        self.room_temp_correct = thermostat['room_temp_correct']
        self.trg_temp_home = thermostat['trg_temp_home']
        self.trg_temp_leave = thermostat['trg_temp_leave']
        self.trg_temp_sleep = thermostat['trg_temp_sleep']
        self.thermostat_online = thermostat['thermostat_online']
        self.thermostat_name = thermostat['thermostat_name']


class XiaowoBoiler(XiaowoDevice):
    def __init__(self, phone, token, gateway_id, boiler):
        self.phone = phone
        self.token = token
        self.gateway_id = gateway_id
        self.thermostat_id = 0
        self.boiler_id = boiler['boiler_id']
        self.heating_trg_temp = boiler['heating_trg_temp']
        self.dhw_trg_temp = boiler['dhw_trg_temp']
        self.auto_ctrl = boiler['auto_ctrl']
        self.season_ctrl = boiler['season_ctrl']
        self.switch_ctrl = boiler['switch_ctrl']
        self.dhw_preheat_enable = boiler['dhw_preheat_enable']
        self.dhw_preheat_status = boiler['dhw_preheat_status']
        self.boiler_online = boiler['boiler_online']
        self.water_pressure_value = boiler['water_pressure_value']
        self.heating_water_temp = boiler['heating_water_temp']
        self.dhw_water_temp = boiler['dhw_water_temp']
        self.heating_return_water_temp = boiler['heating_return_water_temp']
        self.dhw_return_water_temp = boiler['dhw_return_water_temp']
        self.flame_status = boiler['flame_status']
        self.fault_code = boiler['fault_code']

    def update(self, boiler):
        self.heating_trg_temp = boiler['heating_trg_temp']
        self.dhw_trg_temp = boiler['dhw_trg_temp']
        self.auto_ctrl = boiler['auto_ctrl']
        self.season_ctrl = boiler['season_ctrl']
        self.switch_ctrl = boiler['switch_ctrl']
        self.dhw_preheat_enable = boiler['dhw_preheat_enable']
        self.dhw_preheat_status = boiler['dhw_preheat_status']
        self.boiler_online = boiler['boiler_online']
        self.water_pressure_value = boiler['water_pressure_value']
        self.heating_water_temp = boiler['heating_water_temp']
        self.dhw_water_temp = boiler['dhw_water_temp']
        self.heating_return_water_temp = boiler['heating_return_water_temp']
        self.dhw_return_water_temp = boiler['dhw_return_water_temp']
        self.flame_status = boiler['flame_status']
        self.fault_code = boiler['fault_code']


class XiaowoExtBoiler(XiaowoDevice):
    def __init__(self, phone, token, gateway_id, ext_boiler):
        self.phone = phone
        self.token = token
        self.gateway_id = gateway_id
        self.thermostat_id = 0
        self.boiler_id = 0
        self.ch_setpoint = ext_boiler['ch_setpoint']
        self.dhw_setpoint = ext_boiler['dhw_setpoint']
        self.ext_auto_ctrl = ext_boiler['ext_auto_ctrl']
        self.ch_enable = ext_boiler['ch_enable']
        self.dhw_enable = ext_boiler['dhw_enable']
        self.ext_boiler_online = ext_boiler['ext_boiler_online']
        self.ch_water_temp = ext_boiler['ch_water_temp']
        self.dhw_water_temp = ext_boiler['dhw_water_temp']
        self.flame = ext_boiler['flame']
        self.error_code = ext_boiler['error_code']

    def update(self, ext_boiler):
        self.ch_setpoint = ext_boiler['ch_setpoint']
        self.dhw_setpoint = ext_boiler['dhw_setpoint']
        self.ext_auto_ctrl = ext_boiler['ext_auto_ctrl']
        self.ch_enable = ext_boiler['ch_enable']
        self.dhw_enable = ext_boiler['dhw_enable']
        self.ext_boiler_online = ext_boiler['ext_boiler_online']
        self.ch_water_temp = ext_boiler['ch_water_temp']
        self.dhw_water_temp = ext_boiler['dhw_water_temp']
        self.flame = ext_boiler['flame']
        self.error_code = ext_boiler['error_code']

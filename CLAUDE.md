# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Home Assistant custom integration (HACS-distributed) for Ciaowarm (小沃) heating products: thermostats, Ciaowarm wall-mounted boilers, and third-party boilers behind Starlink/Halowarm gateways. The integration is **cloud-polling only** — all device communication goes through the vendor REST API at `https://api.iwarm.com` (paths under `/ciaowarm/hass/v1/`). There is no local protocol.

The whole integration lives in `custom_components/ciaowarm/`. There is no build system, test suite, or linter — testing is manual: copy the `ciaowarm` folder into a Home Assistant config's `custom_components/` and restart HA.

## Architecture

### Data flow

1. `__init__.py:async_setup_entry` — authenticates with phone + authorization code (stored as config entry data; token sent in the `token` HTTP header), fetches the device list once, creates device-registry entries, and wraps everything in `HomeAssistantXiaowoData`, stored at `hass.data[DOMAIN][entry.entry_id]`.
2. `HomeAssistantXiaowoData.async_update` polls the same device-info endpoint every 20 s (`async_track_time_interval`) and calls `device.update(payload)` on the plain data-model objects in `device_list`.
3. Entities in `sensor.py` / `number.py` / `select.py` hold references to those shared data-model objects; their `async_update()` just reads fields off the object (no HTTP).
4. Writes go through `base.py:XiaowoEntity._send_command`, a PUT of `{phone, gateway_id, thermostat_id, boiler_id, option_key, option_value}`. On success the entity also writes the value back onto the shared device object so the next poll round-trips it.

### Data model (`const.py`)

`XiaowoThermostat`, `XiaowoBoiler`, `XiaowoExtBoiler` (all subclassing `XiaowoDevice`) are plain field-bag classes mirroring the JSON payload; `update()` re-assigns every field. Platform files dispatch on `isinstance(device, ...)`.

Device IDs and unique IDs:
- Device registry identifier / `device_id` prefixes: thermostat `t{thermostat_id}`, boiler `b{boiler_id}`, third-party boiler `e{gateway_id}`.
- Entity unique_id = `xiaowo.{device_id}{object_id}` where `object_id` is the first element of the platform's `OPTIONS` dict entry (e.g. `Thermostat_room_temp`).

### Cloud `option_key` codes

Writable parameters are identified by numeric API codes. They live as magic numbers in the platform files — the last element of each `OPTIONS` entry, then again in the `option_key == N` branches of the set/select handlers:

| key | parameter | key | parameter |
|-----|-----------|-----|-----------|
| 7 | boiler dhw_trg_temp | 23 | boiler switch_ctrl |
| 10 | boiler dhw_preheat_status | 27 | boiler auto_ctrl |
| 14/15/16 | thermostat trg_temp_leave/home/sleep | 33 | boiler heating_trg_temp |
| 17 | thermostat work_mode | 157 | ext auto_ctrl |
| 22 | boiler season_ctrl | 160/161 | ext ch_enable / dhw_enable |
| 163 | ext dhw_setpoint | 162 | ext ch_setpoint |

Interlock rule enforced client-side: heating-water target temp (`option_key` 33 and 162) is rejected while the corresponding auto-control flag (`auto_ctrl` / `ext_auto_ctrl`) is enabled.

### Adding or changing a supported parameter

Touches several files in lockstep — keep them in sync:
1. `const.py` — add the field to the data-model class's `__init__` **and** `update()`.
2. The platform file's `OPTIONS` dict (name/label/icon/unit, plus min/max/option_key for `number`, option list/option_key for `select`).
3. That platform's `async_setup_entry` (instantiate the entity) and `async_update` (read the field).
4. If writable: the set/select handler, including the `option_key == N` branch that updates the local device object after a successful command.
5. `README.md` — it documents every supported parameter in bilingual tables (Chinese first, then English); update both halves.

## Conventions

- User-facing strings (entity names, option labels like `开机`/`离家模式`) and log messages are in Chinese; keep new ones consistent with the existing style.
- Commit messages are written in Chinese.
- `manifest.json` `version` is bumped per release (currently `v0.1.4`); `hacs.json` pins the minimum HA version (`2023.12.3`).
- Some API values are integers scaled by 10 (e.g. `room_temp`, `water_pressure_value` — divided by 10 for display); ext-boiler flags come as `1`/`0` while boiler flags are booleans. Match the existing conversion per device type.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Home Assistant custom integration (HACS-distributed) for Ciaowarm (小沃) heating products: thermostats, Ciaowarm wall-mounted boilers, and third-party boilers behind Starlink/Halowarm gateways. The integration is **cloud-polling only** — all device communication goes through the vendor REST API at `https://api.iwarm.com` (paths under `/ciaowarm/hass/v1/`). There is no local protocol.

The whole integration lives in `custom_components/ciaowarm/`. There is no build system, test suite, or linter — testing is manual: copy the `ciaowarm` folder into a Home Assistant config's `custom_components/` and restart HA.

## Architecture

### Data flow

1. `__init__.py:async_setup_entry` — authenticates with phone + authorization code (stored as config entry data; token sent in the `token` HTTP header), fetches the device list once, creates device-registry entries (a gateway parent device per `gateway_id`, then per-device entries `via_device`-linked to it), then builds a `XiaowoCoordinator` (`DataUpdateCoordinator`, 20 s interval) stored as `hass.data[DOMAIN][entry.entry_id] = {"coordinator": ..., "devices": device_list}`. It also removes stale registry entities listed in `STALE_ENTITY_SUFFIXES` (controls superseded by climate/water_heater/switch).
2. `XiaowoCoordinator._async_update_data` polls the same device-info endpoint and calls `device.update(payload)` on the plain data-model objects; failures raise `UpdateFailed`, which flips every entity to unavailable until the next successful poll. Temperature fields listed in `ZERO_GLITCH_FIELDS` (target-temp setpoints + thermostat `room_temp`/`room_temp_correct`; 0 is never a plausible value for any of them, regardless of the cloud's online flag) that come back 0 (a transient cloud glitch while the device↔cloud link flaps) are replaced with the previous poll's value before log-compare/update, so entities don't flicker to 0℃ and no fake logbook entries are written; the log functions also skip entries where either side is 0.
3. All entities (in `sensor.py` / `number.py` / `switch.py` / `climate.py` / `water_heater.py`) extend `base.py:XiaowoEntity(CoordinatorEntity)` and read fields live off the shared data-model object via properties — no per-entity `async_update`. `available` = (coordinator success OR a failure streak below `UNAVAILABLE_AFTER_FAILURES`, a ~5-minute grace window so brief network blips keep entities available with stale data) AND the device's `online` property.
4. Writes go through `base.py:XiaowoEntity._send_command`, a PUT (form-encoded `data=`) of `{phone, gateway_id, thermostat_id, boiler_id, option_key, option_value}` using the shared `async_get_clientsession` session with a 10 s timeout. Failure raises `HomeAssistantError` (shown in the UI). Handlers do **not** write back to the device model or call `async_write_ha_state` — entity state and logbook entries always come from the next coordinator poll (≤ 20 s), for both HA- and app-originated changes. Because climate presets/target temps and the water-heater target temp are entity *attributes* (the logbook only narrates state values, not attribute changes), `XiaowoCoordinator._log_thermostat_changes` / `_log_boiler_changes` compare the shared model against each new payload before `device.update()` and inject Chinese logbook entries via `logbook.async_log_entry` for poll-confirmed changes (fields listed in `THERMOSTAT_LOG_FIELDS` / `BOILER_LOG_FIELDS`). Switch/number entity state changes narrate natively and are deliberately not duplicated.

### Control entities

- `climate.py` — one per thermostat (`xiaowo.t{id}Thermostat_climate`). Presets are the Chinese values 离家/居家/睡眠 (shared with the coordinator's logbook messages via `WORK_MODE_LABELS` in `const.py`, matching the vendor app) mapping to `work_mode` 0/1/2; setting the target temperature writes the setpoint of the *current* mode.
- `water_heater.py` — one per Ciaowarm boiler (`xiaowo.b{id}Boiler_water_heater`). Operations 关机/夏季/冬季 combine `switch_ctrl` + `season_ctrl`; target temperature is `dhw_trg_temp`. Power on/off controls the whole boiler, heating included.
- `switch.py` — binary flags: boiler `auto_ctrl`(27)/`dhw_preheat_status`(10, conditional on `dhw_preheat_enable`) and ext `ext_auto_ctrl`(157)/`ch_enable`(160)/`dhw_enable`(161). Boiler flags are booleans, ext flags `1`/`0`.
- Third-party (ext) boilers have no climate/water_heater entity — they use number/switch only.

### Data model (`const.py`)

`XiaowoThermostat`, `XiaowoBoiler`, `XiaowoExtBoiler` (all subclassing `XiaowoDevice`) are plain field-bag classes mirroring the JSON payload; `update()` re-assigns every field. Platform files dispatch on `isinstance(device, ...)`.

Device IDs and unique IDs:
- Device registry identifier / `device_id` prefixes: gateway `g{gateway_id}` (parent device, no entities), thermostat `t{thermostat_id}`, boiler `b{boiler_id}`, third-party boiler `e{gateway_id}`. The per-device entries are created `via_device`-linked to their gateway device so device pages cross-link (thermostat ↔ boiler via the gateway page); the `via_device` identifier-tuple form is removed in HA 2027.8 (migrate to `via_device_id` then).
- Entity unique_id = `xiaowo.{device_id}{object_id}` where `object_id` is the first element of the platform's `OPTIONS` dict entry (e.g. `Thermostat_room_temp`).

### Cloud `option_key` codes

Writable parameters are identified by numeric API codes. They live as magic numbers in the platform files — the last element of each `OPTIONS` entry, then again in the `option_key == N` branches of the set/turn-on handlers. Keys 14/15/16/17 (thermostat) are written by `climate.py`, 7/22/23 (boiler dhw/mode/power) by `water_heater.py`; the rest by `number.py`/`switch.py`:

| key | parameter | key | parameter |
|-----|-----------|-----|-----------|
| 7 | boiler dhw_trg_temp (water_heater) | 23 | boiler switch_ctrl (water_heater) |
| 10 | boiler dhw_preheat_status (switch) | 27 | boiler auto_ctrl (switch) |
| 14/15/16 | thermostat trg_temp_leave/home/sleep (climate) | 33 | boiler heating_trg_temp |
| 17 | thermostat work_mode (climate) | 157 | ext auto_ctrl (switch) |
| 22 | boiler season_ctrl (water_heater) | 160/161 | ext ch_enable / dhw_enable (switch) |
| 163 | ext dhw_setpoint | 162 | ext ch_setpoint |

Interlock rule enforced client-side: heating-water target temp (`option_key` 33 and 162) raises `HomeAssistantError` while the corresponding auto-control flag (`auto_ctrl` / `ext_auto_ctrl`) is enabled.

### Adding or changing a supported parameter

Touches several files in lockstep — keep them in sync:
1. `const.py` — add the field to the data-model class's `__init__` **and** `update()` (use `.get()` so missing keys become `None`).
2. The platform file's `OPTIONS` dict (name/label/icon/unit, plus min/max/option_key for `number`, option_key for `switch`).
3. That platform's `async_setup_entry` (instantiate the entity) and the property that reads the field (entities have no `async_update`).
4. If writable: the set/turn-on handler sends the command only — no local write-back; state returns with the next poll. If the field is an attribute-only change the logbook can't narrate (climate/water_heater temps, work_mode), also add it to `THERMOSTAT_LOG_FIELDS` / `BOILER_LOG_FIELDS` in `__init__.py` so the coordinator logs poll-confirmed changes.
5. `README.md` — it documents every supported parameter in bilingual tables (Chinese first, then English); update both halves.

## Conventions

- User-facing strings (entity names, option labels like `开机`/`离家模式`) and log messages are in Chinese; keep new ones consistent with the existing style.
- Commit messages are written in Chinese.
- `manifest.json` `version` is bumped per release (currently `v0.2.0`); `hacs.json` pins the minimum HA version (`2025.12` — required for climate/water_heater `native_*` temperature properties and enum sensors). Releases are documented in `CHANGELOG.md`.
- The boiler `flame_status` cloud field is **inverted**: truthy = 无火 (no flame), while ext-boiler `flame` uses 1 = 有火. The mapping in `sensor.py` is correct as-is — don't "fix" it.
- Some API values are integers scaled by 10 (only `room_temp`, `room_temp_correct`, `water_pressure_value` are divided by 10 for display; boiler/ext water temps are not); ext-boiler flags come as `1`/`0` while boiler flags are booleans. Match the existing conversion per device type.

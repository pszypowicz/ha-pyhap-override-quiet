# ha-pyhap-override-quiet

A tiny Home Assistant custom component that silences spurious `pyhap.characteristic` ERROR lines emitted at every HomeKit accessory build for alarm panels with a restricted `valid_values` set (e.g. no `ARM_HOME`).

The errors look like:

```
ERROR (MainThread) [pyhap.characteristic] SecuritySystemCurrentState: value=0 is an invalid value.
ERROR (MainThread) [pyhap.characteristic] SecuritySystemTargetState:  value=0 is an invalid value.
```

The integration works fine; pyhap is over-eager about logging an expected recovery path. See [HAP-python#473](https://github.com/ikalchev/HAP-python/issues/473) and [home-assistant/core#130564](https://github.com/home-assistant/core/issues/130564) / [#156142](https://github.com/home-assistant/core/issues/156142).

## What this does

At startup the component imports `pyhap.characteristic` and replaces `Characteristic.override_properties` with an equivalent that performs the membership check directly instead of going through `valid_value_or_raise` (which logs at ERROR before raising, even though the caller catches and recovers). Result: zero spurious ERROR lines, same behavior.

A `WARNING` log on every HA start confirms the patch is active:

```
WARNING (ImportExecutor_0) [custom_components.pyhap_override_quiet]
  Patched pyhap.characteristic.Characteristic.override_properties (was Characteristic.override_properties)
```

## Install

### Via HACS (recommended)

1. In Home Assistant, open HACS → 3-dot menu (top right) → **Custom repositories**.
2. Add `https://github.com/pszypowicz/ha-pyhap-override-quiet` with type **Integration**, then click **ADD**.
3. Find "pyhap override_properties quiet patch" in the HACS integrations list and click **Download**.
4. Add the following line to `configuration.yaml` so HA imports the module at startup:
   ```yaml
   pyhap_override_quiet: {}
   ```
5. Restart Home Assistant. Look for the `Patched pyhap.characteristic.Characteristic.override_properties` WARNING in the log to confirm the patch is active.

### Manual

1. Copy `custom_components/pyhap_override_quiet/` from this repo into your HA config so the resulting path is `/config/custom_components/pyhap_override_quiet/`.
2. Add `pyhap_override_quiet: {}` to `configuration.yaml`.
3. Restart Home Assistant; check for the confirmation WARNING in the log.

## Compatibility

Targets `pyhap` (HAP-python) as bundled with current Home Assistant Core. The monkey-patch is a verbatim re-implementation of the upstream method; if the upstream signature changes it would need to be re-synced.

## When to remove

When [HAP-python#473](https://github.com/ikalchev/HAP-python/issues/473) lands upstream AND a new pyhap release ships AND HA core bumps its pyhap requirement, this shim becomes redundant. Remove the directory and the configuration.yaml line; restart; verify zero `pyhap.characteristic ... invalid value` errors.

## License

MIT.

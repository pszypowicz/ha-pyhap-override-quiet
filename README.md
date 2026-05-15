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

1. Clone (or copy) into your HA config directory so the resulting path is `/config/custom_components/pyhap_override_quiet/`:
   ```
   cd /config/custom_components
   git clone https://github.com/pszypowicz/ha-pyhap-override-quiet.git
   mv ha-pyhap-override-quiet/custom_components/pyhap_override_quiet ./
   rm -rf ha-pyhap-override-quiet
   ```
   (Or use HACS as a custom repository.)

2. Add this line to `configuration.yaml` so HA imports the module at startup:
   ```yaml
   pyhap_override_quiet: {}
   ```

3. Restart Home Assistant. Look for the `Patched pyhap.characteristic.Characteristic.override_properties` WARNING in the log.

## Compatibility

Targets `pyhap` (HAP-python) as bundled with current Home Assistant Core. The monkey-patch is a verbatim re-implementation of the upstream method; if the upstream signature changes it would need to be re-synced.

## When to remove

When [HAP-python#473](https://github.com/ikalchev/HAP-python/issues/473) lands upstream AND a new pyhap release ships AND HA core bumps its pyhap requirement, this shim becomes redundant. Remove the directory and the configuration.yaml line; restart; verify zero `pyhap.characteristic ... invalid value` errors.

## License

MIT.

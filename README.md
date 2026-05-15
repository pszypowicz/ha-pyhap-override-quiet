# ha-pyhap-override-quiet

A tiny Home Assistant custom component that silences spurious `pyhap.characteristic` ERROR lines emitted at every HomeKit accessory build for alarm panels with a restricted `valid_values` set (e.g. no `ARM_HOME`).

The errors look like:

```
ERROR (MainThread) [pyhap.characteristic] SecuritySystemCurrentState: value=0 is an invalid value.
ERROR (MainThread) [pyhap.characteristic] SecuritySystemTargetState:  value=0 is an invalid value.
```

The integration works fine; pyhap is over-eager about logging an expected recovery path. See [ikalchev/HAP-python#473](https://github.com/ikalchev/HAP-python/issues/473), [home-assistant/core#130564](https://github.com/home-assistant/core/issues/130564), and [home-assistant/core#156142](https://github.com/home-assistant/core/issues/156142).

## What this does

At startup the component imports `pyhap.characteristic` and replaces `Characteristic.override_properties` with an equivalent that performs the membership check directly instead of going through `valid_value_or_raise` (which logs at ERROR before raising, even though the caller catches and recovers). Result: zero spurious ERROR lines, same behavior.

An `INFO` log on every HA start confirms the patch is active:

```
INFO (MainThread) [custom_components.pyhap_override_quiet]
  pyhap.characteristic.Characteristic.override_properties patch active
```

(Detailed before/after info is available at `DEBUG` level if you enable it via `logger:` in `configuration.yaml`.)

## Install

### Via HACS (recommended)

1. In Home Assistant, open HACS → 3-dot menu (top right) → **Custom repositories**.
2. Add `https://github.com/pszypowicz/ha-pyhap-override-quiet` with type **Integration**, then click **ADD**.
3. Find "pyhap override_properties quiet patch" in the HACS integrations list and click **Download**.
4. **Restart Home Assistant.**
5. Go to **Settings → Devices & Services → Add Integration**, search for **"pyhap override_properties quiet patch"** and click it. Confirm on the form.
6. Look for the `Patched pyhap.characteristic.Characteristic.override_properties` WARNING in the log to confirm the patch is active.

No `configuration.yaml` edits required. The integration is single-instance and registers itself via a config entry the moment you click Add Integration.

### Manual

1. Copy `custom_components/pyhap_override_quiet/` from this repo into your HA config so the resulting path is `/config/custom_components/pyhap_override_quiet/`.
2. Restart Home Assistant.
3. Settings → Devices & Services → Add Integration → pick **"pyhap override_properties quiet patch"** → confirm.

### Upgrading from v1.0.x (which used configuration.yaml)

If you previously added `pyhap_override_quiet: {}` to `configuration.yaml`, HA will migrate it to a config entry automatically on the first start after upgrading to v1.1.0. You can then remove the YAML line.

## Compatibility

Targets `pyhap` (HAP-python) as bundled with current Home Assistant Core. The monkey-patch is a verbatim re-implementation of the upstream method; if the upstream signature changes it would need to be re-synced.

## When to remove

When [ikalchev/HAP-python#473](https://github.com/ikalchev/HAP-python/issues/473) lands upstream AND a new pyhap release ships AND HA core bumps its pyhap requirement, this shim becomes redundant. Remove the directory and the configuration.yaml line; restart; verify zero `pyhap.characteristic ... invalid value` errors.

## Icon

The integration icon (`custom_components/pyhap_override_quiet/brand/icon.png` and `icon@2x.png`) is an original mark - a muted-speaker glyph signalling "quiet" - authored for this repository. Source SVG is at `icon.svg`. It is deliberately not derived from Home Assistant or HomeKit branding, per the [home-assistant/brands](https://github.com/home-assistant/brands) guideline that custom integrations must not use Home Assistant branded images.

On Home Assistant 2026.3.0+ the icon is served directly from the integration's `brand/` directory via the Brands Proxy API. The HACS store UI still resolves icons from the `brands.home-assistant.io` CDN, so until HACS adopts the proxy API the icon will not appear in the HACS list - this is cosmetic and does not affect the integration.

## License

MIT.

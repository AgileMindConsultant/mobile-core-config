# mobile-core-config

Public, world-readable tunables for Mobile Core apps (ad caps, cooldowns, multipliers, price points,
bucket weights). This is the only public repo; the code repos are private.

- Served at `https://raw.githubusercontent.com/AgileMindConsultant/mobile-core-config/main/v1/<app_id>.json`.
- Shape: `{ "schema_version": 1, "config_version": <int, bump on every edit>, "values": { "<key>": <value> } }`.
- **Tunables only.** No keys, ad unit ids, store credentials, PII or endpoint secrets - ever.
- Keys must exist in `registry.json` (vendored export of mobile-core's `ConfigKeys`; refresh with
  `python tools/export_config_registry.py --write <path>` in mobile-core). CI (`tools/validate.py`) rejects unknown
  keys, wrong types, out-of-range numbers and secret-shaped strings. Clients also clamp and ignore bad values.
- Edit through a PR; merging to `main` is live to every installed build within one fetch.

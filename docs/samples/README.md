# Telemetry node payload samples

Minimal node payload samples for 6.x, 7.x, and 8.x are referenced by the [Telemetry Version–Path Matrix](../telemetry-version-path-matrix.md).

- **node_payload_6x.json** – One node’s payload from a 6.x collectinfo (or minimal structure).
- **node_payload_7x.json** – Same for 7.x.
- **node_payload_8x.json** – Same for 8.x.

Full bundles used for inspection live in **ingest_samples/**:

- `ingest_samples/collect_info_v6x/`
- `ingest_samples/collect_info_v7x/`
- `ingest_samples/collect_info_v8x/`

To regenerate inspection results and optional minimal payloads, run from project root:

```bash
python3 inspect_collectinfo_bundles.py
```

This updates `ingest_samples/bundle_inspection_summary.json`. The placeholder files in this folder show the expected top-level shape (`as_stat`, `sys_stat`); replace with anonymized snippets from your bundles if desired.

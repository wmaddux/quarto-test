__version__ = "2.0.1"
from ingest.base_ingestor import BaseIngestor

# Canonical metric names used by rules and report (Disk Usage % / HWM).
CANONICAL_DATA_USED_PCT = "service.data_used_pct"
CANONICAL_MEMORY_USED_PCT = "service.memory_used_pct"

# Version-agnostic synonyms: when we see one of these, we also write the canonical row.
# 6.x uses storage-engine.max-used-pct, high-water-disk-pct; 7.x uses data_used_pct.
SYNONYMS_DATA_USED_PCT = frozenset([
    "data_used_pct",
    "storage-engine.max-used-pct",
    "high-water-disk-pct",
])
# 6.x uses high-water-memory-pct; 7.x uses memory_used_pct. memory_free_pct handled separately.
SYNONYMS_MEMORY_USED_PCT = frozenset([
    "memory_used_pct",
    "high-water-memory-pct",
])


def _flatten_ns_metrics(data, prefix=""):
    """Recursively flatten nested namespace metrics to (key, value) with numeric values."""
    for k, v in data.items():
        full_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            yield from _flatten_ns_metrics(v, full_key)
        elif isinstance(v, (int, float)):
            yield full_key, float(v)
        elif isinstance(v, str) and v.replace(".", "", 1).replace("-", "", 1).isdigit():
            try:
                yield full_key, float(v)
            except ValueError:
                pass


def _is_numeric_value(value):
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, str):
        return value.replace(".", "", 1).replace("-", "", 1).isdigit()
    return False


class NamespaceStatsIngestor(BaseIngestor):
    @property
    def name(self):
        return "Namespace Stats"

    def run_ingest(self, node_id, node_data, conn, run_id):
        as_stat = node_data.get('as_stat', {})
        cursor = conn.cursor()

        # Supports 6.x 'namespaces' and 7.x 'statistics.namespace' paths
        ns_container = as_stat.get('statistics', {}).get('namespace', as_stat.get('namespaces', {}))

        if ns_container:
            for ns_name, ns_data in ns_container.items():
                if not isinstance(ns_data, dict):
                    continue
                metrics_block = ns_data.get('service', ns_data)
                if not isinstance(metrics_block, dict):
                    continue
                # Flatten nested metrics (6.x has storage-engine.max-used-pct, etc.)
                for metric_key, value in _flatten_ns_metrics(metrics_block):
                    if not _is_numeric_value(value):
                        continue
                    try:
                        num_val = float(value)
                    except (TypeError, ValueError):
                        continue
                    m_name = f"service.{metric_key}" if not metric_key.startswith('service.') else metric_key
                    cursor.execute(
                        "INSERT INTO namespace_stats VALUES (?, ?, ?, ?, ?, ?)",
                        (run_id, node_id, ns_name, m_name, num_val, 'statistics')
                    )
                    # Canonical mapping: write version-agnostic names for disk/memory % so rules and chart find them
                    key_only = metric_key.replace("service.", "", 1) if metric_key.startswith("service.") else metric_key
                    if key_only in SYNONYMS_DATA_USED_PCT:
                        cursor.execute(
                            "INSERT INTO namespace_stats VALUES (?, ?, ?, ?, ?, ?)",
                            (run_id, node_id, ns_name, CANONICAL_DATA_USED_PCT, num_val, 'statistics')
                        )
                    if key_only in SYNONYMS_MEMORY_USED_PCT:
                        cursor.execute(
                            "INSERT INTO namespace_stats VALUES (?, ?, ?, ?, ?, ?)",
                            (run_id, node_id, ns_name, CANONICAL_MEMORY_USED_PCT, num_val, 'statistics')
                        )
                    if key_only == "memory_free_pct" and 0 <= num_val <= 100:
                        cursor.execute(
                            "INSERT INTO namespace_stats VALUES (?, ?, ?, ?, ?, ?)",
                            (run_id, node_id, ns_name, CANONICAL_MEMORY_USED_PCT, 100.0 - num_val, 'statistics')
                        )

        conn.commit()
        print(f"✅ {self.name} processed for {node_id}")
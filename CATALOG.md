# Aerospike Health Analyzer: Master Rule Catalog (v1.4.0)

This catalog serves as the technical reference for the diagnostic logic implemented in the analyzer. Findings are categorized by their impact on cluster stability, performance, and operational consistency.

## 1. Node & Cluster Health
| ID | Rule Name | Implementation File | Status | Description |
| :--- | :--- | :--- | :--- | :--- |
| **1.a** | **Service Error Skew** | `service_error_skew_check.py` | ✅ Implemented | **Axis: Node vs. Node.** Analyzes `early_tsvc_client_error` distribution. A skew here identifies if a specific node is disproportionately rejecting traffic due to local resource exhaustion or hardware-specific network issues. |
| **1.b** | **Network Acceleration** | `network_acceleration_check.py` | ✅ Implemented | **Axis: Platform vs. Best Practice.** Cloud-aware check that validates **AWS ENA**, **Azure Accelerated Networking (Mellanox)**, or **GCP gVNIC**. If system telemetry is missing (e.g., non-sudo collectinfo), it issues a warning to manually verify these critical low-latency drivers. |
| **1.c** | **Version Consistency** | `version_consistency_check.py` | ✅ Implemented | **Axis: Binary Uniformity.** Compares `asd_build` across the cluster. While Aerospike supports rolling upgrades, permanent mixed-version states are flagged as they can lead to protocol mismatches or inconsistent default behaviors. |



## 2. Storage & Capacity
| ID | Rule Name | Implementation File | Status | Description |
| :--- | :--- | :--- | :--- | :--- |
| **2.a** | **Secondary Index Flash** | `sindex_on_flash_check.py` | ✅ Implemented | **Axis: 7.x Optimization.** For clusters using the `index-type flash` feature, this rule verifies that the SIndex sub-components are properly aligned with NVMe storage parameters to avoid memory-bloat or write-latency spikes. |
| **2.b** | **Sprig Limit Warning** | `sprig_limit_check.py` | ✅ Implemented | **Axis: Primary Index Scalability.** Monitors `partition-tree-sprigs` against the 7.2+ limit. As object counts grow, insufficient sprigs lead to deep red-black trees, increasing the CPU cost of every record lookup. |
| **2.c** | **Storage Deadlock** | `storage_deadlock_check.py` | ✅ Implemented | **Axis: Write Safety.** Audits the gap between `defrag-lwm-pct` and the High Water Mark (HWM). If the HWM is too close to the defrag floor, the node may run out of available write-blocks before it can reclaim them, causing a storage "deadlock." |
| **2.d** | **Disk HWM Check** | `hwm_check.py` | ✅ Implemented | **Axis: Capacity.** Flags namespaces where `data_used_pct` exceeds the 60% recommended threshold. This ensures sufficient headroom for migrations and avoids the performance cliff of forced evictions. |
| **2.e** | **Memory HWM Check** | `memory_hwm_check.py` | ✅ Implemented | **Axis: Capacity.** Monitors system-level `system_free_mem_pct`. It flags nodes with less than 20% free RAM to protect the Linux OOM killer from terminating the `asd` process during peak index utilization. |

## 3. Configuration Consistency
| ID | Rule Name | Implementation File | Status | Description |
| :--- | :--- | :--- | :--- | :--- |
| **3.a** | **Config Symmetry** | `config_symmetry_check.py` | ✅ Implemented | **Axis: Node vs. Node.** Scans the `node_configs` table for peer-to-peer mismatches. It ensures that critical tunables like `service-threads`, `proto-fd-max`, and `rack-id` are identical across all members of the cluster. |
| **3.b** | **Config Drift** | `config_drift_check.py` | ✅ Implemented | **Axis: Runtime vs. Persisted.** Compares the active running state (from `asinfo`) against the `aerospike.conf` file. This detects dynamic changes that have not been persisted, preventing "reset" surprises during the next node restart. |



## 4. Performance & Traffic
| ID | Rule Name | Implementation File | Status | Description |
| :--- | :--- | :--- | :--- | :--- |
| **4.a** | **Hot Key Detection** | `hot_key_check.py` | ✅ Implemented | **Axis: Key Contention.** Aggregates `fail_key_busy` metrics. High rates indicate multiple clients attempting to write to the same record simultaneously, leading to transaction backlogs and increased latency. |
| **4.b** | **Read Not Found Rate** | `read_not_found_check.py` | ✅ Implemented | **Axis: Logic/Cache Health.** Flags namespaces where the ratio of `client_read_not_found` to total reads is abnormally high, suggesting application-level logic errors or premature record expiration (TTL). |
| **4.c** | **Delete Not Found Rate** | `delete_not_found_check.py` | ✅ Implemented | **Axis: Logic Health.** Monitors `client_delete_not_found`. Persistent errors here often indicate that the application is attempting to delete already-expired records or that client-side metadata is out of sync with the cluster. |
| **4.d** | **Batch-Index Success** | — | ❌ Not Implemented | Will audit the success/error ratios for batch sub-transactions to identify client-side retry storms. |
| **4.e** | **PI Query Latency** | — | ❌ Not Implemented | Will monitor Primary Index query durations to identify slow scans or inefficient filtering. |

## 5. Sizing & Licensing
| ID | Rule Name | Implementation File | Status | Description |
| :--- | :--- | :--- | :--- | :--- |
| **5.a** | **License Usage** | — | ❌ Not Implemented | Will correlate cluster throughput and unique object counts against license tier limits. |
| **5.b** | **Sizing Forecast** | — | ❌ Not Implemented | Will project disk and memory exhaustion dates based on current ingestion rates and compression ratios. |

---
**Baseline:** v1.4.0
**Last Updated:** 2026-02-10
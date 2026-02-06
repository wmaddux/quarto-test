# Aerospike Health Analyzer: Master Rule Catalog (v1.2.0)

This catalog tracks the health check logic implemented in the analyzer. Status is updated based on the current baseline.

## 1. Node & Cluster Health
| ID | Rule Name | Implementation File | Status | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1.a | Service Error Skew | `service_error_skew_check.py` | ✅ Implemented | Checks for uneven distribution of errors across nodes. |
| 1.b | ENA Support Check | — | ❌ Not Implemented | Validates Enhanced Networking is enabled for AWS instances. |
| 1.c | Version Consistency | — | ❌ Not Implemented | Ensures all nodes are running the same Aerospike version. |

## 2. Storage & Capacity
| ID | Rule Name | Implementation File | Status | Description |
| :--- | :--- | :--- | :--- | :--- |
| 2.a | Secondary Index Flash | `sindex_on_flash_check.py` | ✅ Implemented | Checks if Sindex is optimized when stored on Flash. |
| 2.b | Sprig Limit Warning | `sprig_limit_check.py` | ✅ Implemented | Monitors if Primary Index sprigs are nearing the 7.2 limits. |
| 2.c | Storage Deadlock Check | `storage_deadlock_check.py` | ✅ Implemented | Audits HWM vs Defrag settings to prevent write-blocks. |
| 2.d | Disk HWM Check | `hwm_check.py` | ✅ Implemented | Monitors `service.data_used_pct` against 60% threshold. |
| 2.e | Memory HWM Check | `memory_hwm_check.py` | ✅ Implemented | Monitors `service.system_free_mem_pct` against 20% threshold. |

## 3. Configuration Consistency
| ID | Rule Name | Implementation File | Status | Description |
| :--- | :--- | :--- | :--- | :--- |
| 3.a | Cross-Node Symmetry | `config_symmetry_check.py` | ✅ Implemented | Identifies mismatched configurations across the cluster. |
| 3.b | Config Drift | — | ❌ Not Implemented | Compares live runtime configs against static file configs. |

## 4. Performance & Traffic
| ID | Rule Name | Implementation File | Status | Description |
| :--- | :--- | :--- | :--- | :--- |
| 4.a | Hot Key Detection | `hot_key_check.py` | ✅ Implemented | Detects "Key Busy" errors indicating high-contention keys. |
| 4.b | Read Not Found Rate | `read_not_found_check.py` | ✅ Implemented | Flags high rates of logical read misses. |
| 4.c | Delete Not Found Rate | `delete_not_found_check.py` | ✅ Implemented | Flags high rates of logical delete errors. |
| 4.d | Batch-Index Success | — | ❌ Not Implemented | Audits batch-index sub-transaction success rates. |
| 4.e | PI Query Latency | — | ❌ Not Implemented | Monitors Primary Index query performance. |
| 4.f | Set Object Skew | — | ❌ Not Implemented | Checks for uneven data distribution at the set level. |

## 5. Sizing & Licensing
| ID | Rule Name | Implementation File | Status | Description |
| :--- | :--- | :--- | :--- | :--- |
| 5.a | License Usage | — | ❌ Not Implemented | Monitors throughput/storage against license limits. |
| 5.b | Sizing Capability | — | ❌ Not Implemented | Projecting growth based on current ingestion rates. |

---
**Baseline:** v1.3.0
**Last Updated:** 2026-02-06

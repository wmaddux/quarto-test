# Aerospike Health Analyzer: Master Rule Catalog (v1.4.1)

This catalog defines the logic used to evaluate cluster health. It is designed to be shared with customers to explain the "Why" behind a finding and the "How" of the resolution.

## 1. Node & Cluster Health

| ID | Rule Name | Implemented | Decision Threshold | Remediation (Why & Action) |
| :--- | :--- | :---: | :--- | :--- |
| **1.a** | **Service Error Skew** | ✅ | Node error count > 20% deviation from cluster average. | **Why:** One node is failing more than peers.<br>**Action:** Check node logs and network stats (`ifconfig`) for that specific IP. |
| **1.b** | **Network Acceleration** | ✅ | **CRITICAL:** Driver not found.<br>**WARNING:** Telemetry missing. | **Why:** High-speed networking (ENA/Mellanox/gVNIC) is unverified.<br>**Action:** Run `ethtool -i eth0`. Use `sudo` for future collections to automate this. |
| **1.c** | **Version Consistency** | ✅ | Multiple `asd_build` versions found in cluster. | **Why:** Mixed versions cause unpredictable behavior.<br>**Action:** Complete the rolling upgrade. If info is missing, re-collect using `sudo asadm -e collectinfo`. |

## 2. Storage & Capacity

| ID | Rule Name | Implemented | Decision Threshold | Remediation (Why & Action) |
| :--- | :--- | :---: | :--- | :--- |
| **2.a** | **SIndex on Flash** | ✅ | `index-type` is `flash` but sub-configs are default. | **Why:** SIndex on Flash requires tuning to prevent disk wear.<br>**Action:** Adjust `mounts` and `write-block-size` per Aerospike 7.x best practices. |
| **2.b** | **Sprig Limit** | ✅ | Object count vs. `partition-tree-sprigs` ratio > 1:256. | **Why:** Too few sprigs cause slow record lookups.<br>**Action:** Increase `partition-tree-sprigs` in the namespace config (requires restart). |
| **2.c** | **Storage Deadlock** | ✅ | `data-used-pct` is within 5% of `defrag-lwm-pct`. | **Why:** Node will stop writing before it can finish cleaning data.<br>**Action:** Lower the defrag floor or increase namespace quota to ensure a "safety gap." |
| **2.d** | **Disk HWM Check** | ✅ | `data_used_pct` > 60%. | **Why:** Running too close to capacity risks forced evictions.<br>**Action:** Add storage capacity or adjust data retention (TTL) policies. |
| **2.e** | **Memory HWM Check** | ✅ | System free memory < 20%. | **Why:** Low RAM risks the Linux OOM killer stopping the process.<br>**Action:** Reduce index memory usage or upgrade the instance RAM. |

## 3. Configuration Consistency

| ID | Rule Name | Implemented | Decision Threshold | Remediation (Why & Action) |
| :--- | :--- | :---: | :--- | :--- |
| **3.a** | **Config Symmetry** | ✅ | Differences in `.conf` settings between peer nodes. | **Why:** Asymmetric nodes create performance bottlenecks.<br>**Action:** Synchronize settings (like `service-threads`) across all cluster members. |
| **3.b** | **Config Drift** | ✅ | Running value (RAM) != Config value (Disk). | **Why:** A dynamic change was made but not saved to the file.<br>**Action:** Update `aerospike.conf` to match current running values to prevent loss on reboot. |

## 4. Performance & Traffic

| ID | Rule Name | Implemented | Decision Threshold | Remediation (Why & Action) |
| :--- | :--- | :---: | :--- | :--- |
| **4.a** | **Hot Key Detection** | ✅ | `fail_key_busy` > 100/sec on any node. | **Why:** Multiple clients are fighting for the same record.<br>**Action:** Evaluate application-side "read-modify-write" loops or implement client-side caching. |
| **4.b** | **Read Not Found** | ✅ | `client_read_not_found` > 5% of total reads. | **Why:** High volume of lookups for records that don't exist.<br>**Action:** Check if TTLs are expiring records too early or if app logic is querying deleted keys. |
| **4.c** | **Delete Not Found** | ✅ | `client_delete_not_found` > 1% of total deletes. | **Why:** App is trying to delete records that are already gone.<br>**Action:** Reduce "double-delete" logic in client code to save CPU/Network overhead. |
| **4.f** | **Set Object Skew** | ✅ | Object count deviation > 10% across nodes for a specific set. | **Why:** Unbalanced sets cause specific nodes to hit HWM earlier than others.<br>**Action:** Verify partition distribution and check for application-side overrides of the default partitioner. |

## 5. Sizing & Capacity

| ID | Rule Name | Implemented | Decision Threshold | Remediation (Why & Action) |
| :--- | :--- | :---: | :--- | :--- |
| **5.a** | **Capacity Forecast** | ✅ | Projected HWM breach within < 30 days based on ingestion rate. | **Why:** Proactive warning before system reaches eviction state.<br>**Action:** Increase node count or expand SSD/NVMe allocation to maintain headroom. |

---
**Baseline:** v1.5.4
**Last Updated:** 2026-02-11
# Aerospike Health Analyzer: Master Rule Catalog (v1.5.4)

This catalog defines the logic used to evaluate cluster health. It is designed to be shared with customers to explain the "Why" behind a finding and the "How" of the resolution.

## 1. Node & Cluster Health

| ID | Rule Name | Implemented | Decision Threshold | Remediation (Why & Action) |
| :--- | :--- | :---: | :--- | :--- |
| **1.a** | **Service Error Skew** | ✅ | Node error count > 20% deviation from cluster average. | **Why:** One node is failing more than peers.<br>**Action:** Check node logs and network stats (`ifconfig`). |
| **1.b** | **Network Acceleration** | ✅ | **CRITICAL:** Driver not found.<br>**WARNING:** Telemetry missing. | **Why:** High-speed networking (ENA/Mellanox/gVNIC) is unverified.<br>**Action:** Run `ethtool -i eth0`. |
| **1.c** | **Version Consistency** | ✅ | Multiple `asd_build` versions found in cluster. | **Why:** Mixed versions cause unpredictable behavior.<br>**Action:** Complete the rolling upgrade. |
| **1.d** | **Fabric Congestion** | ❌ | `fabric_send_delay` > 10ms. | **Why:** Intra-cluster communication is throttled.<br>**Action:** Check for top-of-rack switch saturation. |

## 2. Storage & Capacity

| ID | Rule Name | Implemented | Decision Threshold | Remediation (Why & Action) |
| :--- | :--- | :---: | :--- | :--- |
| **2.a** | **SIndex on Flash** | ✅ | `index-type` is `flash` but sub-configs are default. | **Why:** SIndex on Flash requires tuning to prevent disk wear.<br>**Action:** Adjust `mounts` and `write-block-size`. |
| **2.b** | **Sprig Limit** | ✅ | Object count vs. `partition-tree-sprigs` ratio > 1:256. | **Why:** Too few sprigs cause slow record lookups.<br>**Action:** Increase `partition-tree-sprigs` in config. |
| **2.c** | **Storage Deadlock** | ✅ | `data-used-pct` is within 5% of `defrag-lwm-pct`. | **Why:** Node will stop writing before it can finish cleaning data.<br>**Action:** Lower the defrag floor or increase namespace quota. |

## 3. Configuration Consistency

| ID | Rule Name | Implemented | Decision Threshold | Remediation (Why & Action) |
| :--- | :--- | :---: | :--- | :--- |
| **3.a** | **Config Symmetry** | ✅ | Differences in `.conf` settings between peer nodes. | **Why:** Asymmetric nodes create performance bottlenecks.<br>**Action:** Synchronize settings across all cluster members. |
| **3.b** | **Config Drift** | ✅ | Running value (RAM) != Config value (Disk). | **Why:** A dynamic change was made but not saved to the file.<br>**Action:** Update `aerospike.conf` to match current running values. |

## 4. Performance & Traffic

| ID | Rule Name | Implemented | Decision Threshold | Remediation (Why & Action) |
| :--- | :--- | :---: | :--- | :--- |
| **4.a** | **Hot Key Detection** | ✅ | `fail_key_busy` > 100/sec on any node. | **Why:** Multiple clients are fighting for the same record.<br>**Action:** Evaluate application-side "read-modify-write" loops. |
| **4.f** | **Set Object Skew** | ✅ | Object count deviation > 10% across nodes. | **Why:** Unbalanced sets cause specific nodes to hit HWM early.<br>**Action:** Verify partition distribution. |
| **4.g** | **Unused SIndex** | ❌ | `query_lookup` = 0 over 7 days. | **Why:** Unused indexes waste RAM and slow down writes.<br>**Action:** Drop the index if no longer needed. |

## 5. Sizing & Capacity

| ID | Rule Name | Implemented | Decision Threshold | Remediation (Why & Action) |
| :--- | :--- | :---: | :--- | :--- |
| **5.a** | **Capacity Forecast** | ✅ | Projected HWM breach within < 30 days. | **Why:** Proactive warning before system reaches eviction state.<br>**Action:** Increase node count or expand SSD/NVMe allocation. |

## 6. Security & Access Control

| ID | Rule Name | Implemented | Decision Threshold | Remediation (Why & Action) |
| :--- | :--- | :---: | :--- | :--- |
| **6.a** | **Security Connection Audit**| ✅ | Individual user connections > 500 per node. | **Why:** Potential "connection leak" or unauthorized access spike.<br>**Action:** Review application connection pooling or audit user credentials. |

## 7. Cross-Datacenter Replication (XDR)

| ID | Rule Name | Implemented | Decision Threshold | Remediation (Why & Action) |
| :--- | :--- | :---: | :--- | :--- |
| **7.a** | **XDR Lag Detection** | ❌ | `xdr_ship_latency` > 5000ms. | **Why:** Remote clusters are not receiving updates in real-time.<br>**Action:** Check WAN bandwidth or remote cluster ingest capacity. |

---
**Baseline:** v1.5.4
**Last Updated:** 2026-02-11
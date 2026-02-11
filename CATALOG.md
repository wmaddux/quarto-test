# Aerospike Health Analyzer: Master Rule Catalog (v1.5.4)

[cite_start]This catalog defines the logic used to evaluate cluster health, automating the detection of recurring issue patterns to enable proactive support[cite: 3, 6, 7].

## 1. Node & Cluster Health

| ID | Rule Name | Implemented | Decision Threshold | Remediation (Why & Action) |
| :--- | :--- | :---: | :--- | :--- |
| **1.a** | **Service Error Skew** | ✅ | Node error count > 20% deviation. | [cite_start]**Why:** One node is failing more than peers [cite: 16][cite_start].<br>**Action:** Check node logs and network stats[cite: 16, 46]. |
| **1.b** | **Network Acceleration**| ✅ | **CRITICAL:** Driver not found. | [cite_start]**Why:** High-speed networking (ENA/gVNIC) is unverified [cite: 16][cite_start].<br>**Action:** Run `ethtool -i eth0`[cite: 79]. |
| **1.c** | **Version Consistency** | ✅ | Multiple `asd_build` versions found. | [cite_start]**Why:** Version gaps cause unpredictable behavior [cite: 20, 78][cite_start].<br>**Action:** Complete rolling upgrade[cite: 20]. |
| **1.e** | **THP Status** | ❌ | THP is enabled. | [cite_start]**Why:** Transparent Huge Pages cause latency spikes [cite: 85][cite_start].<br>**Action:** Disable THP at the OS level[cite: 85]. |
| **1.f** | **Clock Skew** | ❌ | `cluster_clock_skew` > 0. | [cite_start]**Why:** Prevents nodes being kicked or TTL drift [cite: 80][cite_start].<br>**Action:** Synchronize NTP/Chrony[cite: 80]. |

## 2. Storage & Capacity

| ID | Rule Name | Implemented | Decision Threshold | Remediation (Why & Action) |
| :--- | :--- | :---: | :--- | :--- |
| **2.a** | **SIndex on Flash** | ✅ | `index-type` flash with default sub-configs. | [cite_start]**Why:** Requires tuning to prevent disk wear [cite: 9, 16][cite_start].<br>**Action:** Adjust `mounts` and `write-block-size`[cite: 16]. |
| **2.b** | **Sprig Limit** | ✅ | Object count vs. sprigs ratio > 1:256. | [cite_start]**Why:** Too few sprigs cause slow record lookups [cite: 79][cite_start].<br>**Action:** Increase `partition-tree-sprigs` (requires restart)[cite: 79]. |
| **2.c** | **Storage Deadlock** | ✅ | `data-used-pct` within 5% of `defrag-lwm-pct`. | [cite_start]**Why:** Node will stop writing before it can defrag [cite: 16, 80][cite_start].<br>**Action:** Lower defrag floor or increase quota[cite: 16]. |
| **2.d** | **Disk HWM Check** | ✅ | `data_used_pct` > 60%. | [cite_start]**Why:** Risks forced evictions [cite: 79][cite_start].<br>**Action:** Add capacity or adjust TTL policies[cite: 17, 37]. |
| **2.e** | **Memory HWM Check** | ✅ | System free memory < 20%. | [cite_start]**Why:** Risks OOM killer stopping the process [cite: 84][cite_start].<br>**Action:** Reduce index RAM or upgrade hardware[cite: 17, 35]. |
| **2.f** | **Heap Efficiency** | ❌ | `heap-efficiency-pct` < 60%. | [cite_start]**Why:** Detects fragmentation in RAM-heavy clusters [cite: 86][cite_start].<br>**Action:** Monitor for `sindex` or namespace RAM growth[cite: 9, 86]. |
| **2.g** | **NSUP Cycle Lag** | ❌ | `nsup_cycle_duration` > `nsup-period`. | [cite_start]**Why:** Expirations/evictions are falling behind [cite: 83][cite_start].<br>**Action:** Increase `nsup-threads` or `nsup-period`[cite: 83]. |

## 3. Configuration Consistency

| ID | Rule Name | Implemented | Decision Threshold | Remediation (Why & Action) |
| :--- | :--- | :---: | :--- | :--- |
| **3.a** | **Config Symmetry** | ✅ | Differences in `.conf` between peer nodes. | [cite_start]**Why:** Asymmetric nodes create bottlenecks [cite: 16][cite_start].<br>**Action:** Synchronize settings across cluster[cite: 16]. |
| **3.b** | **Config Drift** | ✅ | Running value != Config value. | [cite_start]**Why:** Dynamic changes weren't saved to disk [cite: 83][cite_start].<br>**Action:** Update `aerospike.conf` to match running values[cite: 83]. |
| **3.c** | **FD Max Capacity** | ❌ | `proto-fd-max` near limit. | [cite_start]**Why:** Limits simultaneous client connections [cite: 81][cite_start].<br>**Action:** Increase `proto-fd-max`[cite: 81]. |
| **3.d** | **Min Cluster Size** | ❌ | `min-cluster-size` is 1. | [cite_start]**Why:** Risk of data inconsistency in AP split-brain [cite: 83][cite_start].<br>**Action:** Set `min-cluster-size` > 1[cite: 83]. |

## 4. Performance & Traffic

| ID | Rule Name | Implemented | Decision Threshold | Remediation (Why & Action) |
| :--- | :--- | :---: | :--- | :--- |
| **4.a** | **Hot Key Detection** | ✅ | `fail_key_busy` > 100/sec. | [cite_start]**Why:** Clients fighting for the same record [cite: 18, 79][cite_start].<br>**Action:** Implement client-side caching[cite: 18, 79]. |
| **4.b** | **Read Not Found** | ✅ | `read_not_found` > 5% of reads. | [cite_start]**Why:** High volume of queries for non-existent keys [cite: 80][cite_start].<br>**Action:** Check TTLs or application query logic[cite: 37, 80]. |
| **4.c** | **Delete Not Found** | ✅ | `delete_not_found` > 1% of deletes. | [cite_start]**Why:** App is double-deleting records [cite: 81][cite_start].<br>**Action:** Reduce redundant delete overhead[cite: 81]. |
| **4.f** | **Set Object Skew** | ✅ | Object count deviation > 10% across nodes. | [cite_start]**Why:** Unbalanced sets cause premature HWM hits [cite: 16, 18][cite_start].<br>**Action:** Verify partition distribution[cite: 78]. |
| **4.h** | **Cache Read Ratio** | ❌ | `cache_read_pct` < 90%. | [cite_start]**Why:** Suboptimal read-page-cache efficiency [cite: 79][cite_start].<br>**Action:** Verify `read-page-cache` is enabled[cite: 79]. |
| **4.i** | **Proxy Reads** | ❌ | `client_proxy` > 1000/sec. | [cite_start]**Why:** Clients talking to the wrong nodes [cite: 79][cite_start].<br>**Action:** Update client partition map policy[cite: 79]. |

## 5. Sizing & Capacity

| ID | Rule Name | Implemented | Decision Threshold | Remediation (Why & Action) |
| :--- | :--- | :---: | :--- | :--- |
| **5.a** | **Capacity Forecast** | ✅ | Projected HWM breach < 30 days. | [cite_start]**Why:** Proactive warning before evictions [cite: 17, 35][cite_start].<br>**Action:** Increase node count or expand storage[cite: 17, 35]. |

## 6. Security & Access Control

| ID | Rule Name | Implemented | Decision Threshold | Remediation (Why & Action) |
| :--- | :--- | :---: | :--- | :--- |
| **6.a** | **Security Connection Audit**| ✅ | User connections > 500/node. | [cite_start]**Why:** Potential connection leak or unauthorized spike [cite: 36, 81][cite_start].<br>**Action:** Audit credentials and connection pooling[cite: 36, 81]. |

---
**Baseline:** v1.5.4
**Last Updated:** 2026-02-11
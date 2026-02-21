# E2E and check_integrity results by bundle

Run: `python3 tests/run_e2e.py <bundle>` for each bundle in `ingest_samples/collect_info*`, then `python3 check_integrity.py` (with venv activated). Summary below.

---

## 1. collect_info_v6x / nielsen-collect_info_20260113_095356.tar

- **Ingest:** Completed for all 11 nodes.
- **Ingest warnings:**  
  - **SecurityStatsIngestor failed:** `'str' object has no attribute 'items'` on one node (10.92.71.105:3000). Indicates the security/ACL stats payload for that node is a string instead of a dict; ingestor should handle or skip.
- **Integrity (run_e2e):** Failed with `Could not import rules. No module named 'pandas'` when the script was run **without** the project venv activated. With venv activated, `check_integrity.py` runs successfully against the DB produced by this (or any) bundle.

---

## 2. collect_info_v6x / yahoo-collect_info_20251001_122057.tgz

- **Ingest:** Passes when run with venv activated (96 nodes). Earlier failures (disk I/O error, readonly database) were due to the environment/sandbox where the script was run without venv.
- **Integrity (run_e2e):** Passes with venv.

---

## 3. collect_info_v7x / adobe-azure-els.collect_info_20260120_225608.tgz

- **Ingest:** Completed for all 3 nodes. No aerospike.conf in bundle (informational message only).
- **Integrity (run_e2e):** Failed with `No module named 'pandas'` when run without venv. With venv, integrity passes.

---

## 4. collect_info_v8x / swarit_collect_info_20260107_153609.tgz

- **Ingest:** Completed for all 9 nodes. Static config loaded from aerospike.conf.
- **Integrity (run_e2e):** Failed with `No module named 'pandas'` when run without venv. With venv, integrity passes.

---

## 5. collect_info_v8x / swarit_collect_info_20260108_065237.tgz

- **Ingest:** Completed for all 12 nodes. Static config loaded from aerospike.conf.
- **Integrity (run_e2e):** Failed with `No module named 'pandas'` when run without venv. With venv, **check_integrity.py** passes (all 16 rules run; schema matches baseline).

---

## Environment note

**Always activate the venv before running e2e or integrity:**  
`source .venv/bin/activate`  
Then:  
`python3 tests/run_e2e.py <bundle>`  
`python3 check_integrity.py`  

Otherwise `check_integrity.py` cannot import the rules (pandas, etc.) and reports "No module named 'pandas'".

---

## Summary of errors to fix

| Bundle | Error | Action |
|--------|--------|--------|
| nielsen (6.x) | SecurityStatsIngestor: `'str' object has no attribute 'items'` on one node | Harden security_stats ingestor for 6.x when ACL/security block is a string or non-dict. |
| yahoo (6.x) | (Previously saw disk I/O / readonly DB in non-venv run; **passes with venv**.) | None. |
| All | Integrity fails with "No module named 'pandas'" when venv not activated | Document or script: require venv for `run_e2e.py` / `check_integrity.py`. |

With venv activated, **check_integrity.py** passes on a DB produced by any of the successful ingests (nielsen, adobe, swarit 60107, swarit 60108).

# Pipeline & Cron

Pipelines chain multiple Executions and support scheduled execution via cron.

---

## Overview

A **Pipeline** runs a sequence of Executions, passing `data_chain` through all of them. Pipelines can be triggered manually, via HTTP API, or on a cron schedule.

---

## Cron Setup (GUI)

1. Switch to the **Pipelines** tab in the GUI
2. Select or create a pipeline
3. Check **as cron** → enter a cron expression (e.g. `0 9 * * 1-5`)
4. Click **Execute** — runs on schedule until stopped via **Stop** / **Stop All**

The tooltip on the cron input shows a human-readable description (e.g. "At 09:00 AM, Monday through Friday").

---

## Pipeline YAML Format

```yaml
!!python/object:core.pipeline.Pipeline
pipeline: DAILY_REPORT
cronEnabled: true
cronExp: 0 9 * * 1-5
cronDesc: At 09:00 AM, Monday through Friday
list:
- execution: fetch_data
  input: ''
- execution: generate_report
  input: ''
- execution: send_email
  input: '{"to":"team@example.com"}'
```

| Field | Description |
|-------|-------------|
| `pipeline` | Pipeline name (unique identifier) |
| `cronEnabled` | `true` activates the cron schedule |
| `cronExp` | Standard 5-field cron expression |
| `cronDesc` | Auto-generated human-readable description |
| `list` | Ordered list of executions with optional `input` JSON |

---

## Running Pipelines

```bash
# GUI — cron managed via checkbox + expression input, persisted in YAML

# Background — run a pipeline once
python PETP_backgroud.py --run-pipeline DAILY_REPORT --no-http

# Background — run with initial data
python PETP_backgroud.py --run-pipeline DAILY_REPORT --init-data '{"to":"ops@example.com"}' --no-http

# Background — persistent HTTP service (pipelines triggered via POST /petp/exec)
python PETP_backgroud.py

# Docker
docker run --rm -p 8866:8866 petp-background:amd64-local
# then: POST http://localhost:8866/petp/exec  {"action":"pipeline","params":{"pipeline":"DAILY_REPORT"},"wait_for_result":"true"}
```

---

## Cron Architecture

The `Cron` class (`core/cron/cron.py`) manages scheduled pipeline execution:

- **Worker thread** pops from a pending queue with deduplication by pipeline key
- **Per-pipeline thread** waits until the next cron tick, then executes
- **Thread safety**: all shared state guarded by `threading.Lock`; `threading.Event` replaces sleep-polling
- **Dedup**: rejects if key is already in running or pending
- **Stop**: `stop_one()` / `stop_all()` clear state and join threads for clean shutdown
- **Auto-retry**: catches exceptions to survive individual failures

"""Cron execution history — JSON file-based persistence."""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional


class CronHistory:

    def __init__(self, history_dir: str = "log/cron_history", max_records: int = 500):
        self._dir = history_dir
        self._max_records = max_records
        os.makedirs(self._dir, exist_ok=True)

    def record(self, pipeline_name: str, cron_exp: str, result: dict) -> None:
        now = datetime.now()
        record_id = f"{pipeline_name}_{now.strftime('%Y%m%d_%H%M%S_%f')}"
        duration_ms = result.get("meta", {}).get("duration_ms", 0)

        executions_summary = []
        for ex in result.get("meta", {}).get("executions", []):
            executions_summary.append({
                "execution": ex.get("execution"),
                "ok": ex.get("result", {}).get("ok"),
                "duration_ms": ex.get("result", {}).get("meta", {}).get("duration_ms", 0),
            })

        record = {
            "id": record_id,
            "pipeline_name": pipeline_name,
            "cron_exp": cron_exp,
            "start_time": now.isoformat(timespec="seconds"),
            "duration_ms": duration_ms,
            "ok": result.get("ok", False),
            "error": result.get("error"),
            "executions": executions_summary,
        }

        file_path = os.path.join(self._dir, f"{record_id}.json")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(record, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error("CronHistory: failed to write record %s: %s", record_id, e)

        self.cleanup()

    def get_history(self, pipeline_name: Optional[str] = None, limit: int = 50) -> list[dict]:
        try:
            files = sorted(
                [f for f in os.listdir(self._dir) if f.endswith(".json")],
                reverse=True,
            )
        except OSError:
            return []

        if pipeline_name:
            files = [f for f in files if f.startswith(f"{pipeline_name}_")]

        records = []
        for filename in files[:limit]:
            file_path = os.path.join(self._dir, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    record = json.load(f)
                records.append({
                    "id": record.get("id"),
                    "pipeline_name": record.get("pipeline_name"),
                    "cron_exp": record.get("cron_exp"),
                    "start_time": record.get("start_time"),
                    "duration_ms": record.get("duration_ms"),
                    "ok": record.get("ok"),
                    "error": record.get("error"),
                })
            except Exception:
                continue

        return records

    def get_record(self, record_id: str) -> Optional[dict]:
        file_path = os.path.join(self._dir, f"{record_id}.json")
        if not os.path.isfile(file_path):
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def cleanup(self) -> None:
        try:
            files = sorted(f for f in os.listdir(self._dir) if f.endswith(".json"))
        except OSError:
            return

        overflow = len(files) - self._max_records
        if overflow <= 0:
            return

        for filename in files[:overflow]:
            try:
                os.remove(os.path.join(self._dir, filename))
            except OSError:
                pass

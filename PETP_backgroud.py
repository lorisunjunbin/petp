import argparse
import json
import logging
import signal
import threading
import time
from typing import Any

import utils.Logger as Logger
from core.runtime.BackgroundRuntime import BackgroundRuntime
from core.runtime.UiProcessorPolicy import normalize_policy
from httpservice.BackgroundHttpServer import BackgroundHttpServer
from i18n.translations import set_locale
from mvp.model.PETPModel import PETPModel
from utils.DateUtil import DateUtil
from utils.SystemConfig import SystemConfig


def init_log() -> None:
    Logger.init("petp")
    logging.info("\n\n")
    logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    logging.info("PETP background starting @ " + DateUtil.get_now_in_str("%Y-%m-%d %H:%M:%S"))


def build_model() -> PETPModel:
    config = SystemConfig("petpconfig.yaml")
    return PETPModel(config)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PETP background runtime entry")
    parser.add_argument("--nogui-enabled", choices=["true", "false"], help="Enable/disable no-GUI background mode")
    parser.add_argument("--ui-policy", choices=["skip", "abort"], help="Policy for GUI processors in no-GUI mode")
    parser.add_argument("--log-level", help="Override log level")
    parser.add_argument("--http-port", type=int, help="Override HTTP port")
    parser.add_argument("--http-token", help="Override HTTP auth token")
    parser.add_argument("--run-execution", help="Run one execution immediately")
    parser.add_argument("--run-pipeline", help="Run one pipeline immediately")
    parser.add_argument("--init-data", default="{}", help="JSON object for initial data")
    parser.add_argument("--no-http", action="store_true",
                        help="Run immediate job and exit without starting HTTP server")
    return parser.parse_args()


def _to_bool(value: Any, default: bool = True) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


def _merge_config(args: argparse.Namespace, model: PETPModel) -> dict:
    nogui_enabled = _to_bool(args.nogui_enabled, getattr(model, "nogui_enabled", True))
    ui_policy = normalize_policy(args.ui_policy or getattr(model, "nogui_ui_processor_policy", "skip"), "skip")

    return {
        "nogui_enabled": nogui_enabled,
        "ui_policy": ui_policy,
        "log_level": args.log_level or getattr(model, "log_level", "INFO"),
        "http_port": args.http_port or int(getattr(model, "http_port", 8866)),
        "http_timeout": int(getattr(model, "http_request_timeout", 600)),
        "http_token": args.http_token if args.http_token is not None else getattr(model, "http_request_token", None),
        "run_execution": args.run_execution,
        "run_pipeline": args.run_pipeline,
        "init_data": args.init_data,
        "no_http": args.no_http,
    }


def _run_immediate(runtime: BackgroundRuntime, cfg: dict) -> None:
    try:
        init_data = json.loads(cfg["init_data"] or "{}")
        if not isinstance(init_data, dict):
            raise ValueError("--init-data must be a JSON object")
    except Exception as e:
        raise ValueError(f"Invalid --init-data: {e}") from e

    if cfg["run_execution"]:
        result = runtime.run_execution(cfg["run_execution"], init_data)
        logging.info("Immediate execution result: %s", json.dumps(result, ensure_ascii=False, default=str))

    if cfg["run_pipeline"]:
        result = runtime.run_pipeline(cfg["run_pipeline"], init_data)
        logging.info("Immediate pipeline result: %s", json.dumps(result, ensure_ascii=False, default=str))


def start_background_app() -> None:
    init_log()
    model = build_model()
    set_locale(getattr(model, 'language', 'zh'))
    args = parse_args()
    cfg = _merge_config(args, model)

    logging.getLogger().setLevel(logging.getLevelName(cfg["log_level"]))

    if not cfg["nogui_enabled"]:
        logging.warning("nogui_enabled=false, background app exits")
        return

    runtime = BackgroundRuntime(model, ui_policy=cfg["ui_policy"])
    _run_immediate(runtime, cfg)

    if cfg["no_http"]:
        logging.info("--no-http enabled, background app exits after immediate run")
        return

    server = BackgroundHttpServer(runtime, cfg["http_port"], cfg["http_timeout"], cfg["http_token"])
    server.start()

    stop_event = threading.Event()

    def _shutdown_handler(signum, frame):
        logging.info("Receive shutdown signal: %s", signum)
        stop_event.set()

    signal.signal(signal.SIGINT, _shutdown_handler)
    signal.signal(signal.SIGTERM, _shutdown_handler)

    while not stop_event.is_set():
        time.sleep(0.5)

    server.stop()
    logging.info("PETP background shutdown @" + DateUtil.get_now_in_str("%Y-%m-%d %H:%M:%S"))
    logging.info("<<<<<<<<<<<<<<<<<<<<<<<<<<<<")


def main() -> None:
    start_background_app()


if __name__ == "__main__":
    main()

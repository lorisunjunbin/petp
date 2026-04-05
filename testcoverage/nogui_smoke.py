import os
import sys
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.runtime.BackgroundRuntime import BackgroundRuntime
from mvp.model.PETPModel import PETPModel
from utils.SystemConfig import SystemConfig


def main():
    model = PETPModel(SystemConfig("petpconfig.yaml"))
    runtime = BackgroundRuntime(model, ui_policy="skip")

    result = runtime.run_execution("ENDECODER", {})
    print(json.dumps(result, ensure_ascii=False, default=str))

    if not result.get("ok"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()





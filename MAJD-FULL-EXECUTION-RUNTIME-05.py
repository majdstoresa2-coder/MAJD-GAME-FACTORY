#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-FULL-EXECUTION-RUNTIME-05.py
=================================

FULL EXECUTION RUNTIME - SOVEREIGN MONITOR

Responsibilities:
- Execute MAJD real game executor (03)
- Execute official platform bridge (04)
- Record runtime/build status
- Support normal CLI execution for CI/CD
- Support optional sovereign continuous monitor
- Support optional monitoring API
- Avoid blocking GitHub Actions during normal tests
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import random
import sys
import time
import traceback
import uuid

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


# ============================================================
# OPTIONAL DEPENDENCIES
# ============================================================

try:
    import schedule  # type: ignore
except ImportError:
    schedule = None

try:
    from fastapi import FastAPI  # type: ignore
    import uvicorn  # type: ignore
except ImportError:
    FastAPI = None
    uvicorn = None


# ============================================================
# PATHS & CONSTANTS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent

REAL_GAME_EXECUTOR_FILE = (
    ROOT_DIR / "MAJD-REAL-GAME-EXECUTOR-03.py"
)

OFFICIAL_PLATFORM_BRIDGE_FILE = (
    ROOT_DIR / "MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py"
)

OUTPUT_DIR = ROOT_DIR / "majd_game_output"

ASSETS_DIR = ROOT_DIR / "public" / "assets"

MONITOR_LOG = ROOT_DIR / "majd_monitor_log.json"

DEFAULT_MONITOR_INTERVAL_MINUTES = 60
DEFAULT_RETRY_INTERVAL_MINUTES = 5

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

ASSETS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# TIME
# ============================================================

def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


# ============================================================
# MODULE LOADER
# ============================================================

def load_python_module(
    path: Path,
    module_name: str,
):
    if not path.exists():
        raise FileNotFoundError(
            f"Required file not found: {path.name}"
        )

    spec = importlib.util.spec_from_file_location(
        module_name,
        str(path),
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"Unable to load module: {path.name}"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    sys.modules[module_name] = module

    spec.loader.exec_module(module)

    return module


# ============================================================
# SAFE GAME NAME
# ============================================================

def safe_name(value: str) -> str:
    import re

    value = str(
        value or "MAJD-GAME"
    ).strip()

    value = re.sub(
        r"[^\w\u0600-\u06FF\- ]+",
        "",
        value,
        flags=re.UNICODE,
    )

    value = re.sub(
        r"\s+",
        "-",
        value,
    ).strip("-_")

    return value[:80] or "MAJD-GAME"


# ============================================================
# UNIQUE GAME PROFILE
# ============================================================

def get_random_game_profile() -> Dict[str, Any]:

    colors = [
        "royalblue",
        "gold",
        "crimson",
        "seagreen",
        "darkviolet",
        "orangered",
    ]

    positions = [
        (0, 0, 0),
        (2, 1, 0),
        (-2, 1, 0),
        (0, 2, 0),
        (3, 0, 0),
        (-3, 0, 0),
    ]

    sample_size = random.randint(
        3,
        len(positions),
    )

    primary = random.choice(colors)

    secondary_candidates = [
        color
        for color in colors
        if color != primary
    ]

    secondary = random.choice(
        secondary_candidates
    )

    return {
        "primary_color": primary,
        "secondary_color": secondary,
        "object_positions": random.sample(
            positions,
            k=sample_size,
        ),
    }


# ============================================================
# MONITOR LOG
# ============================================================

def log_build_status(
    status: str,
    game_id: str,
    details: Optional[Dict[str, Any]] = None,
) -> None:

    log_entry = {
        "timestamp": utc_now(),
        "status": status,
        "game_id": game_id,
        "details": details or {},
    }

    with MONITOR_LOG.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(
                log_entry,
                ensure_ascii=False,
            )
            + "\n"
        )


def read_monitor_logs(
    limit: int = 200,
) -> list:

    if not MONITOR_LOG.exists():
        return []

    logs = []

    try:
        with MONITOR_LOG.open(
            "r",
            encoding="utf-8",
        ) as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                try:
                    logs.append(
                        json.loads(line)
                    )
                except json.JSONDecodeError:
                    continue

    except OSError:
        return []

    if limit > 0:
        logs = logs[-limit:]

    return logs


# ============================================================
# 1. REAL GAME EXECUTOR (03)
# ============================================================

def execute_real_game_executor(
    command: str,
    job_id: str,
) -> Dict[str, Any]:

    try:

        module = load_python_module(
            REAL_GAME_EXECUTOR_FILE,
            "majd_real_game_executor_03",
        )

        function = getattr(
            module,
            "execute_game_request",
            None,
        )

        if not callable(function):

            return {
                "success": False,
                "error": (
                    "EXECUTOR_INTERFACE_NOT_FOUND"
                ),
            }

        request = {
            "type": "CREATE_GAME",
            "name": safe_name(
                command[:80]
            ),
            "genre": "ADVENTURE",
            "dimension": "2D",
            "platform": ["WEB"],
            "request": command,
        }

        result = function(
            request=request,
            job_id=job_id,
            output_root=str(
                OUTPUT_DIR
            ),
        )

        if not isinstance(
            result,
            dict,
        ):
            return {
                "success": False,
                "error": (
                    "EXECUTOR_INVALID_RESPONSE"
                ),
            }

        return result

    except Exception as exc:

        log_build_status(
            "EXECUTOR_EXCEPTION",
            job_id,
            {
                "error": str(exc),
            },
        )

        return {
            "success": False,
            "error": str(exc),
            "traceback": traceback.format_exc(),
        }


# ============================================================
# 2. OFFICIAL PLATFORM BRIDGE (04)
# ============================================================

def execute_official_bridge(
    game_artifact_path: Path,
    job_id: str,
    game_name: str,
) -> Dict[str, Any]:

    try:

        module = load_python_module(
            OFFICIAL_PLATFORM_BRIDGE_FILE,
            "majd_official_platform_bridge_04",
        )

        publish_func = getattr(
            module,
            "publish_game",
            None,
        )

        if not callable(
            publish_func
        ):

            return {
                "success": False,
                "error": (
                    "BRIDGE_INTERFACE_MISSING"
                ),
            }

        result = publish_func(
            game_dir=game_artifact_path,
            game_name=game_name,
            job_id=job_id,
        )

        if not isinstance(
            result,
            dict,
        ):

            return {
                "success": False,
                "error": (
                    "BRIDGE_INVALID_RESPONSE"
                ),
            }

        return result

    except Exception as exc:

        log_build_status(
            "BRIDGE_EXCEPTION",
            job_id,
            {
                "error": str(exc),
            },
        )

        return {
            "success": False,
            "error": str(exc),
            "traceback": traceback.format_exc(),
        }


# ============================================================
# FULL EXECUTION RUNTIME
# ============================================================

class MajdFullExecutionRuntime:

    def __init__(self) -> None:

        self.runtime_id = str(
            uuid.uuid4()
        )

    def execute(
        self,
        command: str,
    ) -> Dict[str, Any]:

        command = str(
            command or ""
        ).strip()

        state: Dict[str, Any] = {
            "runtime_id": self.runtime_id,
            "command": command,
            "started_at": utc_now(),
            "stages": {},
        }

        if not command:

            state.update(
                {
                    "success": False,
                    "error": (
                        "EMPTY_COMMAND"
                    ),
                    "finished_at": utc_now(),
                }
            )

            return state

        try:

            # --------------------------------------------
            # DESIGN PROFILE
            # --------------------------------------------

            game_profile = (
                get_random_game_profile()
            )

            state[
                "design_profile"
            ] = game_profile

            # --------------------------------------------
            # EXECUTOR 03
            # --------------------------------------------

            executor_result = (
                execute_real_game_executor(
                    command,
                    self.runtime_id,
                )
            )

            state["stages"][
                "executor"
            ] = executor_result

            if not executor_result.get(
                "success"
            ):

                state["success"] = False

                state["error"] = (
                    executor_result.get(
                        "error"
                    )
                    or "EXECUTOR_FAILED"
                )

                state[
                    "finished_at"
                ] = utc_now()

                log_build_status(
                    "EXECUTOR_FAILED",
                    self.runtime_id,
                    {
                        "error": state[
                            "error"
                        ]
                    },
                )

                return state

            # --------------------------------------------
            # ARTIFACT
            # --------------------------------------------

            artifact_value = (
                executor_result.get(
                    "artifact"
                )
                or executor_result.get(
                    "artifact_path"
                )
                or executor_result.get(
                    "game_path"
                )
            )

            if not artifact_value:

                state["success"] = False

                state["error"] = (
                    "EXECUTOR_ARTIFACT_MISSING"
                )

                state[
                    "finished_at"
                ] = utc_now()

                log_build_status(
                    "ARTIFACT_MISSING",
                    self.runtime_id,
                )

                return state

            artifact_path = Path(
                str(artifact_value)
            )

            if not artifact_path.is_absolute():

                artifact_path = (
                    ROOT_DIR
                    / artifact_path
                ).resolve()

            state["artifact_path"] = str(
                artifact_path
            )

            if not artifact_path.exists():

                state["success"] = False

                state["error"] = (
                    "ARTIFACT_NOT_FOUND"
                )

                state[
                    "finished_at"
                ] = utc_now()

                log_build_status(
                    "ARTIFACT_NOT_FOUND",
                    self.runtime_id,
                    {
                        "artifact": str(
                            artifact_path
                        )
                    },
                )

                return state

            # --------------------------------------------
            # GAME NAME
            # --------------------------------------------

            game_name = str(
                executor_result.get(
                    "game"
                )
                or executor_result.get(
                    "game_name"
                )
                or safe_name(
                    command[:80]
                )
            )

            state[
                "game_name"
            ] = game_name

            # --------------------------------------------
            # PLATFORM BRIDGE 04
            # --------------------------------------------

            bridge_result = (
                execute_official_bridge(
                    artifact_path,
                    self.runtime_id,
                    game_name,
                )
            )

            state["stages"][
                "bridge"
            ] = bridge_result

            if not bridge_result.get(
                "success"
            ):

                state["success"] = False

                state["error"] = (
                    bridge_result.get(
                        "error"
                    )
                    or "BRIDGE_FAILED"
                )

                state[
                    "finished_at"
                ] = utc_now()

                log_build_status(
                    "BRIDGE_FAILED",
                    self.runtime_id,
                    {
                        "error": state[
                            "error"
                        ]
                    },
                )

                return state

            # --------------------------------------------
            # SUCCESS
            # --------------------------------------------

            state["success"] = True

            state["game_path"] = (
                bridge_result.get(
                    "game_path"
                )
                or bridge_result.get(
                    "url"
                )
            )

            state["game_id"] = (
                bridge_result.get(
                    "game_id"
                )
                or self.runtime_id
            )

            state[
                "finished_at"
            ] = utc_now()

            log_build_status(
                "SUCCESS",
                self.runtime_id,
                {
                    "game_id": state[
                        "game_id"
                    ],
                    "game_path": state[
                        "game_path"
                    ],
                },
            )

            return state

        except Exception as exc:

            state["success"] = False

            state["error"] = (
                f"EXCEPTION: {exc}"
            )

            state[
                "traceback"
            ] = traceback.format_exc()

            state[
                "finished_at"
            ] = utc_now()

            log_build_status(
                "CRASHED",
                self.runtime_id,
                {
                    "error": str(exc),
                },
            )

            return state


# ============================================================
# AUTOMATIC GAME GENERATION
# ============================================================

AUTO_GAME_COMMANDS = [
    "أنشئ لعبة مغامرات استراتيجية",
    "أنشئ لعبة بناء عالم ثلاثي الأبعاد",
    "أنشئ لعبة حروب وأساطير",
    "أنشئ لعبة صيد وكنوز",
]


def auto_generate_game() -> Dict[str, Any]:

    print(
        f"[{utc_now()}] "
        "بدء دورة التطوير السيادي..."
    )

    runtime = (
        MajdFullExecutionRuntime()
    )

    command = random.choice(
        AUTO_GAME_COMMANDS
    )

    result = runtime.execute(
        command
    )

    if result.get(
        "success"
    ):

        print(
            f"[{utc_now()}] "
            "تم إنشاء اللعبة بنجاح."
        )

        print(
            "Game ID:",
            result.get(
                "game_id"
            ),
        )

        print(
            "Game Path:",
            result.get(
                "game_path"
            ),
        )

    else:

        print(
            f"[{utc_now()}] "
            "فشلت دورة الإنشاء."
        )

        print(
            "Error:",
            result.get(
                "error"
            ),
        )

    return result


# ============================================================
# OPTIONAL FASTAPI MONITOR
# ============================================================

app = None

if FastAPI is not None:

    app = FastAPI(
        title=(
            "MAJD Sovereign Monitor"
        ),
        version="1.0.0",
    )

    @app.get("/health")
    async def monitor_health():
        return {
            "success": True,
            "service": (
                "MAJD-SOVEREIGN-MONITOR"
            ),
            "status": "ONLINE",
            "timestamp": utc_now(),
        }

    @app.get("/logs")
    async def get_logs(
        limit: int = 200,
    ):

        safe_limit = max(
            1,
            min(
                int(limit),
                1000,
            ),
        )

        return {
            "success": True,
            "logs": read_monitor_logs(
                safe_limit
            ),
        }


# ============================================================
# OPTIONAL API SERVER
# ============================================================

def run_api_server(
    host: str = "0.0.0.0",
    port: int = 8000,
) -> None:

    if (
        FastAPI is None
        or uvicorn is None
        or app is None
    ):
        raise RuntimeError(
            "FASTAPI_DEPENDENCIES_NOT_INSTALLED: "
            "install fastapi and uvicorn "
            "to use --serve."
        )

    print(
        "MAJD Monitor API:",
        f"http://{host}:{port}",
    )

    uvicorn.run(
        app,
        host=host,
        port=port,
    )


# ============================================================
# SOVEREIGN MONITOR
# ============================================================

def run_monitor(
    interval_minutes: int = (
        DEFAULT_MONITOR_INTERVAL_MINUTES
    ),
) -> None:

    if schedule is None:

        raise RuntimeError(
            "SCHEDULE_DEPENDENCY_NOT_INSTALLED: "
            "install schedule to use "
            "--monitor."
        )

    interval_minutes = max(
        1,
        int(interval_minutes),
    )

    print(
        "MAJD SOVEREIGN MONITOR ONLINE."
    )

    print(
        "Automatic generation interval:",
        f"{interval_minutes} minute(s).",
    )

    schedule.clear()

    schedule.every(
        interval_minutes
    ).minutes.do(
        auto_generate_game
    )

    # Execute one cycle immediately.
    auto_generate_game()

    try:

        while True:

            schedule.run_pending()

            time.sleep(1)

    except KeyboardInterrupt:

        print(
            "\nMAJD monitor stopped."
        )


# ============================================================
# CLI
# ============================================================

def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description=(
            "MAJD Full Execution Runtime"
        )
    )

    parser.add_argument(
        "command",
        nargs="*",
        help=(
            "Game creation command."
        ),
    )

    parser.add_argument(
        "--monitor",
        action="store_true",
        help=(
            "Run sovereign continuous monitor."
        ),
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=(
            DEFAULT_MONITOR_INTERVAL_MINUTES
        ),
        help=(
            "Monitor interval in minutes."
        ),
    )

    parser.add_argument(
        "--serve",
        action="store_true",
        help=(
            "Run monitoring API."
        ),
    )

    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API host.",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API port.",
    )

    parser.add_argument(
        "--auto-once",
        action="store_true",
        help=(
            "Execute one automatic "
            "generation cycle and exit."
        ),
    )

    return parser


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    parser = build_parser()

    args = parser.parse_args()

    # --------------------------------------------------------
    # MONITOR MODE
    # --------------------------------------------------------

    if args.monitor:

        try:

            run_monitor(
                interval_minutes=(
                    args.interval
                )
            )

            return 0

        except Exception as exc:

            print(
                json.dumps(
                    {
                        "success": False,
                        "mode": "monitor",
                        "error": str(exc),
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                file=sys.stderr,
            )

            return 1

    # --------------------------------------------------------
    # API MODE
    # --------------------------------------------------------

    if args.serve:

        try:

            run_api_server(
                host=args.host,
                port=args.port,
            )

            return 0

        except Exception as exc:

            print(
                json.dumps(
                    {
                        "success": False,
                        "mode": "serve",
                        "error": str(exc),
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                file=sys.stderr,
            )

            return 1

    # --------------------------------------------------------
    # AUTO ONCE
    # --------------------------------------------------------

    if args.auto_once:

        result = auto_generate_game()

        print(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=2,
            )
        )

        return (
            0
            if result.get(
                "success"
            )
            else 1
        )

    # --------------------------------------------------------
    # NORMAL CI / CLI EXECUTION
    # --------------------------------------------------------

    if not args.command:

        parser.error(
            "Provide a command, "
            "--auto-once, --monitor, "
            "or --serve."
        )

    command = " ".join(
        args.command
    ).strip()

    result = (
        MajdFullExecutionRuntime()
        .execute(command)
    )

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )
    )

    return (
        0
        if result.get(
            "success"
        )
        else 1
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    raise SystemExit(
        main()
    )

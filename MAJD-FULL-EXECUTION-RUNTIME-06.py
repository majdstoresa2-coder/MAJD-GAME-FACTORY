#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-FULL-EXECUTION-RUNTIME-06.py
============================================================

MAJD SOVEREIGN AUTONOMOUS FULL EXECUTION RUNTIME
المشغل السيادي الذاتي الكامل لمنصة مجد

وظيفة الملف:
- يحافظ على وضع أوامر المالك الحالي.
- يدعم التشغيل الذاتي الدائم بدون أمر يدوي.
- يربط 01 العقل المدبر.
- يقرأ 02 الشركة السيادية ومركز أوامر المالك.
- يتحقق من 03 منفذ الألعاب الحقيقي و04 جسر المنصة.
- يفحص ملفات بايثون والخدمات وDocker والتخزين والموقع.
- يكتشف الأعطال تلقائيا.
- يرسل الإصلاحات الروتينية للعقل المدبر 01.
- يعيد الفحص بعد الإصلاح.
- يحفظ الحالة والتدقيق والتقارير.
- لا يعتبر أي قدرة OPERATIONAL بدون دليل حقيقي.
- يدعم العربية والإنجليزية في تقارير المالك.

تشغيل مباشر:
  python3 MAJD-FULL-EXECUTION-RUNTIME-06.py --once
  python3 MAJD-FULL-EXECUTION-RUNTIME-06.py --autonomous
  python3 MAJD-FULL-EXECUTION-RUNTIME-06.py --autonomous-status
  python3 MAJD-FULL-EXECUTION-RUNTIME-06.py "أمر المالك"

إذا شُغّل بدون أي arguments يبدأ التشغيل الذاتي الدائم تلقائيا.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import inspect
import json
import os
import signal
import subprocess
import sys
import time
import traceback
import urllib.error
import urllib.request
import uuid

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple


# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent

MASTERMIND_FILE = ROOT_DIR / "MAJD-AI-MASTERMIND-01.py"
SOVEREIGN_COMPANY_FILE = ROOT_DIR / "MAJD-AI-SOVEREIGN-COMPANY-02.py"
OWNER_COMMAND_CENTER_FILE = ROOT_DIR / "MAJD-OWNER-COMMAND-CENTER-02.py"
REAL_GAME_EXECUTOR_FILE = ROOT_DIR / "MAJD-REAL-GAME-EXECUTOR-03.py"
OFFICIAL_PLATFORM_BRIDGE_FILE = ROOT_DIR / "MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py"

STATE_DIR = ROOT_DIR / "majd_factory_state"
RUNTIME_DIR = STATE_DIR / "runtime"
AUTONOMOUS_DIR = STATE_DIR / "autonomous"
AUDIT_DIR = STATE_DIR / "audit"
REPORT_DIR = STATE_DIR / "reports"
OUTPUT_DIR = ROOT_DIR / "majd_game_output"
PUBLIC_DIR = ROOT_DIR / "public"
ARTIFACTS_DIR = PUBLIC_DIR / "artifacts"

AUTONOMOUS_STATE_FILE = AUTONOMOUS_DIR / "autonomous-runtime-state.json"
AUTONOMOUS_LATEST_REPORT = REPORT_DIR / "autonomous-latest.json"
AUTONOMOUS_AUDIT_FILE = AUDIT_DIR / "autonomous-runtime.jsonl"
PID_FILE = AUTONOMOUS_DIR / "majd-autonomous-runtime.pid"

for directory in (
    STATE_DIR,
    RUNTIME_DIR,
    AUTONOMOUS_DIR,
    AUDIT_DIR,
    REPORT_DIR,
    OUTPUT_DIR,
    PUBLIC_DIR,
    ARTIFACTS_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)


# ============================================================
# IDENTITY / CONFIG
# ============================================================

SYSTEM_NAME = "MAJD-GAME-FACTORY"
RUNTIME_NAME = "MAJD-FULL-EXECUTION-RUNTIME"
VERSION = "3.2.0-AUTONOMOUS-BILINGUAL"
DEFAULT_OWNER = "MAJD"

OFFICIAL_MAJD_PLATFORM = os.getenv(
    "MAJD_OFFICIAL_PLATFORM",
    "https://majd.shop",
).rstrip("/")

LOCAL_API_HEALTH_URL = os.getenv(
    "MAJD_LOCAL_API_HEALTH_URL",
    "http://127.0.0.1:8000/health",
)

DEFAULT_CYCLE_SECONDS = max(
    30,
    int(os.getenv("MAJD_AUTONOMOUS_CYCLE_SECONDS", "300")),
)

DEFAULT_HTTP_TIMEOUT = max(
    2,
    int(os.getenv("MAJD_HTTP_TIMEOUT", "10")),
)

MAX_AUTONOMOUS_REPAIR_ATTEMPTS = max(
    1,
    int(os.getenv("MAJD_AUTONOMOUS_REPAIR_ATTEMPTS", "3")),
)

STOP_REQUESTED = False


# ============================================================
# LANGUAGE / TIME
# ============================================================

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def bilingual(ar: str, en: str, **extra: Any) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "message_ar": ar,
        "message_en": en,
    }
    result.update(extra)
    return result


def status_message(status: str) -> Dict[str, str]:
    messages = {
        "STARTING": (
            "جارٍ بدء تشغيل مجد.",
            "MAJD runtime is starting.",
        ),
        "RUNNING": (
            "التشغيل الذاتي يعمل.",
            "Autonomous runtime is running.",
        ),
        "RUNNING_HEALTHY": (
            "التشغيل الذاتي يعمل والمنصة سليمة.",
            "Autonomous runtime is running and the platform is healthy.",
        ),
        "RUNNING_DEGRADED": (
            "التشغيل الذاتي يعمل مع وجود مشكلات قيد المعالجة.",
            "Autonomous runtime is running with issues under repair.",
        ),
        "PLATFORM_HEALTHY": (
            "المنصة تعمل بصورة طبيعية.",
            "The platform is operating normally.",
        ),
        "ISSUES_DETECTED": (
            "اكتشف النظام مشكلات وسيبدأ الإصلاح الذاتي.",
            "The runtime detected issues and will start autonomous repair.",
        ),
        "REPAIRED_AND_VERIFIED": (
            "تم إصلاح المشكلات والتحقق من النتيجة.",
            "Issues were repaired and the result was verified.",
        ),
        "DEGRADED_AFTER_REPAIR": (
            "بقيت مشكلات بعد محاولة الإصلاح وسيواصل النظام المحاولة.",
            "Some issues remain after repair and the runtime will continue trying.",
        ),
        "OWNER_ACTION_REQUIRED": (
            "يوجد إجراء خارجي أو حساس يحتاج المالك.",
            "An external or sensitive action requires the owner.",
        ),
        "COMPLETED": (
            "اكتمل التنفيذ بنجاح.",
            "Execution completed successfully.",
        ),
        "STOPPED": (
            "تم إيقاف التشغيل الذاتي.",
            "Autonomous runtime has stopped.",
        ),
    }

    ar, en = messages.get(
        status,
        (f"الحالة: {status}", f"Status: {status}"),
    )

    return {
        "message_ar": ar,
        "message_en": en,
    }


# ============================================================
# BASIC HELPERS
# ============================================================

def safe_str(value: Any) -> str:
    try:
        return str(value)
    except Exception:
        return "<unprintable>"


def truncate_text(value: Any, limit: int = 12000) -> str:
    text = safe_str(value)

    if len(text) <= limit:
        return text

    return text[:limit] + "\n...[TRUNCATED]..."


def sha256_file(path: Path) -> Optional[str]:
    if not path.exists() or not path.is_file():
        return None

    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


# ============================================================
# JSON / AUDIT
# ============================================================

def save_json(
    path: Path,
    data: Dict[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = path.with_suffix(
        path.suffix + ".tmp"
    )

    with temporary.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

    temporary.replace(path)


def load_json(
    path: Path,
    default: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if default is None:
        default = {}

    if not path.exists():
        return dict(default)

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            value = json.load(file)

        if isinstance(value, dict):
            return value

    except Exception:
        pass

    return dict(default)


def append_jsonl(
    path: Path,
    data: Dict[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(
                data,
                ensure_ascii=False,
                default=str,
            )
        )
        file.write("\n")


# ============================================================
# MODULE LOADER
# ============================================================

def load_module(
    path: Path,
    module_name: str,
) -> Any:
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

    module = importlib.util.module_from_spec(spec)

    sys.modules[module_name] = module

    spec.loader.exec_module(module)

    return module


def find_callable(
    module: Any,
    names: Iterable[str],
) -> Optional[Callable[..., Any]]:
    for name in names:
        value = getattr(
            module,
            name,
            None,
        )

        if callable(value):
            return value

    return None


def call_supported(
    function: Callable[..., Any],
    values: Dict[str, Any],
) -> Any:
    signature = inspect.signature(function)
    parameters = signature.parameters

    accepts_kwargs = any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD
        for parameter in parameters.values()
    )

    kwargs: Dict[str, Any] = {}

    for key, value in values.items():
        if accepts_kwargs or key in parameters:
            kwargs[key] = value

    return function(**kwargs)


# ============================================================
# PROCESS EXECUTION
# ============================================================

def run_process(
    command: List[str],
    timeout: int = 60,
    cwd: Optional[Path] = None,
) -> Dict[str, Any]:
    started = utc_now()

    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd or ROOT_DIR),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

        return {
            "success":
                completed.returncode == 0,

            "command":
                command,

            "returncode":
                completed.returncode,

            "stdout":
                truncate_text(
                    completed.stdout
                ),

            "stderr":
                truncate_text(
                    completed.stderr
                ),

            "started_at":
                started,

            "finished_at":
                utc_now(),
        }

    except subprocess.TimeoutExpired as error:
        return {
            "success": False,
            "status": "PROCESS_TIMEOUT",
            "command": command,
            "error": safe_str(error),
            **bilingual(
                "انتهت مهلة تنفيذ العملية.",
                "Process execution timed out.",
            ),
        }

    except Exception as error:
        return {
            "success": False,
            "status": "PROCESS_EXCEPTION",
            "command": command,
            "error":
                f"{type(error).__name__}: {error}",

            **bilingual(
                "حدث خطأ أثناء تنفيذ العملية.",
                "An error occurred while executing the process.",
            ),
        }


# ============================================================
# CORE FILES
# ============================================================

def verify_required_files() -> Dict[str, Any]:
    required = {
        "01_mastermind":
            MASTERMIND_FILE,

        "02_owner_command_center":
            OWNER_COMMAND_CENTER_FILE,

        "03_real_game_executor":
            REAL_GAME_EXECUTOR_FILE,

        "04_official_platform_bridge":
            OFFICIAL_PLATFORM_BRIDGE_FILE,
    }

    optional = {
        "02_sovereign_company":
            SOVEREIGN_COMPANY_FILE,
    }

    files: Dict[str, Any] = {}
    missing: List[str] = []

    for name, path in required.items():
        exists = (
            path.exists()
            and path.is_file()
            and path.stat().st_size > 0
        )

        files[name] = {
            "file": path.name,
            "required": True,
            "exists": exists,
            "size":
                path.stat().st_size
                if path.exists()
                else 0,

            "sha256":
                sha256_file(path)
                if exists
                else None,
        }

        if not exists:
            missing.append(path.name)

    for name, path in optional.items():
        exists = (
            path.exists()
            and path.is_file()
            and path.stat().st_size > 0
        )

        files[name] = {
            "file": path.name,
            "required": False,
            "exists": exists,
            "size":
                path.stat().st_size
                if path.exists()
                else 0,

            "sha256":
                sha256_file(path)
                if exists
                else None,
        }

    return {
        "success":
            not missing,

        "files":
            files,

        "missing":
            missing,

        **(
            bilingual(
                "جميع الملفات الأساسية موجودة.",
                "All required core files are present.",
            )
            if not missing
            else bilingual(
                "توجد ملفات أساسية مفقودة.",
                "Some required core files are missing.",
            )
        ),
    }


# ============================================================
# PYTHON SYNTAX
# ============================================================

def discover_python_files() -> List[Path]:
    ignored_parts = {
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        "majd_game_output",
        "majd_factory_state",
    }

    discovered: List[Path] = []

    for path in ROOT_DIR.rglob("*.py"):
        if any(
            part in ignored_parts
            for part in path.parts
        ):
            continue

        if path.is_file():
            discovered.append(path)

    return sorted(discovered)


def verify_python_syntax(
    paths: Optional[List[Path]] = None,
) -> Dict[str, Any]:
    if paths is None:
        paths = discover_python_files()

    failed: List[str] = []
    results: List[Dict[str, Any]] = []

    for path in paths:
        process = run_process(
            [
                sys.executable,
                "-m",
                "py_compile",
                str(path),
            ],
            timeout=30,
        )

        try:
            display = str(
                path.relative_to(ROOT_DIR)
            )
        except ValueError:
            display = str(path)

        item = {
            "file":
                display,

            "success":
                bool(
                    process.get("success")
                ),
        }

        if not item["success"]:
            item["error"] = (
                process.get("stderr")
                or process.get("error")
                or "PYTHON_SYNTAX_FAILED"
            )

            failed.append(display)

        results.append(item)

    return {
        "success":
            not failed,

        "checked":
            len(results),

        "failed":
            failed,

        "results":
            results,
    }


# ============================================================
# HTTP HEALTH
# ============================================================

def http_probe(
    url: str,
    timeout: int = DEFAULT_HTTP_TIMEOUT,
) -> Dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent":
                "MAJD-AUTONOMOUS-RUNTIME/3.2"
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=timeout,
        ) as response:
            code = int(
                getattr(
                    response,
                    "status",
                    200,
                )
            )

            body = response.read(
                1024 * 1024
            ).decode(
                "utf-8",
                errors="replace",
            )

            success = (
                200 <= code < 400
            )

            return {
                "success":
                    success,

                "url":
                    url,

                "status_code":
                    code,

                "body":
                    truncate_text(
                        body,
                        4000,
                    ),
            }

    except urllib.error.HTTPError as error:
        return {
            "success": False,
            "url": url,
            "status_code": error.code,
            "error": safe_str(error),
        }

    except Exception as error:
        return {
            "success": False,
            "url": url,
            "status": "HTTP_PROBE_FAILED",
            "error":
                f"{type(error).__name__}: {error}",
        }


# ============================================================
# DOCKER
# ============================================================

def inspect_docker() -> Dict[str, Any]:
    process = run_process(
        [
            "docker",
            "ps",
            "--format",
            "{{.Names}}|{{.Status}}|{{.Ports}}",
        ],
        timeout=30,
    )

    if not process.get("success"):
        return {
            "success": False,
            "status":
                "DOCKER_UNAVAILABLE_OR_FAILED",

            "details":
                process,
        }

    containers: List[
        Dict[str, Any]
    ] = []

    for line in str(
        process.get(
            "stdout",
            "",
        )
    ).splitlines():
        line = line.strip()

        if not line:
            continue

        parts = line.split("|", 2)

        containers.append(
            {
                "name":
                    parts[0]
                    if len(parts) > 0
                    else "",

                "status":
                    parts[1]
                    if len(parts) > 1
                    else "",

                "ports":
                    parts[2]
                    if len(parts) > 2
                    else "",
            }
        )

    return {
        "success": True,
        "containers": containers,
    }


# ============================================================
# DISK
# ============================================================

def inspect_disk() -> Dict[str, Any]:
    try:
        stat = os.statvfs(ROOT_DIR)

        total = (
            stat.f_blocks
            * stat.f_frsize
        )

        available = (
            stat.f_bavail
            * stat.f_frsize
        )

        used = total - available

        used_percent = (
            (used / total) * 100.0
            if total > 0
            else 0.0
        )

        return {
            "success":
                used_percent < 90.0,

            "total_bytes":
                total,

            "used_bytes":
                used,

            "available_bytes":
                available,

            "used_percent":
                round(
                    used_percent,
                    2,
                ),

            "threshold_percent":
                90.0,
        }

    except Exception as error:
        return {
            "success": False,
            "status":
                "DISK_INSPECTION_FAILED",

            "error":
                f"{type(error).__name__}: {error}",
        }


# ============================================================
# OWNER COMMAND CENTER
# ============================================================

class OwnerCommandCenterRuntime:
    def __init__(self) -> None:
        self.module = load_module(
            OWNER_COMMAND_CENTER_FILE,
            "majd_owner_command_center_02_runtime",
        )

    def parse(
        self,
        command: str,
    ) -> Dict[str, Any]:
        parser_class = getattr(
            self.module,
            "OwnerCommandParser",
            None,
        )

        if parser_class is None:
            return {
                "type":
                    "GENERAL_OWNER_COMMAND",

                "raw":
                    command,

                "warning":
                    "OWNER_COMMAND_PARSER_NOT_FOUND",
            }

        try:
            parser = parser_class()

            result = parser.parse(
                command
            )

            if not isinstance(
                result,
                dict,
            ):
                return {
                    "type":
                        "GENERAL_OWNER_COMMAND",

                    "raw":
                        command,

                    "warning":
                        "INVALID_PARSE_RESULT",
                }

            result_type = str(
                result.get(
                    "type",
                    "",
                )
            ).upper()

            if (
                not result_type
                or result_type == "UNKNOWN"
            ):
                result["type"] = (
                    "GENERAL_OWNER_COMMAND"
                )

            return result

        except Exception as error:
            return {
                "type":
                    "GENERAL_OWNER_COMMAND",

                "raw":
                    command,

                "parser_error":
                    f"{type(error).__name__}: {error}",
            }

    def execute(
        self,
        command: str,
        owner: str,
    ) -> Dict[str, Any]:
        function = getattr(
            self.module,
            "execute_owner_command",
            None,
        )

        if not callable(function):
            return {
                "success": False,
                "status":
                    "OWNER_COMMAND_INTERFACE_MISSING",
            }

        try:
            result = call_supported(
                function,
                {
                    "command": command,
                    "owner": owner,
                },
            )

        except Exception as error:
            return {
                "success": False,
                "status":
                    "OWNER_COMMAND_EXECUTION_EXCEPTION",

                "error":
                    f"{type(error).__name__}: {error}",

                "traceback":
                    traceback.format_exc(),
            }

        if not isinstance(
            result,
            dict,
        ):
            return {
                "success": False,
                "status":
                    "INVALID_OWNER_COMMAND_RESULT",

                "result_type":
                    type(result).__name__,
            }

        return result


# ============================================================
# MASTERMIND BRIDGE
# ============================================================

class MastermindRuntime:
    FUNCTION_NAMES = (
        "execute_request",
        "process_request",
        "execute_game_request",
        "run",
        "run_request",
        "execute",
    )

    def __init__(self) -> None:
        self.module = load_module(
            MASTERMIND_FILE,
            "majd_ai_mastermind_01_runtime",
        )

    def execute(
        self,
        command: str,
        request: Dict[str, Any],
        runtime_id: str,
        owner: str,
    ) -> Dict[str, Any]:
        function = find_callable(
            self.module,
            self.FUNCTION_NAMES,
        )

        if function is None:
            mastermind_class = getattr(
                self.module,
                "Mastermind",
                None,
            )

            if mastermind_class is None:
                return {
                    "success": False,
                    "status":
                        "MASTERMIND_INTERFACE_NOT_FOUND",
                }

            try:
                instance = call_supported(
                    mastermind_class,
                    {
                        "owner": owner,
                    },
                )

            except Exception as error:
                return {
                    "success": False,
                    "status":
                        "MASTERMIND_INITIALIZATION_FAILED",

                    "error":
                        f"{type(error).__name__}: {error}",
                }

            function = find_callable(
                instance,
                (
                    "execute_request",
                    "process_request",
                    "run_request",
                    "run",
                    "execute",
                ),
            )

            if function is None:
                return {
                    "success": False,
                    "status":
                        "MASTERMIND_RUN_INTERFACE_MISSING",
                }

        try:
            result = call_supported(
                function,
                {
                    "command":
                        command,

                    "request":
                        request,

                    "payload":
                        request,

                    "job_id":
                        runtime_id,

                    "runtime_id":
                        runtime_id,

                    "owner":
                        owner,

                    "output_root":
                        str(OUTPUT_DIR),
                },
            )

        except Exception as error:
            return {
                "success": False,
                "status":
                    "MASTERMIND_EXECUTION_EXCEPTION",

                "error":
                    f"{type(error).__name__}: {error}",

                "traceback":
                    traceback.format_exc(),
            }

        if not isinstance(
            result,
            dict,
        ):
            return {
                "success": False,
                "status":
                    "INVALID_MASTERMIND_RESULT",

                "result_type":
                    type(result).__name__,
            }

        return result


# ============================================================
# SOVEREIGN COMPANY BRIDGE
# ============================================================

class SovereignCompanyRuntime:
    STATUS_FUNCTIONS = (
        "get_company_status",
        "company_status",
        "get_status",
        "status",
        "health",
        "health_check",
        "self_test",
        "inspect_company",
        "report",
    )

    def __init__(self) -> None:
        self.available = (
            SOVEREIGN_COMPANY_FILE.exists()
            and SOVEREIGN_COMPANY_FILE.is_file()
            and SOVEREIGN_COMPANY_FILE.stat().st_size > 0
        )

        self.module = None

        if self.available:
            self.module = load_module(
                SOVEREIGN_COMPANY_FILE,
                "majd_ai_sovereign_company_02_runtime",
            )

    def inspect(
        self,
    ) -> Dict[str, Any]:
        if not self.available:
            return {
                "success": False,
                "status":
                    "SOVEREIGN_COMPANY_FILE_MISSING",
            }

        assert self.module is not None

        function = find_callable(
            self.module,
            self.STATUS_FUNCTIONS,
        )

        if function is not None:
            try:
                result = call_supported(
                    function,
                    {
                        "owner":
                            DEFAULT_OWNER,

                        "root_dir":
                            str(ROOT_DIR),
                    },
                )

                if isinstance(
                    result,
                    dict,
                ):
                    return {
                        "success": True,
                        "status":
                            "SOVEREIGN_COMPANY_INSPECTED",

                        "source":
                            getattr(
                                function,
                                "__name__",
                                "unknown",
                            ),

                        "company":
                            result,
                    }

            except Exception as error:
                return {
                    "success": False,
                    "status":
                        "SOVEREIGN_COMPANY_INSPECTION_FAILED",

                    "error":
                        f"{type(error).__name__}: {error}",
                }

        return {
            "success": True,
            "status":
                "SOVEREIGN_COMPANY_MODULE_LOADED",

            "warning":
                "NO_STANDARD_COMPANY_STATUS_INTERFACE",
        }


# ============================================================
# PLAYABLE ARTIFACT
# ============================================================

def verify_playable_artifact(
    artifact_value: Any,
) -> Dict[str, Any]:
    if not artifact_value:
        return {
            "success": False,
            "status":
                "PLAYABLE_ARTIFACT_MISSING",
        }

    artifact = Path(
        str(artifact_value)
    )

    if not artifact.is_absolute():
        artifact = (
            ROOT_DIR
            / artifact
        ).resolve()
    else:
        artifact = (
            artifact.resolve()
        )

    if (
        not artifact.exists()
        or not artifact.is_dir()
    ):
        return {
            "success": False,
            "status":
                "PLAYABLE_ARTIFACT_NOT_FOUND",

            "artifact":
                str(artifact),
        }

    index_file = (
        artifact
        / "index.html"
    )

    if (
        not index_file.exists()
        or index_file.stat().st_size <= 0
    ):
        return {
            "success": False,
            "status":
                "PLAYABLE_INDEX_NOT_FOUND_OR_EMPTY",

            "artifact":
                str(artifact),
        }

    files = [
        path
        for path in artifact.rglob("*")
        if path.is_file()
    ]

    javascript_files = [
        path
        for path in files
        if path.suffix.lower()
        in (".js", ".mjs")
    ]

    if not javascript_files:
        return {
            "success": False,
            "status":
                "PLAYABLE_JAVASCRIPT_NOT_FOUND",

            "artifact":
                str(artifact),
        }

    return {
        "success": True,
        "status":
            "PLAYABLE_ARTIFACT_VERIFIED",

        "artifact":
            str(artifact),

        "index":
            str(index_file),

        "file_count":
            len(files),
    }


# ============================================================
# PUBLISHED RESULT
# ============================================================

def verify_published_result(
    platform_result: Dict[str, Any],
) -> Dict[str, Any]:
    if not isinstance(
        platform_result,
        dict,
    ):
        return {
            "success": False,
            "status":
                "PLATFORM_RESULT_INVALID",
        }

    if not platform_result.get(
        "success"
    ):
        return {
            "success": False,
            "status":
                platform_result.get(
                    "status",
                    "PLATFORM_NOT_SUCCESSFUL",
                ),
        }

    published_directory = (
        platform_result.get(
            "published_directory"
        )
    )

    public_url = (
        platform_result.get(
            "public_url"
        )
    )

    game_path = (
        platform_result.get(
            "game_path"
        )
    )

    if (
        not published_directory
        or not public_url
        or not game_path
    ):
        return {
            "success": False,
            "status":
                "PUBLISHED_RESULT_INCOMPLETE",
        }

    published_path = Path(
        str(
            published_directory
        )
    )

    if not published_path.is_absolute():
        published_path = (
            ROOT_DIR
            / published_path
        ).resolve()

    index_file = (
        published_path
        / "index.html"
    )

    if (
        not published_path.exists()
        or not index_file.exists()
    ):
        return {
            "success": False,
            "status":
                "PUBLISHED_ARTIFACT_NOT_FOUND",
        }

    return {
        "success": True,
        "status":
            "PUBLISHED_RESULT_VERIFIED",

        "published_directory":
            str(published_path),

        "index":
            str(index_file),

        "game_path":
            game_path,

        "public_url":
            public_url,
    }


# ============================================================
# FINAL RESULT
# ============================================================

def verify_mastermind_result(
    command_type: str,
    result: Dict[str, Any],
) -> Dict[str, Any]:
    if not isinstance(
        result,
        dict,
    ):
        return {
            "success": False,
            "status":
                "INVALID_FINAL_RESULT",
        }

    if not result.get(
        "success"
    ):
        return {
            "success": False,
            "status":
                result.get(
                    "status",
                    "MASTERMIND_FAILED",
                ),

            "result":
                result,
        }

    if command_type != "CREATE_GAME":
        return {
            "success": True,
            "status":
                "MASTERMIND_RESULT_VERIFIED",

            "result":
                result,
        }

    artifact_verification = (
        verify_playable_artifact(
            result.get(
                "artifact"
            )
        )
    )

    if not artifact_verification.get(
        "success"
    ):
        return {
            "success": False,
            "status":
                artifact_verification.get(
                    "status"
                ),

            "artifact_verification":
                artifact_verification,
        }

    platform_result = (
        result.get(
            "platform"
        )
    )

    if not isinstance(
        platform_result,
        dict,
    ):
        return {
            "success": False,
            "status":
                "PLATFORM_RESULT_MISSING",
        }

    publication_verification = (
        verify_published_result(
            platform_result
        )
    )

    if not publication_verification.get(
        "success"
    ):
        return {
            "success": False,
            "status":
                publication_verification.get(
                    "status"
                ),

            "publication_verification":
                publication_verification,
        }

    return {
        "success": True,
        "status":
            "FULL_EXECUTION_VERIFIED",

        "artifact":
            artifact_verification,

        "publication":
            publication_verification,

        "result":
            result,
    }


# ============================================================
# OWNER COMMAND RUNTIME
# ============================================================

class MajdFullExecutionRuntime:
    def __init__(self) -> None:
        self.runtime_id = str(
            uuid.uuid4()
        )

    def state_path(
        self,
    ) -> Path:
        return (
            RUNTIME_DIR
            / f"{self.runtime_id}.json"
        )

    def save(
        self,
        state: Dict[str, Any],
    ) -> None:
        state[
            "updated_at"
        ] = utc_now()

        save_json(
            self.state_path(),
            state,
        )

    def execute(
        self,
        command: str,
        owner: str = DEFAULT_OWNER,
    ) -> Dict[str, Any]:
        command = str(
            command or ""
        ).strip()

        state: Dict[str, Any] = {
            "runtime_id":
                self.runtime_id,

            "system":
                SYSTEM_NAME,

            "runtime":
                RUNTIME_NAME,

            "version":
                VERSION,

            "owner":
                owner,

            "command":
                command,

            "official_platform":
                OFFICIAL_MAJD_PLATFORM,

            "started_at":
                utc_now(),

            "updated_at":
                utc_now(),

            "finished_at":
                None,

            "success":
                False,

            "status":
                "STARTING",

            "stages":
                {},

            **status_message(
                "STARTING"
            ),
        }

        self.save(state)

        try:
            if not command:
                state[
                    "status"
                ] = (
                    "EMPTY_OWNER_COMMAND"
                )

                state.update(
                    bilingual(
                        "أمر المالك لا يمكن أن يكون فارغا.",
                        "Owner command cannot be empty.",
                    )
                )

                state[
                    "finished_at"
                ] = utc_now()

                self.save(state)

                return state

            files_result = (
                verify_required_files()
            )

            state[
                "stages"
            ][
                "core_files"
            ] = files_result

            if not files_result.get(
                "success"
            ):
                state[
                    "status"
                ] = (
                    "REQUIRED_FILES_MISSING"
                )

                state[
                    "finished_at"
                ] = utc_now()

                self.save(state)

                return state

            owner_runtime = (
                OwnerCommandCenterRuntime()
            )

            parsed_request = (
                owner_runtime.parse(
                    command
                )
            )

            command_type = str(
                parsed_request.get(
                    "type",
                    "GENERAL_OWNER_COMMAND",
                )
            ).upper()

            if (
                not command_type
                or command_type == "UNKNOWN"
            ):
                command_type = (
                    "GENERAL_OWNER_COMMAND"
                )

                parsed_request[
                    "type"
                ] = command_type

            state[
                "stages"
            ][
                "command"
            ] = {
                "success":
                    True,

                "type":
                    command_type,

                "request":
                    parsed_request,
            }

            if command_type in (
                "STATUS",
                "SYSTEM_STATUS",
            ):
                result = (
                    owner_runtime.execute(
                        command=command,
                        owner=owner,
                    )
                )

                state[
                    "stages"
                ][
                    "owner_status"
                ] = result

                state[
                    "result"
                ] = result

                state[
                    "success"
                ] = bool(
                    result.get(
                        "success",
                        False,
                    )
                )

                state[
                    "status"
                ] = str(
                    result.get(
                        "status"
                    )
                    or (
                        "COMPLETED"
                        if state[
                            "success"
                        ]
                        else
                        "FAILED"
                    )
                )

                state[
                    "finished_at"
                ] = utc_now()

                self.save(state)

                return state

            mastermind = (
                MastermindRuntime()
            )

            mastermind_result = (
                mastermind.execute(
                    command=
                        command,

                    request=
                        parsed_request,

                    runtime_id=
                        self.runtime_id,

                    owner=
                        owner,
                )
            )

            state[
                "stages"
            ][
                "mastermind"
            ] = mastermind_result

            if not mastermind_result.get(
                "success"
            ):
                state[
                    "status"
                ] = str(
                    mastermind_result.get(
                        "status",
                        "MASTERMIND_FAILED",
                    )
                )

                state[
                    "result"
                ] = (
                    mastermind_result
                )

                state[
                    "finished_at"
                ] = utc_now()

                self.save(state)

                return state

            verification = (
                verify_mastermind_result(
                    command_type=
                        command_type,

                    result=
                        mastermind_result,
                )
            )

            state[
                "stages"
            ][
                "final_verification"
            ] = verification

            if not verification.get(
                "success"
            ):
                state[
                    "status"
                ] = str(
                    verification.get(
                        "status",
                        "FINAL_VERIFICATION_FAILED",
                    )
                )

                state[
                    "result"
                ] = (
                    mastermind_result
                )

                state[
                    "finished_at"
                ] = utc_now()

                self.save(state)

                return state

            state[
                "success"
            ] = True

            state[
                "status"
            ] = (
                "COMPLETED"
            )

            state[
                "result"
            ] = (
                mastermind_result
            )

            state[
                "verification"
            ] = verification

            state.update(
                status_message(
                    "COMPLETED"
                )
            )

            if command_type == "CREATE_GAME":
                publication = (
                    verification.get(
                        "publication",
                        {},
                    )
                )

                artifact = (
                    verification.get(
                        "artifact",
                        {},
                    )
                )

                state[
                    "artifact"
                ] = (
                    artifact.get(
                        "artifact"
                    )
                )

                state[
                    "game_path"
                ] = (
                    publication.get(
                        "game_path"
                    )
                )

                state[
                    "public_url"
                ] = (
                    publication.get(
                        "public_url"
                    )
                )

                state[
                    "published"
                ] = True

            state[
                "finished_at"
            ] = utc_now()

            self.save(state)

            return state

        except Exception as error:
            state[
                "success"
            ] = False

            state[
                "status"
            ] = (
                "RUNTIME_EXCEPTION"
            )

            state[
                "error"
            ] = (
                f"{type(error).__name__}: "
                f"{error}"
            )

            state[
                "traceback"
            ] = (
                traceback.format_exc()
            )

            state[
                "finished_at"
            ] = utc_now()

            self.save(state)

            return state


# ============================================================
# AUTONOMOUS FINDINGS
# ============================================================

def finding(
    finding_id: str,
    severity: str,
    component: str,
    status: str,
    message_ar: str,
    message_en: str,
    repairable: bool = True,
    owner_required: bool = False,
    evidence: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "id":
            finding_id,

        "severity":
            severity.upper(),

        "component":
            component,

        "status":
            status,

        "message_ar":
            message_ar,

        "message_en":
            message_en,

        "repairable":
            repairable,

        "owner_required":
            owner_required,

        "evidence":
            evidence or {},

        "detected_at":
            utc_now(),
    }


def derive_findings(
    inspection: Dict[str, Any],
) -> List[Dict[str, Any]]:
    findings: List[
        Dict[str, Any]
    ] = []

    if not inspection.get(
        "core_files",
        {},
    ).get(
        "success"
    ):
        findings.append(
            finding(
                "CORE_FILES_MISSING",
                "CRITICAL",
                "CORE",
                "FAILED",
                "ملفات أساسية مطلوبة مفقودة أو فارغة.",
                "Required core files are missing or empty.",
                evidence=
                    inspection.get(
                        "core_files",
                        {},
                    ),
            )
        )

    if not inspection.get(
        "python_syntax",
        {},
    ).get(
        "success"
    ):
        findings.append(
            finding(
                "PYTHON_SYNTAX_FAILURE",
                "CRITICAL",
                "SOURCE_CODE",
                "FAILED",
                "يوجد خطأ Syntax في ملف بايثون واحد أو أكثر.",
                "One or more Python files contain syntax errors.",
                evidence=
                    inspection.get(
                        "python_syntax",
                        {},
                    ),
            )
        )

    if not inspection.get(
        "local_api",
        {},
    ).get(
        "success"
    ):
        findings.append(
            finding(
                "LOCAL_API_UNHEALTHY",
                "HIGH",
                "MAJD_AI_CORE",
                "DEGRADED",
                "فشل فحص صحة API المحلي.",
                "Local API health probe failed.",
                evidence=
                    inspection.get(
                        "local_api",
                        {},
                    ),
            )
        )

    if not inspection.get(
        "official_platform",
        {},
    ).get(
        "success"
    ):
        findings.append(
            finding(
                "OFFICIAL_PLATFORM_UNREACHABLE",
                "CRITICAL",
                "PUBLIC_PLATFORM",
                "FAILED",
                "تعذر الوصول إلى منصة مجد الرسمية.",
                "Official MAJD platform is unreachable.",
                evidence=
                    inspection.get(
                        "official_platform",
                        {},
                    ),
            )
        )

    if not inspection.get(
        "docker",
        {},
    ).get(
        "success"
    ):
        findings.append(
            finding(
                "DOCKER_DEGRADED",
                "HIGH",
                "DOCKER",
                "DEGRADED",
                "Docker غير متاح أو فشل فحصه.",
                "Docker is unavailable or failed inspection.",
                evidence=
                    inspection.get(
                        "docker",
                        {},
                    ),
            )
        )

    if not inspection.get(
        "disk",
        {},
    ).get(
        "success"
    ):
        findings.append(
            finding(
                "DISK_CAPACITY_RISK",
                "HIGH",
                "SERVER_STORAGE",
                "DEGRADED",
                "مساحة تخزين السيرفر تحتاج معالجة.",
                "Server storage requires attention.",
                evidence=
                    inspection.get(
                        "disk",
                        {},
                    ),
            )
        )

    if not inspection.get(
        "sovereign_company",
        {},
    ).get(
        "success"
    ):
        findings.append(
            finding(
                "SOVEREIGN_COMPANY_UNAVAILABLE",
                "HIGH",
                "SOVEREIGN_COMPANY",
                "UNAVAILABLE",
                "تعذر فحص الشركة السيادية 02.",
                "Unable to inspect Sovereign Company 02.",
                evidence=
                    inspection.get(
                        "sovereign_company",
                        {},
                    ),
            )
        )

    return findings


# ============================================================
# AUTONOMOUS OBJECTIVE
# ============================================================

def build_autonomous_objective(
    cycle_id: str,
    findings: List[Dict[str, Any]],
) -> Tuple[
    str,
    Dict[str, Any],
]:
    request = {
        "type":
            "AUTONOMOUS_PLATFORM_MAINTENANCE",

        "source":
            RUNTIME_NAME,

        "cycle_id":
            cycle_id,

        "owner":
            DEFAULT_OWNER,

        "autonomous":
            True,

        "language": {
            "primary":
                "ar",

            "secondary":
                "en",
        },

        "findings":
            findings,

        "policy": {
            "routine_owner_approval_required":
                False,

            "preserve_working_features":
                True,

            "prefer_existing_components":
                True,

            "allow_code_generation":
                True,

            "allow_code_repair":
                True,

            "allow_integration":
                True,

            "allow_testing":
                True,

            "allow_routine_service_recovery":
                True,

            "require_real_verification":
                True,

            "never_fake_operational":
                True,

            "protect_owner_authority":
                True,

            "protect_secrets":
                True,

            "owner_reports_bilingual":
                True,
        },
    }

    command = (
        "MAJD AUTONOMOUS PLATFORM MAINTENANCE / "
        "صيانة منصة مجد الذاتية. "
        "Inspect the supplied findings and repair all routine "
        "technical problems that can be repaired safely without "
        "owner interaction. Use existing MAJD components first. "
        "Create or repair code when required. Preserve working "
        "functionality. Test every change. Do not report "
        "OPERATIONAL without real evidence. Protect OWNER "
        "authority and secrets. Return structured Arabic and "
        "English owner messages."
    )

    return command, request


# ============================================================
# AUTONOMOUS RUNTIME
# ============================================================

class MajdAutonomousRuntime:
    def __init__(
        self,
        owner: str = DEFAULT_OWNER,
        cycle_seconds: int = DEFAULT_CYCLE_SECONDS,
    ) -> None:
        self.owner = owner

        self.cycle_seconds = max(
            30,
            int(
                cycle_seconds
            ),
        )

        self.session_id = str(
            uuid.uuid4()
        )

        self.started_at = utc_now()

        previous = load_json(
            AUTONOMOUS_STATE_FILE,
            {},
        )

        self.total_cycles = int(
            previous.get(
                "total_cycles",
                0,
            )
            or 0
        )

        self.successful_cycles = int(
            previous.get(
                "successful_cycles",
                0,
            )
            or 0
        )

        self.failed_cycles = int(
            previous.get(
                "failed_cycles",
                0,
            )
            or 0
        )

        self.repair_cycles = int(
            previous.get(
                "repair_cycles",
                0,
            )
            or 0
        )

    def audit(
        self,
        event: str,
        data: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:
        append_jsonl(
            AUTONOMOUS_AUDIT_FILE,
            {
                "time":
                    utc_now(),

                "session_id":
                    self.session_id,

                "event":
                    event,

                "data":
                    data or {},
            },
        )

    def save_state(
        self,
        status: str,
        cycle: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:
        state = {
            "system":
                SYSTEM_NAME,

            "runtime":
                RUNTIME_NAME,

            "version":
                VERSION,

            "mode":
                "AUTONOMOUS_PERSISTENT",

            "owner":
                self.owner,

            "session_id":
                self.session_id,

            "pid":
                os.getpid(),

            "status":
                status,

            **status_message(
                status
            ),

            "started_at":
                self.started_at,

            "updated_at":
                utc_now(),

            "cycle_seconds":
                self.cycle_seconds,

            "total_cycles":
                self.total_cycles,

            "successful_cycles":
                self.successful_cycles,

            "failed_cycles":
                self.failed_cycles,

            "repair_cycles":
                self.repair_cycles,

            "last_cycle":
                cycle,
        }

        save_json(
            AUTONOMOUS_STATE_FILE,
            state,
        )

    def inspect_platform(
        self,
    ) -> Dict[str, Any]:
        inspection: Dict[
            str,
            Any
        ] = {
            "time":
                utc_now(),

            "core_files":
                verify_required_files(),

            "python_syntax":
                verify_python_syntax(),

            "local_api":
                http_probe(
                    LOCAL_API_HEALTH_URL
                ),

            "official_platform":
                http_probe(
                    OFFICIAL_MAJD_PLATFORM
                ),

            "docker":
                inspect_docker(),

            "disk":
                inspect_disk(),
        }

        try:
            company_runtime = (
                SovereignCompanyRuntime()
            )

            inspection[
                "sovereign_company"
            ] = (
                company_runtime.inspect()
            )

        except Exception as error:
            inspection[
                "sovereign_company"
            ] = {
                "success":
                    False,

                "status":
                    "SOVEREIGN_COMPANY_EXCEPTION",

                "error":
                    f"{type(error).__name__}: {error}",
            }

        return inspection

    def repair(
        self,
        cycle_id: str,
        findings: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        repairable = [
            item
            for item in findings
            if item.get(
                "repairable",
                True,
            )
            and not item.get(
                "owner_required",
                False,
            )
        ]

        if not repairable:
            return {
                "success":
                    True,

                "status":
                    "NO_AUTONOMOUS_REPAIR_REQUIRED",
            }

        command, request = (
            build_autonomous_objective(
                cycle_id=
                    cycle_id,

                findings=
                    repairable,
            )
        )

        attempts: List[
            Dict[str, Any]
        ] = []

        for attempt in range(
            1,
            MAX_AUTONOMOUS_REPAIR_ATTEMPTS + 1,
        ):
            runtime_id = (
                f"AUTO-{cycle_id}-{attempt}"
            )

            try:
                mastermind = (
                    MastermindRuntime()
                )

                result = (
                    mastermind.execute(
                        command=
                            command,

                        request=
                            request,

                        runtime_id=
                            runtime_id,

                        owner=
                            self.owner,
                    )
                )

            except Exception as error:
                result = {
                    "success":
                        False,

                    "status":
                        "AUTONOMOUS_MASTERMIND_EXCEPTION",

                    "error":
                        f"{type(error).__name__}: {error}",
                }

            attempts.append(
                {
                    "attempt":
                        attempt,

                    "runtime_id":
                        runtime_id,

                    "result":
                        result,
                }
            )

            self.audit(
                "AUTONOMOUS_REPAIR_ATTEMPT",
                {
                    "cycle_id":
                        cycle_id,

                    "attempt":
                        attempt,

                    "success":
                        bool(
                            result.get(
                                "success"
                            )
                        ),

                    "status":
                        result.get(
                            "status"
                        ),
                },
            )

            if result.get(
                "success"
            ):
                return {
                    "success":
                        True,

                    "status":
                        "MASTERMIND_REPAIR_EXECUTED",

                    "attempts":
                        attempts,

                    "result":
                        result,
                }

            if (
                attempt
                <
                MAX_AUTONOMOUS_REPAIR_ATTEMPTS
            ):
                time.sleep(2)

        return {
            "success":
                False,

            "status":
                "AUTONOMOUS_REPAIR_FAILED",

            "attempts":
                attempts,
        }

    def run_cycle(
        self,
    ) -> Dict[str, Any]:
        cycle_id = str(
            uuid.uuid4()
        )

        self.total_cycles += 1

        cycle: Dict[
            str,
            Any
        ] = {
            "cycle_id":
                cycle_id,

            "started_at":
                utc_now(),

            "finished_at":
                None,

            "success":
                False,

            "status":
                "INSPECTING",

            **bilingual(
                "جارٍ فحص المنصة.",
                "Inspecting the platform.",
            ),

            "inspection":
                {},

            "findings":
                [],

            "repair":
                None,

            "verification":
                None,
        }

        self.audit(
            "CYCLE_STARTED",
            {
                "cycle_id":
                    cycle_id,
            },
        )

        try:
            inspection = (
                self.inspect_platform()
            )

            cycle[
                "inspection"
            ] = inspection

            findings = (
                derive_findings(
                    inspection
                )
            )

            cycle[
                "findings"
            ] = findings

            if not findings:
                cycle[
                    "success"
                ] = True

                cycle[
                    "status"
                ] = (
                    "PLATFORM_HEALTHY"
                )

                cycle.update(
                    status_message(
                        "PLATFORM_HEALTHY"
                    )
                )

                cycle[
                    "finished_at"
                ] = utc_now()

                self.successful_cycles += 1

                save_json(
                    AUTONOMOUS_LATEST_REPORT,
                    cycle,
                )

                self.save_state(
                    "RUNNING_HEALTHY",
                    cycle,
                )

                return cycle

            cycle[
                "status"
            ] = (
                "ISSUES_DETECTED"
            )

            cycle.update(
                status_message(
                    "ISSUES_DETECTED"
                )
            )

            self.repair_cycles += 1

            repair_result = (
                self.repair(
                    cycle_id=
                        cycle_id,

                    findings=
                        findings,
                )
            )

            cycle[
                "repair"
            ] = repair_result

            verification = (
                self.inspect_platform()
            )

            cycle[
                "verification"
            ] = verification

            remaining = (
                derive_findings(
                    verification
                )
            )

            cycle[
                "remaining_findings"
            ] = remaining

            if not remaining:
                cycle[
                    "success"
                ] = True

                cycle[
                    "status"
                ] = (
                    "REPAIRED_AND_VERIFIED"
                )

                cycle.update(
                    status_message(
                        "REPAIRED_AND_VERIFIED"
                    )
                )

                self.successful_cycles += 1

            else:
                cycle[
                    "success"
                ] = False

                cycle[
                    "status"
                ] = (
                    "DEGRADED_AFTER_REPAIR"
                )

                cycle.update(
                    status_message(
                        "DEGRADED_AFTER_REPAIR"
                    )
                )

                self.failed_cycles += 1

            cycle[
                "finished_at"
            ] = utc_now()

            save_json(
                AUTONOMOUS_LATEST_REPORT,
                cycle,
            )

            self.save_state(
                (
                    "RUNNING_HEALTHY"
                    if cycle[
                        "success"
                    ]
                    else
                    "RUNNING_DEGRADED"
                ),
                cycle,
            )

            return cycle

        except Exception as error:
            self.failed_cycles += 1

            cycle[
                "success"
            ] = False

            cycle[
                "status"
            ] = (
                "AUTONOMOUS_CYCLE_EXCEPTION"
            )

            cycle[
                "error"
            ] = (
                f"{type(error).__name__}: "
                f"{error}"
            )

            cycle[
                "traceback"
            ] = (
                traceback.format_exc()
            )

            cycle[
                "finished_at"
            ] = utc_now()

            save_json(
                AUTONOMOUS_LATEST_REPORT,
                cycle,
            )

            self.save_state(
                "RUNNING_DEGRADED",
                cycle,
            )

            return cycle

    def interruptible_wait(
        self,
        seconds: int,
    ) -> None:
        global STOP_REQUESTED

        deadline = (
            time.monotonic()
            + max(
                0,
                seconds,
            )
        )

        while (
            not STOP_REQUESTED
            and time.monotonic()
            < deadline
        ):
            remaining = (
                deadline
                - time.monotonic()
            )

            time.sleep(
                min(
                    1.0,
                    max(
                        0.05,
                        remaining,
                    ),
                )
            )

    def run_once(
        self,
    ) -> Dict[str, Any]:
        self.save_state(
            "RUNNING"
        )

        result = (
            self.run_cycle()
        )

        self.save_state(
            (
                "RUNNING_HEALTHY"
                if result.get(
                    "success"
                )
                else
                "RUNNING_DEGRADED"
            ),
            result,
        )

        return result

    def run_forever(
        self,
    ) -> int:
        global STOP_REQUESTED

        PID_FILE.write_text(
            str(
                os.getpid()
            ),
            encoding="utf-8",
        )

        self.audit(
            "AUTONOMOUS_RUNTIME_STARTED",
            {
                "pid":
                    os.getpid(),

                "cycle_seconds":
                    self.cycle_seconds,
            },
        )

        self.save_state(
            "STARTING"
        )

        try:
            while not STOP_REQUESTED:
                self.save_state(
                    "RUNNING"
                )

                cycle = (
                    self.run_cycle()
                )

                print(
                    json.dumps(
                        {
                            "time":
                                utc_now(),

                            "mode":
                                "AUTONOMOUS",

                            "cycle_id":
                                cycle.get(
                                    "cycle_id"
                                ),

                            "success":
                                cycle.get(
                                    "success"
                                ),

                            "status":
                                cycle.get(
                                    "status"
                                ),

                            "message_ar":
                                cycle.get(
                                    "message_ar"
                                ),

                            "message_en":
                                cycle.get(
                                    "message_en"
                                ),

                            "findings":
                                len(
                                    cycle.get(
                                        "findings",
                                        [],
                                    )
                                ),

                            "remaining_findings":
                                len(
                                    cycle.get(
                                        "remaining_findings",
                                        [],
                                    )
                                ),
                        },
                        ensure_ascii=False,
                    ),
                    flush=True,
                )

                if STOP_REQUESTED:
                    break

                self.interruptible_wait(
                    self.cycle_seconds
                )

            self.save_state(
                "STOPPED"
            )

            self.audit(
                "AUTONOMOUS_RUNTIME_STOPPED",
                {},
            )

            return 0

        finally:
            try:
                if PID_FILE.exists():
                    PID_FILE.unlink()
            except Exception:
                pass


# ============================================================
# SIGNALS
# ============================================================

def request_shutdown(
    signum: int,
    frame: Any,
) -> None:
    global STOP_REQUESTED

    STOP_REQUESTED = True

    try:
        append_jsonl(
            AUTONOMOUS_AUDIT_FILE,
            {
                "time":
                    utc_now(),

                "event":
                    "SHUTDOWN_SIGNAL",

                "signal":
                    signum,
            },
        )

    except Exception:
        pass


def install_signal_handlers() -> None:
    signal.signal(
        signal.SIGTERM,
        request_shutdown,
    )

    signal.signal(
        signal.SIGINT,
        request_shutdown,
    )


# ============================================================
# PUBLIC API
# ============================================================

def execute_full_factory(
    command: str,
    owner: str = DEFAULT_OWNER,
    **kwargs: Any,
) -> Dict[str, Any]:
    runtime = (
        MajdFullExecutionRuntime()
    )

    return runtime.execute(
        command=
            command,

        owner=
            owner,
    )


def execute_owner_runtime(
    command: str,
    owner: str = DEFAULT_OWNER,
    **kwargs: Any,
) -> Dict[str, Any]:
    return execute_full_factory(
        command=
            command,

        owner=
            owner,
    )


def execute(
    command: str,
    owner: str = DEFAULT_OWNER,
    **kwargs: Any,
) -> Dict[str, Any]:
    return execute_full_factory(
        command=
            command,

        owner=
            owner,
    )


def run(
    command: str,
    owner: str = DEFAULT_OWNER,
    **kwargs: Any,
) -> Dict[str, Any]:
    return execute_full_factory(
        command=
            command,

        owner=
            owner,
    )


def run_autonomous_once(
    owner: str = DEFAULT_OWNER,
    cycle_seconds: int = DEFAULT_CYCLE_SECONDS,
    **kwargs: Any,
) -> Dict[str, Any]:
    install_signal_handlers()

    runtime = (
        MajdAutonomousRuntime(
            owner=
                owner,

            cycle_seconds=
                cycle_seconds,
        )
    )

    return runtime.run_once()


def run_autonomous_forever(
    owner: str = DEFAULT_OWNER,
    cycle_seconds: int = DEFAULT_CYCLE_SECONDS,
    **kwargs: Any,
) -> int:
    install_signal_handlers()

    runtime = (
        MajdAutonomousRuntime(
            owner=
                owner,

            cycle_seconds=
                cycle_seconds,
        )
    )

    return runtime.run_forever()


def get_autonomous_status() -> Dict[str, Any]:
    state = load_json(
        AUTONOMOUS_STATE_FILE,
        {},
    )

    pid = state.get(
        "pid"
    )

    process_alive = False

    if (
        isinstance(
            pid,
            int,
        )
        and pid > 0
    ):
        try:
            os.kill(
                pid,
                0,
            )

            process_alive = True

        except Exception:
            process_alive = False

    state[
        "process_alive"
    ] = process_alive

    state[
        "state_file"
    ] = str(
        AUTONOMOUS_STATE_FILE
    )

    state[
        "latest_report"
    ] = str(
        AUTONOMOUS_LATEST_REPORT
    )

    if (
        "message_ar"
        not in state
    ):
        state.update(
            bilingual(
                "هذه هي حالة التشغيل الذاتي الحالية.",
                "This is the current autonomous runtime status.",
            )
        )

    return state


# ============================================================
# OUTPUT
# ============================================================

def print_result(
    result: Dict[str, Any],
) -> None:
    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    )


# ============================================================
# CLI
# ============================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "MAJD SOVEREIGN AUTONOMOUS "
            "FULL EXECUTION RUNTIME 06 / "
            "المشغل السيادي الذاتي الكامل لمجد"
        )
    )

    # هذا هو الإصلاح الأساسي:
    # command لم يعد إجباريا.
    parser.add_argument(
        "command",
        nargs="*",
        help=(
            "Owner command in Arabic or English / "
            "أمر المالك بالعربية أو الإنجليزية"
        ),
    )

    parser.add_argument(
        "--owner",
        default=
            DEFAULT_OWNER,

        help=
            "Owner identity / هوية المالك",
    )

    parser.add_argument(
        "--autonomous",
        action=
            "store_true",

        help=(
            "Run autonomous persistent runtime / "
            "تشغيل ذاتي دائم"
        ),
    )

    parser.add_argument(
        "--once",
        action=
            "store_true",

        help=(
            "Run one autonomous cycle then exit / "
            "تشغيل دورة ذاتية واحدة"
        ),
    )

    parser.add_argument(
        "--autonomous-status",
        action=
            "store_true",

        help=(
            "Show autonomous runtime status / "
            "عرض حالة التشغيل الذاتي"
        ),
    )

    parser.add_argument(
        "--cycle-seconds",
        type=
            int,

        default=
            DEFAULT_CYCLE_SECONDS,

        help=(
            "Seconds between autonomous cycles / "
            "الثواني بين دورات التشغيل الذاتي"
        ),
    )

    args = (
        parser.parse_args()
    )

    if args.autonomous_status:
        print_result(
            get_autonomous_status()
        )

        return 0

    if args.once:
        result = (
            run_autonomous_once(
                owner=
                    args.owner,

                cycle_seconds=
                    args.cycle_seconds,
            )
        )

        print_result(
            result
        )

        return (
            0
            if result.get(
                "success"
            )
            else 1
        )

    if args.autonomous:
        return (
            run_autonomous_forever(
                owner=
                    args.owner,

                cycle_seconds=
                    args.cycle_seconds,
            )
        )

    command = " ".join(
        args.command
    ).strip()

    # إذا ما فيه أمر يبدأ التشغيل الذاتي تلقائيا.
    if not command:
        return (
            run_autonomous_forever(
                owner=
                    args.owner,

                cycle_seconds=
                    args.cycle_seconds,
            )
        )

    print(
        "=============================================="
    )

    print(
        "MAJD GAME FACTORY"
    )

    print(
        "SOVEREIGN FULL EXECUTION RUNTIME 06"
    )

    print(
        "المشغل السيادي الكامل لمجد"
    )

    print(
        "=============================================="
    )

    print(
        f"OWNER / المالك: {args.owner}"
    )

    print(
        f"COMMAND / الأمر: {command}"
    )

    print(
        f"PLATFORM / المنصة: "
        f"{OFFICIAL_MAJD_PLATFORM}"
    )

    print(
        "=============================================="
    )

    result = (
        execute_full_factory(
            command=
                command,

            owner=
                args.owner,
        )
    )

    print_result(
        result
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

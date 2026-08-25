#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-FULL-EXECUTION-RUNTIME-06.py
============================================================

MAJD SOVEREIGN AUTONOMOUS FULL EXECUTION RUNTIME
المشغّل السيادي الذاتي الكامل لمنصة مجد

هذا الملف هو بوابة التشغيل المركزية والدائمة لمنصة MAJD-GAME-FACTORY.

يدعم وضعين:

1) OWNER COMMAND MODE
   وضع أوامر المالك:
   - يحافظ على السلوك الحالي.
   - يستقبل أمر المالك بالعربية أو الإنجليزية.
   - يستخدم مركز أوامر المالك.
   - يمرر الأهداف التنفيذية إلى العقل المدبر 01.
   - يتحقق من النتائج الحقيقية وArtifact والنشر.

2) AUTONOMOUS PERSISTENT MODE
   وضع التشغيل الذاتي الدائم:
   - لا يحتاج أوامر يومية من المالك.
   - يراقب المنصة والشركة والخدمات باستمرار.
   - يكتشف الأعطال والنواقص تلقائياً.
   - يرسل أهداف الإصلاح والتنفيذ تلقائياً إلى العقل المدبر 01.
   - يعيد الفحص بعد الإصلاح.
   - لا يعلن النجاح أو OPERATIONAL بدون دليل حقيقي.
   - يحفظ الحالة والتدقيق والتقارير.
   - يستمر بعد فشل أي دورة منفردة.
   - يدعم الإغلاق الآمن.
   - يمكن تشغيله كخدمة دائمة.

السلسلة:
06 AUTONOMOUS RUNTIME
   ↓
01 MASTERMIND
   ↓
02 SOVEREIGN COMPANY / CAPABILITIES
   ↓
03 REAL GAME EXECUTOR
   ↓
04 OFFICIAL PLATFORM BRIDGE
   ↓
06 VERIFICATION / MONITORING / REPORTING

قاعدة أساسية:
06 لا يكرر مسؤوليات 01 أو 02 أو 03.
01 = العقل المدبر
02 = الشركة السيادية وقدراتها
03 = التنفيذ الحقيقي للألعاب
04 = الجسر الرسمي للنشر
06 = التشغيل الدائم والمراقبة والتحقق والتقارير

لغة المالك:
- العربية والإنجليزية مدعومتان.
- كل رسالة إدارية مهمة يمكن أن تحتوي message_ar و message_en.
- المعرفات التقنية الداخلية تبقى بالإنجليزية لثبات النظام.
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
BACKUP_DIR = STATE_DIR / "backups"

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
    BACKUP_DIR,
    OUTPUT_DIR,
    PUBLIC_DIR,
    ARTIFACTS_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)


# ============================================================
# IDENTITY
# ============================================================

SYSTEM_NAME = "MAJD-GAME-FACTORY"
RUNTIME_NAME = "MAJD-FULL-EXECUTION-RUNTIME"
VERSION = "3.1.0-AUTONOMOUS-BILINGUAL"
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

AUTONOMOUS_ENABLED_BY_DEFAULT = (
    os.getenv("MAJD_AUTONOMOUS_ENABLED", "true").strip().lower()
    in ("1", "true", "yes", "on")
)

STOP_REQUESTED = False


# ============================================================
# TIME / LANGUAGE
# ============================================================

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def bilingual(
    ar: str,
    en: str,
    **extra: Any,
) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "message_ar": ar,
        "message_en": en,
    }
    result.update(extra)
    return result


def status_message(status: str) -> Dict[str, str]:
    mapping = {
        "STARTING": (
            "جارٍ بدء التشغيل.",
            "Runtime is starting.",
        ),
        "VERIFYING_CORE": (
            "جارٍ التحقق من ملفات النظام الأساسية.",
            "Verifying core system files.",
        ),
        "OWNER_COMMAND_CENTER": (
            "جارٍ تشغيل مركز أوامر المالك.",
            "Running owner command center.",
        ),
        "MASTERMIND_EXECUTION": (
            "جارٍ تنفيذ المهمة عبر العقل المدبر.",
            "Executing task through the mastermind.",
        ),
        "FINAL_VERIFICATION": (
            "جارٍ التحقق النهائي من النتيجة.",
            "Performing final result verification.",
        ),
        "COMPLETED": (
            "اكتمل التنفيذ بنجاح.",
            "Execution completed successfully.",
        ),
        "PLATFORM_HEALTHY": (
            "المنصة تعمل بصورة طبيعية.",
            "The platform is operating normally.",
        ),
        "REPAIRED_AND_VERIFIED": (
            "تم إصلاح المشكلات والتحقق من النتيجة.",
            "Issues were repaired and the result was verified.",
        ),
        "DEGRADED_AFTER_REPAIR": (
            "بقيت مشكلات بعد محاولة الإصلاح.",
            "Some issues remain after the repair attempt.",
        ),
        "OWNER_ACTION_REQUIRED": (
            "يوجد إجراء خارجي أو حساس يحتاج المالك.",
            "An external or sensitive action requires the owner.",
        ),
        "AUTONOMOUS_CYCLE_EXCEPTION": (
            "حدث خطأ في دورة التشغيل الذاتي وسيستمر النظام في الدورة التالية.",
            "An autonomous cycle error occurred; the runtime will continue with the next cycle.",
        ),
    }

    ar, en = mapping.get(
        status,
        (f"الحالة: {status}", f"Status: {status}"),
    )

    return {
        "message_ar": ar,
        "message_en": en,
    }


# ============================================================
# SAFE HELPERS
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
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


# ============================================================
# JSON / AUDIT
# ============================================================

def save_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary = path.with_suffix(path.suffix + ".tmp")

    with temporary.open("w", encoding="utf-8") as file:
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
        with path.open("r", encoding="utf-8") as file:
            value = json.load(file)

        if isinstance(value, dict):
            return value
    except Exception:
        pass

    return dict(default)


def append_jsonl(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8") as file:
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

def load_module(path: Path, module_name: str) -> Any:
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


# ============================================================
# FUNCTION DISCOVERY / SAFE CALL
# ============================================================

def find_callable(
    module: Any,
    names: Iterable[str],
) -> Optional[Callable[..., Any]]:
    for name in names:
        value = getattr(module, name, None)
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
            "success": completed.returncode == 0,
            "command": command,
            "returncode": completed.returncode,
            "stdout": truncate_text(completed.stdout),
            "stderr": truncate_text(completed.stderr),
            "started_at": started,
            "finished_at": utc_now(),
        }

    except subprocess.TimeoutExpired as error:
        return {
            "success": False,
            "command": command,
            "status": "PROCESS_TIMEOUT",
            "error": safe_str(error),
            "started_at": started,
            "finished_at": utc_now(),
            **bilingual(
                "انتهت مهلة تنفيذ العملية.",
                "The process execution timed out.",
            ),
        }

    except Exception as error:
        return {
            "success": False,
            "command": command,
            "status": "PROCESS_EXCEPTION",
            "error": f"{type(error).__name__}: {error}",
            "started_at": started,
            "finished_at": utc_now(),
            **bilingual(
                "حدث خطأ أثناء تنفيذ العملية.",
                "An error occurred while executing the process.",
            ),
        }


# ============================================================
# REQUIRED FILE VERIFICATION
# ============================================================

def verify_required_files() -> Dict[str, Any]:
    required = {
        "01_mastermind": MASTERMIND_FILE,
        "02_owner_command_center": OWNER_COMMAND_CENTER_FILE,
        "03_real_game_executor": REAL_GAME_EXECUTOR_FILE,
        "04_official_platform_bridge": OFFICIAL_PLATFORM_BRIDGE_FILE,
    }

    optional_but_important = {
        "02_sovereign_company": SOVEREIGN_COMPANY_FILE,
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
            "exists": exists,
            "required": True,
            "size": path.stat().st_size if path.exists() else 0,
            "sha256": sha256_file(path) if exists else None,
        }

        if not exists:
            missing.append(path.name)

    for name, path in optional_but_important.items():
        exists = (
            path.exists()
            and path.is_file()
            and path.stat().st_size > 0
        )

        files[name] = {
            "file": path.name,
            "exists": exists,
            "required": False,
            "size": path.stat().st_size if path.exists() else 0,
            "sha256": sha256_file(path) if exists else None,
        }

    return {
        "success": not missing,
        "files": files,
        "missing": missing,
        **(
            bilingual(
                "جميع الملفات الأساسية المطلوبة موجودة.",
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
        "public",
        "majd_factory_state",
    }

    discovered: List[Path] = []

    for path in ROOT_DIR.rglob("*.py"):
        if any(part in ignored_parts for part in path.parts):
            continue

        if path.is_file():
            discovered.append(path)

    return sorted(discovered)


def verify_python_syntax(
    paths: Optional[List[Path]] = None,
) -> Dict[str, Any]:
    if paths is None:
        paths = discover_python_files()

    results: List[Dict[str, Any]] = []
    failed: List[str] = []

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
            display_path = str(path.relative_to(ROOT_DIR))
        except ValueError:
            display_path = str(path)

        item: Dict[str, Any] = {
            "file": display_path,
            "success": bool(process.get("success")),
        }

        if not item["success"]:
            item["error"] = (
                process.get("stderr")
                or process.get("error")
                or "PYTHON_SYNTAX_FAILED"
            )
            failed.append(item["file"])

        results.append(item)

    return {
        "success": not failed,
        "checked": len(results),
        "failed": failed,
        "results": results,
        **(
            bilingual(
                "جميع ملفات بايثون التي تم فحصها سليمة نحويًا.",
                "All checked Python files passed syntax validation.",
            )
            if not failed
            else bilingual(
                "توجد أخطاء Syntax في بعض ملفات بايثون.",
                "Some Python files contain syntax errors.",
            )
        ),
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
            "User-Agent": "MAJD-AUTONOMOUS-RUNTIME/3.1"
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=timeout,
        ) as response:
            body = response.read(
                1024 * 1024
            ).decode(
                "utf-8",
                errors="replace",
            )

            code = int(
                getattr(response, "status", 200)
            )

            success = 200 <= code < 400

            return {
                "success": success,
                "url": url,
                "status_code": code,
                "body": truncate_text(body, 4000),
                **(
                    bilingual(
                        "خدمة الويب متاحة.",
                        "Web service is reachable.",
                    )
                    if success
                    else bilingual(
                        "خدمة الويب أعادت حالة غير سليمة.",
                        "Web service returned an unhealthy status.",
                    )
                ),
            }

    except urllib.error.HTTPError as error:
        return {
            "success": False,
            "url": url,
            "status_code": error.code,
            "error": safe_str(error),
            **bilingual(
                "فشل فحص خدمة الويب.",
                "Web service health probe failed.",
            ),
        }

    except Exception as error:
        return {
            "success": False,
            "url": url,
            "status": "HTTP_PROBE_FAILED",
            "error": f"{type(error).__name__}: {error}",
            **bilingual(
                "تعذر الوصول إلى خدمة الويب.",
                "Unable to reach the web service.",
            ),
        }


# ============================================================
# DOCKER / DISK
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
            "status": "DOCKER_UNAVAILABLE_OR_FAILED",
            "details": process,
            **bilingual(
                "Docker غير متاح أو فشل فحصه.",
                "Docker is unavailable or its inspection failed.",
            ),
        }

    containers: List[Dict[str, Any]] = []

    for line in str(process.get("stdout", "")).splitlines():
        line = line.strip()

        if not line:
            continue

        parts = line.split("|", 2)

        containers.append(
            {
                "name": parts[0] if len(parts) > 0 else "",
                "status": parts[1] if len(parts) > 1 else "",
                "ports": parts[2] if len(parts) > 2 else "",
            }
        )

    names = {item["name"] for item in containers}

    expected = {
        "majd-ai-core",
        "majd-web-ui",
    }

    missing_expected = sorted(expected - names)
    success = not missing_expected

    return {
        "success": success,
        "containers": containers,
        "missing_expected": missing_expected,
        **(
            bilingual(
                "حاويات مجد الأساسية تعمل.",
                "Core MAJD containers are running.",
            )
            if success
            else bilingual(
                "بعض حاويات مجد الأساسية غير ظاهرة.",
                "Some core MAJD containers are missing.",
            )
        ),
    }


def inspect_disk() -> Dict[str, Any]:
    try:
        stat = os.statvfs(ROOT_DIR)

        total = stat.f_blocks * stat.f_frsize
        available = stat.f_bavail * stat.f_frsize
        used = total - available

        used_percent = (
            (used / total) * 100.0
            if total > 0
            else 0.0
        )

        healthy = used_percent < 90.0

        return {
            "success": healthy,
            "total_bytes": total,
            "used_bytes": used,
            "available_bytes": available,
            "used_percent": round(used_percent, 2),
            "threshold_percent": 90.0,
            **(
                bilingual(
                    "مساحة التخزين ضمن الحد الآمن.",
                    "Storage usage is within the safe threshold.",
                )
                if healthy
                else bilingual(
                    "استخدام مساحة التخزين تجاوز الحد الآمن.",
                    "Storage usage exceeded the safe threshold.",
                )
            ),
        }

    except Exception as error:
        return {
            "success": False,
            "status": "DISK_INSPECTION_FAILED",
            "error": f"{type(error).__name__}: {error}",
            **bilingual(
                "فشل فحص مساحة التخزين.",
                "Storage inspection failed.",
            ),
        }


# ============================================================
# OWNER COMMAND CENTER BRIDGE
# ============================================================

class OwnerCommandCenterRuntime:
    def __init__(self) -> None:
        self.module = load_module(
            OWNER_COMMAND_CENTER_FILE,
            "majd_owner_command_center_02_runtime",
        )

    def parse(self, command: str) -> Dict[str, Any]:
        parser_class = getattr(
            self.module,
            "OwnerCommandParser",
            None,
        )

        if parser_class is None:
            return {
                "type": "GENERAL_OWNER_COMMAND",
                "raw": command,
                "warning": "OWNER_COMMAND_PARSER_NOT_FOUND",
                **bilingual(
                    "لم يتم العثور على محلل أوامر المالك؛ سيتم تمرير الأمر كهدف عام.",
                    "Owner command parser was not found; the command will be forwarded as a general objective.",
                ),
            }

        try:
            parser = parser_class()
            result = parser.parse(command)

            if not isinstance(result, dict):
                return {
                    "type": "GENERAL_OWNER_COMMAND",
                    "raw": command,
                    "warning": "INVALID_PARSE_RESULT",
                    **bilingual(
                        "نتيجة تحليل الأمر غير صالحة؛ سيتم تمرير الأمر كهدف عام.",
                        "Command parsing result was invalid; the command will be forwarded as a general objective.",
                    ),
                }

            result_type = str(
                result.get("type", "")
            ).upper()

            if not result_type or result_type == "UNKNOWN":
                result["type"] = "GENERAL_OWNER_COMMAND"

            return result

        except Exception as error:
            return {
                "type": "GENERAL_OWNER_COMMAND",
                "raw": command,
                "parser_error": (
                    f"{type(error).__name__}: {error}"
                ),
                **bilingual(
                    "حدث خطأ أثناء تحليل أمر المالك؛ سيتم تمريره كهدف عام.",
                    "An error occurred while parsing the owner command; it will be forwarded as a general objective.",
                ),
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
                "status": "OWNER_COMMAND_INTERFACE_MISSING",
                **bilingual(
                    "واجهة تنفيذ أوامر المالك غير موجودة.",
                    "Owner command execution interface is missing.",
                ),
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
                "status": "OWNER_COMMAND_EXECUTION_EXCEPTION",
                "error": (
                    f"{type(error).__name__}: {error}"
                ),
                "traceback": traceback.format_exc(),
                **bilingual(
                    "حدث خطأ أثناء تنفيذ أمر المالك.",
                    "An error occurred while executing the owner command.",
                ),
            }

        if not isinstance(result, dict):
            return {
                "success": False,
                "status": "INVALID_OWNER_COMMAND_RESULT",
                "result_type": type(result).__name__,
                **bilingual(
                    "نتيجة مركز أوامر المالك غير صالحة.",
                    "Owner command center returned an invalid result.",
                ),
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
                    "status": "MASTERMIND_INTERFACE_NOT_FOUND",
                    "file": MASTERMIND_FILE.name,
                    **bilingual(
                        "لم يتم العثور على واجهة تشغيل للعقل المدبر.",
                        "No execution interface was found for the mastermind.",
                    ),
                }

            try:
                instance = call_supported(
                    mastermind_class,
                    {"owner": owner},
                )

            except Exception as error:
                return {
                    "success": False,
                    "status": "MASTERMIND_INITIALIZATION_FAILED",
                    "error": (
                        f"{type(error).__name__}: {error}"
                    ),
                    "traceback": traceback.format_exc(),
                    **bilingual(
                        "فشل تشغيل العقل المدبر.",
                        "Mastermind initialization failed.",
                    ),
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
                    "status": "MASTERMIND_RUN_INTERFACE_MISSING",
                    **bilingual(
                        "لم يتم العثور على دالة تشغيل للعقل المدبر.",
                        "Mastermind run interface is missing.",
                    ),
                }

        try:
            result = call_supported(
                function,
                {
                    "command": command,
                    "request": request,
                    "payload": request,
                    "job_id": runtime_id,
                    "runtime_id": runtime_id,
                    "owner": owner,
                    "output_root": str(OUTPUT_DIR),
                },
            )

        except Exception as error:
            return {
                "success": False,
                "status": "MASTERMIND_EXECUTION_EXCEPTION",
                "error": (
                    f"{type(error).__name__}: {error}"
                ),
                "traceback": traceback.format_exc(),
                **bilingual(
                    "حدث خطأ أثناء تنفيذ مهمة العقل المدبر.",
                    "An error occurred while executing the mastermind task.",
                ),
            }

        if not isinstance(result, dict):
            return {
                "success": False,
                "status": "INVALID_MASTERMIND_RESULT",
                "result_type": type(result).__name__,
                **bilingual(
                    "أعاد العقل المدبر نتيجة غير صالحة.",
                    "Mastermind returned an invalid result.",
                ),
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

    def inspect(self) -> Dict[str, Any]:
        if not self.available:
            return {
                "success": False,
                "status": "SOVEREIGN_COMPANY_FILE_MISSING",
                "file": SOVEREIGN_COMPANY_FILE.name,
                **bilingual(
                    "ملف الشركة السيادية غير موجود.",
                    "Sovereign company file is missing.",
                ),
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
                        "owner": DEFAULT_OWNER,
                        "root_dir": str(ROOT_DIR),
                    },
                )

                if isinstance(result, dict):
                    return {
                        "success": True,
                        "status": "SOVEREIGN_COMPANY_INSPECTED",
                        "source": getattr(
                            function,
                            "__name__",
                            "unknown",
                        ),
                        "company": result,
                        **bilingual(
                            "تم فحص الشركة السيادية.",
                            "Sovereign company was inspected.",
                        ),
                    }

            except Exception as error:
                return {
                    "success": False,
                    "status": "SOVEREIGN_COMPANY_INSPECTION_FAILED",
                    "error": (
                        f"{type(error).__name__}: {error}"
                    ),
                    **bilingual(
                        "فشل فحص الشركة السيادية.",
                        "Sovereign company inspection failed.",
                    ),
                }

        public_names = [
            name
            for name in dir(self.module)
            if not name.startswith("_")
        ]

        return {
            "success": True,
            "status": "SOVEREIGN_COMPANY_MODULE_LOADED",
            "file": SOVEREIGN_COMPANY_FILE.name,
            "public_symbols": public_names[:250],
            "warning": "NO_STANDARD_COMPANY_STATUS_INTERFACE",
            **bilingual(
                "تم تحميل الشركة السيادية لكن لم توجد واجهة حالة قياسية.",
                "Sovereign company loaded, but no standard status interface was found.",
            ),
        }


# ============================================================
# PLAYABLE ARTIFACT VERIFIER
# ============================================================

def verify_playable_artifact(
    artifact_value: Any,
) -> Dict[str, Any]:
    if not artifact_value:
        return {
            "success": False,
            "status": "PLAYABLE_ARTIFACT_MISSING",
            **bilingual(
                "Artifact القابل للعب غير موجود.",
                "Playable artifact is missing.",
            ),
        }

    artifact = Path(str(artifact_value))

    if not artifact.is_absolute():
        artifact = (ROOT_DIR / artifact).resolve()
    else:
        artifact = artifact.resolve()

    if not artifact.exists():
        return {
            "success": False,
            "status": "PLAYABLE_ARTIFACT_NOT_FOUND",
            "artifact": str(artifact),
            **bilingual(
                "لم يتم العثور على Artifact القابل للعب.",
                "Playable artifact was not found.",
            ),
        }

    if not artifact.is_dir():
        return {
            "success": False,
            "status": "PLAYABLE_ARTIFACT_NOT_DIRECTORY",
            "artifact": str(artifact),
            **bilingual(
                "مسار Artifact ليس مجلدًا.",
                "Artifact path is not a directory.",
            ),
        }

    index_file = artifact / "index.html"

    if not index_file.exists():
        return {
            "success": False,
            "status": "PLAYABLE_INDEX_NOT_FOUND",
            "artifact": str(artifact),
            **bilingual(
                "ملف index.html غير موجود داخل Artifact.",
                "index.html is missing from the artifact.",
            ),
        }

    if index_file.stat().st_size <= 0:
        return {
            "success": False,
            "status": "PLAYABLE_INDEX_EMPTY",
            "artifact": str(artifact),
            **bilingual(
                "ملف index.html فارغ.",
                "index.html is empty.",
            ),
        }

    files = [
        path
        for path in artifact.rglob("*")
        if path.is_file()
    ]

    javascript_files = [
        path
        for path in files
        if path.suffix.lower() in (".js", ".mjs")
    ]

    if not javascript_files:
        return {
            "success": False,
            "status": "PLAYABLE_JAVASCRIPT_NOT_FOUND",
            "artifact": str(artifact),
            **bilingual(
                "لم يتم العثور على JavaScript داخل اللعبة.",
                "No JavaScript files were found in the playable artifact.",
            ),
        }

    return {
        "success": True,
        "status": "PLAYABLE_ARTIFACT_VERIFIED",
        "artifact": str(artifact),
        "index": str(index_file),
        "file_count": len(files),
        **bilingual(
            "تم التحقق من Artifact القابل للعب.",
            "Playable artifact was verified.",
        ),
    }


# ============================================================
# PUBLISHED ARTIFACT VERIFIER
# ============================================================

def verify_published_result(
    platform_result: Dict[str, Any],
) -> Dict[str, Any]:
    if not isinstance(platform_result, dict):
        return {
            "success": False,
            "status": "PLATFORM_RESULT_INVALID",
            **bilingual(
                "نتيجة النشر غير صالحة.",
                "Publication result is invalid.",
            ),
        }

    if not platform_result.get("success"):
        return {
            "success": False,
            "status": platform_result.get(
                "status",
                "PLATFORM_NOT_SUCCESSFUL",
            ),
            "platform": platform_result,
            **bilingual(
                "منصة النشر لم تعد نتيجة ناجحة.",
                "Publication platform did not return a successful result.",
            ),
        }

    published_directory = platform_result.get(
        "published_directory"
    )

    if not published_directory:
        return {
            "success": False,
            "status": "PUBLISHED_DIRECTORY_MISSING",
            "platform": platform_result,
            **bilingual(
                "مجلد النسخة المنشورة غير محدد.",
                "Published directory is missing.",
            ),
        }

    published_path = Path(str(published_directory))

    if not published_path.is_absolute():
        published_path = (
            ROOT_DIR / published_path
        ).resolve()
    else:
        published_path = published_path.resolve()

    if not published_path.exists():
        return {
            "success": False,
            "status": "PUBLISHED_DIRECTORY_NOT_FOUND",
            "published_directory": str(published_path),
            **bilingual(
                "مجلد النسخة المنشورة غير موجود.",
                "Published directory does not exist.",
            ),
        }

    index_file = published_path / "index.html"

    if not index_file.exists():
        return {
            "success": False,
            "status": "PUBLISHED_INDEX_NOT_FOUND",
            "published_directory": str(published_path),
            **bilingual(
                "ملف index.html غير موجود في النسخة المنشورة.",
                "index.html is missing from the published build.",
            ),
        }

    public_url = platform_result.get("public_url")
    game_path = platform_result.get("game_path")

    if not public_url:
        return {
            "success": False,
            "status": "PUBLIC_URL_MISSING",
            **bilingual(
                "الرابط العام غير موجود.",
                "Public URL is missing.",
            ),
        }

    if not game_path:
        return {
            "success": False,
            "status": "GAME_PATH_MISSING",
            **bilingual(
                "مسار اللعبة المنشورة غير موجود.",
                "Published game path is missing.",
            ),
        }

    return {
        "success": True,
        "status": "PUBLISHED_RESULT_VERIFIED",
        "published_directory": str(published_path),
        "index": str(index_file),
        "game_path": game_path,
        "public_url": public_url,
        **bilingual(
            "تم التحقق من النسخة المنشورة.",
            "Published result was verified.",
        ),
    }


# ============================================================
# FINAL MASTERMIND RESULT VERIFICATION
# ============================================================

def verify_mastermind_result(
    command_type: str,
    result: Dict[str, Any],
) -> Dict[str, Any]:
    if not isinstance(result, dict):
        return {
            "success": False,
            "status": "INVALID_FINAL_RESULT",
            **bilingual(
                "النتيجة النهائية غير صالحة.",
                "Final result is invalid.",
            ),
        }

    if not result.get("success"):
        return {
            "success": False,
            "status": result.get(
                "status",
                "MASTERMIND_FAILED",
            ),
            "result": result,
            **bilingual(
                "العقل المدبر لم يعد نتيجة ناجحة.",
                "Mastermind did not return a successful result.",
            ),
        }

    if command_type != "CREATE_GAME":
        return {
            "success": True,
            "status": "MASTERMIND_RESULT_VERIFIED",
            "result": result,
            **bilingual(
                "تم التحقق من نتيجة العقل المدبر.",
                "Mastermind result was verified.",
            ),
        }

    artifact_verification = verify_playable_artifact(
        result.get("artifact")
    )

    if not artifact_verification.get("success"):
        return {
            "success": False,
            "status": artifact_verification.get(
                "status",
                "ARTIFACT_FINAL_VERIFICATION_FAILED",
            ),
            "artifact_verification": artifact_verification,
            "mastermind_result": result,
            **bilingual(
                "فشل التحقق النهائي من Artifact.",
                "Final artifact verification failed.",
            ),
        }

    platform_result = result.get("platform")

    if not isinstance(platform_result, dict):
        return {
            "success": False,
            "status": "PLATFORM_RESULT_MISSING",
            "artifact_verification": artifact_verification,
            "mastermind_result": result,
            **bilingual(
                "نتيجة منصة النشر غير موجودة.",
                "Publication platform result is missing.",
            ),
        }

    publication_verification = verify_published_result(
        platform_result
    )

    if not publication_verification.get("success"):
        return {
            "success": False,
            "status": publication_verification.get(
                "status",
                "PUBLICATION_FINAL_VERIFICATION_FAILED",
            ),
            "artifact_verification": artifact_verification,
            "publication_verification": publication_verification,
            "mastermind_result": result,
            **bilingual(
                "فشل التحقق النهائي من النشر.",
                "Final publication verification failed.",
            ),
        }

    return {
        "success": True,
        "status": "FULL_EXECUTION_VERIFIED",
        "artifact": artifact_verification,
        "publication": publication_verification,
        "result": result,
        **bilingual(
            "تم التحقق من التنفيذ الكامل بنجاح.",
            "Full execution was verified successfully.",
        ),
    }


# ============================================================
# OWNER COMMAND RUNTIME
# ============================================================

class MajdFullExecutionRuntime:
    def __init__(self) -> None:
        self.runtime_id = str(uuid.uuid4())

    def state_path(self) -> Path:
        return RUNTIME_DIR / f"{self.runtime_id}.json"

    def save(self, state: Dict[str, Any]) -> None:
        state["updated_at"] = utc_now()
        save_json(self.state_path(), state)

    def execute(
        self,
        command: str,
        owner: str = DEFAULT_OWNER,
    ) -> Dict[str, Any]:
        command = str(command or "").strip()

        state: Dict[str, Any] = {
            "runtime_id": self.runtime_id,
            "system": SYSTEM_NAME,
            "runtime": RUNTIME_NAME,
            "version": VERSION,
            "owner": owner,
            "command": command,
            "official_platform": OFFICIAL_MAJD_PLATFORM,
            "started_at": utc_now(),
            "updated_at": utc_now(),
            "finished_at": None,
            "success": False,
            "status": "STARTING",
            "stages": {},
            **status_message("STARTING"),
        }

        self.save(state)

        try:
            if not command:
                state["status"] = "EMPTY_OWNER_COMMAND"
                state["error"] = "Owner command cannot be empty."
                state.update(
                    bilingual(
                        "أمر المالك لا يمكن أن يكون فارغًا.",
                        "Owner command cannot be empty.",
                    )
                )
                state["finished_at"] = utc_now()
                self.save(state)
                return state

            state["status"] = "VERIFYING_CORE"
            state.update(status_message("VERIFYING_CORE"))
            self.save(state)

            files_result = verify_required_files()
            state["stages"]["core_files"] = files_result

            if not files_result.get("success"):
                state["status"] = "REQUIRED_FILES_MISSING"
                state["error"] = "REQUIRED_FILES_MISSING"
                state.update(
                    bilingual(
                        "توجد ملفات أساسية مفقودة، لذلك تم إيقاف التنفيذ.",
                        "Required core files are missing, so execution was stopped.",
                    )
                )
                state["finished_at"] = utc_now()
                self.save(state)
                return state

            state["status"] = "OWNER_COMMAND_CENTER"
            state.update(status_message("OWNER_COMMAND_CENTER"))
            self.save(state)

            owner_runtime = OwnerCommandCenterRuntime()
            parsed_request = owner_runtime.parse(command)

            command_type = str(
                parsed_request.get(
                    "type",
                    "GENERAL_OWNER_COMMAND",
                )
            ).upper()

            if not command_type or command_type == "UNKNOWN":
                command_type = "GENERAL_OWNER_COMMAND"
                parsed_request["type"] = command_type

            state["stages"]["command"] = {
                "success": True,
                "status": "OWNER_COMMAND_PARSED",
                "type": command_type,
                "request": parsed_request,
                **bilingual(
                    "تم تحليل أمر المالك.",
                    "Owner command was parsed.",
                ),
            }
            self.save(state)

            if command_type in (
                "STATUS",
                "SYSTEM_STATUS",
            ):
                state["status"] = "OWNER_STATUS_EXECUTION"
                state.update(
                    bilingual(
                        "جارٍ تنفيذ طلب حالة النظام.",
                        "Executing system status request.",
                    )
                )
                self.save(state)

                result = owner_runtime.execute(
                    command=command,
                    owner=owner,
                )

                state["stages"]["owner_status"] = result
                state["result"] = result
                state["success"] = bool(
                    result.get("success", False)
                )

                state["status"] = str(
                    result.get("status")
                    or (
                        "COMPLETED"
                        if state["success"]
                        else "FAILED"
                    )
                )

                if not state["success"]:
                    state["error"] = (
                        result.get("error")
                        or result.get("message")
                        or state["status"]
                    )

                state["finished_at"] = utc_now()
                self.save(state)
                return state

            state["status"] = "MASTERMIND_EXECUTION"
            state.update(
                status_message("MASTERMIND_EXECUTION")
            )
            self.save(state)

            mastermind = MastermindRuntime()

            mastermind_result = mastermind.execute(
                command=command,
                request=parsed_request,
                runtime_id=self.runtime_id,
                owner=owner,
            )

            state["stages"]["mastermind"] = mastermind_result
            self.save(state)

            if not mastermind_result.get("success"):
                state["success"] = False
                state["status"] = str(
                    mastermind_result.get(
                        "status",
                        "MASTERMIND_FAILED",
                    )
                )
                state["error"] = (
                    mastermind_result.get("error")
                    or mastermind_result.get("message")
                    or state["status"]
                )
                state["result"] = mastermind_result
                state.update(
                    bilingual(
                        "فشل تنفيذ المهمة عبر العقل المدبر.",
                        "Task execution through the mastermind failed.",
                    )
                )
                state["finished_at"] = utc_now()
                self.save(state)
                return state

            state["status"] = "FINAL_VERIFICATION"
            state.update(
                status_message("FINAL_VERIFICATION")
            )
            self.save(state)

            final_verification = verify_mastermind_result(
                command_type=command_type,
                result=mastermind_result,
            )

            state["stages"]["final_verification"] = (
                final_verification
            )
            self.save(state)

            if not final_verification.get("success"):
                state["success"] = False
                state["status"] = str(
                    final_verification.get(
                        "status",
                        "FINAL_VERIFICATION_FAILED",
                    )
                )
                state["error"] = state["status"]
                state["result"] = mastermind_result
                state.update(
                    bilingual(
                        "فشل التحقق النهائي من نتيجة التنفيذ.",
                        "Final execution verification failed.",
                    )
                )
                state["finished_at"] = utc_now()
                self.save(state)
                return state

            state["success"] = True
            state["status"] = "COMPLETED"
            state["result"] = mastermind_result
            state["verification"] = final_verification

            if command_type == "CREATE_GAME":
                publication = final_verification.get(
                    "publication",
                    {},
                )
                artifact = final_verification.get(
                    "artifact",
                    {},
                )

                state["artifact"] = artifact.get("artifact")
                state["game_path"] = publication.get("game_path")
                state["public_url"] = publication.get("public_url")
                state["published"] = True

                state.update(
                    bilingual(
                        "تم تنفيذ أمر إنشاء اللعبة عبر العقل المدبر، وبناء اللعبة والتحقق من Artifact والنسخة المنشورة فعليًا.",
                        "The game creation command was executed through the mastermind, and the game, artifact, and published build were verified.",
                    )
                )
            else:
                state.update(
                    bilingual(
                        "تم تنفيذ أمر المالك عبر العقل المدبر وتم التحقق من النتيجة.",
                        "The owner command was executed through the mastermind and the result was verified.",
                    )
                )

            state["finished_at"] = utc_now()
            self.save(state)
            return state

        except Exception as error:
            state["success"] = False
            state["status"] = "RUNTIME_EXCEPTION"
            state["error"] = (
                f"{type(error).__name__}: {error}"
            )
            state["traceback"] = traceback.format_exc()
            state.update(
                bilingual(
                    "حدث خطأ غير متوقع في Runtime.",
                    "An unexpected runtime error occurred.",
                )
            )
            state["finished_at"] = utc_now()
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
        "id": finding_id,
        "severity": severity.upper(),
        "component": component,
        "status": status,
        "message_ar": message_ar,
        "message_en": message_en,
        "repairable": bool(repairable),
        "owner_required": bool(owner_required),
        "evidence": evidence or {},
        "detected_at": utc_now(),
    }


def derive_findings(
    inspection: Dict[str, Any],
) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []

    core = inspection.get("core_files", {})
    if not core.get("success"):
        findings.append(
            finding(
                "CORE_FILES_MISSING",
                "CRITICAL",
                "CORE",
                "FAILED",
                "ملفات أساسية مطلوبة مفقودة أو فارغة.",
                "Required core files are missing or empty.",
                repairable=True,
                evidence=core,
            )
        )

    syntax = inspection.get("python_syntax", {})
    if not syntax.get("success"):
        findings.append(
            finding(
                "PYTHON_SYNTAX_FAILURE",
                "CRITICAL",
                "SOURCE_CODE",
                "FAILED",
                "يوجد خطأ Syntax في ملف بايثون واحد أو أكثر.",
                "One or more Python files contain syntax errors.",
                repairable=True,
                evidence=syntax,
            )
        )

    local_api = inspection.get("local_api", {})
    if not local_api.get("success"):
        findings.append(
            finding(
                "LOCAL_API_UNHEALTHY",
                "HIGH",
                "MAJD_AI_CORE",
                "DEGRADED",
                "فشل فحص صحة API المحلي لمجد.",
                "Local MAJD API health probe failed.",
                repairable=True,
                evidence=local_api,
            )
        )

    official = inspection.get("official_platform", {})
    if not official.get("success"):
        findings.append(
            finding(
                "OFFICIAL_PLATFORM_UNREACHABLE",
                "CRITICAL",
                "PUBLIC_PLATFORM",
                "FAILED",
                "تعذر الوصول إلى منصة مجد الرسمية.",
                "Official MAJD platform is unreachable.",
                repairable=True,
                evidence=official,
            )
        )

    docker = inspection.get("docker", {})
    if not docker.get("success"):
        findings.append(
            finding(
                "DOCKER_SERVICES_DEGRADED",
                "HIGH",
                "DOCKER",
                "DEGRADED",
                "بعض خدمات Docker الأساسية لمجد غير سليمة.",
                "Some core MAJD Docker services are unhealthy.",
                repairable=True,
                evidence=docker,
            )
        )

    disk = inspection.get("disk", {})
    if not disk.get("success"):
        findings.append(
            finding(
                "DISK_CAPACITY_RISK",
                "HIGH",
                "SERVER_STORAGE",
                "DEGRADED",
                "مساحة تخزين السيرفر تحتاج معالجة.",
                "Server storage requires attention.",
                repairable=True,
                evidence=disk,
            )
        )

    company = inspection.get("sovereign_company", {})
    if not company.get("success"):
        findings.append(
            finding(
                "SOVEREIGN_COMPANY_UNAVAILABLE",
                "HIGH",
                "SOVEREIGN_COMPANY",
                "UNAVAILABLE",
                "تعذر فحص الشركة السيادية 02.",
                "Unable to inspect Sovereign Company 02.",
                repairable=True,
                evidence=company,
            )
        )

    return findings


# ============================================================
# AUTONOMOUS OBJECTIVE
# ============================================================

def build_autonomous_objective(
    cycle_id: str,
    findings: List[Dict[str, Any]],
) -> Tuple[str, Dict[str, Any]]:
    compact_findings = [
        {
            "id": item.get("id"),
            "severity": item.get("severity"),
            "component": item.get("component"),
            "status": item.get("status"),
            "message_ar": item.get("message_ar"),
            "message_en": item.get("message_en"),
            "owner_required": item.get(
                "owner_required",
                False,
            ),
        }
        for item in findings
    ]

    request = {
        "type": "AUTONOMOUS_PLATFORM_MAINTENANCE",
        "source": RUNTIME_NAME,
        "cycle_id": cycle_id,
        "owner": DEFAULT_OWNER,
        "autonomous": True,
        "language": {
            "owner_reports": ["ar", "en"],
            "primary": "ar",
            "secondary": "en",
        },
        "findings": compact_findings,
        "policy": {
            "routine_owner_approval_required": False,
            "preserve_working_features": True,
            "prefer_existing_components": True,
            "allow_code_generation": True,
            "allow_code_repair": True,
            "allow_integration": True,
            "allow_testing": True,
            "allow_routine_service_recovery": True,
            "require_real_verification": True,
            "never_fake_operational": True,
            "rollback_on_failed_change": True,
            "protect_owner_authority": True,
            "protect_secrets": True,
            "owner_reports_bilingual": True,
        },
    }

    command = (
        "MAJD AUTONOMOUS PLATFORM MAINTENANCE / "
        "صيانة منصة مجد الذاتية. "
        "Inspect the supplied findings and repair all routine "
        "technical problems that can be repaired safely without "
        "owner interaction. Use existing MAJD components first. "
        "If code is missing or defective, create or repair it. "
        "Preserve working functionality. Test every change. "
        "Do not report success without real evidence. "
        "Never mark a capability OPERATIONAL unless its real "
        "adapter, engine, or service exists and passes verification. "
        "Protect OWNER authority and secrets. "
        "Return a structured result with Arabic and English owner messages. "
        "افحص المشاكل المرسلة وأصلح المشاكل التشغيلية الروتينية "
        "دون إزعاج المالك، واستخدم مكونات مجد الموجودة أولاً، "
        "وأنشئ أو أصلح الكود عند الحاجة، واختبر كل تغيير، "
        "ولا تعتبر أي قدرة تشغيلية بدون تحقق حقيقي، "
        "واحفظ سلطة المالك والأسرار، وأعد تقريراً عربياً وإنجليزياً."
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
            int(cycle_seconds),
        )
        self.session_id = str(uuid.uuid4())
        self.started_at = utc_now()

        previous = load_json(
            AUTONOMOUS_STATE_FILE,
            {},
        )

        self.total_cycles = int(
            previous.get("total_cycles", 0) or 0
        )
        self.successful_cycles = int(
            previous.get("successful_cycles", 0) or 0
        )
        self.failed_cycles = int(
            previous.get("failed_cycles", 0) or 0
        )
        self.repair_cycles = int(
            previous.get("repair_cycles", 0) or 0
        )

    def audit(
        self,
        event: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        append_jsonl(
            AUTONOMOUS_AUDIT_FILE,
            {
                "time": utc_now(),
                "system": SYSTEM_NAME,
                "runtime": RUNTIME_NAME,
                "version": VERSION,
                "session_id": self.session_id,
                "event": event,
                "data": data or {},
            },
        )

    def save_state(
        self,
        status: str,
        cycle: Optional[Dict[str, Any]] = None,
    ) -> None:
        state = {
            "system": SYSTEM_NAME,
            "runtime": RUNTIME_NAME,
            "version": VERSION,
            "mode": "AUTONOMOUS_PERSISTENT",
            "enabled": True,
            "owner": self.owner,
            "owner_language": {
                "primary": "ar",
                "secondary": "en",
            },
            "session_id": self.session_id,
            "pid": os.getpid(),
            "status": status,
            **status_message(status),
            "started_at": self.started_at,
            "updated_at": utc_now(),
            "cycle_seconds": self.cycle_seconds,
            "total_cycles": self.total_cycles,
            "successful_cycles": self.successful_cycles,
            "failed_cycles": self.failed_cycles,
            "repair_cycles": self.repair_cycles,
            "last_cycle": cycle,
        }

        save_json(
            AUTONOMOUS_STATE_FILE,
            state,
        )

    def inspect_platform(self) -> Dict[str, Any]:
        inspection: Dict[str, Any] = {
            "time": utc_now(),
        }

        inspection["core_files"] = verify_required_files()
        inspection["python_syntax"] = verify_python_syntax()
        inspection["local_api"] = http_probe(
            LOCAL_API_HEALTH_URL
        )
        inspection["official_platform"] = http_probe(
            OFFICIAL_MAJD_PLATFORM
        )
        inspection["docker"] = inspect_docker()
        inspection["disk"] = inspect_disk()

        try:
            company_runtime = SovereignCompanyRuntime()
            inspection["sovereign_company"] = (
                company_runtime.inspect()
            )
        except Exception as error:
            inspection["sovereign_company"] = {
                "success": False,
                "status": "SOVEREIGN_COMPANY_EXCEPTION",
                "error": (
                    f"{type(error).__name__}: {error}"
                ),
                **bilingual(
                    "حدث خطأ أثناء فحص الشركة السيادية.",
                    "An error occurred while inspecting the sovereign company.",
                ),
            }

        return inspection

    def repair(
        self,
        cycle_id: str,
        findings: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        owner_blockers = [
            item
            for item in findings
            if item.get("owner_required")
        ]

        repairable = [
            item
            for item in findings
            if item.get("repairable", True)
            and not item.get(
                "owner_required",
                False,
            )
        ]

        if not repairable:
            return {
                "success": not owner_blockers,
                "status": (
                    "OWNER_ACTION_REQUIRED"
                    if owner_blockers
                    else "NO_AUTONOMOUS_REPAIR_REQUIRED"
                ),
                "owner_blockers": owner_blockers,
                **(
                    status_message("OWNER_ACTION_REQUIRED")
                    if owner_blockers
                    else bilingual(
                        "لا توجد إصلاحات تلقائية مطلوبة.",
                        "No autonomous repairs are required.",
                    )
                ),
            }

        command, request = build_autonomous_objective(
            cycle_id=cycle_id,
            findings=repairable,
        )

        attempts: List[Dict[str, Any]] = []

        for attempt in range(
            1,
            MAX_AUTONOMOUS_REPAIR_ATTEMPTS + 1,
        ):
            runtime_id = (
                f"AUTO-{cycle_id}-{attempt}"
            )

            try:
                mastermind = MastermindRuntime()
                result = mastermind.execute(
                    command=command,
                    request=request,
                    runtime_id=runtime_id,
                    owner=self.owner,
                )
            except Exception as error:
                result = {
                    "success": False,
                    "status": "AUTONOMOUS_MASTERMIND_EXCEPTION",
                    "error": (
                        f"{type(error).__name__}: {error}"
                    ),
                    "traceback": traceback.format_exc(),
                    **bilingual(
                        "حدث خطأ أثناء الإصلاح الذاتي عبر العقل المدبر.",
                        "An error occurred during autonomous repair through the mastermind.",
                    ),
                }

            attempts.append(
                {
                    "attempt": attempt,
                    "runtime_id": runtime_id,
                    "result": result,
                }
            )

            self.audit(
                "AUTONOMOUS_REPAIR_ATTEMPT",
                {
                    "cycle_id": cycle_id,
                    "attempt": attempt,
                    "success": bool(
                        result.get("success")
                    ),
                    "status": result.get("status"),
                },
            )

            if result.get("success"):
                return {
                    "success": True,
                    "status": "MASTERMIND_REPAIR_EXECUTED",
                    "attempts": attempts,
                    "result": result,
                    "owner_blockers": owner_blockers,
                    **bilingual(
                        "نفذ العقل المدبر محاولة إصلاح ناجحة.",
                        "Mastermind completed a successful repair attempt.",
                    ),
                }

            if attempt < MAX_AUTONOMOUS_REPAIR_ATTEMPTS:
                time.sleep(2)

        return {
            "success": False,
            "status": "AUTONOMOUS_REPAIR_FAILED",
            "attempts": attempts,
            "owner_blockers": owner_blockers,
            **bilingual(
                "فشلت محاولات الإصلاح الذاتي في هذه الدورة.",
                "Autonomous repair attempts failed in this cycle.",
            ),
        }

    def run_cycle(self) -> Dict[str, Any]:
        cycle_id = str(uuid.uuid4())

        self.total_cycles += 1

        cycle: Dict[str, Any] = {
            "cycle_id": cycle_id,
            "started_at": utc_now(),
            "finished_at": None,
            "success": False,
            "status": "INSPECTING",
            **bilingual(
                "جارٍ فحص المنصة.",
                "Inspecting the platform.",
            ),
            "inspection": {},
            "findings": [],
            "repair": None,
            "verification": None,
        }

        self.audit(
            "CYCLE_STARTED",
            {"cycle_id": cycle_id},
        )

        try:
            inspection = self.inspect_platform()
            cycle["inspection"] = inspection

            findings = derive_findings(
                inspection
            )
            cycle["findings"] = findings

            if not findings:
                cycle["success"] = True
                cycle["status"] = "PLATFORM_HEALTHY"
                cycle.update(
                    status_message("PLATFORM_HEALTHY")
                )
                self.successful_cycles += 1
                cycle["finished_at"] = utc_now()

                self.save_state(
                    "RUNNING_HEALTHY",
                    cycle,
                )

                save_json(
                    AUTONOMOUS_LATEST_REPORT,
                    cycle,
                )

                self.audit(
                    "CYCLE_HEALTHY",
                    {"cycle_id": cycle_id},
                )

                return cycle

            cycle["status"] = "ISSUES_DETECTED"
            cycle.update(
                bilingual(
                    "اكتشف النظام مشكلات وسيبدأ الإصلاح الذاتي.",
                    "The runtime detected issues and will start autonomous repair.",
                )
            )

            self.repair_cycles += 1

            repair_result = self.repair(
                cycle_id=cycle_id,
                findings=findings,
            )

            cycle["repair"] = repair_result

            verification = self.inspect_platform()
            cycle["verification"] = verification

            remaining = derive_findings(
                verification
            )

            cycle["remaining_findings"] = remaining

            if not remaining:
                cycle["success"] = True
                cycle["status"] = "REPAIRED_AND_VERIFIED"
                cycle.update(
                    status_message(
                        "REPAIRED_AND_VERIFIED"
                    )
                )
                self.successful_cycles += 1
            else:
                owner_required = [
                    item
                    for item in remaining
                    if item.get("owner_required")
                ]

                if (
                    owner_required
                    and len(owner_required)
                    == len(remaining)
                ):
                    cycle["success"] = True
                    cycle["status"] = "OWNER_ACTION_REQUIRED"
                    cycle.update(
                        status_message(
                            "OWNER_ACTION_REQUIRED"
                        )
                    )
                    self.successful_cycles += 1
                else:
                    cycle["success"] = False
                    cycle["status"] = "DEGRADED_AFTER_REPAIR"
                    cycle.update(
                        status_message(
                            "DEGRADED_AFTER_REPAIR"
                        )
                    )
                    self.failed_cycles += 1

            cycle["finished_at"] = utc_now()

            self.save_state(
                (
                    "RUNNING_HEALTHY"
                    if cycle["success"]
                    else "RUNNING_DEGRADED"
                ),
                cycle,
            )

            save_json(
                AUTONOMOUS_LATEST_REPORT,
                cycle,
            )

            return cycle

        except Exception as error:
            self.failed_cycles += 1

            cycle["success"] = False
            cycle["status"] = "AUTONOMOUS_CYCLE_EXCEPTION"
            cycle["error"] = (
                f"{type(error).__name__}: {error}"
            )
            cycle["traceback"] = traceback.format_exc()
            cycle.update(
                status_message(
                    "AUTONOMOUS_CYCLE_EXCEPTION"
                )
            )
            cycle["finished_at"] = utc_now()

            self.save_state(
                "RUNNING_DEGRADED",
                cycle,
            )

            save_json(
                AUTONOMOUS_LATEST_REPORT,
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
            + max(0, seconds)
        )

        while (
            not STOP_REQUESTED
            and time.monotonic() < deadline
        ):
            remaining = (
                deadline
                - time.monotonic()
            )

            time.sleep(
                min(
                    1.0,
                    max(0.05, remaining),
                )
            )

    def run_forever(self) -> int:
        global STOP_REQUESTED

        PID_FILE.write_text(
            str(os.getpid()),
            encoding="utf-8",
        )

        self.audit(
            "AUTONOMOUS_RUNTIME_STARTED",
            {
                "pid": os.getpid(),
                "cycle_seconds": self.cycle_seconds,
            },
        )

        self.save_state("STARTING")

        try:
            while not STOP_REQUESTED:
                self.save_state("RUNNING")

                cycle = self.run_cycle()

                print(
                    json.dumps(
                        {
                            "time": utc_now(),
                            "mode": "AUTONOMOUS",
                            "cycle_id": cycle.get(
                                "cycle_id"
                            ),
                            "success": cycle.get(
                                "success"
                            ),
                            "status": cycle.get(
                                "status"
                            ),
                            "message_ar": cycle.get(
                                "message_ar"
                            ),
                            "message_en": cycle.get(
                                "message_en"
                            ),
                            "findings": len(
                                cycle.get(
                                    "findings",
                                    [],
                                )
                            ),
                            "remaining_findings": len(
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

            self.save_state("STOPPED")

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

    def run_once(self) -> Dict[str, Any]:
        self.save_state("RUNNING_ONCE")

        result = self.run_cycle()

        self.save_state(
            "ONCE_COMPLETED",
            result,
        )

        return result


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
                "time": utc_now(),
                "event": "SHUTDOWN_SIGNAL",
                "signal": signum,
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
# PUBLIC OWNER API
# ============================================================

def execute_full_factory(
    command: str,
    owner: str = DEFAULT_OWNER,
    **kwargs: Any,
) -> Dict[str, Any]:
    runtime = MajdFullExecutionRuntime()

    return runtime.execute(
        command=command,
        owner=owner,
    )


def execute_owner_runtime(
    command: str,
    owner: str = DEFAULT_OWNER,
    **kwargs: Any,
) -> Dict[str, Any]:
    return execute_full_factory(
        command=command,
        owner=owner,
    )


def execute(
    command: str,
    owner: str = DEFAULT_OWNER,
    **kwargs: Any,
) -> Dict[str, Any]:
    return execute_full_factory(
        command=command,
        owner=owner,
    )


def run(
    command: str,
    owner: str = DEFAULT_OWNER,
    **kwargs: Any,
) -> Dict[str, Any]:
    return execute_full_factory(
        command=command,
        owner=owner,
    )


# ============================================================
# PUBLIC AUTONOMOUS API
# ============================================================

def run_autonomous_once(
    owner: str = DEFAULT_OWNER,
    **kwargs: Any,
) -> Dict[str, Any]:
    runtime = MajdAutonomousRuntime(
        owner=owner,
    )

    return runtime.run_once()


def run_autonomous_forever(
    owner: str = DEFAULT_OWNER,
    cycle_seconds: int = DEFAULT_CYCLE_SECONDS,
    **kwargs: Any,
) -> int:
    install_signal_handlers()

    runtime = MajdAutonomousRuntime(
        owner=owner,
        cycle_seconds=cycle_seconds,
    )

    return runtime.run_forever()


def get_autonomous_status() -> Dict[str, Any]:
    state = load_json(
        AUTONOMOUS_STATE_FILE,
        {},
    )

    pid = state.get("pid")
    process_alive = False

    if isinstance(pid, int) and pid > 0:
        try:
            os.kill(pid, 0)
            process_alive = True
        except Exception:
            process_alive = False

    state["process_alive"] = process_alive
    state["state_file"] = str(
        AUTONOMOUS_STATE_FILE
    )
    state["latest_report"] = str(
        AUTONOMOUS_LATEST_REPORT
    )

    if "message_ar" not in state:
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
            "FULL EXECUTION RUNTIME 06"
        )
    )

    parser.add_argument(
        "command",
        nargs="*",
        help=(
            "Owner command in Arabic or English. "
            "أمر المالك بالعربية أو الإنجليزية."
        ),
    )

    parser.add_argument(
        "--owner",
        default=DEFAULT_OWNER,
        help="Owner identity / هوية المالك",
    )

    parser.add_argument(
        "--autonomous",
        action="store_true",
        help=(
            "Run MAJD autonomous persistent runtime. "
            "تشغيل مجد الذاتي الدائم."
        ),
    )

    parser.add_argument(
        "--once",
        action="store_true",
        help=(
            "Run one autonomous cycle and exit. "
            "تشغيل دورة ذاتية واحدة ثم الخروج."
        ),
    )

    parser.add_argument(
        "--autonomous-status",
        action="store_true",
        help=(
            "Show autonomous runtime state. "
            "عرض حالة التشغيل الذاتي."
        ),
    )

    parser.add_argument(
        "--cycle-seconds",
        type=int,
        default=DEFAULT_CYCLE_SECONDS,
        help=(
            "Seconds between autonomous cycles. "
            "عدد الثواني بين دورات التشغيل الذاتي."
        ),
    )

    args = parser.parse_args()

    if args.autonomous_status:
        result = get_autonomous_status()
        print_result(result)
        return 0

    if args.once:
        install_signal_handlers()

        runtime = MajdAutonomousRuntime(
            owner=args.owner,
            cycle_seconds=args.cycle_seconds,
        )

        result = runtime.run_once()

        print_result(result)

        return 0 if result.get("success") else 1

    if args.autonomous:
        return run_autonomous_forever(
            owner=args.owner,
            cycle_seconds=args.cycle_seconds,
        )

    command = " ".join(
        args.command
    ).strip()

    if not command:
        if AUTONOMOUS_ENABLED_BY_DEFAULT:
            return run_autonomous_forever(
                owner=args.owner,
                cycle_seconds=args.cycle_seconds,
            )

        parser.error(
            "Owner command required when autonomous mode is disabled."
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
        f"PLATFORM / المنصة: {OFFICIAL_MAJD_PLATFORM}"
    )
    print(
        "=============================================="
    )

    result = execute_full_factory(
        command=command,
        owner=args.owner,
    )

    print_result(result)

    return 0 if result.get("success") else 1


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    raise SystemExit(main())

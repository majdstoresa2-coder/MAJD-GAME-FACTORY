#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-FULL-EXECUTION-RUNTIME-06.py
============================================================
MAJD SOVEREIGN AUTONOMOUS FULL EXECUTION RUNTIME
المشغّل السيادي الذاتي الشامل لمنصة مجد

06 هو المشغّل الدائم للشركة والمنصة، وليس نسخة من 01 أو 02 أو 03.

01 = العقل المدبر: التخطيط، البرمجة، الإصلاح، التطوير والتنفيذ الذكي.
02 = الشركة السيادية: الأقسام، القدرات، الحالات والسياسات التشغيلية.
03 = منفذ الألعاب الحقيقي.
04 = جسر النشر الرسمي.
06 = التشغيل الدائم، الاكتشاف، التسليم إلى 01، التحقق، الحماية، rollback،
     التقارير، الاستمرار، والتشغيل كخدمة.

الهدف:
- لا ينتظر أوامر يومية من المالك.
- إذا وجد عطلاً: يصلحه عبر 01 ويتحقق.
- إذا لم يجد عطلاً: لا ينام كـ Health Monitor فقط؛ بل يطلب من 01 فحص
  الشركة والمستودع واختيار العمل التالي الآمن: ربط قدرة، إصلاح نقص،
  تطوير واجهة، تحسين خدمة، اختبار، QA، تكامل، أو إكمال جزء غير تشغيلي.
- لا يعلن OPERATIONAL بدون دليل حقيقي.
- لا يطلب من المالك كوداً.
- لا يرجع للمالك إلا في حاجز خارجي/قانوني/مالي/هوية/سر لا يمكن إنشاؤه.
- يحافظ على سلطة المالك والأسرار.
- تقارير المالك عربية + إنجليزية.

CLI:
  python3 MAJD-FULL-EXECUTION-RUNTIME-06.py --once
  python3 MAJD-FULL-EXECUTION-RUNTIME-06.py --autonomous
  python3 MAJD-FULL-EXECUTION-RUNTIME-06.py --autonomous-status
  python3 MAJD-FULL-EXECUTION-RUNTIME-06.py --install-service
  python3 MAJD-FULL-EXECUTION-RUNTIME-06.py --service-status
  python3 MAJD-FULL-EXECUTION-RUNTIME-06.py "أمر المالك"

إذا شُغّل بدون arguments يبدأ Autonomous Persistent Runtime.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import inspect
import json
import os
import shutil
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
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple


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

SERVICE_NAME = "majd-autonomous.service"
SERVICE_FILE = Path("/etc/systemd/system") / SERVICE_NAME

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
# IDENTITY / CONFIG
# ============================================================

SYSTEM_NAME = "MAJD-GAME-FACTORY"
RUNTIME_NAME = "MAJD-FULL-EXECUTION-RUNTIME"
VERSION = "4.0.0-AUTONOMOUS-COMPANY-WIDE-BILINGUAL"
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

PROACTIVE_WORK_ENABLED = os.getenv(
    "MAJD_PROACTIVE_WORK_ENABLED",
    "true",
).strip().lower() in ("1", "true", "yes", "on")

PROACTIVE_EVERY_N_CYCLES = max(
    1,
    int(os.getenv("MAJD_PROACTIVE_EVERY_N_CYCLES", "1")),
)

VERIFY_PUBLIC_PLATFORM_AFTER_CHANGE = os.getenv(
    "MAJD_VERIFY_PUBLIC_PLATFORM_AFTER_CHANGE",
    "true",
).strip().lower() in ("1", "true", "yes", "on")

STOP_REQUESTED = False


# ============================================================
# SAFE SOURCE BACKUP POLICY
# ============================================================

SOURCE_EXTENSIONS: Set[str] = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".json",
    ".html",
    ".css",
    ".scss",
    ".yaml",
    ".yml",
    ".toml",
    ".sh",
    ".md",
    ".txt",
}

IGNORED_DIR_NAMES: Set[str] = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "majd_factory_state",
    "majd_game_output",
    "dist",
    "build",
    ".next",
    ".cache",
    "coverage",
}

SECRET_NAMES: Set[str] = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    "credentials.json",
    "secrets.json",
}


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


def status_message(
    status: str,
) -> Dict[str, str]:
    mapping = {
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
        "PROACTIVE_WORK_COMPLETED": (
            "اكتملت دورة عمل استباقية للعقل المدبر وتم التحقق منها.",
            "A proactive mastermind work cycle completed and was verified.",
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
            "بقيت مشكلات بعد الإصلاح وسيواصل النظام المعالجة.",
            "Some issues remain after repair; the runtime will continue.",
        ),
        "OWNER_ACTION_REQUIRED": (
            "يوجد حاجز حقيقي يحتاج المالك.",
            "A real blocker requires the owner.",
        ),
        "COMPLETED": (
            "اكتمل التنفيذ بنجاح.",
            "Execution completed successfully.",
        ),
        "STOPPED": (
            "تم إيقاف التشغيل الذاتي.",
            "Autonomous runtime stopped.",
        ),
    }

    ar, en = mapping.get(
        status,
        (
            f"الحالة: {status}",
            f"Status: {status}",
        ),
    )

    return {
        "message_ar": ar,
        "message_en": en,
    }


# ============================================================
# BASIC HELPERS
# ============================================================

def safe_str(
    value: Any,
) -> str:
    try:
        return str(value)
    except Exception:
        return "<unprintable>"


def truncate_text(
    value: Any,
    limit: int = 12000,
) -> str:
    text = safe_str(value)

    if len(text) <= limit:
        return text

    return (
        text[:limit]
        + "\n...[TRUNCATED]..."
    )


def sha256_file(
    path: Path,
) -> Optional[str]:
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
    default: Optional[
        Dict[str, Any]
    ] = None,
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
# PROCESS
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
                "انتهت مهلة العملية.",
                "Process execution timed out.",
            ),
        }

    except Exception as error:
        return {
            "success": False,
            "status": "PROCESS_EXCEPTION",
            "command": command,

            "error":
                f"{type(error).__name__}: "
                f"{error}",

            **bilingual(
                "حدث خطأ أثناء تنفيذ العملية.",
                "An error occurred while executing the process.",
            ),
        }


# ============================================================
# MODULE LOADER / CALL
# ============================================================

def load_module(
    path: Path,
    module_name: str,
) -> Any:
    if not path.exists():
        raise FileNotFoundError(
            f"Required file not found: "
            f"{path.name}"
        )

    spec = (
        importlib.util
        .spec_from_file_location(
            module_name,
            str(path),
        )
    )

    if (
        spec is None
        or spec.loader is None
    ):
        raise RuntimeError(
            f"Unable to load module: "
            f"{path.name}"
        )

    module = (
        importlib.util
        .module_from_spec(spec)
    )

    sys.modules[
        module_name
    ] = module

    spec.loader.exec_module(
        module
    )

    return module


def find_callable(
    module: Any,
    names: Iterable[str],
) -> Optional[
    Callable[..., Any]
]:
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
    signature = inspect.signature(
        function
    )

    parameters = (
        signature.parameters
    )

    accepts_kwargs = any(
        p.kind
        == inspect.Parameter.VAR_KEYWORD

        for p
        in parameters.values()
    )

    kwargs: Dict[
        str,
        Any
    ] = {}

    for key, value in values.items():
        if (
            accepts_kwargs
            or key in parameters
        ):
            kwargs[key] = value

    return function(
        **kwargs
    )


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

    important = {
        "02_sovereign_company":
            SOVEREIGN_COMPANY_FILE,
    }

    files: Dict[
        str,
        Any
    ] = {}

    missing: List[str] = []

    for name, path in required.items():
        exists = (
            path.exists()
            and path.is_file()
            and path.stat().st_size > 0
        )

        files[name] = {
            "file":
                path.name,

            "exists":
                exists,

            "required":
                True,

            "size":
                (
                    path.stat().st_size
                    if path.exists()
                    else 0
                ),

            "sha256":
                (
                    sha256_file(path)
                    if exists
                    else None
                ),
        }

        if not exists:
            missing.append(
                path.name
            )

    for name, path in important.items():
        exists = (
            path.exists()
            and path.is_file()
            and path.stat().st_size > 0
        )

        files[name] = {
            "file":
                path.name,

            "exists":
                exists,

            "required":
                False,

            "size":
                (
                    path.stat().st_size
                    if path.exists()
                    else 0
                ),

            "sha256":
                (
                    sha256_file(path)
                    if exists
                    else None
                ),
        }

    return {
        "success":
            not missing,

        "files":
            files,

        "missing":
            missing,
    }


# ============================================================
# SOURCE DISCOVERY / BACKUP / ROLLBACK
# ============================================================

def is_source_path(
    path: Path,
) -> bool:
    try:
        relative = (
            path.relative_to(
                ROOT_DIR
            )
        )
    except ValueError:
        return False

    if any(
        part in IGNORED_DIR_NAMES
        for part in relative.parts
    ):
        return False

    if path.name in SECRET_NAMES:
        return False

    if (
        path.suffix.lower()
        not in SOURCE_EXTENSIONS
    ):
        return False

    return path.is_file()


def discover_source_files() -> List[Path]:
    result: List[Path] = []

    for path in ROOT_DIR.rglob("*"):
        if is_source_path(path):
            result.append(path)

    return sorted(result)


def create_source_backup(
    cycle_id: str,
) -> Dict[str, Any]:
    backup_root = (
        BACKUP_DIR
        / cycle_id
    )

    backup_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    files = discover_source_files()

    manifest: Dict[
        str,
        Any
    ] = {
        "cycle_id":
            cycle_id,

        "created_at":
            utc_now(),

        "backup_root":
            str(backup_root),

        "files":
            {},

        "source_set":
            [],
    }

    for source in files:
        relative = (
            source.relative_to(
                ROOT_DIR
            )
        )

        destination = (
            backup_root
            / relative
        )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            source,
            destination,
        )

        manifest[
            "source_set"
        ].append(
            str(relative)
        )

        manifest[
            "files"
        ][
            str(relative)
        ] = {
            "sha256":
                sha256_file(source),

            "size":
                source.stat().st_size,
        }

    save_json(
        backup_root
        / "manifest.json",

        manifest,
    )

    return {
        "success":
            True,

        "status":
            "SOURCE_BACKUP_CREATED",

        "backup_root":
            str(backup_root),

        "file_count":
            len(files),

        "manifest":
            str(
                backup_root
                / "manifest.json"
            ),
    }


def rollback_source_backup(
    cycle_id: str,
) -> Dict[str, Any]:
    backup_root = (
        BACKUP_DIR
        / cycle_id
    )

    manifest_file = (
        backup_root
        / "manifest.json"
    )

    if not manifest_file.exists():
        return {
            "success":
                False,

            "status":
                "ROLLBACK_MANIFEST_MISSING",
        }

    manifest = load_json(
        manifest_file,
        {},
    )

    original_set = set(
        str(x)
        for x
        in manifest.get(
            "source_set",
            [],
        )
    )

    restored: List[str] = []
    removed_new: List[str] = []

    for relative in sorted(
        original_set
    ):
        backup_file = (
            backup_root
            / relative
        )

        target = (
            ROOT_DIR
            / relative
        )

        if backup_file.exists():
            target.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            shutil.copy2(
                backup_file,
                target,
            )

            restored.append(
                relative
            )

    current_set = {
        str(
            path.relative_to(
                ROOT_DIR
            )
        )
        for path
        in discover_source_files()
    }

    for relative in sorted(
        current_set - original_set
    ):
        target = (
            ROOT_DIR
            / relative
        )

        try:
            target.unlink()
            removed_new.append(
                relative
            )
        except Exception:
            pass

    return {
        "success":
            True,

        "status":
            "SOURCE_ROLLBACK_COMPLETED",

        "restored":
            restored,

        "removed_new":
            removed_new,
    }


def source_change_report(
    cycle_id: str,
) -> Dict[str, Any]:
    manifest = load_json(
        BACKUP_DIR
        / cycle_id
        / "manifest.json",

        {},
    )

    originals = manifest.get(
        "files",
        {},
    )

    original_set = set(
        originals.keys()
    )

    current_files = (
        discover_source_files()
    )

    current_map = {
        str(
            path.relative_to(
                ROOT_DIR
            )
        ): {
            "sha256":
                sha256_file(path),

            "size":
                path.stat().st_size,
        }

        for path
        in current_files
    }

    changed: List[str] = []
    created: List[str] = []
    deleted: List[str] = []

    for relative in sorted(
        original_set
    ):
        current = current_map.get(
            relative
        )

        if current is None:
            deleted.append(
                relative
            )
            continue

        if (
            current.get("sha256")
            !=
            originals[
                relative
            ].get("sha256")
        ):
            changed.append(
                relative
            )

    for relative in sorted(
        set(current_map)
        - original_set
    ):
        created.append(
            relative
        )

    return {
        "success":
            True,

        "changed_files":
            changed,

        "created_files":
            created,

        "deleted_files":
            deleted,

        "has_changes":
            bool(
                changed
                or created
                or deleted
            ),
    }


# ============================================================
# SYNTAX
# ============================================================

def discover_python_files() -> List[Path]:
    return [
        path

        for path
        in discover_source_files()

        if path.suffix.lower()
        == ".py"
    ]


def verify_python_syntax(
    paths: Optional[
        List[Path]
    ] = None,
) -> Dict[str, Any]:
    if paths is None:
        paths = (
            discover_python_files()
        )

    failed: List[str] = []
    results: List[
        Dict[str, Any]
    ] = []

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
                path.relative_to(
                    ROOT_DIR
                )
            )
        except ValueError:
            display = str(path)

        item: Dict[
            str,
            Any
        ] = {
            "file":
                display,

            "success":
                bool(
                    process.get(
                        "success"
                    )
                ),
        }

        if not item["success"]:
            item["error"] = (
                process.get(
                    "stderr"
                )
                or process.get(
                    "error"
                )
                or
                "PYTHON_SYNTAX_FAILED"
            )

            failed.append(
                display
            )

        results.append(
            item
        )

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
# HTTP / DOCKER / DISK
# ============================================================

def http_probe(
    url: str,
    timeout: int = DEFAULT_HTTP_TIMEOUT,
) -> Dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent":
                "MAJD-AUTONOMOUS-RUNTIME/4.0"
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

            return {
                "success":
                    200 <= code < 400,

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
            "success":
                False,

            "url":
                url,

            "status_code":
                error.code,

            "error":
                safe_str(
                    error
                ),
        }

    except Exception as error:
        return {
            "success":
                False,

            "url":
                url,

            "status":
                "HTTP_PROBE_FAILED",

            "error":
                f"{type(error).__name__}: "
                f"{error}",
        }


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

    if not process.get(
        "success"
    ):
        return {
            "success":
                False,

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

        parts = line.split(
            "|",
            2,
        )

        containers.append(
            {
                "name":
                    (
                        parts[0]
                        if len(parts) > 0
                        else ""
                    ),

                "status":
                    (
                        parts[1]
                        if len(parts) > 1
                        else ""
                    ),

                "ports":
                    (
                        parts[2]
                        if len(parts) > 2
                        else ""
                    ),
            }
        )

    names = {
        item["name"]
        for item
        in containers
    }

    expected = {
        "majd-ai-core",
        "majd-web-ui",
    }

    missing_expected = sorted(
        expected - names
    )

    return {
        "success":
            not missing_expected,

        "containers":
            containers,

        "missing_expected":
            missing_expected,
    }


def inspect_disk() -> Dict[str, Any]:
    try:
        stat = os.statvfs(
            ROOT_DIR
        )

        total = (
            stat.f_blocks
            * stat.f_frsize
        )

        available = (
            stat.f_bavail
            * stat.f_frsize
        )

        used = (
            total
            - available
        )

        used_percent = (
            used
            / total
            * 100.0
            if total > 0
            else 0.0
        )

        return {
            "success":
                used_percent
                < 90.0,

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
            "success":
                False,

            "status":
                "DISK_INSPECTION_FAILED",

            "error":
                f"{type(error).__name__}: "
                f"{error}",
        }


# ============================================================
# OWNER COMMAND CENTER
# ============================================================

class OwnerCommandCenterRuntime:

    def __init__(
        self,
    ) -> None:
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
            parser = (
                parser_class()
            )

            result = (
                parser.parse(
                    command
                )
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
                or
                result_type
                == "UNKNOWN"
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
                    f"{type(error).__name__}: "
                    f"{error}",
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

        if not callable(
            function
        ):
            return {
                "success":
                    False,

                "status":
                    "OWNER_COMMAND_INTERFACE_MISSING",
            }

        try:
            result = call_supported(
                function,
                {
                    "command":
                        command,

                    "owner":
                        owner,
                },
            )

        except Exception as error:
            return {
                "success":
                    False,

                "status":
                    "OWNER_COMMAND_EXECUTION_EXCEPTION",

                "error":
                    f"{type(error).__name__}: "
                    f"{error}",

                "traceback":
                    traceback.format_exc(),
            }

        if not isinstance(
            result,
            dict,
        ):
            return {
                "success":
                    False,

                "status":
                    "INVALID_OWNER_COMMAND_RESULT",

                "result_type":
                    type(
                        result
                    ).__name__,
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

    def __init__(
        self,
    ) -> None:
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
                    "success":
                        False,

                    "status":
                        "MASTERMIND_INTERFACE_NOT_FOUND",
                }

            try:
                instance = call_supported(
                    mastermind_class,
                    {
                        "owner":
                            owner,
                    },
                )

            except Exception as error:
                return {
                    "success":
                        False,

                    "status":
                        "MASTERMIND_INITIALIZATION_FAILED",

                    "error":
                        f"{type(error).__name__}: "
                        f"{error}",
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
                    "success":
                        False,

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
                        str(
                            OUTPUT_DIR
                        ),
                },
            )

        except Exception as error:
            return {
                "success":
                    False,

                "status":
                    "MASTERMIND_EXECUTION_EXCEPTION",

                "error":
                    f"{type(error).__name__}: "
                    f"{error}",

                "traceback":
                    traceback.format_exc(),
            }

        if not isinstance(
            result,
            dict,
        ):
            return {
                "success":
                    False,

                "status":
                    "INVALID_MASTERMIND_RESULT",

                "result_type":
                    type(
                        result
                    ).__name__,
            }

        return result


# ============================================================
# COMPANY 02 CLI INSPECTION
# ============================================================

def parse_json_from_process(
    process: Dict[str, Any],
) -> Optional[
    Dict[str, Any]
]:
    stdout = str(
        process.get(
            "stdout",
            "",
        )
    ).strip()

    if not stdout:
        return None

    try:
        value = json.loads(
            stdout
        )

        return (
            value
            if isinstance(
                value,
                dict,
            )
            else None
        )

    except Exception:
        pass

    start = stdout.find(
        "{"
    )

    end = stdout.rfind(
        "}"
    )

    if (
        start >= 0
        and end > start
    ):
        try:
            value = json.loads(
                stdout[
                    start:
                    end + 1
                ]
            )

            return (
                value
                if isinstance(
                    value,
                    dict,
                )
                else None
            )

        except Exception:
            return None

    return None


def inspect_sovereign_company() -> Dict[str, Any]:
    if not SOVEREIGN_COMPANY_FILE.exists():
        return {
            "success":
                False,

            "status":
                "SOVEREIGN_COMPANY_FILE_MISSING",
        }

    health_process = run_process(
        [
            sys.executable,
            str(
                SOVEREIGN_COMPANY_FILE
            ),
            "--health",
        ],
        timeout=120,
    )

    self_test_process = run_process(
        [
            sys.executable,
            str(
                SOVEREIGN_COMPANY_FILE
            ),
            "--self-test",
        ],
        timeout=180,
    )

    health = (
        parse_json_from_process(
            health_process
        )
    )

    self_test = (
        parse_json_from_process(
            self_test_process
        )
    )

    success = bool(
        health_process.get(
            "success"
        )
        and
        self_test_process.get(
            "success"
        )
        and isinstance(
            health,
            dict,
        )
        and isinstance(
            self_test,
            dict,
        )
    )

    return {
        "success":
            success,

        "status":
            (
                "SOVEREIGN_COMPANY_INSPECTED"
                if success
                else
                "SOVEREIGN_COMPANY_INSPECTION_FAILED"
            ),

        "health":
            health,

        "self_test":
            self_test,

        "health_process": {
            "success":
                health_process.get(
                    "success"
                ),

            "returncode":
                health_process.get(
                    "returncode"
                ),

            "stderr":
                health_process.get(
                    "stderr"
                ),
        },

        "self_test_process": {
            "success":
                self_test_process.get(
                    "success"
                ),

            "returncode":
                self_test_process.get(
                    "returncode"
                ),

            "stderr":
                self_test_process.get(
                    "stderr"
                ),
        },
    }


def extract_company_gaps(
    company: Dict[str, Any],
) -> Dict[str, Any]:
    gaps: List[
        Dict[str, Any]
    ] = []

    required_gaps: List[
        Dict[str, Any]
    ] = []

    def walk(
        value: Any,
    ) -> None:
        if isinstance(
            value,
            dict,
        ):
            status = str(
                value.get(
                    "status",
                    "",
                )
            ).upper()

            cap_id = (
                value.get("id")
                or
                value.get(
                    "capability"
                )
                or
                value.get(
                    "capability_id"
                )
                or
                value.get(
                    "name"
                )
            )

            required = bool(
                value.get(
                    "required",
                    False,
                )
            )

            if (
                status
                in {
                    "UNAVAILABLE",
                    "MISSING",
                    "DEGRADED",
                    "NOT_CONFIGURED",
                    "FAILED",
                }
                and cap_id
            ):
                item = {
                    "id":
                        safe_str(
                            cap_id
                        ),

                    "status":
                        status,

                    "required":
                        required,

                    "adapter":
                        value.get(
                            "adapter"
                        ),

                    "engine":
                        value.get(
                            "engine"
                        ),

                    "reason":
                        (
                            value.get(
                                "reason"
                            )
                            or
                            value.get(
                                "message"
                            )
                        ),
                }

                gaps.append(
                    item
                )

                if required:
                    required_gaps.append(
                        item
                    )

            for child in value.values():
                walk(
                    child
                )

        elif isinstance(
            value,
            list,
        ):
            for child in value:
                walk(
                    child
                )

    walk(
        company
    )

    seen: Set[
        Tuple[str, str]
    ] = set()

    unique: List[
        Dict[str, Any]
    ] = []

    for item in gaps:
        key = (
            item["id"],
            item["status"],
        )

        if key not in seen:
            seen.add(
                key
            )

            unique.append(
                item
            )

    seen_req: Set[
        Tuple[str, str]
    ] = set()

    unique_req: List[
        Dict[str, Any]
    ] = []

    for item in required_gaps:
        key = (
            item["id"],
            item["status"],
        )

        if key not in seen_req:
            seen_req.add(
                key
            )

            unique_req.append(
                item
            )

    return {
        "gap_count":
            len(unique),

        "required_gap_count":
            len(unique_req),

        "gaps":
            unique[:200],

        "required_gaps":
            unique_req[:100],
    }


# ============================================================
# ARTIFACT / PUBLICATION
# ============================================================

def verify_playable_artifact(
    artifact_value: Any,
) -> Dict[str, Any]:
    if not artifact_value:
        return {
            "success":
                False,

            "status":
                "PLAYABLE_ARTIFACT_MISSING",
        }

    artifact = Path(
        str(
            artifact_value
        )
    )

    artifact = (
        (
            ROOT_DIR
            / artifact
        ).resolve()

        if not artifact.is_absolute()

        else artifact.resolve()
    )

    if (
        not artifact.exists()
        or
        not artifact.is_dir()
    ):
        return {
            "success":
                False,

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
        or
        index_file.stat().st_size
        <= 0
    ):
        return {
            "success":
                False,

            "status":
                "PLAYABLE_INDEX_NOT_FOUND_OR_EMPTY",

            "artifact":
                str(artifact),
        }

    files = [
        path

        for path
        in artifact.rglob("*")

        if path.is_file()
    ]

    javascript_files = [
        path

        for path
        in files

        if path.suffix.lower()
        in (
            ".js",
            ".mjs",
        )
    ]

    if not javascript_files:
        return {
            "success":
                False,

            "status":
                "PLAYABLE_JAVASCRIPT_NOT_FOUND",

            "artifact":
                str(artifact),
        }

    return {
        "success":
            True,

        "status":
            "PLAYABLE_ARTIFACT_VERIFIED",

        "artifact":
            str(artifact),

        "index":
            str(
                index_file
            ),

        "file_count":
            len(files),
    }


def verify_published_result(
    platform_result: Dict[str, Any],
) -> Dict[str, Any]:
    if not isinstance(
        platform_result,
        dict,
    ):
        return {
            "success":
                False,

            "status":
                "PLATFORM_RESULT_INVALID",
        }

    if not platform_result.get(
        "success"
    ):
        return {
            "success":
                False,

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
        or
        not public_url
        or
        not game_path
    ):
        return {
            "success":
                False,

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
        or
        not index_file.exists()
    ):
        return {
            "success":
                False,

            "status":
                "PUBLISHED_ARTIFACT_NOT_FOUND",
        }

    return {
        "success":
            True,

        "status":
            "PUBLISHED_RESULT_VERIFIED",

        "published_directory":
            str(
                published_path
            ),

        "index":
            str(
                index_file
            ),

        "game_path":
            game_path,

        "public_url":
            public_url,
    }


def verify_mastermind_result(
    command_type: str,
    result: Dict[str, Any],
) -> Dict[str, Any]:
    if not isinstance(
        result,
        dict,
    ):
        return {
            "success":
                False,

            "status":
                "INVALID_FINAL_RESULT",
        }

    if not result.get(
        "success"
    ):
        return {
            "success":
                False,

            "status":
                result.get(
                    "status",
                    "MASTERMIND_FAILED",
                ),

            "result":
                result,
        }

    if (
        command_type
        != "CREATE_GAME"
    ):
        return {
            "success":
                True,

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
            "success":
                False,

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
            "success":
                False,

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
            "success":
                False,

            "status":
                publication_verification.get(
                    "status"
                ),

            "publication_verification":
                publication_verification,
        }

    return {
        "success":
            True,

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

    def __init__(
        self,
    ) -> None:
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

        state: Dict[
            str,
            Any
        ] = {
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

        self.save(
            state
        )

        try:
            if not command:
                state[
                    "status"
                ] = (
                    "EMPTY_OWNER_COMMAND"
                )

                state.update(
                    bilingual(
                        "أمر المالك لا يمكن أن يكون فارغاً.",
                        "Owner command cannot be empty.",
                    )
                )

                state[
                    "finished_at"
                ] = utc_now()

                self.save(
                    state
                )

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

                self.save(
                    state
                )

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
                or
                command_type
                == "UNKNOWN"
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
                        command=
                            command,

                        owner=
                            owner,
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
                    or
                    (
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

                self.save(
                    state
                )

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
                ] = mastermind_result

                state[
                    "finished_at"
                ] = utc_now()

                self.save(
                    state
                )

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
                ] = mastermind_result

                state[
                    "finished_at"
                ] = utc_now()

                self.save(
                    state
                )

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
            ] = mastermind_result

            state[
                "verification"
            ] = verification

            state.update(
                status_message(
                    "COMPLETED"
                )
            )

            if (
                command_type
                == "CREATE_GAME"
            ):
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
                ] = artifact.get(
                    "artifact"
                )

                state[
                    "game_path"
                ] = publication.get(
                    "game_path"
                )

                state[
                    "public_url"
                ] = publication.get(
                    "public_url"
                )

                state[
                    "published"
                ] = True

            state[
                "finished_at"
            ] = utc_now()

            self.save(
                state
            )

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
            ] = traceback.format_exc()

            state[
                "finished_at"
            ] = utc_now()

            self.save(
                state
            )

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
    evidence: Optional[
        Dict[str, Any]
    ] = None,
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
) -> List[
    Dict[str, Any]
]:
    findings: List[
        Dict[str, Any]
    ] = []

    checks = [
        (
            "core_files",
            "CORE_FILES_MISSING",
            "CRITICAL",
            "CORE",
            "FAILED",
            "ملفات أساسية مطلوبة مفقودة أو فارغة.",
            "Required core files are missing or empty.",
        ),
        (
            "python_syntax",
            "PYTHON_SYNTAX_FAILURE",
            "CRITICAL",
            "SOURCE_CODE",
            "FAILED",
            "يوجد خطأ Syntax في ملف بايثون واحد أو أكثر.",
            "One or more Python files contain syntax errors.",
        ),
        (
            "local_api",
            "LOCAL_API_UNHEALTHY",
            "HIGH",
            "MAJD_AI_CORE",
            "DEGRADED",
            "فشل فحص صحة API المحلي.",
            "Local API health probe failed.",
        ),
        (
            "official_platform",
            "OFFICIAL_PLATFORM_UNREACHABLE",
            "CRITICAL",
            "PUBLIC_PLATFORM",
            "FAILED",
            "تعذر الوصول إلى منصة مجد الرسمية.",
            "Official MAJD platform is unreachable.",
        ),
        (
            "docker",
            "DOCKER_DEGRADED",
            "HIGH",
            "DOCKER",
            "DEGRADED",
            "خدمات Docker الأساسية غير سليمة.",
            "Core Docker services are unhealthy.",
        ),
        (
            "disk",
            "DISK_CAPACITY_RISK",
            "HIGH",
            "SERVER_STORAGE",
            "DEGRADED",
            "مساحة تخزين السيرفر تحتاج معالجة.",
            "Server storage requires attention.",
        ),
        (
            "sovereign_company",
            "SOVEREIGN_COMPANY_UNAVAILABLE",
            "HIGH",
            "SOVEREIGN_COMPANY",
            "UNAVAILABLE",
            "تعذر فحص الشركة السيادية 02.",
            "Unable to inspect Sovereign Company 02.",
        ),
    ]

    for (
        key,
        fid,
        severity,
        component,
        status,
        ar,
        en,
    ) in checks:
        evidence = inspection.get(
            key,
            {},
        )

        if not evidence.get(
            "success"
        ):
            findings.append(
                finding(
                    fid,
                    severity,
                    component,
                    status,
                    ar,
                    en,
                    repairable=True,
                    evidence=evidence,
                )
            )

    company_gaps = inspection.get(
        "company_gaps",
        {},
    )

    required_gaps = company_gaps.get(
        "required_gaps",
        [],
    )

    if required_gaps:
        findings.append(
            finding(
                "REQUIRED_COMPANY_CAPABILITIES_NOT_OPERATIONAL",
                "HIGH",
                "SOVEREIGN_COMPANY",
                "DEGRADED",
                "توجد قدرات مطلوبة في الشركة غير تشغيلية بعد.",
                "Required company capabilities are not operational yet.",
                repairable=True,
                evidence={
                    "required_gap_count":
                        len(
                            required_gaps
                        ),

                    "required_gaps":
                        required_gaps,
                },
            )
        )

    return findings


# ============================================================
# AUTONOMOUS POLICIES / OBJECTIVES
# ============================================================

def base_autonomous_policy() -> Dict[str, Any]:
    return {
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

        "allow_ui_development":
            True,

        "allow_testing":
            True,

        "allow_qa":
            True,

        "allow_build":
            True,

        "allow_routine_deployment":
            True,

        "allow_routine_service_recovery":
            True,

        "allow_dependency_configuration_when_safe":
            True,

        "require_real_verification":
            True,

        "never_fake_operational":
            True,

        "rollback_on_failed_change":
            True,

        "protect_owner_authority":
            True,

        "protect_secrets":
            True,

        "do_not_expose_internal_platform_secrets_to_users":
            True,

        "owner_reports_bilingual":
            True,

        "user_ai_scope_is_majd_services_only":
            True,

        "do_not_require_owner_code_input":
            True,

        "owner_only_for_true_external_blockers":
            True,
    }


def build_repair_objective(
    cycle_id: str,
    findings: List[
        Dict[str, Any]
    ],
    inspection: Dict[str, Any],
) -> Tuple[
    str,
    Dict[str, Any],
]:
    request = {
        "type":
            "AUTONOMOUS_PLATFORM_REPAIR",

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

        "company_gaps":
            inspection.get(
                "company_gaps",
                {},
            ),

        "policy":
            base_autonomous_policy(),
    }

    command = (
        "MAJD AUTONOMOUS REPAIR / إصلاح مجد الذاتي. "
        "You are the sovereign MAJD mastermind. Repair all routine technical "
        "problems in the supplied findings without waiting for owner commands. "
        "Inspect the repository and existing components first. Reuse healthy "
        "components. If code, adapters, tests, integration, UI work, service "
        "configuration, or safe deployment work is required, create or modify "
        "it yourself. Preserve working behavior. Do not ask the owner to write "
        "code. Test every change. Never mark anything OPERATIONAL without real "
        "evidence. Protect secrets and owner authority. Return a structured "
        "Arabic and English result."
    )

    return (
        command,
        request,
    )


def build_proactive_objective(
    cycle_id: str,
    inspection: Dict[str, Any],
) -> Tuple[
    str,
    Dict[str, Any],
]:
    request = {
        "type":
            "AUTONOMOUS_CONTINUOUS_COMPANY_OPERATION",

        "source":
            RUNTIME_NAME,

        "cycle_id":
            cycle_id,

        "owner":
            DEFAULT_OWNER,

        "autonomous":
            True,

        "proactive":
            True,

        "language": {
            "primary":
                "ar",

            "secondary":
                "en",
        },

        "company_gaps":
            inspection.get(
                "company_gaps",
                {},
            ),

        "platform_snapshot": {
            "core_files":
                inspection.get(
                    "core_files",
                    {},
                ),

            "local_api":
                inspection.get(
                    "local_api",
                    {},
                ),

            "official_platform":
                inspection.get(
                    "official_platform",
                    {},
                ),

            "docker":
                inspection.get(
                    "docker",
                    {},
                ),

            "disk":
                inspection.get(
                    "disk",
                    {},
                ),
        },

        "policy":
            base_autonomous_policy(),
    }

    command = (
        "MAJD CONTINUOUS AUTONOMOUS OPERATION / تشغيل مجد الذاتي المستمر. "
        "The platform may be healthy, but your job is not to stop at health. "
        "Act as the permanent sovereign technical operator of MAJD-GAME-FACTORY. "
        "Inspect Sovereign Company 02, the repository, runtime integrations, "
        "official public platform, owner dashboard, user-facing experience, "
        "game/media factories, QA, security, monitoring, reporting, and all "
        "existing project files. Select the highest-value SAFE unfinished, "
        "degraded, disconnected, placeholder, or non-operational work item that "
        "can be completed autonomously now. Then implement it yourself: plan, "
        "write or modify code when needed, integrate, test, repair failures, "
        "and verify the real result. Prefer existing components and do not "
        "duplicate working systems. Never claim external engines/services are "
        "operational without real configuration and health/production proof. "
        "Do not ask the owner for code or routine approvals. Only report a "
        "blocker if it truly requires an external credential, identity action, "
        "high-impact legal/financial approval, or another thing software cannot "
        "create. Preserve owner authority and platform secrets. Return a "
        "structured Arabic + English report of what you actually changed and "
        "verified."
    )

    return (
        command,
        request,
    )


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

        self.started_at = (
            utc_now()
        )

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

        self.proactive_cycles = int(
            previous.get(
                "proactive_cycles",
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

                "system":
                    SYSTEM_NAME,

                "runtime":
                    RUNTIME_NAME,

                "version":
                    VERSION,

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
                "AUTONOMOUS_PERSISTENT_COMPANY_WIDE",

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

            "proactive_work_enabled":
                PROACTIVE_WORK_ENABLED,

            "total_cycles":
                self.total_cycles,

            "successful_cycles":
                self.successful_cycles,

            "failed_cycles":
                self.failed_cycles,

            "repair_cycles":
                self.repair_cycles,

            "proactive_cycles":
                self.proactive_cycles,

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
        company = (
            inspect_sovereign_company()
        )

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

            "sovereign_company":
                company,
        }

        inspection[
            "company_gaps"
        ] = extract_company_gaps(
            company
        )

        return inspection

    def execute_mastermind_objective(
        self,
        cycle_id: str,
        command: str,
        request: Dict[str, Any],
        objective_kind: str,
    ) -> Dict[str, Any]:
        attempts: List[
            Dict[str, Any]
        ] = []

        for attempt in range(
            1,
            MAX_AUTONOMOUS_REPAIR_ATTEMPTS + 1,
        ):
            runtime_id = (
                f"AUTO-{cycle_id}-"
                f"{objective_kind}-"
                f"{attempt}"
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
                        f"{type(error).__name__}: "
                        f"{error}",

                    "traceback":
                        traceback.format_exc(),
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
                "MASTERMIND_OBJECTIVE_ATTEMPT",
                {
                    "cycle_id":
                        cycle_id,

                    "objective_kind":
                        objective_kind,

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
                        "MASTERMIND_OBJECTIVE_EXECUTED",

                    "objective_kind":
                        objective_kind,

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
                "MASTERMIND_OBJECTIVE_FAILED",

            "objective_kind":
                objective_kind,

            "attempts":
                attempts,
        }

    def verify_after_autonomous_change(
        self,
        cycle_id: str,
        before_inspection: Dict[str, Any],
    ) -> Dict[str, Any]:
        changes = (
            source_change_report(
                cycle_id
            )
        )

        syntax = (
            verify_python_syntax()
        )

        after = (
            self.inspect_platform()
        )

        checks = {
            "source_changes":
                changes,

            "python_syntax":
                syntax,

            "platform_inspection":
                after,

            "public_platform_ok":
                bool(
                    after.get(
                        "official_platform",
                        {},
                    ).get(
                        "success"
                    )
                ),

            "local_api_ok":
                bool(
                    after.get(
                        "local_api",
                        {},
                    ).get(
                        "success"
                    )
                ),

            "core_files_ok":
                bool(
                    after.get(
                        "core_files",
                        {},
                    ).get(
                        "success"
                    )
                ),

            "company_inspection_ok":
                bool(
                    after.get(
                        "sovereign_company",
                        {},
                    ).get(
                        "success"
                    )
                ),
        }

        success = (
            checks[
                "python_syntax"
            ].get(
                "success"
            )
            and
            checks[
                "core_files_ok"
            ]
            and
            checks[
                "company_inspection_ok"
            ]
            and
            (
                checks[
                    "public_platform_ok"
                ]
                if
                VERIFY_PUBLIC_PLATFORM_AFTER_CHANGE
                else True
            )
        )

        return {
            "success":
                bool(
                    success
                ),

            "status":
                (
                    "AUTONOMOUS_CHANGE_VERIFIED"
                    if success
                    else
                    "AUTONOMOUS_CHANGE_VERIFICATION_FAILED"
                ),

            "checks":
                checks,
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
                "جارٍ فحص المنصة والشركة.",
                "Inspecting platform and company.",
            ),

            "inspection":
                {},

            "findings":
                [],

            "mode_executed":
                None,

            "backup":
                None,

            "mastermind":
                None,

            "verification":
                None,

            "rollback":
                None,
        }

        self.audit(
            "CYCLE_STARTED",
            {
                "cycle_id":
                    cycle_id
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

            should_proactive = (
                PROACTIVE_WORK_ENABLED

                and

                self.total_cycles
                %
                PROACTIVE_EVERY_N_CYCLES
                == 0
            )

            if findings:
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

                cycle[
                    "mode_executed"
                ] = (
                    "REPAIR"
                )

                self.repair_cycles += 1

                command, request = (
                    build_repair_objective(
                        cycle_id,
                        findings,
                        inspection,
                    )
                )

            elif should_proactive:
                cycle[
                    "status"
                ] = (
                    "PROACTIVE_WORK"
                )

                cycle.update(
                    bilingual(
                        "المنصة سليمة؛ بدأ العقل المدبر دورة تطوير وتشغيل استباقية.",
                        "Platform is healthy; mastermind started a proactive operation cycle.",
                    )
                )

                cycle[
                    "mode_executed"
                ] = (
                    "PROACTIVE"
                )

                self.proactive_cycles += 1

                command, request = (
                    build_proactive_objective(
                        cycle_id,
                        inspection,
                    )
                )

            else:
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

                self.successful_cycles += 1

                cycle[
                    "finished_at"
                ] = utc_now()

                save_json(
                    AUTONOMOUS_LATEST_REPORT,
                    cycle,
                )

                self.save_state(
                    "RUNNING_HEALTHY",
                    cycle,
                )

                return cycle

            backup = (
                create_source_backup(
                    cycle_id
                )
            )

            cycle[
                "backup"
            ] = backup

            objective_kind = (
                cycle[
                    "mode_executed"
                ]
                or
                "AUTONOMOUS"
            )

            mastermind_result = (
                self.execute_mastermind_objective(
                    cycle_id=
                        cycle_id,

                    command=
                        command,

                    request=
                        request,

                    objective_kind=
                        objective_kind,
                )
            )

            cycle[
                "mastermind"
            ] = mastermind_result

            verification = (
                self.verify_after_autonomous_change(
                    cycle_id=
                        cycle_id,

                    before_inspection=
                        inspection,
                )
            )

            cycle[
                "verification"
            ] = verification

            objective_ok = bool(
                mastermind_result.get(
                    "success"
                )
            )

            verification_ok = bool(
                verification.get(
                    "success"
                )
            )

            if (
                objective_ok
                and
                verification_ok
            ):
                cycle[
                    "success"
                ] = True

                if (
                    objective_kind
                    == "REPAIR"
                ):
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

                else:
                    cycle[
                        "status"
                    ] = (
                        "PROACTIVE_WORK_COMPLETED"
                    )

                    cycle.update(
                        status_message(
                            "PROACTIVE_WORK_COMPLETED"
                        )
                    )

                self.successful_cycles += 1

            else:
                rollback = (
                    rollback_source_backup(
                        cycle_id
                    )
                )

                cycle[
                    "rollback"
                ] = rollback

                rollback_verification = (
                    self.inspect_platform()
                )

                cycle[
                    "rollback_verification"
                ] = rollback_verification

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

            self.audit(
                "CYCLE_FINISHED",
                {
                    "cycle_id":
                        cycle_id,

                    "success":
                        cycle[
                            "success"
                        ],

                    "status":
                        cycle[
                            "status"
                        ],

                    "mode":
                        cycle[
                            "mode_executed"
                        ],
                },
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

            if (
                cycle.get(
                    "backup",
                    {},
                ).get(
                    "success"
                )
            ):
                cycle[
                    "rollback"
                ] = rollback_source_backup(
                    cycle_id
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

            self.audit(
                "CYCLE_EXCEPTION",
                {
                    "cycle_id":
                        cycle_id,

                    "error":
                        cycle[
                            "error"
                        ],
                },
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

            and

            time.monotonic()
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

                "proactive_work_enabled":
                    PROACTIVE_WORK_ENABLED,
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
                                "AUTONOMOUS_COMPANY_WIDE",

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

                            "work_mode":
                                cycle.get(
                                    "mode_executed"
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

                            "source_changes":
                                (
                                    cycle.get(
                                        "verification",
                                        {},
                                    )
                                    .get(
                                        "checks",
                                        {},
                                    )
                                    .get(
                                        "source_changes",
                                        {},
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
# SERVICE INSTALLATION
# ============================================================

def install_systemd_service() -> Dict[str, Any]:
    if os.geteuid() != 0:
        return {
            "success":
                False,

            "status":
                "ROOT_REQUIRED",

            **bilingual(
                "تثبيت الخدمة يحتاج صلاحية root.",
                "Installing the service requires root privileges.",
            ),
        }

    python_path = (
        shutil.which(
            "python3"
        )
        or
        sys.executable
    )

    service_text = f"""[Unit]
Description=MAJD Sovereign Autonomous Company Runtime
After=network-online.target docker.service
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory={ROOT_DIR}
ExecStart={python_path} {Path(__file__).resolve()} --autonomous
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1
Environment=MAJD_PROACTIVE_WORK_ENABLED=true

[Install]
WantedBy=multi-user.target
"""

    try:
        SERVICE_FILE.write_text(
            service_text,
            encoding="utf-8",
        )

    except Exception as error:
        return {
            "success":
                False,

            "status":
                "SERVICE_FILE_WRITE_FAILED",

            "error":
                f"{type(error).__name__}: "
                f"{error}",
        }

    reload_result = run_process(
        [
            "systemctl",
            "daemon-reload",
        ],
        timeout=30,
    )

    enable_result = run_process(
        [
            "systemctl",
            "enable",
            "--now",
            SERVICE_NAME,
        ],
        timeout=60,
    )

    status_result = run_process(
        [
            "systemctl",
            "--no-pager",
            "--full",
            "status",
            SERVICE_NAME,
        ],
        timeout=30,
    )

    success = bool(
        reload_result.get(
            "success"
        )
        and
        enable_result.get(
            "success"
        )
    )

    return {
        "success":
            success,

        "status":
            (
                "SERVICE_INSTALLED"
                if success
                else
                "SERVICE_INSTALL_FAILED"
            ),

        "service_file":
            str(
                SERVICE_FILE
            ),

        "daemon_reload":
            reload_result,

        "enable_now":
            enable_result,

        "service_status":
            status_result,

        **bilingual(
            (
                "تم تثبيت تشغيل مجد الذاتي كخدمة دائمة."
                if success
                else
                "فشل تثبيت خدمة مجد الدائمة."
            ),
            (
                "MAJD autonomous runtime was installed as a permanent service."
                if success
                else
                "Failed to install the permanent MAJD service."
            ),
        ),
    }


def systemd_service_status() -> Dict[str, Any]:
    result = run_process(
        [
            "systemctl",
            "--no-pager",
            "--full",
            "status",
            SERVICE_NAME,
        ],
        timeout=30,
    )

    return {
        "success":
            bool(
                result.get(
                    "success"
                )
            ),

        "status":
            (
                "SERVICE_RUNNING"
                if result.get(
                    "success"
                )
                else
                "SERVICE_NOT_RUNNING"
            ),

        "details":
            result,
    }


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
    return (
        MajdFullExecutionRuntime()
        .execute(
            command=
                command,

            owner=
                owner,
        )
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

    return (
        MajdAutonomousRuntime(
            owner=
                owner,

            cycle_seconds=
                cycle_seconds,
        )
        .run_once()
    )


def run_autonomous_forever(
    owner: str = DEFAULT_OWNER,
    cycle_seconds: int = DEFAULT_CYCLE_SECONDS,
    **kwargs: Any,
) -> int:
    install_signal_handlers()

    return (
        MajdAutonomousRuntime(
            owner=
                owner,

            cycle_seconds=
                cycle_seconds,
        )
        .run_forever()
    )


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
        and
        pid > 0
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
            "MAJD SOVEREIGN AUTONOMOUS COMPANY-WIDE RUNTIME 06 / "
            "المشغّل السيادي الذاتي الشامل لمجد"
        )
    )

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
            "Run persistent autonomous runtime / "
            "تشغيل ذاتي دائم"
        ),
    )

    parser.add_argument(
        "--once",
        action=
            "store_true",

        help=(
            "Run one full autonomous cycle / "
            "تشغيل دورة ذاتية شاملة واحدة"
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
            "Seconds between cycles / "
            "الثواني بين الدورات"
        ),
    )

    parser.add_argument(
        "--install-service",
        action=
            "store_true",

        help=(
            "Install and start permanent systemd service / "
            "تثبيت الخدمة الدائمة"
        ),
    )

    parser.add_argument(
        "--service-status",
        action=
            "store_true",

        help=(
            "Show permanent service status / "
            "عرض حالة الخدمة الدائمة"
        ),
    )

    args = (
        parser.parse_args()
    )

    if args.install_service:
        result = (
            install_systemd_service()
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

    if args.service_status:
        result = (
            systemd_service_status()
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
        "المشغّل السيادي الكامل لمجد"
    )

    print(
        "=============================================="
    )

    print(
        f"OWNER / المالك: "
        f"{args.owner}"
    )

    print(
        f"COMMAND / الأمر: "
        f"{command}"
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

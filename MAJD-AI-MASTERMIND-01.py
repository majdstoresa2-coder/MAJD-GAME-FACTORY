#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-AI-MASTERMIND-01.py
============================================================

MAJD SOVEREIGN AUTONOMOUS MASTERMIND
COMPLETE REPLACEMENT BUILD

المسؤول المركزي عن:
- استقبال أوامر المالك.
- اكتشاف ملفات MAJD 01–10 الموجودة فعلياً.
- اكتشاف واجهات وقدرات المكونات بدون افتراض أسماء غير موجودة.
- إنشاء Capability Registry.
- تخطيط الأهداف.
- اختيار المنفذ الحقيقي المناسب.
- تنفيذ الأوامر.
- فحص Python.
- فحص Imports.
- فحص Interfaces.
- اكتشاف الأخطاء.
- النسخ الاحتياطي.
- الإصلاح الذاتي.
- إعادة الاختبار.
- Rollback عند Regression.
- تشغيل مصنع الألعاب الحقيقي.
- التحقق من Artifact.
- النشر عبر الجسر الرسمي.
- التحقق من النشر.
- إدارة المحتوى والإعلام عند توفر المكونات.
- إدارة Social / Live عند توفر المكونات.
- Security Monitoring.
- Content Safety.
- Electronic Legal Assistant orchestration.
- Owner Dashboard state.
- Continuous Monitoring.
- Audit Logging.
- منع النجاح الوهمي.

قاعدة أساسية:
أي Capability غير موجودة فعلياً لا تعتبر جاهزة.
أي Adapter خارجي غير متصل يظهر NOT_CONNECTED أو UNAVAILABLE.
أي عملية لم يتم التحقق منها لا تعتبر SUCCESS.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import inspect
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
import urllib.request
import uuid

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple


# ============================================================
# IDENTITY
# ============================================================

SYSTEM_NAME = "MAJD-GAME-FACTORY"
MASTERMIND_NAME = "MAJD-SOVEREIGN-MASTERMIND"
VERSION = "4.0.0"

DEFAULT_OWNER = "MAJD"

MAX_REPAIR_ATTEMPTS = int(
    os.getenv("MAJD_MAX_REPAIR_ATTEMPTS", "5")
)

COMMAND_TIMEOUT = int(
    os.getenv("MAJD_COMMAND_TIMEOUT", "900")
)

AI_TIMEOUT = int(
    os.getenv("MAJD_AI_TIMEOUT", "180")
)

MONITOR_INTERVAL = int(
    os.getenv("MAJD_MONITOR_INTERVAL", "300")
)


# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent

STATE_DIR = ROOT_DIR / "majd_factory_state"
MASTERMIND_STATE_DIR = STATE_DIR / "mastermind"
LOG_DIR = STATE_DIR / "logs"
BACKUP_DIR = STATE_DIR / "backups"
DASHBOARD_DIR = STATE_DIR / "dashboard"
SECURITY_DIR = STATE_DIR / "security"
LEGAL_DIR = STATE_DIR / "legal"
MONITOR_DIR = STATE_DIR / "monitor"
REGISTRY_DIR = STATE_DIR / "registry"

OUTPUT_DIR = ROOT_DIR / "majd_game_output"

for directory in (
    STATE_DIR,
    MASTERMIND_STATE_DIR,
    LOG_DIR,
    BACKUP_DIR,
    DASHBOARD_DIR,
    SECURITY_DIR,
    LEGAL_DIR,
    MONITOR_DIR,
    REGISTRY_DIR,
    OUTPUT_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)


# ============================================================
# KNOWN OFFICIAL COMPONENT NUMBERS
# ============================================================

OFFICIAL_NUMBERS = tuple(
    f"{number:02d}"
    for number in range(1, 11)
)

THIS_FILE = Path(__file__).resolve()

KNOWN_CORE_FILES = {
    "01": "MAJD-AI-MASTERMIND-01.py",
    "02": "MAJD-OWNER-COMMAND-CENTER-02.py",
    "03": "MAJD-REAL-GAME-EXECUTOR-03.py",
    "04": "MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py",
    "05": "MAJD-AI-ORCHESTRATOR-05.py",
    "06": "MAJD-FULL-EXECUTION-RUNTIME-06.py",
}

AGENT_FILE = ROOT_DIR / "majd_ai_agent.py"


# ============================================================
# LOCAL AI
# ============================================================

LOCAL_AI_URL = os.getenv(
    "MAJD_LOCAL_AI_URL",
    "",
).strip()

LOCAL_AI_MODEL = os.getenv(
    "MAJD_LOCAL_AI_MODEL",
    "majd-sovereign",
).strip()


# ============================================================
# TIME
# ============================================================

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ============================================================
# JSON
# ============================================================

def write_json(
    path: Path,
    value: Any,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary = path.with_suffix(
        path.suffix + ".tmp"
    )

    with temporary.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            value,
            file,
            ensure_ascii=False,
            indent=2,
            default=str,
        )
        file.flush()
        os.fsync(file.fileno())

    temporary.replace(path)


def read_json(
    path: Path,
    default: Any = None,
) -> Any:
    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)
    except Exception:
        return default


# ============================================================
# HASH
# ============================================================

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        while True:
            chunk = file.read(1024 * 1024)

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


# ============================================================
# PATH SAFETY
# ============================================================

def is_inside_root(path: Path) -> bool:
    try:
        path.resolve().relative_to(
            ROOT_DIR.resolve()
        )
        return True
    except Exception:
        return False


def safe_project_path(
    value: str | Path,
) -> Path:
    candidate = Path(value)

    if not candidate.is_absolute():
        candidate = ROOT_DIR / candidate

    candidate = candidate.resolve()

    if not is_inside_root(candidate):
        raise PermissionError(
            "Refusing path outside MAJD-GAME-FACTORY"
        )

    return candidate


# ============================================================
# MODULE LOADER
# ============================================================

def load_module(
    path: Path,
    name: Optional[str] = None,
) -> Any:
    path = safe_project_path(path)

    if not path.exists():
        raise FileNotFoundError(path.name)

    module_name = (
        name
        or
        f"_majd_dynamic_{uuid.uuid4().hex}"
    )

    specification = (
        importlib.util.spec_from_file_location(
            module_name,
            str(path),
        )
    )

    if (
        specification is None
        or specification.loader is None
    ):
        raise ImportError(
            f"Unable to load {path.name}"
        )

    module = (
        importlib.util.module_from_spec(
            specification
        )
    )

    sys.modules[module_name] = module

    specification.loader.exec_module(module)

    return module


# ============================================================
# SUPPORTED CALL
# ============================================================

def call_supported(
    function: Callable[..., Any],
    values: Dict[str, Any],
) -> Any:
    try:
        signature = inspect.signature(function)
    except (TypeError, ValueError):
        return function(**values)

    accepts_kwargs = any(
        parameter.kind
        == inspect.Parameter.VAR_KEYWORD
        for parameter
        in signature.parameters.values()
    )

    kwargs = {
        key: value
        for key, value in values.items()
        if (
            accepts_kwargs
            or key in signature.parameters
        )
    }

    return function(**kwargs)


# ============================================================
# RESULT NORMALIZATION
# ============================================================

def normalize_result(
    value: Any,
) -> Dict[str, Any]:
    if isinstance(value, dict):
        result = dict(value)

        # Never manufacture success.
        if "success" not in result:
            result["success"] = False
            result.setdefault(
                "status",
                "UNVERIFIED_COMPONENT_RESULT",
            )

        return result

    if value is None:
        return {
            "success": False,
            "status": "COMPONENT_RETURNED_NONE",
        }

    return {
        "success": False,
        "status": "UNVERIFIED_COMPONENT_RESULT",
        "result": str(value),
    }


# ============================================================
# PROCESS EXECUTION
# ============================================================

@dataclass
class CommandResult:
    command: List[str]
    returncode: int
    stdout: str
    stderr: str
    success: bool
    duration_seconds: float


class ProcessExecutor:

    BLOCKED_COMMANDS = {
        "reboot",
        "shutdown",
        "poweroff",
        "halt",
        "mkfs",
        "fdisk",
        "parted",
    }

    def run(
        self,
        command: List[str],
        cwd: Optional[Path] = None,
        timeout: int = COMMAND_TIMEOUT,
    ) -> CommandResult:

        if not command:
            return CommandResult(
                command=[],
                returncode=1,
                stdout="",
                stderr="Empty command",
                success=False,
                duration_seconds=0.0,
            )

        executable = Path(
            str(command[0])
        ).name.lower()

        if executable in self.BLOCKED_COMMANDS:
            return CommandResult(
                command=command,
                returncode=126,
                stdout="",
                stderr=(
                    "Blocked destructive command: "
                    f"{executable}"
                ),
                success=False,
                duration_seconds=0.0,
            )

        working_directory = safe_project_path(
            cwd or ROOT_DIR
        )

        started = time.time()

        try:
            completed = subprocess.run(
                command,
                cwd=str(working_directory),
                capture_output=True,
                text=True,
                timeout=timeout,
                env=os.environ.copy(),
            )

            return CommandResult(
                command=command,
                returncode=completed.returncode,
                stdout=completed.stdout or "",
                stderr=completed.stderr or "",
                success=(
                    completed.returncode == 0
                ),
                duration_seconds=(
                    time.time() - started
                ),
            )

        except subprocess.TimeoutExpired as error:
            return CommandResult(
                command=command,
                returncode=124,
                stdout=(
                    error.stdout
                    if isinstance(error.stdout, str)
                    else ""
                ),
                stderr="Command timed out.",
                success=False,
                duration_seconds=(
                    time.time() - started
                ),
            )

        except Exception as error:
            return CommandResult(
                command=command,
                returncode=1,
                stdout="",
                stderr=(
                    f"{type(error).__name__}: "
                    f"{error}"
                ),
                success=False,
                duration_seconds=(
                    time.time() - started
                ),
            )


# ============================================================
# AUDIT
# ============================================================

class AuditLogger:

    def __init__(
        self,
        operation_id: str,
    ):
        self.operation_id = operation_id
        self.path = (
            LOG_DIR / f"{operation_id}.jsonl"
        )

    def log(
        self,
        event: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        record = {
            "time": utc_now(),
            "operation_id": self.operation_id,
            "event": event,
            "data": data or {},
        }

        with self.path.open(
            "a",
            encoding="utf-8",
        ) as file:
            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                    default=str,
                )
                + "\n"
            )


# ============================================================
# BACKUP / ROLLBACK
# ============================================================

class BackupManager:

    def __init__(
        self,
        operation_id: str,
    ):
        self.operation_id = operation_id

        self.root = (
            BACKUP_DIR / operation_id
        )

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.manifest: Dict[str, str] = {}

    def backup(
        self,
        path: Path,
    ) -> Optional[str]:
        path = safe_project_path(path)

        if not path.exists():
            return None

        relative = path.relative_to(ROOT_DIR)
        target = self.root / relative

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if path.is_dir():
            if target.exists():
                shutil.rmtree(target)

            shutil.copytree(path, target)

        else:
            shutil.copy2(path, target)

        self.manifest[str(relative)] = str(target)

        return str(target)

    def restore(
        self,
        path: Path,
    ) -> Dict[str, Any]:
        path = safe_project_path(path)

        relative = str(
            path.relative_to(ROOT_DIR)
        )

        backup_value = self.manifest.get(relative)

        if not backup_value:
            return {
                "success": False,
                "status": "BACKUP_NOT_FOUND",
                "path": relative,
            }

        backup = Path(backup_value)

        if not backup.exists():
            return {
                "success": False,
                "status": "BACKUP_NOT_FOUND",
                "path": relative,
            }

        if backup.is_dir():
            if path.exists():
                shutil.rmtree(path)

            shutil.copytree(backup, path)

        else:
            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            shutil.copy2(backup, path)

        return {
            "success": True,
            "status": "ROLLBACK_COMPLETED",
            "path": relative,
        }


# ============================================================
# STATIC PYTHON DISCOVERY
# ============================================================

class StaticPythonDiscovery:

    @staticmethod
    def discover(
        path: Path,
    ) -> Dict[str, Any]:

        result: Dict[str, Any] = {
            "functions": [],
            "async_functions": [],
            "classes": [],
            "imports": [],
        }

        try:
            source = path.read_text(
                encoding="utf-8"
            )

            tree = ast.parse(
                source,
                filename=str(path),
            )

            for node in tree.body:
                if isinstance(
                    node,
                    ast.FunctionDef,
                ):
                    result["functions"].append(
                        node.name
                    )

                elif isinstance(
                    node,
                    ast.AsyncFunctionDef,
                ):
                    result[
                        "async_functions"
                    ].append(node.name)

                elif isinstance(
                    node,
                    ast.ClassDef,
                ):
                    result["classes"].append(
                        node.name
                    )

                elif isinstance(
                    node,
                    ast.Import,
                ):
                    for item in node.names:
                        result["imports"].append(
                            item.name
                        )

                elif isinstance(
                    node,
                    ast.ImportFrom,
                ):
                    if node.module:
                        result["imports"].append(
                            node.module
                        )

            result["success"] = True

        except Exception as error:
            result["success"] = False
            result["error"] = (
                f"{type(error).__name__}: {error}"
            )

        return result


# ============================================================
# COMPONENT
# ============================================================

@dataclass
class ComponentRecord:
    number: str
    filename: str
    path: str
    exists: bool
    size: int = 0
    sha256: Optional[str] = None
    importable: bool = False
    static_functions: List[str] = field(
        default_factory=list
    )
    static_async_functions: List[str] = field(
        default_factory=list
    )
    static_classes: List[str] = field(
        default_factory=list
    )
    runtime_callables: List[str] = field(
        default_factory=list
    )
    capabilities: List[str] = field(
        default_factory=list
    )
    error: Optional[str] = None


# ============================================================
# COMPONENT DISCOVERY 01–10
# ============================================================

class ComponentDiscovery:

    FILE_NUMBER_PATTERN = re.compile(
        r"(?:^|[-_])([0-9]{2})(?:\.py$|[-_])",
        re.IGNORECASE,
    )

    IGNORE = {
        ".git",
        "__pycache__",
        "node_modules",
        ".venv",
        "venv",
        "majd_factory_state",
        "majd_game_output",
    }

    CAPABILITY_WORDS = {
        "game": "GAME",
        "executor": "EXECUTION",
        "execute": "EXECUTION",
        "publish": "PUBLISH",
        "platform": "PLATFORM",
        "owner": "OWNER_COMMAND",
        "command": "OWNER_COMMAND",
        "orchestrator": "ORCHESTRATION",
        "orchestrate": "ORCHESTRATION",
        "runtime": "RUNTIME",
        "content": "CONTENT",
        "media": "MEDIA",
        "video": "VIDEO",
        "movie": "MOVIE",
        "film": "MOVIE",
        "series": "SERIES",
        "audio": "AUDIO",
        "voice": "VOICE",
        "music": "MUSIC",
        "image": "IMAGE",
        "social": "SOCIAL",
        "live": "LIVE",
        "stream": "LIVE",
        "agency": "AGENCY",
        "payment": "PAYMENTS",
        "wallet": "WALLET",
        "ads": "ADS",
        "advert": "ADS",
        "dashboard": "DASHBOARD",
        "security": "SECURITY",
        "legal": "LEGAL",
        "contract": "LEGAL",
        "monitor": "MONITORING",
        "health": "HEALTH",
        "repair": "REPAIR",
        "diagnose": "DIAGNOSTICS",
        "test": "TESTING",
        "verify": "VERIFICATION",
        "build": "BUILD",
    }

    def discover_files(
        self,
    ) -> Dict[str, List[Path]]:

        discovered: Dict[
            str,
            List[Path]
        ] = {
            number: []
            for number in OFFICIAL_NUMBERS
        }

        for path in ROOT_DIR.glob("*.py"):

            if not path.is_file():
                continue

            match = self.FILE_NUMBER_PATTERN.search(
                path.name
            )

            if not match:
                continue

            number = match.group(1)

            if number in discovered:
                discovered[number].append(
                    path.resolve()
                )

        for number, filename in (
            KNOWN_CORE_FILES.items()
        ):
            path = (
                ROOT_DIR / filename
            ).resolve()

            if (
                number in discovered
                and path.exists()
                and path not in discovered[number]
            ):
                discovered[number].insert(
                    0,
                    path,
                )

        return discovered

    def infer_capabilities(
        self,
        filename: str,
        functions: Iterable[str],
        classes: Iterable[str],
    ) -> List[str]:

        text = " ".join(
            [
                filename,
                *functions,
                *classes,
            ]
        ).lower()

        capabilities: Set[str] = set()

        for word, capability in (
            self.CAPABILITY_WORDS.items()
        ):
            if word in text:
                capabilities.add(capability)

        return sorted(capabilities)

    def inspect_file(
        self,
        number: str,
        path: Path,
        runtime_import: bool = True,
    ) -> ComponentRecord:

        static = (
            StaticPythonDiscovery.discover(path)
        )

        record = ComponentRecord(
            number=number,
            filename=path.name,
            path=str(path),
            exists=path.exists(),
            size=(
                path.stat().st_size
                if path.exists()
                else 0
            ),
            sha256=(
                sha256_file(path)
                if path.exists()
                else None
            ),
        )

        record.static_functions = list(
            static.get("functions", [])
        )

        record.static_async_functions = list(
            static.get(
                "async_functions",
                [],
            )
        )

        record.static_classes = list(
            static.get("classes", [])
        )

        if not static.get("success"):
            record.error = static.get("error")

        if (
            runtime_import
            and number != "01"
            and static.get("success")
        ):
            try:
                module = load_module(
                    path,
                    (
                        f"_majd_discovery_"
                        f"{number}_"
                        f"{uuid.uuid4().hex}"
                    ),
                )

                record.importable = True

                record.runtime_callables = sorted(
                    name
                    for name in dir(module)
                    if (
                        not name.startswith("_")
                        and callable(
                            getattr(
                                module,
                                name,
                                None,
                            )
                        )
                    )
                )

            except Exception as error:
                record.importable = False
                record.error = (
                    f"{type(error).__name__}: "
                    f"{error}"
                )

        elif number == "01":
            record.importable = True
            record.runtime_callables = list(
                record.static_functions
            )

        record.capabilities = (
            self.infer_capabilities(
                record.filename,
                (
                    record.runtime_callables
                    or record.static_functions
                ),
                record.static_classes,
            )
        )

        return record

    def discover(
        self,
        runtime_import: bool = True,
    ) -> Dict[str, Any]:

        files = self.discover_files()

        components: Dict[
            str,
            List[Dict[str, Any]]
        ] = {}

        for number in OFFICIAL_NUMBERS:
            records = []

            for path in files[number]:
                records.append(
                    asdict(
                        self.inspect_file(
                            number,
                            path,
                            runtime_import=runtime_import,
                        )
                    )
                )

            components[number] = records

        missing = [
            number
            for number in OFFICIAL_NUMBERS
            if not components[number]
        ]

        result = {
            "success": True,
            "generated_at": utc_now(),
            "components": components,
            "missing_numbers": missing,
        }

        write_json(
            REGISTRY_DIR / "components.json",
            result,
        )

        return result


# ============================================================
# CAPABILITY REGISTRY
# ============================================================

class CapabilityRegistry:

    GENERIC_ENTRYPOINTS = (
        "execute_request",
        "process_request",
        "process_command",
        "run_command",
        "execute",
        "run",
    )

    CAPABILITY_ENTRYPOINTS = {
        "GAME": (
            "execute_game_request",
            "create_game",
            "build_game",
            "generate_game",
        ),
        "PUBLISH": (
            "publish_game",
            "publish",
            "send_game",
            "send_to_majd",
        ),
        "CONTENT": (
            "create_content",
            "generate_content",
            "process_content",
        ),
        "MEDIA": (
            "create_media",
            "generate_media",
            "process_media",
        ),
        "SOCIAL": (
            "publish_social",
            "process_social",
            "social_publish",
        ),
        "LIVE": (
            "start_live",
            "process_live",
            "stream",
        ),
        "PAYMENTS": (
            "process_payment",
            "execute_payment",
        ),
        "ADS": (
            "process_ad",
            "publish_ad",
            "create_ad",
        ),
        "LEGAL": (
            "review_contract",
            "generate_contract",
            "legal_review",
        ),
        "SECURITY": (
            "security_check",
            "scan_security",
        ),
        "MONITORING": (
            "health",
            "health_check",
            "status",
            "monitor",
        ),
        "REPAIR": (
            "repair",
            "repair_system",
            "auto_repair",
        ),
    }

    def __init__(
        self,
        discovery: ComponentDiscovery,
    ):
        self.discovery = discovery
        self.registry: Dict[
            str,
            List[Dict[str, Any]]
        ] = {}

    def build(self) -> Dict[str, Any]:

        report = self.discovery.discover(
            runtime_import=True
        )

        registry: Dict[
            str,
            List[Dict[str, Any]]
        ] = {}

        for number, records in (
            report["components"].items()
        ):
            for record in records:

                callables = set(
                    record.get(
                        "runtime_callables",
                        [],
                    )
                    or record.get(
                        "static_functions",
                        [],
                    )
                )

                capabilities = set(
                    record.get(
                        "capabilities",
                        [],
                    )
                )

                for capability in capabilities:

                    preferred = (
                        self.CAPABILITY_ENTRYPOINTS
                        .get(
                            capability,
                            (),
                        )
                    )

                    entrypoints = [
                        name
                        for name in preferred
                        if name in callables
                    ]

                    entrypoints.extend(
                        name
                        for name
                        in self.GENERIC_ENTRYPOINTS
                        if (
                            name in callables
                            and name not in entrypoints
                        )
                    )

                    registry.setdefault(
                        capability,
                        [],
                    ).append(
                        {
                            "number": number,
                            "filename": record[
                                "filename"
                            ],
                            "path": record["path"],
                            "entrypoints": entrypoints,
                            "importable": record.get(
                                "importable",
                                False,
                            ),
                        }
                    )

        self.registry = registry

        result = {
            "success": True,
            "generated_at": utc_now(),
            "capabilities": registry,
            "available": sorted(
                registry.keys()
            ),
        }

        write_json(
            REGISTRY_DIR / "capabilities.json",
            result,
        )

        return result

    def providers(
        self,
        capability: str,
    ) -> List[Dict[str, Any]]:
        return list(
            self.registry.get(
                capability.upper(),
                [],
            )
        )


# ============================================================
# PYTHON CHECKER
# ============================================================

class PythonChecker:

    def __init__(
        self,
        executor: ProcessExecutor,
    ):
        self.executor = executor

    def compile_file(
        self,
        path: Path,
    ) -> CommandResult:

        return self.executor.run(
            [
                sys.executable,
                "-m",
                "py_compile",
                str(path),
            ],
            cwd=ROOT_DIR,
        )

    def compile_project(
        self,
    ) -> Dict[str, Any]:

        checked = []
        failed = []

        for path in sorted(
            ROOT_DIR.glob("*.py")
        ):
            result = self.compile_file(path)

            item = {
                "file": path.name,
                "success": result.success,
                "stderr": result.stderr[-6000:],
            }

            checked.append(item)

            if not result.success:
                failed.append(item)

        return {
            "success": not failed,
            "checked": checked,
            "failed": failed,
        }


# ============================================================
# DEPENDENCY MANAGER
# ============================================================

class DependencyManager:

    PYTHON_IMPORT_MAP = {
        "PIL": "pillow",
        "yaml": "pyyaml",
        "cv2": "opencv-python",
        "sklearn": "scikit-learn",
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
    }

    def __init__(
        self,
        executor: ProcessExecutor,
        logger: AuditLogger,
    ):
        self.executor = executor
        self.logger = logger

    def detect_virtual_python(
        self,
    ) -> Optional[Path]:

        candidates = [
            ROOT_DIR / ".venv" / "bin" / "python",
            ROOT_DIR / "venv" / "bin" / "python",
            ROOT_DIR / ".venv" / "Scripts" / "python.exe",
            ROOT_DIR / "venv" / "Scripts" / "python.exe",
        ]

        for candidate in candidates:
            if candidate.exists():
                return candidate

        return None

    def repair_missing_python_module(
        self,
        error_text: str,
    ) -> Dict[str, Any]:

        match = re.search(
            r"No module named ['\"]([^'\"]+)['\"]",
            error_text,
            re.IGNORECASE,
        )

        if not match:
            return {
                "success": False,
                "status": (
                    "DEPENDENCY_NAME_NOT_DETECTED"
                ),
            }

        module = (
            match.group(1)
            .split(".")[0]
        )

        package = (
            self.PYTHON_IMPORT_MAP.get(
                module,
                module,
            )
        )

        python_binary = (
            self.detect_virtual_python()
        )

        if python_binary is None:
            return {
                "success": False,
                "status": (
                    "VIRTUAL_ENVIRONMENT_REQUIRED"
                ),
                "module": module,
                "package": package,
                "message": (
                    "Dependency repair refused "
                    "because no project virtual "
                    "environment was detected."
                ),
            }

        self.logger.log(
            "DEPENDENCY_REPAIR_STARTED",
            {
                "module": module,
                "package": package,
                "python": str(python_binary),
            },
        )

        result = self.executor.run(
            [
                str(python_binary),
                "-m",
                "pip",
                "install",
                package,
            ],
            cwd=ROOT_DIR,
            timeout=600,
        )

        return asdict(result)


# ============================================================
# LOCAL AI ADAPTER
# ============================================================

class LocalAIAdapter:

    def __init__(
        self,
        logger: AuditLogger,
    ):
        self.logger = logger

    @property
    def available(self) -> bool:
        return bool(LOCAL_AI_URL)

    def status(self) -> Dict[str, Any]:
        return {
            "configured": bool(LOCAL_AI_URL),
            "model": (
                LOCAL_AI_MODEL
                if LOCAL_AI_URL
                else None
            ),
            "status": (
                "CONFIGURED"
                if LOCAL_AI_URL
                else "NOT_CONNECTED"
            ),
        }

    def ask(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> Optional[str]:

        if not self.available:
            return None

        endpoint = (
            LOCAL_AI_URL.rstrip("/")
            + "/v1/chat/completions"
        )

        payload = {
            "model": LOCAL_AI_MODEL,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        }

        request = urllib.request.Request(
            endpoint,
            data=json.dumps(
                payload
            ).encode("utf-8"),
            headers={
                "Content-Type":
                    "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=AI_TIMEOUT,
            ) as response:
                body = json.loads(
                    response.read().decode(
                        "utf-8"
                    )
                )

            choices = (
                body.get("choices")
                or []
            )

            if not choices:
                return None

            return (
                choices[0]
                .get("message", {})
                .get("content")
            )

        except Exception as error:
            self.logger.log(
                "LOCAL_AI_ERROR",
                {
                    "error": (
                        f"{type(error).__name__}: "
                        f"{error}"
                    )
                },
            )

            return None


# ============================================================
# CODE MANAGER
# ============================================================

class CodeManager:

    def __init__(
        self,
        backup: BackupManager,
        logger: AuditLogger,
        checker: PythonChecker,
    ):
        self.backup = backup
        self.logger = logger
        self.checker = checker

    def replace_python_file(
        self,
        path: Path,
        content: str,
    ) -> Dict[str, Any]:

        path = safe_project_path(path)

        if path.suffix.lower() != ".py":
            return {
                "success": False,
                "status": "NON_PYTHON_REPAIR_REFUSED",
            }

        backup_path = self.backup.backup(path)

        before_hash = (
            sha256_file(path)
            if path.exists()
            else None
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            content,
            encoding="utf-8",
        )

        compile_result = (
            self.checker.compile_file(path)
        )

        if not compile_result.success:
            rollback = self.backup.restore(path)

            return {
                "success": False,
                "status": (
                    "REPAIR_REGRESSION_ROLLED_BACK"
                ),
                "compile": asdict(
                    compile_result
                ),
                "rollback": rollback,
            }

        after_hash = sha256_file(path)

        result = {
            "success": True,
            "status": "FILE_REPLACED_AND_COMPILED",
            "path": str(path),
            "backup": backup_path,
            "before_sha256": before_hash,
            "after_sha256": after_hash,
        }

        self.logger.log(
            "FILE_REPLACED",
            result,
        )

        return result


# ============================================================
# DIAGNOSTICS
# ============================================================

class DiagnosticEngine:

    def diagnose(
        self,
        failure: Dict[str, Any],
    ) -> Dict[str, Any]:

        text = json.dumps(
            failure,
            ensure_ascii=False,
            default=str,
        )

        lowered = text.lower()

        if (
            "no module named" in lowered
            or "modulenotfounderror" in lowered
        ):
            return {
                "type": "MISSING_PYTHON_MODULE",
                "repairable": True,
                "details": text[-10000:],
            }

        if (
            "syntaxerror" in lowered
            or "indentationerror" in lowered
            or "taberror" in lowered
        ):
            return {
                "type": "PYTHON_SYNTAX_ERROR",
                "repairable": True,
                "details": text[-10000:],
            }

        if "interface" in lowered:
            return {
                "type": "INTERFACE_MISMATCH",
                "repairable": True,
                "details": text[-10000:],
            }

        if "artifact" in lowered:
            return {
                "type": "ARTIFACT_FAILURE",
                "repairable": True,
                "details": text[-10000:],
            }

        if (
            "publish" in lowered
            or "publication" in lowered
        ):
            return {
                "type": "PUBLICATION_FAILURE",
                "repairable": True,
                "details": text[-10000:],
            }

        return {
            "type": "UNKNOWN",
            "repairable": False,
            "details": text[-10000:],
        }


# ============================================================
# AUTONOMOUS REPAIR
# ============================================================

class AutonomousRepairEngine:

    def __init__(
        self,
        operation_id: str,
        logger: AuditLogger,
        checker: PythonChecker,
    ):
        self.operation_id = operation_id
        self.logger = logger
        self.executor = ProcessExecutor()
        self.backup = BackupManager(
            operation_id
        )
        self.dependencies = DependencyManager(
            self.executor,
            logger,
        )
        self.ai = LocalAIAdapter(logger)
        self.code = CodeManager(
            self.backup,
            logger,
            checker,
        )

    def repair(
        self,
        diagnosis: Dict[str, Any],
        failure: Dict[str, Any],
    ) -> Dict[str, Any]:

        repair_type = diagnosis.get("type")

        if repair_type == "MISSING_PYTHON_MODULE":
            return (
                self.dependencies
                .repair_missing_python_module(
                    json.dumps(
                        failure,
                        ensure_ascii=False,
                        default=str,
                    )
                )
            )

        if repair_type not in {
            "PYTHON_SYNTAX_ERROR",
            "INTERFACE_MISMATCH",
            "ARTIFACT_FAILURE",
            "PUBLICATION_FAILURE",
        }:
            return {
                "success": False,
                "status": (
                    "AUTOMATIC_REPAIR_NOT_AVAILABLE"
                ),
                "diagnosis": diagnosis,
            }

        if not self.ai.available:
            return {
                "success": False,
                "status": (
                    "CODE_REPAIR_ENGINE_UNAVAILABLE"
                ),
                "ai": self.ai.status(),
                "diagnosis": diagnosis,
            }

        relevant_files = []

        for path in ROOT_DIR.glob("*.py"):
            if path.is_file():
                relevant_files.append(
                    {
                        "path": path.name,
                        "sha256": sha256_file(path),
                        "size": path.stat().st_size,
                    }
                )

        prompt = (
            "Repair the MAJD-GAME-FACTORY failure.\n"
            "Return JSON only.\n"
            "Schema:\n"
            "{"
            "\"success\":true,"
            "\"changes\":["
            "{"
            "\"path\":\"relative.py\","
            "\"content\":\"COMPLETE FILE CONTENT\""
            "}"
            "]"
            "}\n"
            "Rules:\n"
            "- Complete-file replacement only.\n"
            "- Never modify outside project root.\n"
            "- Never claim success without changes.\n"
            "- Preserve existing working interfaces.\n\n"
            "FAILURE:\n"
            + json.dumps(
                failure,
                ensure_ascii=False,
                default=str,
            )
            + "\nDIAGNOSIS:\n"
            + json.dumps(
                diagnosis,
                ensure_ascii=False,
                default=str,
            )
            + "\nFILES:\n"
            + json.dumps(
                relevant_files,
                ensure_ascii=False,
            )
        )

        answer = self.ai.ask(
            (
                "You are MAJD Sovereign autonomous "
                "repair engine. Apply conservative "
                "complete-file repairs and never "
                "manufacture success."
            ),
            prompt,
        )

        if not answer:
            return {
                "success": False,
                "status": "AI_REPAIR_EMPTY",
            }

        try:
            cleaned = answer.strip()

            cleaned = re.sub(
                r"^```(?:json)?\s*",
                "",
                cleaned,
            )

            cleaned = re.sub(
                r"\s*```$",
                "",
                cleaned,
            )

            data = json.loads(cleaned)

        except Exception as error:
            return {
                "success": False,
                "status": (
                    "AI_REPAIR_RESPONSE_INVALID"
                ),
                "error": str(error),
            }

        applied = []

        for change in (
            data.get("changes")
            or []
        ):
            relative = str(
                change.get("path")
                or ""
            ).strip()

            content = change.get("content")

            if (
                not relative
                or not isinstance(content, str)
                or not content.strip()
            ):
                continue

            target = safe_project_path(
                ROOT_DIR / relative
            )

            # Do not let 01 rewrite itself while it is
            # currently executing.
            if target.resolve() == THIS_FILE:
                applied.append(
                    {
                        "success": False,
                        "status": (
                            "SELF_REWRITE_REQUIRES_"
                            "CONTROLLED_RESTART"
                        ),
                        "path": relative,
                    }
                )
                continue

            applied.append(
                self.code.replace_python_file(
                    target,
                    content,
                )
            )

        success = bool(applied) and all(
            item.get("success")
            for item in applied
        )

        return {
            "success": success,
            "status": (
                "AI_CODE_REPAIR_APPLIED"
                if success
                else "AI_REPAIR_INCOMPLETE"
            ),
            "changes": applied,
        }


# ============================================================
# CONTENT SAFETY
# ============================================================

class ContentSafetyPolicy:

    SEXUAL_TERMS = {
        "porn",
        "pornography",
        "explicit sex",
        "إباحية",
        "اباحيه",
        "إباحي",
        "محتوى جنسي صريح",
    }

    SENSITIVE_GOVERNMENT_TERMS = {
        "restricted government facility",
        "secure government facility",
        "classified government location",
        "موقع حكومي محظور",
        "منشأة حكومية محظورة",
        "منشأة أمنية",
        "موقع أمني حساس",
        "مركبة حكومية حساسة",
        "سيارة حكومية حساسة",
    }

    def inspect_text(
        self,
        text: str,
    ) -> Dict[str, Any]:

        normalized = str(
            text or ""
        ).lower()

        violations = []

        if any(
            term.lower() in normalized
            for term in self.SEXUAL_TERMS
        ):
            violations.append(
                {
                    "policy":
                        "EXPLICIT_SEXUAL_CONTENT",
                    "action": "BLOCK",
                }
            )

        if any(
            term.lower() in normalized
            for term
            in self.SENSITIVE_GOVERNMENT_TERMS
        ):
            violations.append(
                {
                    "policy":
                        "SENSITIVE_GOVERNMENT_CONTENT",
                    "action": "BLOCK_REVIEW",
                }
            )

        return {
            "success": not violations,
            "status": (
                "CONTENT_ALLOWED"
                if not violations
                else "CONTENT_BLOCKED"
            ),
            "violations": violations,
        }


# ============================================================
# SECURITY CENTER
# ============================================================

class SecurityCenter:

    def __init__(
        self,
        logger: AuditLogger,
    ):
        self.logger = logger
        self.events_file = (
            SECURITY_DIR / "events.jsonl"
        )

    def record(
        self,
        event_type: str,
        severity: str,
        source: Optional[str] = None,
        target: Optional[str] = None,
        action: Optional[str] = None,
        result: Optional[str] = None,
        details: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Dict[str, Any]:

        event = {
            "id": str(uuid.uuid4()),
            "time": utc_now(),
            "event_type": event_type,
            "severity": severity.upper(),
            "source": source,
            "target": target,
            "action": action,
            "result": result,
            "details": details or {},
        }

        with self.events_file.open(
            "a",
            encoding="utf-8",
        ) as file:
            file.write(
                json.dumps(
                    event,
                    ensure_ascii=False,
                    default=str,
                )
                + "\n"
            )

        self.logger.log(
            "SECURITY_EVENT",
            event,
        )

        return event

    def recent(
        self,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:

        if not self.events_file.exists():
            return []

        lines = self.events_file.read_text(
            encoding="utf-8"
        ).splitlines()

        result = []

        for line in lines[-limit:]:
            try:
                result.append(
                    json.loads(line)
                )
            except Exception:
                continue

        return result


# ============================================================
# LEGAL ASSISTANT
# ============================================================

class ElectronicLegalAssistant:

    DISCLAIMER = (
        "MAJD Electronic Legal Assistant is an AI "
        "assistance capability and is not a human "
        "licensed lawyer. Matters requiring formal "
        "legal approval must be reviewed by an "
        "appropriately qualified legal professional."
    )

    def __init__(
        self,
        ai: LocalAIAdapter,
        logger: AuditLogger,
    ):
        self.ai = ai
        self.logger = logger

    def execute(
        self,
        command: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:

        if not self.ai.available:
            return {
                "success": False,
                "status": "LEGAL_AI_NOT_CONNECTED",
                "disclaimer": self.DISCLAIMER,
            }

        prompt = (
            "Act as MAJD Electronic Legal Assistant.\n"
            "Assist with contract drafting/review, "
            "terms, privacy, developer agreements, "
            "creator agreements, agency agreements, "
            "advertising, sponsorship and IP review.\n"
            "Do not claim to be a licensed lawyer.\n"
            "Flag matters requiring formal legal "
            "approval.\n\n"
            f"COMMAND:\n{command}\n\n"
            "PAYLOAD:\n"
            + json.dumps(
                payload,
                ensure_ascii=False,
                default=str,
            )
        )

        answer = self.ai.ask(
            (
                "You are an electronic legal "
                "assistance system for MAJD. "
                "Provide analysis and drafting "
                "assistance, not licensed legal "
                "representation."
            ),
            prompt,
        )

        if not answer:
            return {
                "success": False,
                "status": "LEGAL_AI_EMPTY",
                "disclaimer": self.DISCLAIMER,
            }

        result = {
            "success": True,
            "status": (
                "LEGAL_ASSISTANCE_COMPLETED"
            ),
            "result": answer,
            "disclaimer": self.DISCLAIMER,
        }

        self.logger.log(
            "LEGAL_ASSISTANCE",
            {
                "command": command,
                "status": result["status"],
            },
        )

        return result


# ============================================================
# ARTIFACT VERIFIER
# ============================================================

class ArtifactVerifier:

    KEYS = (
        "artifact",
        "artifact_path",
        "build_path",
        "game_dir",
        "output_path",
        "playable_artifact",
    )

    def extract(
        self,
        result: Dict[str, Any],
    ) -> Optional[Path]:

        containers = [
            result,
        ]

        for key in (
            "result",
            "build",
            "output",
            "game",
        ):
            nested = result.get(key)

            if isinstance(nested, dict):
                containers.append(nested)

        for container in containers:
            for key in self.KEYS:
                value = container.get(key)

                if not value:
                    continue

                path = Path(str(value))

                if not path.is_absolute():
                    path = (
                        ROOT_DIR / path
                    ).resolve()
                else:
                    path = path.resolve()

                if is_inside_root(path):
                    return path

        return None

    def verify(
        self,
        result: Dict[str, Any],
    ) -> Dict[str, Any]:

        artifact = self.extract(result)

        if artifact is None:
            return {
                "success": False,
                "status": "ARTIFACT_MISSING",
            }

        if not artifact.exists():
            return {
                "success": False,
                "status": "ARTIFACT_NOT_FOUND",
                "artifact": str(artifact),
            }

        if not artifact.is_dir():
            return {
                "success": False,
                "status": (
                    "ARTIFACT_NOT_DIRECTORY"
                ),
                "artifact": str(artifact),
            }

        files = [
            item
            for item in artifact.rglob("*")
            if item.is_file()
        ]

        if not files:
            return {
                "success": False,
                "status": "ARTIFACT_EMPTY",
                "artifact": str(artifact),
            }

        index = artifact / "index.html"

        if (
            not index.exists()
            or not index.is_file()
            or index.stat().st_size <= 0
        ):
            return {
                "success": False,
                "status": (
                    "PLAYABLE_INDEX_NOT_FOUND"
                ),
                "artifact": str(artifact),
            }

        return {
            "success": True,
            "status": "ARTIFACT_VERIFIED",
            "artifact": str(artifact),
            "index": str(index),
            "file_count": len(files),
        }


# ============================================================
# COMMAND CLASSIFIER
# ============================================================

class CommandClassifier:

    RULES: Tuple[
        Tuple[str, Tuple[str, ...]],
        ...
    ] = (
        (
            "CREATE_GAME",
            (
                "أنشئ لعبة",
                "انشئ لعبة",
                "اصنع لعبة",
                "ابني لعبة",
                "سوي لعبة",
                "create game",
                "build game",
                "make game",
            ),
        ),
        (
            "REPAIR",
            (
                "اصلح",
                "أصلح",
                "إصلاح",
                "اصلاح",
                "صحح",
                "مشاكل",
                "أخطاء",
                "اخطاء",
                "repair",
                "fix",
                "debug",
            ),
        ),
        (
            "INSPECT",
            (
                "افحص",
                "فحص",
                "راجع",
                "اختبر",
                "check",
                "inspect",
                "test",
                "validate",
            ),
        ),
        (
            "LEGAL",
            (
                "عقد",
                "عقود",
                "قانون",
                "قانوني",
                "محامي",
                "خصوصية",
                "شروط وأحكام",
                "contract",
                "legal",
                "privacy policy",
                "terms",
            ),
        ),
        (
            "SECURITY",
            (
                "اختراق",
                "أمن",
                "امن",
                "هجوم",
                "مخترق",
                "security",
                "attack",
                "intrusion",
            ),
        ),
        (
            "CONTENT",
            (
                "فيلم",
                "مسلسل",
                "فيديو",
                "صورة",
                "محتوى",
                "movie",
                "series",
                "video",
                "content",
                "image",
            ),
        ),
        (
            "SOCIAL",
            (
                "تيك توك",
                "سناب",
                "يوتيوب",
                "تويتر",
                "social",
                "tiktok",
                "snapchat",
                "youtube",
            ),
        ),
        (
            "LIVE",
            (
                "بث مباشر",
                "لايف",
                "live stream",
                "livestream",
            ),
        ),
        (
            "PAYMENTS",
            (
                "دفع",
                "مدفوعات",
                "محفظة",
                "mada",
                "apple pay",
                "payment",
                "wallet",
            ),
        ),
        (
            "ADS",
            (
                "إعلان",
                "اعلان",
                "إعلانات",
                "اعلانات",
                "advertisement",
                "ads",
            ),
        ),
        (
            "STATUS",
            (
                "حالة المنصة",
                "وش يصير",
                "ماذا يحدث",
                "status",
                "health",
                "dashboard",
            ),
        ),
    )

    def classify(
        self,
        command: str,
    ) -> Dict[str, Any]:

        lowered = str(
            command or ""
        ).lower()

        scores: Dict[str, int] = {}

        for command_type, phrases in self.RULES:
            score = sum(
                1
                for phrase in phrases
                if phrase.lower() in lowered
            )

            if score:
                scores[command_type] = score

        if scores:
            selected = max(
                scores,
                key=scores.get,
            )
        else:
            selected = (
                "GENERAL_OWNER_COMMAND"
            )

        return {
            "type": selected,
            "scores": scores,
        }


# ============================================================
# ROUTER
# ============================================================

class CapabilityRouter:

    TYPE_TO_CAPABILITIES = {
        "CREATE_GAME": [
            "GAME",
            "EXECUTION",
        ],
        "CONTENT": [
            "CONTENT",
            "MEDIA",
        ],
        "SOCIAL": [
            "SOCIAL",
            "CONTENT",
        ],
        "LIVE": [
            "LIVE",
            "MEDIA",
        ],
        "PAYMENTS": [
            "PAYMENTS",
        ],
        "ADS": [
            "ADS",
        ],
        "SECURITY": [
            "SECURITY",
        ],
        "REPAIR": [
            "REPAIR",
            "DIAGNOSTICS",
        ],
        "INSPECT": [
            "HEALTH",
            "TESTING",
            "VERIFICATION",
        ],
        "STATUS": [
            "DASHBOARD",
            "MONITORING",
            "HEALTH",
        ],
    }

    def __init__(
        self,
        registry: CapabilityRegistry,
    ):
        self.registry = registry

    def route(
        self,
        command_type: str,
    ) -> Dict[str, Any]:

        desired = (
            self.TYPE_TO_CAPABILITIES.get(
                command_type,
                [],
            )
        )

        candidates = []

        for capability in desired:
            for provider in (
                self.registry.providers(
                    capability
                )
            ):
                if (
                    provider.get("importable")
                    and provider.get(
                        "entrypoints"
                    )
                ):
                    candidates.append(
                        {
                            "capability":
                                capability,
                            **provider,
                        }
                    )

        return {
            "success": bool(candidates),
            "desired_capabilities": desired,
            "candidates": candidates,
            "status": (
                "ROUTE_FOUND"
                if candidates
                else "NO_CAPABILITY_ROUTE"
            ),
        }


# ============================================================
# COMPONENT EXECUTOR
# ============================================================

class ComponentExecutor:

    def execute_provider(
        self,
        provider: Dict[str, Any],
        command: str,
        request: Dict[str, Any],
        job_id: str,
    ) -> Dict[str, Any]:

        path = Path(provider["path"])

        try:
            module = load_module(
                path,
                (
                    "_majd_execute_"
                    + uuid.uuid4().hex
                ),
            )

        except Exception as error:
            return {
                "success": False,
                "status": (
                    "COMPONENT_LOAD_FAILED"
                ),
                "component": provider,
                "error": (
                    f"{type(error).__name__}: "
                    f"{error}"
                ),
                "traceback":
                    traceback.format_exc(),
            }

        entrypoints = (
            provider.get("entrypoints")
            or []
        )

        for name in entrypoints:

            function = getattr(
                module,
                name,
                None,
            )

            if not callable(function):
                continue

            try:
                value = call_supported(
                    function,
                    {
                        "command": command,
                        "request": request,
                        "payload": request,
                        "job_id": job_id,
                        "owner": DEFAULT_OWNER,
                        "output_root":
                            str(OUTPUT_DIR),
                    },
                )

                result = normalize_result(
                    value
                )

                result.setdefault(
                    "component",
                    provider["filename"],
                )

                result.setdefault(
                    "entrypoint",
                    name,
                )

                return result

            except Exception as error:
                return {
                    "success": False,
                    "status": (
                        "COMPONENT_EXECUTION_FAILED"
                    ),
                    "component":
                        provider["filename"],
                    "entrypoint": name,
                    "error": (
                        f"{type(error).__name__}: "
                        f"{error}"
                    ),
                    "traceback":
                        traceback.format_exc(),
                }

        return {
            "success": False,
            "status": (
                "COMPONENT_ENTRYPOINT_MISSING"
            ),
            "component":
                provider["filename"],
        }


# ============================================================
# OFFICIAL GAME PIPELINE
# ============================================================

class GamePipeline:

    def __init__(
        self,
        registry: CapabilityRegistry,
        executor: ComponentExecutor,
    ):
        self.registry = registry
        self.executor = executor
        self.verifier = ArtifactVerifier()

    def _select_executor(
        self,
    ) -> Optional[Dict[str, Any]]:

        providers = (
            self.registry.providers("GAME")
            + self.registry.providers(
                "EXECUTION"
            )
        )

        # Prefer official 03 if discovered.
        providers.sort(
            key=lambda item: (
                0
                if item.get("number") == "03"
                else 1
            )
        )

        for provider in providers:
            if (
                provider.get("importable")
                and provider.get("entrypoints")
            ):
                return provider

        return None

    def _select_publisher(
        self,
    ) -> Optional[Dict[str, Any]]:

        providers = (
            self.registry.providers(
                "PUBLISH"
            )
        )

        providers.sort(
            key=lambda item: (
                0
                if item.get("number") == "04"
                else 1
            )
        )

        for provider in providers:
            if (
                provider.get("importable")
                and provider.get("entrypoints")
            ):
                return provider

        return None

    def run(
        self,
        command: str,
        request: Dict[str, Any],
        job_id: str,
    ) -> Dict[str, Any]:

        executor_provider = (
            self._select_executor()
        )

        if executor_provider is None:
            return {
                "success": False,
                "status": (
                    "REAL_GAME_EXECUTOR_UNAVAILABLE"
                ),
            }

        build = self.executor.execute_provider(
            executor_provider,
            command,
            request,
            job_id,
        )

        if not build.get("success"):
            return {
                "success": False,
                "status": (
                    "REAL_GAME_EXECUTION_FAILED"
                ),
                "executor": build,
            }

        artifact = self.verifier.verify(build)

        if not artifact.get("success"):
            return {
                "success": False,
                "status": (
                    "ARTIFACT_VERIFICATION_FAILED"
                ),
                "executor": build,
                "artifact_verification":
                    artifact,
            }

        publisher = self._select_publisher()

        if publisher is None:
            return {
                "success": False,
                "status": (
                    "OFFICIAL_PLATFORM_BRIDGE_UNAVAILABLE"
                ),
                "artifact":
                    artifact,
            }

        publish_request = dict(request)

        publish_request.update(
            {
                "artifact":
                    artifact["artifact"],
                "artifact_path":
                    artifact["artifact"],
                "game_dir":
                    artifact["artifact"],
                "build_path":
                    artifact["artifact"],
            }
        )

        published = (
            self.executor.execute_provider(
                publisher,
                command,
                publish_request,
                job_id,
            )
        )

        if not published.get("success"):
            return {
                "success": False,
                "status": (
                    "OFFICIAL_PLATFORM_PUBLISH_FAILED"
                ),
                "artifact":
                    artifact,
                "publisher":
                    published,
            }

        # Publishing success must contain evidence.
        evidence = any(
            published.get(key)
            for key in (
                "public_url",
                "published_directory",
                "game_path",
                "receipt",
                "publication",
            )
        )

        if not evidence:
            return {
                "success": False,
                "status": (
                    "PUBLICATION_NOT_VERIFIED"
                ),
                "artifact":
                    artifact,
                "publisher":
                    published,
            }

        return {
            "success": True,
            "status": (
                "GAME_BUILT_AND_PUBLISHED"
            ),
            "artifact": artifact,
            "executor": build,
            "publisher": published,
        }


# ============================================================
# OWNER DASHBOARD
# ============================================================

class OwnerDashboard:

    def __init__(
        self,
        security: SecurityCenter,
    ):
        self.security = security
        self.path = (
            DASHBOARD_DIR / "owner-status.json"
        )

    def update(
        self,
        **values: Any,
    ) -> Dict[str, Any]:

        current = read_json(
            self.path,
            {},
        ) or {}

        current.update(values)

        current["updated_at"] = utc_now()

        write_json(
            self.path,
            current,
        )

        return current

    def snapshot(
        self,
    ) -> Dict[str, Any]:

        data = read_json(
            self.path,
            {},
        ) or {}

        data["security_events"] = (
            self.security.recent(50)
        )

        data["updated_at"] = utc_now()

        return data


# ============================================================
# MASTER STATE
# ============================================================

@dataclass
class MastermindState:
    operation_id: str
    owner: str
    command: str
    started_at: str
    updated_at: str
    status: str

    success: bool = False
    attempts: int = 0

    command_type: str = (
        "GENERAL_OWNER_COMMAND"
    )

    plan: List[
        Dict[str, Any]
    ] = field(
        default_factory=list
    )

    events: List[
        Dict[str, Any]
    ] = field(
        default_factory=list
    )

    result: Optional[
        Dict[str, Any]
    ] = None

    error: Optional[str] = None


# ============================================================
# MASTERMIND
# ============================================================

class Mastermind:

    def __init__(
        self,
        owner: str = DEFAULT_OWNER,
        max_repair_attempts: int = (
            MAX_REPAIR_ATTEMPTS
        ),
    ):

        self.owner = owner

        self.max_repair_attempts = max(
            1,
            int(max_repair_attempts),
        )

        self.operation_id = str(
            uuid.uuid4()
        )

        self.logger = AuditLogger(
            self.operation_id
        )

        self.process = ProcessExecutor()

        self.python_checker = PythonChecker(
            self.process
        )

        self.discovery = ComponentDiscovery()

        self.registry = CapabilityRegistry(
            self.discovery
        )

        self.registry.build()

        self.router = CapabilityRouter(
            self.registry
        )

        self.component_executor = (
            ComponentExecutor()
        )

        self.game_pipeline = GamePipeline(
            self.registry,
            self.component_executor,
        )

        self.classifier = CommandClassifier()

        self.diagnostics = DiagnosticEngine()

        self.repair_engine = (
            AutonomousRepairEngine(
                self.operation_id,
                self.logger,
                self.python_checker,
            )
        )

        self.ai = LocalAIAdapter(
            self.logger
        )

        self.security = SecurityCenter(
            self.logger
        )

        self.legal = (
            ElectronicLegalAssistant(
                self.ai,
                self.logger,
            )
        )

        self.content_policy = (
            ContentSafetyPolicy()
        )

        self.dashboard = OwnerDashboard(
            self.security
        )

    # --------------------------------------------------------
    # STATE
    # --------------------------------------------------------

    def _state_path(self) -> Path:
        return (
            MASTERMIND_STATE_DIR
            / f"{self.operation_id}.json"
        )

    def _save_state(
        self,
        state: MastermindState,
    ) -> None:
        state.updated_at = utc_now()

        write_json(
            self._state_path(),
            asdict(state),
        )

    def _event(
        self,
        state: MastermindState,
        event_type: str,
        data: Dict[str, Any],
    ) -> None:

        event = {
            "time": utc_now(),
            "type": event_type,
            "data": data,
        }

        state.events.append(event)

        self.logger.log(
            event_type,
            data,
        )

        self._save_state(state)

    # --------------------------------------------------------
    # REGISTRY
    # --------------------------------------------------------

    def refresh_registry(
        self,
    ) -> Dict[str, Any]:

        result = self.registry.build()

        self.router = CapabilityRouter(
            self.registry
        )

        self.game_pipeline = GamePipeline(
            self.registry,
            self.component_executor,
        )

        return result

    # --------------------------------------------------------
    # INSPECTION
    # --------------------------------------------------------

    def inspect_factory(
        self,
    ) -> Dict[str, Any]:

        compile_report = (
            self.python_checker
            .compile_project()
        )

        component_report = (
            self.discovery.discover(
                runtime_import=True
            )
        )

        registry_report = (
            self.refresh_registry()
        )

        import_failures = []

        for records in (
            component_report[
                "components"
            ].values()
        ):
            for record in records:
                if (
                    record["number"] != "01"
                    and not record.get(
                        "importable"
                    )
                ):
                    import_failures.append(
                        {
                            "file":
                                record["filename"],
                            "error":
                                record.get("error"),
                        }
                    )

        # 01 itself is mandatory.
        has_01 = bool(
            component_report[
                "components"
            ].get("01")
        )

        success = bool(
            has_01
            and compile_report.get("success")
            and not import_failures
        )

        return {
            "success": success,
            "status": (
                "FACTORY_VERIFIED"
                if success
                else "FACTORY_CHECK_FAILED"
            ),
            "python_compile":
                compile_report,
            "components":
                component_report,
            "capability_registry":
                registry_report,
            "import_failures":
                import_failures,
            "ai":
                self.ai.status(),
        }

    # --------------------------------------------------------
    # REQUEST NORMALIZATION
    # --------------------------------------------------------

    def normalize_request(
        self,
        command: str,
        request: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Dict[str, Any]:

        data = dict(request or {})

        data.setdefault(
            "request",
            command,
        )

        data.setdefault(
            "description",
            command,
        )

        classification = (
            self.classifier.classify(
                command
            )
        )

        data.setdefault(
            "type",
            classification["type"],
        )

        data.setdefault(
            "owner",
            self.owner,
        )

        data.setdefault(
            "autonomous",
            True,
        )

        data.setdefault(
            "auto_repair",
            True,
        )

        data.setdefault(
            "auto_test",
            True,
        )

        data.setdefault(
            "auto_retry",
            True,
        )

        data["classification"] = (
            classification
        )

        return data

    # --------------------------------------------------------
    # PLAN
    # --------------------------------------------------------

    def build_plan(
        self,
        request: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        request_type = str(
            request.get("type")
            or "GENERAL_OWNER_COMMAND"
        ).upper()

        common = [
            "DISCOVER",
            "VALIDATE",
            "PLAN",
        ]

        if request_type == "CREATE_GAME":
            stages = common + [
                "BUILD",
                "VERIFY_ARTIFACT",
                "PUBLISH",
                "VERIFY_PUBLICATION",
            ]

        elif request_type in {
            "REPAIR",
            "INSPECT",
        }:
            stages = common + [
                "DIAGNOSE",
                "BACKUP",
                "REPAIR",
                "TEST",
                "VERIFY",
                "RETRY_IF_REQUIRED",
            ]

        else:
            stages = common + [
                "ROUTE",
                "EXECUTE",
                "VERIFY",
                "REPAIR_IF_REQUIRED",
                "FINAL_VERIFY",
            ]

        return [
            {
                "stage": stage,
                "status": "PENDING",
            }
            for stage in stages
        ]

    # --------------------------------------------------------
    # REPAIR
    # --------------------------------------------------------

    def repair_failure(
        self,
        failure: Dict[str, Any],
        state: MastermindState,
    ) -> Dict[str, Any]:

        diagnosis = (
            self.diagnostics.diagnose(
                failure
            )
        )

        self._event(
            state,
            "DIAGNOSIS",
            diagnosis,
        )

        if not diagnosis.get(
            "repairable"
        ):
            return {
                "success": False,
                "status": (
                    "FAILURE_NOT_AUTOMATICALLY_"
                    "REPAIRABLE"
                ),
                "diagnosis": diagnosis,
            }

        self.dashboard.update(
            status="REPAIRING",
            operation_id=self.operation_id,
            diagnosis=diagnosis,
        )

        repair = (
            self.repair_engine.repair(
                diagnosis,
                failure,
            )
        )

        self._event(
            state,
            "REPAIR_RESULT",
            repair,
        )

        return repair

    # --------------------------------------------------------
    # INSPECT / REPAIR COMMAND
    # --------------------------------------------------------

    def run_repair_cycle(
        self,
        state: MastermindState,
    ) -> Dict[str, Any]:

        attempts = []

        for attempt in range(
            1,
            self.max_repair_attempts + 1,
        ):

            state.attempts = attempt
            state.status = "DIAGNOSING"

            self._save_state(state)

            self.dashboard.update(
                status="DIAGNOSING",
                operation_id=self.operation_id,
                attempt=attempt,
            )

            inspection = (
                self.inspect_factory()
            )

            self._event(
                state,
                "FACTORY_INSPECTION",
                inspection,
            )

            if inspection.get("success"):
                return {
                    "success": True,
                    "status": (
                        "FACTORY_VERIFIED"
                    ),
                    "attempt": attempt,
                    "inspection": inspection,
                    "attempts": attempts,
                }

            failure = {
                "stage": "FACTORY_INSPECTION",
                "result": inspection,
            }

            repair = self.repair_failure(
                failure,
                state,
            )

            attempts.append(
                {
                    "attempt": attempt,
                    "failure": failure,
                    "repair": repair,
                }
            )

            self.dashboard.update(
                status="TESTING",
                operation_id=self.operation_id,
                attempt=attempt,
            )

            recheck = self.inspect_factory()

            self._event(
                state,
                "REPAIR_RECHECK",
                recheck,
            )

            if recheck.get("success"):
                return {
                    "success": True,
                    "status": (
                        "REPAIR_VERIFIED"
                    ),
                    "attempt": attempt,
                    "repair": repair,
                    "inspection": recheck,
                    "attempts": attempts,
                }

            if not repair.get("success"):
                return {
                    "success": False,
                    "status": repair.get(
                        "status",
                        "AUTONOMOUS_REPAIR_FAILED",
                    ),
                    "repair": repair,
                    "inspection": recheck,
                    "attempts": attempts,
                }

        return {
            "success": False,
            "status": (
                "MAX_AUTONOMOUS_REPAIR_"
                "ATTEMPTS_REACHED"
            ),
            "attempts": attempts,
            "inspection":
                self.inspect_factory(),
        }

    # --------------------------------------------------------
    # GENERIC CAPABILITY
    # --------------------------------------------------------

    def execute_routed(
        self,
        command: str,
        request: Dict[str, Any],
        state: MastermindState,
    ) -> Dict[str, Any]:

        command_type = str(
            request.get("type")
            or "GENERAL_OWNER_COMMAND"
        ).upper()

        route = self.router.route(
            command_type
        )

        self._event(
            state,
            "CAPABILITY_ROUTE",
            route,
        )

        if not route.get("success"):
            return {
                "success": False,
                "status": (
                    "CAPABILITY_NOT_CONNECTED"
                ),
                "command_type": command_type,
                "route": route,
            }

        failures = []

        for provider in route["candidates"]:

            result = (
                self.component_executor
                .execute_provider(
                    provider,
                    command,
                    request,
                    self.operation_id,
                )
            )

            self._event(
                state,
                "COMPONENT_RESULT",
                result,
            )

            if result.get("success"):
                return {
                    "success": True,
                    "status": (
                        "COMMAND_EXECUTED_AND_VERIFIED"
                    ),
                    "provider": provider,
                    "result": result,
                }

            failures.append(
                {
                    "provider": provider,
                    "result": result,
                }
            )

        return {
            "success": False,
            "status": (
                "ALL_CAPABILITY_PROVIDERS_FAILED"
            ),
            "failures": failures,
        }

    # --------------------------------------------------------
    # GENERAL OWNER COMMAND
    # --------------------------------------------------------

    def execute_general_owner_command(
        self,
        command: str,
        request: Dict[str, Any],
        state: MastermindState,
    ) -> Dict[str, Any]:

        # General commands are not rejected merely
        # because no static keyword exists.
        #
        # First ask orchestration-capable discovered
        # components. If none exist, return a truthful
        # OWNER_ACTION_REQUIRED / capability state.

        providers = (
            self.registry.providers(
                "ORCHESTRATION"
            )
            + self.registry.providers(
                "OWNER_COMMAND"
            )
            + self.registry.providers(
                "RUNTIME"
            )
        )

        unique = []
        seen = set()

        for provider in providers:
            key = (
                provider["path"],
                tuple(
                    provider.get(
                        "entrypoints",
                        []
                    )
                ),
            )

            if key in seen:
                continue

            seen.add(key)

            if (
                provider.get("importable")
                and provider.get("entrypoints")
            ):
                unique.append(provider)

        if not unique:
            return {
                "success": False,
                "status": (
                    "OWNER_ACTION_REQUIRED"
                ),
                "message": (
                    "No real discovered orchestration "
                    "provider can execute this command."
                ),
                "available_capabilities":
                    sorted(
                        self.registry.registry.keys()
                    ),
            }

        failures = []

        for provider in unique:

            result = (
                self.component_executor
                .execute_provider(
                    provider,
                    command,
                    request,
                    self.operation_id,
                )
            )

            self._event(
                state,
                "GENERAL_COMMAND_PROVIDER",
                result,
            )

            if result.get("success"):
                return {
                    "success": True,
                    "status": (
                        "GENERAL_COMMAND_COMPLETED"
                    ),
                    "provider": provider,
                    "result": result,
                }

            failures.append(
                {
                    "provider": provider,
                    "result": result,
                }
            )

        return {
            "success": False,
            "status": (
                "GENERAL_COMMAND_EXECUTION_FAILED"
            ),
            "failures": failures,
        }

    # --------------------------------------------------------
    # MAIN RUN
    # --------------------------------------------------------

    def run(
        self,
        command: str = "",
        request: Optional[
            Dict[str, Any]
        ] = None,
        payload: Optional[
            Dict[str, Any]
        ] = None,
        job_id: Optional[str] = None,
        owner: Optional[str] = None,
        output_root: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:

        if owner:
            self.owner = owner

        if job_id:
            self.operation_id = str(job_id)

            self.logger = AuditLogger(
                self.operation_id
            )

            self.ai = LocalAIAdapter(
                self.logger
            )

            self.security = SecurityCenter(
                self.logger
            )

            self.legal = (
                ElectronicLegalAssistant(
                    self.ai,
                    self.logger,
                )
            )

            self.dashboard = OwnerDashboard(
                self.security
            )

            self.repair_engine = (
                AutonomousRepairEngine(
                    self.operation_id,
                    self.logger,
                    self.python_checker,
                )
            )

        supplied_request = (
            request
            or payload
            or {}
        )

        if not command:
            command = str(
                supplied_request.get("command")
                or supplied_request.get(
                    "request"
                )
                or supplied_request.get(
                    "description"
                )
                or ""
            ).strip()

        if not command:
            return {
                "success": False,
                "status": "EMPTY_COMMAND",
            }

        normalized = (
            self.normalize_request(
                command,
                supplied_request,
            )
        )

        request_type = str(
            normalized.get("type")
            or "GENERAL_OWNER_COMMAND"
        ).upper()

        state = MastermindState(
            operation_id=self.operation_id,
            owner=self.owner,
            command=command,
            started_at=utc_now(),
            updated_at=utc_now(),
            status="RECEIVED",
            command_type=request_type,
        )

        state.plan = self.build_plan(
            normalized
        )

        self._save_state(state)

        self.dashboard.update(
            system=SYSTEM_NAME,
            mastermind=MASTERMIND_NAME,
            version=VERSION,
            status="RUNNING",
            operation_id=self.operation_id,
            command=command,
            command_type=request_type,
            started_at=state.started_at,
            plan=state.plan,
        )

        self.logger.log(
            "OWNER_OBJECTIVE_RECEIVED",
            {
                "command": command,
                "request": normalized,
            },
        )

        try:

            self.refresh_registry()

            # --------------------------------------------
            # CONTENT SAFETY BEFORE PUBLIC CONTENT ACTIONS
            # --------------------------------------------

            if request_type in {
                "CONTENT",
                "SOCIAL",
                "LIVE",
                "ADS",
            }:
                safety = (
                    self.content_policy
                    .inspect_text(command)
                )

                self._event(
                    state,
                    "CONTENT_SAFETY_CHECK",
                    safety,
                )

                if not safety.get("success"):
                    result = {
                        "success": False,
                        "status": (
                            "CONTENT_POLICY_BLOCKED"
                        ),
                        "policy": safety,
                    }

                    state.result = result
                    state.status = (
                        result["status"]
                    )
                    state.success = False

                    self._save_state(state)

                    self.dashboard.update(
                        status="FAILED",
                        operation_id=
                            self.operation_id,
                        result=result,
                    )

                    return result

            # --------------------------------------------
            # STATUS
            # --------------------------------------------

            if request_type == "STATUS":

                result = {
                    "success": True,
                    "status": (
                        "STATUS_RETRIEVED"
                    ),
                    "dashboard":
                        self.dashboard.snapshot(),
                    "factory":
                        self.inspect_factory(),
                }

            # --------------------------------------------
            # INSPECTION / REPAIR
            # --------------------------------------------

            elif request_type in {
                "REPAIR",
                "INSPECT",
            }:
                result = self.run_repair_cycle(
                    state
                )

            # --------------------------------------------
            # LEGAL
            # --------------------------------------------

            elif request_type == "LEGAL":
                result = self.legal.execute(
                    command,
                    normalized,
                )

            # --------------------------------------------
            # SECURITY
            # --------------------------------------------

            elif request_type == "SECURITY":

                inspection = (
                    self.inspect_factory()
                )

                result = {
                    "success": True,
                    "status": (
                        "SECURITY_STATUS_RETRIEVED"
                    ),
                    "recent_events":
                        self.security.recent(100),
                    "factory": inspection,
                }

            # --------------------------------------------
            # GAME
            # --------------------------------------------

            elif request_type == "CREATE_GAME":

                self.dashboard.update(
                    status="RUNNING",
                    stage="BUILD",
                    operation_id=
                        self.operation_id,
                )

                result = (
                    self.game_pipeline.run(
                        command,
                        normalized,
                        self.operation_id,
                    )
                )

                if not result.get("success"):

                    repair = (
                        self.repair_failure(
                            result,
                            state,
                        )
                    )

                    if repair.get("success"):

                        self.refresh_registry()

                        result = (
                            self.game_pipeline.run(
                                command,
                                normalized,
                                self.operation_id,
                            )
                        )

            # --------------------------------------------
            # KNOWN ROUTED CAPABILITIES
            # --------------------------------------------

            elif request_type in {
                "CONTENT",
                "SOCIAL",
                "LIVE",
                "PAYMENTS",
                "ADS",
            }:

                result = self.execute_routed(
                    command,
                    normalized,
                    state,
                )

                if not result.get("success"):

                    repair = (
                        self.repair_failure(
                            result,
                            state,
                        )
                    )

                    if repair.get("success"):
                        self.refresh_registry()

                        result = (
                            self.execute_routed(
                                command,
                                normalized,
                                state,
                            )
                        )

            # --------------------------------------------
            # GENERAL OWNER OBJECTIVE
            # --------------------------------------------

            else:

                result = (
                    self.execute_general_owner_command(
                        command,
                        normalized,
                        state,
                    )
                )

            # --------------------------------------------
            # FINAL STATE
            # --------------------------------------------

            state.result = result

            state.success = bool(
                result.get("success")
            )

            state.status = str(
                result.get("status")
                or (
                    "VERIFIED"
                    if state.success
                    else "FAILED"
                )
            )

            if not state.success:
                state.error = str(
                    result.get("error")
                    or result.get("status")
                    or "UNKNOWN_FAILURE"
                )

            self._save_state(state)

            self.dashboard.update(
                status=(
                    "VERIFIED"
                    if state.success
                    else "FAILED"
                ),
                operation_id=
                    self.operation_id,
                command=command,
                command_type=request_type,
                result=result,
                finished_at=utc_now(),
                available_capabilities=
                    sorted(
                        self.registry.registry.keys()
                    ),
            )

            self.logger.log(
                "MASTERMIND_FINAL_RESULT",
                result,
            )

            return result

        except Exception as error:

            result = {
                "success": False,
                "status": (
                    "MASTERMIND_EXCEPTION"
                ),
                "operation_id":
                    self.operation_id,
                "error": (
                    f"{type(error).__name__}: "
                    f"{error}"
                ),
                "traceback":
                    traceback.format_exc(),
            }

            state.success = False
            state.status = "FAILED"
            state.error = result["error"]
            state.result = result

            self._save_state(state)

            self.dashboard.update(
                status="FAILED",
                operation_id=
                    self.operation_id,
                result=result,
            )

            self.logger.log(
                "MASTERMIND_EXCEPTION",
                result,
            )

            return result


# ============================================================
# CONTINUOUS MONITOR
# ============================================================

class ContinuousMonitor:

    def __init__(
        self,
        owner: str = DEFAULT_OWNER,
        interval: int = MONITOR_INTERVAL,
    ):
        self.owner = owner
        self.interval = max(
            30,
            int(interval),
        )

        self.stop_event = (
            threading.Event()
        )

    def stop(self) -> None:
        self.stop_event.set()

    def run_forever(self) -> None:

        while not self.stop_event.is_set():

            mastermind = Mastermind(
                owner=self.owner
            )

            result = (
                mastermind.inspect_factory()
            )

            write_json(
                MONITOR_DIR / "latest.json",
                {
                    "time": utc_now(),
                    "result": result,
                },
            )

            if not result.get("success"):

                repair_state = (
                    MastermindState(
                        operation_id=
                            mastermind.operation_id,
                        owner=self.owner,
                        command=(
                            "AUTONOMOUS_MONITOR_REPAIR"
                        ),
                        started_at=utc_now(),
                        updated_at=utc_now(),
                        status="DIAGNOSING",
                        command_type="REPAIR",
                    )
                )

                mastermind.run_repair_cycle(
                    repair_state
                )

            self.stop_event.wait(
                self.interval
            )


# ============================================================
# PUBLIC API
# ============================================================

def execute_request(
    command: str = "",
    request: Optional[
        Dict[str, Any]
    ] = None,
    payload: Optional[
        Dict[str, Any]
    ] = None,
    job_id: Optional[str] = None,
    owner: str = DEFAULT_OWNER,
    output_root: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:

    mastermind = Mastermind(
        owner=owner
    )

    return mastermind.run(
        command=command,
        request=request,
        payload=payload,
        job_id=job_id,
        owner=owner,
        output_root=output_root,
        **kwargs,
    )


def process_game_request(
    **kwargs: Any,
) -> Dict[str, Any]:
    return execute_request(**kwargs)


def process_request(
    **kwargs: Any,
) -> Dict[str, Any]:
    return execute_request(**kwargs)


def execute_game_request(
    request: Dict[str, Any],
    job_id: Optional[str] = None,
    owner: str = DEFAULT_OWNER,
    **kwargs: Any,
) -> Dict[str, Any]:

    data = dict(request)

    data["type"] = "CREATE_GAME"

    command = str(
        data.get("command")
        or data.get("request")
        or data.get("description")
        or ""
    )

    return execute_request(
        command=command,
        request=data,
        job_id=job_id,
        owner=owner,
        **kwargs,
    )


def run(
    command: str = "",
    request: Optional[
        Dict[str, Any]
    ] = None,
    payload: Optional[
        Dict[str, Any]
    ] = None,
    job_id: Optional[str] = None,
    owner: str = DEFAULT_OWNER,
    **kwargs: Any,
) -> Dict[str, Any]:

    return execute_request(
        command=command,
        request=request,
        payload=payload,
        job_id=job_id,
        owner=owner,
        **kwargs,
    )


# ============================================================
# CLI
# ============================================================

def main() -> int:

    parser = argparse.ArgumentParser(
        description=(
            "MAJD SOVEREIGN AUTONOMOUS "
            "MASTERMIND"
        )
    )

    parser.add_argument(
        "command",
        nargs="*",
        help="Owner objective",
    )

    parser.add_argument(
        "--owner",
        default=DEFAULT_OWNER,
    )

    parser.add_argument(
        "--status",
        action="store_true",
    )

    parser.add_argument(
        "--inspect",
        action="store_true",
    )

    parser.add_argument(
        "--discover",
        action="store_true",
    )

    parser.add_argument(
        "--capabilities",
        action="store_true",
    )

    parser.add_argument(
        "--monitor",
        action="store_true",
    )

    args = parser.parse_args()

    if args.status:

        mastermind = Mastermind(
            owner=args.owner
        )

        result = {
            "success": True,
            "system": SYSTEM_NAME,
            "mastermind": MASTERMIND_NAME,
            "version": VERSION,
            "root": str(ROOT_DIR),
            "ai": mastermind.ai.status(),
            "dashboard":
                mastermind.dashboard.snapshot(),
        }

        print(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )

        return 0

    if args.discover:

        result = (
            ComponentDiscovery()
            .discover(
                runtime_import=True
            )
        )

        print(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )

        return 0

    if args.capabilities:

        registry = CapabilityRegistry(
            ComponentDiscovery()
        )

        result = registry.build()

        print(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )

        return 0

    if args.inspect:

        mastermind = Mastermind(
            owner=args.owner
        )

        result = (
            mastermind.inspect_factory()
        )

        print(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )

        return (
            0
            if result.get("success")
            else 1
        )

    if args.monitor:

        monitor = ContinuousMonitor(
            owner=args.owner
        )

        print(
            json.dumps(
                {
                    "success": True,
                    "status": (
                        "CONTINUOUS_MONITOR_STARTED"
                    ),
                    "interval_seconds":
                        monitor.interval,
                },
                ensure_ascii=False,
                indent=2,
            )
        )

        try:
            monitor.run_forever()

        except KeyboardInterrupt:
            monitor.stop()

        return 0

    command = " ".join(
        args.command
    ).strip()

    if not command:
        command = input(
            "👑 OWNER > "
        ).strip()

    mastermind = Mastermind(
        owner=args.owner
    )

    result = mastermind.run(
        command=command,
        owner=args.owner,
    )

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    )

    return (
        0
        if result.get("success")
        else 1
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    raise SystemExit(
        main()
    )

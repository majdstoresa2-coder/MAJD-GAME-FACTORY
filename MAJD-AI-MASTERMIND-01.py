#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-AI-MASTERMIND-01.py
============================================================
MAJD SOVEREIGN AUTONOMOUS MASTERMIND
VERSION 4.0.0

العقل المدبر المركزي لمنصة ومصنع مجد.

الهدف:
OWNER
  ↓
01 MASTERMIND
  ↓
فهم وتصنيف الأمر
  ↓
اختيار المنفذ الحقيقي
  ├─ 02 OWNER COMMAND CENTER
  ├─ 03 REAL GAME EXECUTOR
  ├─ 04 OFFICIAL PLATFORM BRIDGE
  ├─ 05 AI ORCHESTRATOR
  ├─ 06 FULL EXECUTION RUNTIME
  └─ 08 CONTENT + MEDIA FACTORY
  ↓
تنفيذ حقيقي
  ↓
تحقق
  ↓
إصلاح تلقائي عند الإمكان
  ↓
إعادة اختبار
  ↓
نتيجة حقيقية فقط

قواعد سيادية:
- لا نجاح وهمي.
- لا يعتبر None نجاحاً.
- لا يعتبر مجرد استدعاء دالة نجاحاً.
- لا يعتبر Artifact صالحاً دون وجوده فعلياً.
- لا يعتبر نشر لعبة ناجحاً دون تحقق من النسخة المنشورة.
- لا يتم تعديل أي مسار خارج MAJD-GAME-FACTORY.
- النسخ الاحتياطي إلزامي قبل استبدال أي ملف.
- إصلاح Python يستخدم بيئة المشروع الافتراضية فقط.
- لا يستخدم --break-system-packages.
- لا يعبث بحزم Python الخاصة بنظام Ubuntu.
- 01 يدير ويوجه؛ لا يكرر مسؤوليات الملفات الأخرى.
"""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
import os
import re
import shutil
import subprocess
import sys
import time
import traceback
import urllib.request
import uuid

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple


# ============================================================
# IDENTITY
# ============================================================

SYSTEM_NAME = "MAJD-GAME-FACTORY"
MASTERMIND_NAME = "MAJD-SOVEREIGN-MASTERMIND"
VERSION = "4.0.0"

DEFAULT_OWNER = "MAJD"

MAX_REPAIR_ATTEMPTS = int(
    os.getenv(
        "MAJD_MAX_REPAIR_ATTEMPTS",
        "5",
    )
)

COMMAND_TIMEOUT = int(
    os.getenv(
        "MAJD_COMMAND_TIMEOUT",
        "900",
    )
)

AI_TIMEOUT = int(
    os.getenv(
        "MAJD_AI_TIMEOUT",
        "180",
    )
)


# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent

STATE_DIR = ROOT_DIR / "majd_factory_state"
MASTERMIND_STATE_DIR = STATE_DIR / "mastermind"
LOG_DIR = STATE_DIR / "logs"
BACKUP_DIR = STATE_DIR / "backups"
OUTPUT_DIR = ROOT_DIR / "majd_game_output"
PUBLIC_DIR = ROOT_DIR / "public"
ARTIFACTS_DIR = PUBLIC_DIR / "artifacts"

for directory in (
    STATE_DIR,
    MASTERMIND_STATE_DIR,
    LOG_DIR,
    BACKUP_DIR,
    OUTPUT_DIR,
    PUBLIC_DIR,
    ARTIFACTS_DIR,
):
    directory.mkdir(
        parents=True,
        exist_ok=True,
    )


OWNER_COMMAND_CENTER_FILE = (
    ROOT_DIR / "MAJD-OWNER-COMMAND-CENTER-02.py"
)

REAL_GAME_EXECUTOR_FILE = (
    ROOT_DIR / "MAJD-REAL-GAME-EXECUTOR-03.py"
)

OFFICIAL_PLATFORM_BRIDGE_FILE = (
    ROOT_DIR / "MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py"
)

AI_ORCHESTRATOR_FILE = (
    ROOT_DIR / "MAJD-AI-ORCHESTRATOR-05.py"
)

FULL_RUNTIME_FILE = (
    ROOT_DIR / "MAJD-FULL-EXECUTION-RUNTIME-06.py"
)

CONTENT_MEDIA_FACTORY_FILE = (
    ROOT_DIR / "MAJD-AI-CONTENT-MEDIA-FACTORY-08.py"
)

AGENT_FILE = (
    ROOT_DIR / "majd_ai_agent.py"
)


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
# TIME / JSON / HASH
# ============================================================

def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def write_json(
    path: Path,
    value: Any,
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
            value,
            file,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

        file.flush()

        try:
            os.fsync(
                file.fileno()
            )
        except OSError:
            pass

    temporary.replace(
        path
    )


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as file:
        while True:
            chunk = file.read(
                1024 * 1024
            )

            if not chunk:
                break

            digest.update(
                chunk
            )

    return digest.hexdigest()


# ============================================================
# PATH SAFETY
# ============================================================

def is_inside_root(
    path: Path,
) -> bool:
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
    candidate = Path(
        value
    )

    if not candidate.is_absolute():
        candidate = (
            ROOT_DIR
            /
            candidate
        )

    candidate = candidate.resolve()

    if not is_inside_root(
        candidate
    ):
        raise PermissionError(
            "Refusing path outside MAJD-GAME-FACTORY"
        )

    return candidate


# ============================================================
# MODULE LOADER
# ============================================================

def load_module(
    path: Path,
    name: str,
) -> Any:
    path = safe_project_path(
        path
    )

    if not path.exists():
        raise FileNotFoundError(
            str(path)
        )

    specification = (
        importlib.util
        .spec_from_file_location(
            name,
            str(path),
        )
    )

    if (
        specification is None
        or
        specification.loader is None
    ):
        raise ImportError(
            f"Unable to load module: {path.name}"
        )

    module = (
        importlib.util
        .module_from_spec(
            specification
        )
    )

    sys.modules[
        name
    ] = module

    specification.loader.exec_module(
        module
    )

    return module


# ============================================================
# SAFE FUNCTION CALL
# ============================================================

def call_supported(
    function: Callable[..., Any],
    values: Dict[str, Any],
) -> Any:
    try:
        signature = inspect.signature(
            function
        )
    except (
        TypeError,
        ValueError,
    ):
        return function(
            **values
        )

    accepts_kwargs = any(
        parameter.kind
        ==
        inspect.Parameter.VAR_KEYWORD
        for parameter
        in signature.parameters.values()
    )

    if accepts_kwargs:
        return function(
            **values
        )

    supported: Dict[
        str,
        Any
    ] = {}

    for key, value in values.items():
        if key in signature.parameters:
            supported[
                key
            ] = value

    return function(
        **supported
    )


# ============================================================
# RESULT NORMALIZATION
# ============================================================

def normalize_component_result(
    value: Any,
    component: str,
) -> Dict[str, Any]:
    """
    Strict normalization.

    None is NEVER success.
    A dict must explicitly contain success=True.
    Non-dict values are not trusted as success.
    """

    if value is None:
        return {
            "success": False,
            "status": "COMPONENT_RETURNED_NONE",
            "component": component,
        }

    if isinstance(
        value,
        dict,
    ):
        result = dict(
            value
        )

        if result.get(
            "success"
        ) is not True:
            result[
                "success"
            ] = False

            result.setdefault(
                "status",
                "COMPONENT_DID_NOT_CONFIRM_SUCCESS",
            )

        result.setdefault(
            "component",
            component,
        )

        return result

    return {
        "success": False,
        "status": "UNVERIFIED_COMPONENT_RESULT",
        "component": component,
        "result_type": type(value).__name__,
        "result": str(value),
    }


# ============================================================
# DATA TYPES
# ============================================================

@dataclass
class CommandResult:
    command: List[str]
    returncode: int
    stdout: str
    stderr: str
    success: bool
    duration_seconds: float


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

    route: Optional[str] = None

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
# AUDIT LOGGER
# ============================================================

class AuditLogger:

    def __init__(
        self,
        operation_id: str,
    ):
        self.operation_id = (
            operation_id
        )

        self.path = (
            LOG_DIR
            /
            f"{operation_id}.jsonl"
        )


    def log(
        self,
        event: str,
        data: Optional[
            Dict[str, Any]
        ] = None,
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
                +
                "\n"
            )


# ============================================================
# BACKUP MANAGER
# ============================================================

class BackupManager:

    def __init__(
        self,
        operation_id: str,
    ):
        self.root = (
            BACKUP_DIR
            /
            operation_id
        )

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )


    def backup(
        self,
        path: Path,
    ) -> Optional[str]:
        path = safe_project_path(
            path
        )

        if not path.exists():
            return None

        target = (
            self.root
            /
            path.relative_to(
                ROOT_DIR
            )
        )

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if path.is_dir():
            if target.exists():
                shutil.rmtree(
                    target
                )

            shutil.copytree(
                path,
                target,
            )
        else:
            shutil.copy2(
                path,
                target,
            )

        return str(
            target
        )


# ============================================================
# PYTHON ENVIRONMENT
# ============================================================

class PythonEnvironment:

    @staticmethod
    def project_python() -> Path:
        candidates = (
            ROOT_DIR
            /
            ".venv"
            /
            "bin"
            /
            "python",

            ROOT_DIR
            /
            "venv"
            /
            "bin"
            /
            "python",
        )

        for candidate in candidates:
            if (
                candidate.exists()
                and
                candidate.is_file()
            ):
                return candidate

        executable = Path(
            sys.executable
        ).resolve()

        try:
            executable.relative_to(
                ROOT_DIR.resolve()
            )

            return executable

        except Exception:
            raise RuntimeError(
                "PROJECT_VIRTUAL_ENVIRONMENT_REQUIRED"
            )


# ============================================================
# PROCESS EXECUTOR
# ============================================================

class ProcessExecutor:

    BLOCKED_COMMANDS = {
        "reboot",
        "shutdown",
        "poweroff",
        "halt",
        "mkfs",
        "fdisk",
        "parted",
        "dd",
    }


    def run(
        self,
        command: List[str],
        cwd: Optional[
            Path
        ] = None,
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
            str(
                command[0]
            )
        ).name

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
                cwd=str(
                    working_directory
                ),
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
                    completed.returncode
                    ==
                    0
                ),
                duration_seconds=(
                    time.time()
                    -
                    started
                ),
            )

        except subprocess.TimeoutExpired as error:
            return CommandResult(
                command=command,
                returncode=124,
                stdout=(
                    error.stdout
                    if isinstance(
                        error.stdout,
                        str,
                    )
                    else ""
                ),
                stderr="Command timed out.",
                success=False,
                duration_seconds=(
                    time.time()
                    -
                    started
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
                    time.time()
                    -
                    started
                ),
            )


# ============================================================
# PROJECT INSPECTOR
# ============================================================

class ProjectInspector:

    IGNORE = {
        ".git",
        "__pycache__",
        "node_modules",
        ".venv",
        "venv",
        "majd_factory_state",
        "majd_game_output",
    }

    CORE = {
        "01":
            "MAJD-AI-MASTERMIND-01.py",

        "02":
            "MAJD-OWNER-COMMAND-CENTER-02.py",

        "03":
            "MAJD-REAL-GAME-EXECUTOR-03.py",

        "04":
            "MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py",

        "05":
            "MAJD-AI-ORCHESTRATOR-05.py",

        "06":
            "MAJD-FULL-EXECUTION-RUNTIME-06.py",

        "08":
            "MAJD-AI-CONTENT-MEDIA-FACTORY-08.py",

        "agent":
            "majd_ai_agent.py",
    }


    def list_files(
        self,
        limit: int = 5000,
    ) -> List[str]:
        result: List[
            str
        ] = []

        for path in ROOT_DIR.rglob(
            "*"
        ):
            if len(
                result
            ) >= limit:
                break

            try:
                relative = path.relative_to(
                    ROOT_DIR
                )
            except Exception:
                continue

            if any(
                part in self.IGNORE
                for part in relative.parts
            ):
                continue

            if path.is_file():
                result.append(
                    str(
                        relative
                    )
                )

        return sorted(
            result
        )


    def detect_stack(
        self,
    ) -> Dict[str, Any]:
        return {
            "python":
                any(
                    ROOT_DIR.glob(
                        "*.py"
                    )
                ),

            "node":
                (
                    ROOT_DIR
                    /
                    "package.json"
                ).exists(),

            "requirements":
                (
                    ROOT_DIR
                    /
                    "requirements.txt"
                ).exists(),

            "docker":
                (
                    ROOT_DIR
                    /
                    "Dockerfile"
                ).exists(),

            "docker_compose":
                any(
                    (
                        ROOT_DIR
                        /
                        filename
                    ).exists()
                    for filename
                    in (
                        "docker-compose.yml",
                        "docker-compose.yaml",
                        "compose.yml",
                        "compose.yaml",
                    )
                ),
        }


    def core_status(
        self,
    ) -> Dict[str, Any]:
        result: Dict[
            str,
            Any
        ] = {}

        for number, filename in (
            self.CORE.items()
        ):
            path = (
                ROOT_DIR
                /
                filename
            )

            result[
                number
            ] = {
                "file":
                    filename,

                "exists":
                    path.exists(),

                "size":
                    (
                        path.stat().st_size
                        if path.exists()
                        else 0
                    ),

                "sha256":
                    (
                        sha256_file(
                            path
                        )
                        if path.exists()
                        else None
                    ),
            }

        return result


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
        python = PythonEnvironment.project_python()

        return self.executor.run(
            [
                str(
                    python
                ),
                "-m",
                "py_compile",
                str(
                    path
                ),
            ],
            cwd=ROOT_DIR,
        )


    def compile_project(
        self,
    ) -> Dict[str, Any]:
        checked = []
        failed = []

        for path in sorted(
            ROOT_DIR.glob(
                "*.py"
            )
        ):
            try:
                result = (
                    self.compile_file(
                        path
                    )
                )

                item = {
                    "file":
                        path.name,

                    "success":
                        result.success,

                    "stderr":
                        result.stderr[
                            -6000:
                        ],
                }

            except Exception as error:
                item = {
                    "file":
                        path.name,

                    "success":
                        False,

                    "stderr":
                        (
                            f"{type(error).__name__}: "
                            f"{error}"
                        ),
                }

            checked.append(
                item
            )

            if not item[
                "success"
            ]:
                failed.append(
                    item
                )

        return {
            "success":
                not failed,

            "checked":
                checked,

            "failed":
                failed,
        }


    def import_core(
        self,
    ) -> Dict[str, Any]:
        checked = []
        failed = []

        for key, filename in (
            ProjectInspector
            .CORE.items()
        ):
            path = (
                ROOT_DIR
                /
                filename
            )

            if not path.exists():
                continue

            try:
                load_module(
                    path,
                    (
                        f"_majd_check_"
                        f"{key}_"
                        f"{uuid.uuid4().hex}"
                    ),
                )

                item = {
                    "file":
                        filename,
                    "success":
                        True,
                }

            except Exception as error:
                item = {
                    "file":
                        filename,

                    "success":
                        False,

                    "error":
                        (
                            f"{type(error).__name__}: "
                            f"{error}"
                        ),

                    "traceback":
                        traceback.format_exc()[
                            -6000:
                        ],
                }

                failed.append(
                    item
                )

            checked.append(
                item
            )

        return {
            "success":
                not failed,

            "checked":
                checked,

            "failed":
                failed,
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


    def repair_missing_python_module(
        self,
        error_text: str,
    ) -> Optional[
        Dict[str, Any]
    ]:
        match = re.search(
            (
                r"No module named "
                r"['\"]([^'\"]+)['\"]"
            ),
            error_text,
        )

        if not match:
            return None

        module = (
            match.group(1)
            .split(".")[0]
        )

        package = (
            self.PYTHON_IMPORT_MAP
            .get(
                module,
                module,
            )
        )

        try:
            python = (
                PythonEnvironment
                .project_python()
            )

        except Exception as error:
            return {
                "success": False,
                "status": "PROJECT_VENV_REQUIRED",
                "error": str(error),
            }

        self.logger.log(
            "PYTHON_DEPENDENCY_INSTALL",
            {
                "module":
                    module,
                "package":
                    package,
                "python":
                    str(
                        python
                    ),
            },
        )

        result = self.executor.run(
            [
                str(
                    python
                ),
                "-m",
                "pip",
                "install",
                package,
            ],
            cwd=ROOT_DIR,
            timeout=600,
        )

        return asdict(
            result
        )


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
    def available(
        self,
    ) -> bool:
        return bool(
            LOCAL_AI_URL
        )


    def ask(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> Optional[str]:
        if not self.available:
            return None

        endpoint = (
            LOCAL_AI_URL.rstrip(
                "/"
            )
            +
            "/v1/chat/completions"
        )

        payload = {
            "model":
                LOCAL_AI_MODEL,

            "temperature":
                0.1,

            "messages": [
                {
                    "role":
                        "system",
                    "content":
                        system_prompt,
                },
                {
                    "role":
                        "user",
                    "content":
                        user_prompt,
                },
            ],
        }

        request = urllib.request.Request(
            endpoint,
            data=json.dumps(
                payload
            ).encode(
                "utf-8"
            ),
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
                    response
                    .read()
                    .decode(
                        "utf-8"
                    )
                )

            choices = (
                body.get(
                    "choices"
                )
                or
                []
            )

            if not choices:
                return None

            return (
                choices[0]
                .get(
                    "message",
                    {}
                )
                .get(
                    "content"
                )
            )

        except Exception as error:
            self.logger.log(
                "LOCAL_AI_ERROR",
                {
                    "error":
                        (
                            f"{type(error).__name__}: "
                            f"{error}"
                        ),
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
    ):
        self.backup = backup
        self.logger = logger


    def replace_file(
        self,
        path: Path,
        content: str,
    ) -> Dict[str, Any]:
        path = safe_project_path(
            path
        )

        backup = self.backup.backup(
            path
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary = path.with_suffix(
            path.suffix + ".majd-tmp"
        )

        temporary.write_text(
            content,
            encoding="utf-8",
        )

        if path.suffix == ".py":
            try:
                python = (
                    PythonEnvironment
                    .project_python()
                )

                check = subprocess.run(
                    [
                        str(
                            python
                        ),
                        "-m",
                        "py_compile",
                        str(
                            temporary
                        ),
                    ],
                    cwd=str(
                        ROOT_DIR
                    ),
                    capture_output=True,
                    text=True,
                    timeout=120,
                )

                if check.returncode != 0:
                    temporary.unlink(
                        missing_ok=True
                    )

                    return {
                        "success":
                            False,

                        "status":
                            "REPLACEMENT_SYNTAX_INVALID",

                        "path":
                            str(
                                path
                            ),

                        "stderr":
                            check.stderr,
                    }

            except Exception as error:
                temporary.unlink(
                    missing_ok=True
                )

                return {
                    "success":
                        False,

                    "status":
                        "REPLACEMENT_VALIDATION_FAILED",

                    "error":
                        (
                            f"{type(error).__name__}: "
                            f"{error}"
                        ),
                }

        temporary.replace(
            path
        )

        self.logger.log(
            "FILE_REPLACED",
            {
                "path":
                    str(
                        path.relative_to(
                            ROOT_DIR
                        )
                    ),

                "backup":
                    backup,

                "sha256":
                    sha256_file(
                        path
                    ),
            },
        )

        return {
            "success":
                True,

            "status":
                "FILE_REPLACED",

            "path":
                str(
                    path
                ),

            "backup":
                backup,

            "sha256":
                sha256_file(
                    path
                ),
        }


# ============================================================
# INTERFACE CHECKER
# ============================================================

class InterfaceChecker:

    CHECKS = (
        (
            OWNER_COMMAND_CENTER_FILE,
            "02",
            (
                "process_command",
                "execute_command",
                "execute_request",
                "run_command",
                "run",
                "execute",
            ),
        ),
        (
            REAL_GAME_EXECUTOR_FILE,
            "03",
            (
                "execute_game_request",
                "execute",
                "run",
            ),
        ),
        (
            OFFICIAL_PLATFORM_BRIDGE_FILE,
            "04",
            (
                "publish_game",
            ),
        ),
        (
            AI_ORCHESTRATOR_FILE,
            "05",
            (
                "orchestrate",
                "execute",
                "run",
                "process",
                "process_command",
            ),
        ),
        (
            FULL_RUNTIME_FILE,
            "06",
            (
                "execute_command",
                "process_command",
                "run_command",
                "execute",
                "run",
            ),
        ),
        (
            CONTENT_MEDIA_FACTORY_FILE,
            "08",
            (
                "execute_request",
                "process_request",
                "execute_command",
                "process_command",
                "create_content",
                "run",
                "execute",
            ),
        ),
    )


    def check(
        self,
    ) -> Dict[str, Any]:
        results = []
        failed = []

        for (
            path,
            number,
            names,
        ) in self.CHECKS:
            if not path.exists():
                item = {
                    "file":
                        path.name,

                    "number":
                        number,

                    "success":
                        False,

                    "error":
                        "FILE_MISSING",
                }

                results.append(
                    item
                )

                failed.append(
                    item
                )

                continue

            try:
                module = load_module(
                    path,
                    (
                        f"_majd_iface_"
                        f"{number}_"
                        f"{uuid.uuid4().hex}"
                    ),
                )

                found = [
                    name
                    for name in names
                    if callable(
                        getattr(
                            module,
                            name,
                            None,
                        )
                    )
                ]

                item = {
                    "file":
                        path.name,

                    "number":
                        number,

                    "success":
                        bool(
                            found
                        ),

                    "found":
                        found,

                    "expected_any":
                        list(
                            names
                        ),
                }

            except Exception as error:
                item = {
                    "file":
                        path.name,

                    "number":
                        number,

                    "success":
                        False,

                    "error":
                        (
                            f"{type(error).__name__}: "
                            f"{error}"
                        ),
                }

            results.append(
                item
            )

            if not item[
                "success"
            ]:
                failed.append(
                    item
                )

        return {
            "success":
                not failed,

            "checked":
                results,

            "failed":
                failed,
        }


# ============================================================
# DIAGNOSTIC ENGINE
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
            "no module named"
            in lowered
            or
            "modulenotfounderror"
            in lowered
        ):
            return {
                "type":
                    "MISSING_PYTHON_MODULE",

                "repairable":
                    True,

                "details":
                    text[
                        -12000:
                    ],
            }

        if any(
            token in lowered
            for token
            in (
                "syntaxerror",
                "indentationerror",
                "taberror",
            )
        ):
            return {
                "type":
                    "PYTHON_SYNTAX_ERROR",

                "repairable":
                    True,

                "details":
                    text[
                        -12000:
                    ],
            }

        if (
            "interface"
            in lowered
        ):
            return {
                "type":
                    "INTERFACE_MISMATCH",

                "repairable":
                    True,

                "details":
                    text[
                        -12000:
                    ],
            }

        if (
            "artifact"
            in lowered
        ):
            return {
                "type":
                    "ARTIFACT_FAILURE",

                "repairable":
                    True,

                "details":
                    text[
                        -12000:
                    ],
            }

        return {
            "type":
                "UNKNOWN",

            "repairable":
                False,

            "details":
                text[
                    -12000:
                ],
        }


# ============================================================
# AUTONOMOUS REPAIR ENGINE
# ============================================================

class AutonomousRepairEngine:

    def __init__(
        self,
        operation_id: str,
        logger: AuditLogger,
    ):
        self.operation_id = (
            operation_id
        )

        self.logger = logger

        self.executor = (
            ProcessExecutor()
        )

        self.backup = (
            BackupManager(
                operation_id
            )
        )

        self.dependencies = (
            DependencyManager(
                self.executor,
                logger,
            )
        )

        self.code = (
            CodeManager(
                self.backup,
                logger,
            )
        )

        self.ai = (
            LocalAIAdapter(
                logger
            )
        )


    def repair(
        self,
        diagnosis: Dict[str, Any],
        failure: Dict[str, Any],
    ) -> Dict[str, Any]:
        repair_type = diagnosis.get(
            "type"
        )

        if (
            repair_type
            ==
            "MISSING_PYTHON_MODULE"
        ):
            text = json.dumps(
                failure,
                ensure_ascii=False,
                default=str,
            )

            result = (
                self.dependencies
                .repair_missing_python_module(
                    text
                )
            )

            return (
                result
                or
                {
                    "success":
                        False,

                    "status":
                        "DEPENDENCY_NAME_NOT_DETECTED",
                }
            )

        if repair_type in {
            "PYTHON_SYNTAX_ERROR",
            "INTERFACE_MISMATCH",
            "ARTIFACT_FAILURE",
        }:
            if not self.ai.available:
                return {
                    "success":
                        False,

                    "status":
                        "CODE_REPAIR_ENGINE_UNAVAILABLE",

                    "diagnosis":
                        diagnosis,
                }

            files = (
                ProjectInspector()
                .list_files(
                    limit=600
                )
            )

            prompt = (
                "Repair MAJD-GAME-FACTORY from the "
                "real failure below.\n\n"

                "Return JSON only:\n"
                "{"
                "\"success\":true,"
                "\"changes\":["
                "{"
                "\"path\":\"relative/path.py\","
                "\"content\":\"COMPLETE FILE CONTENT\""
                "}"
                "]"
                "}\n\n"

                "Rules:\n"
                "- Complete replacement files only.\n"
                "- Never modify outside MAJD-GAME-FACTORY.\n"
                "- Preserve existing public interfaces when possible.\n"
                "- Never claim success without a real change.\n"
                "- Do not remove sovereign validation.\n\n"

                "FAILURE:\n"
                +
                json.dumps(
                    failure,
                    ensure_ascii=False,
                    default=str,
                )
                +
                "\n\nDIAGNOSIS:\n"
                +
                json.dumps(
                    diagnosis,
                    ensure_ascii=False,
                    default=str,
                )
                +
                "\n\nPROJECT FILES:\n"
                +
                json.dumps(
                    files,
                    ensure_ascii=False,
                )
            )

            answer = self.ai.ask(
                (
                    "You are MAJD Sovereign autonomous "
                    "code repair engine. "
                    "Never return fake success."
                ),
                prompt,
            )

            if not answer:
                return {
                    "success":
                        False,

                    "status":
                        "AI_REPAIR_EMPTY",
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

                data = json.loads(
                    cleaned
                )

                applied = []
                rejected = []

                for change in (
                    data.get(
                        "changes"
                    )
                    or
                    []
                ):
                    relative = str(
                        change.get(
                            "path"
                        )
                        or
                        ""
                    ).strip()

                    content = change.get(
                        "content"
                    )

                    if (
                        not relative
                        or
                        not isinstance(
                            content,
                            str,
                        )
                        or
                        not content.strip()
                    ):
                        continue

                    result = (
                        self.code
                        .replace_file(
                            ROOT_DIR
                            /
                            relative,
                            content,
                        )
                    )

                    if result.get(
                        "success"
                    ):
                        applied.append(
                            result
                        )
                    else:
                        rejected.append(
                            result
                        )

                return {
                    "success":
                        bool(
                            applied
                        )
                        and
                        not rejected,

                    "status":
                        (
                            "AI_CODE_REPAIR_APPLIED"
                            if (
                                applied
                                and
                                not rejected
                            )
                            else
                            "AI_CODE_REPAIR_INCOMPLETE"
                        ),

                    "changes":
                        applied,

                    "rejected":
                        rejected,
                }

            except Exception as error:
                return {
                    "success":
                        False,

                    "status":
                        "AI_REPAIR_RESPONSE_INVALID",

                    "error":
                        (
                            f"{type(error).__name__}: "
                            f"{error}"
                        ),
                }

        return {
            "success":
                False,

            "status":
                "AUTOMATIC_REPAIR_NOT_AVAILABLE",

            "diagnosis":
                diagnosis,
        }


# ============================================================
# GENERIC COMPONENT ADAPTER
# ============================================================

class ComponentAdapter:

    def __init__(
        self,
        path: Path,
        component: str,
        functions: Iterable[str],
    ):
        self.path = path
        self.component = component
        self.functions = tuple(
            functions
        )


    def execute(
        self,
        values: Dict[str, Any],
    ) -> Dict[str, Any]:
        if not self.path.exists():
            return {
                "success":
                    False,

                "status":
                    "COMPONENT_FILE_MISSING",

                "component":
                    self.component,

                "file":
                    self.path.name,
            }

        try:
            module = load_module(
                self.path,
                (
                    f"_majd_component_"
                    f"{self.component}_"
                    f"{uuid.uuid4().hex}"
                ),
            )

        except Exception as error:
            return {
                "success":
                    False,

                "status":
                    "COMPONENT_LOAD_FAILED",

                "component":
                    self.component,

                "error":
                    (
                        f"{type(error).__name__}: "
                        f"{error}"
                    ),

                "traceback":
                    traceback.format_exc(),
            }

        for name in self.functions:
            function = getattr(
                module,
                name,
                None,
            )

            if not callable(
                function
            ):
                continue

            try:
                value = call_supported(
                    function,
                    values,
                )

                result = normalize_component_result(
                    value,
                    self.component,
                )

                result.setdefault(
                    "interface",
                    name,
                )

                return result

            except Exception as error:
                return {
                    "success":
                        False,

                    "status":
                        "COMPONENT_EXECUTION_EXCEPTION",

                    "component":
                        self.component,

                    "interface":
                        name,

                    "error":
                        (
                            f"{type(error).__name__}: "
                            f"{error}"
                        ),

                    "traceback":
                        traceback.format_exc(),
                }

        return {
            "success":
                False,

            "status":
                "COMPONENT_INTERFACE_MISSING",

            "component":
                self.component,

            "expected_any":
                list(
                    self.functions
                ),
        }


# ============================================================
# OWNER COMMAND CENTER 02
# ============================================================

class OwnerCommandCenterBridge(
    ComponentAdapter
):

    def __init__(
        self,
    ):
        super().__init__(
            OWNER_COMMAND_CENTER_FILE,
            "02_OWNER_COMMAND_CENTER",
            (
                "process_command",
                "execute_command",
                "execute_request",
                "run_command",
                "run",
                "execute",
            ),
        )


# ============================================================
# ORCHESTRATOR 05
# ============================================================

class OrchestratorBridge(
    ComponentAdapter
):

    def __init__(
        self,
    ):
        super().__init__(
            AI_ORCHESTRATOR_FILE,
            "05_AI_ORCHESTRATOR",
            (
                "orchestrate",
                "process_command",
                "process",
                "execute",
                "run",
            ),
        )


# ============================================================
# FULL RUNTIME 06
# ============================================================

class FullRuntimeBridge(
    ComponentAdapter
):

    def __init__(
        self,
    ):
        super().__init__(
            FULL_RUNTIME_FILE,
            "06_FULL_EXECUTION_RUNTIME",
            (
                "execute_command",
                "process_command",
                "run_command",
                "execute",
                "run",
            ),
        )


# ============================================================
# CONTENT / MEDIA FACTORY 08
# ============================================================

class ContentMediaBridge(
    ComponentAdapter
):

    def __init__(
        self,
    ):
        super().__init__(
            CONTENT_MEDIA_FACTORY_FILE,
            "08_CONTENT_MEDIA_FACTORY",
            (
                "execute_request",
                "process_request",
                "execute_command",
                "process_command",
                "create_content",
                "run",
                "execute",
            ),
        )


# ============================================================
# REAL GAME EXECUTOR 03
# ============================================================

class GameExecutorBridge:

    def execute(
        self,
        request: Dict[str, Any],
        job_id: str,
    ) -> Dict[str, Any]:
        if not REAL_GAME_EXECUTOR_FILE.exists():
            return {
                "success":
                    False,

                "status":
                    "REAL_EXECUTOR_FILE_MISSING",
            }

        try:
            module = load_module(
                REAL_GAME_EXECUTOR_FILE,
                (
                    "majd_real_game_executor_03_"
                    +
                    uuid.uuid4().hex
                ),
            )

            function = getattr(
                module,
                "execute_game_request",
                None,
            )

            if not callable(
                function
            ):
                return {
                    "success":
                        False,

                    "status":
                        "REAL_EXECUTOR_INTERFACE_MISSING",

                    "required":
                        "execute_game_request",
                }

            value = call_supported(
                function,
                {
                    "request":
                        request,

                    "payload":
                        request,

                    "job_id":
                        job_id,

                    "output_root":
                        str(
                            OUTPUT_DIR
                        ),
                },
            )

            return normalize_component_result(
                value,
                "03_REAL_GAME_EXECUTOR",
            )

        except Exception as error:
            return {
                "success":
                    False,

                "status":
                    "REAL_GAME_EXECUTOR_EXCEPTION",

                "error":
                    (
                        f"{type(error).__name__}: "
                        f"{error}"
                    ),

                "traceback":
                    traceback.format_exc(),
            }


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


    def _candidate(
        self,
        value: Any,
    ) -> Optional[Path]:
        if not value:
            return None

        path = Path(
            str(
                value
            )
        ).expanduser()

        if not path.is_absolute():
            path = (
                ROOT_DIR
                /
                path
            ).resolve()
        else:
            path = path.resolve()

        if not is_inside_root(
            path
        ):
            return None

        if not path.exists():
            return None

        return path


    def extract(
        self,
        result: Dict[str, Any],
    ) -> Optional[Path]:
        for key in self.KEYS:
            path = self._candidate(
                result.get(
                    key
                )
            )

            if path is not None:
                return path

        for nested_key in (
            "result",
            "build",
            "output",
            "game",
        ):
            nested = result.get(
                nested_key
            )

            if not isinstance(
                nested,
                dict,
            ):
                continue

            for key in self.KEYS:
                path = self._candidate(
                    nested.get(
                        key
                    )
                )

                if path is not None:
                    return path

        return None


    def verify(
        self,
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        path = self.extract(
            result
        )

        if path is None:
            return {
                "success":
                    False,

                "status":
                    "ARTIFACT_MISSING",
            }

        if not is_inside_root(
            path
        ):
            return {
                "success":
                    False,

                "status":
                    "ARTIFACT_OUTSIDE_PROJECT",

                "artifact":
                    str(
                        path
                    ),
            }

        if not path.exists():
            return {
                "success":
                    False,

                "status":
                    "ARTIFACT_NOT_FOUND",

                "artifact":
                    str(
                        path
                    ),
            }

        if not path.is_dir():
            return {
                "success":
                    False,

                "status":
                    "ARTIFACT_NOT_DIRECTORY",

                "artifact":
                    str(
                        path
                    ),
            }

        files = [
            item
            for item
            in path.rglob(
                "*"
            )
            if item.is_file()
        ]

        if not files:
            return {
                "success":
                    False,

                "status":
                    "ARTIFACT_EMPTY",

                "artifact":
                    str(
                        path
                    ),
            }

        index = (
            path
            /
            "index.html"
        )

        if (
            not index.exists()
            or
            not index.is_file()
            or
            index.stat().st_size <= 0
        ):
            return {
                "success":
                    False,

                "status":
                    "PLAYABLE_INDEX_NOT_FOUND",

                "artifact":
                    str(
                        path
                    ),
            }

        return {
            "success":
                True,

            "status":
                "ARTIFACT_VERIFIED",

            "artifact":
                str(
                    path
                ),

            "index":
                str(
                    index
                ),

            "file_count":
                len(
                    files
                ),
        }


# ============================================================
# OFFICIAL PLATFORM BRIDGE 04
# ============================================================

class PlatformBridge:

    def publish(
        self,
        artifact: str,
        request: Dict[str, Any],
        job_id: str,
    ) -> Dict[str, Any]:
        if not OFFICIAL_PLATFORM_BRIDGE_FILE.exists():
            return {
                "success":
                    False,

                "status":
                    "PLATFORM_BRIDGE_FILE_MISSING",
            }

        try:
            module = load_module(
                OFFICIAL_PLATFORM_BRIDGE_FILE,
                (
                    "majd_official_platform_bridge_04_"
                    +
                    uuid.uuid4().hex
                ),
            )

            publish_function = getattr(
                module,
                "publish_game",
                None,
            )

            if not callable(
                publish_function
            ):
                return {
                    "success":
                        False,

                    "status":
                        "PLATFORM_BRIDGE_INTERFACE_MISSING",

                    "required":
                        "publish_game",
                }

            value = call_supported(
                publish_function,
                {
                    "game_dir":
                        Path(
                            artifact
                        ),

                    "artifact":
                        Path(
                            artifact
                        ),

                    "artifact_path":
                        artifact,

                    "build_path":
                        artifact,

                    "game_name":
                        str(
                            request.get(
                                "name"
                            )
                            or
                            "MAJD-GAME"
                        ),

                    "job_id":
                        job_id,

                    "request":
                        request,

                    "payload":
                        request,
                },
            )

            return normalize_component_result(
                value,
                "04_OFFICIAL_PLATFORM_BRIDGE",
            )

        except Exception as error:
            return {
                "success":
                    False,

                "status":
                    "PLATFORM_BRIDGE_EXCEPTION",

                "error":
                    (
                        f"{type(error).__name__}: "
                        f"{error}"
                    ),

                "traceback":
                    traceback.format_exc(),
            }


# ============================================================
# PUBLICATION VERIFIER
# ============================================================

class PublicationVerifier:

    def verify(
        self,
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        if result.get(
            "success"
        ) is not True:
            return {
                "success":
                    False,

                "status":
                    "BRIDGE_REPORTED_FAILURE",
            }

        directory_value = (
            result.get(
                "published_directory"
            )
            or
            result.get(
                "publish_dir"
            )
            or
            result.get(
                "destination"
            )
        )

        if not directory_value:
            return {
                "success":
                    False,

                "status":
                    "PUBLISHED_DIRECTORY_MISSING",
            }

        directory = Path(
            str(
                directory_value
            )
        )

        if not directory.is_absolute():
            directory = (
                ROOT_DIR
                /
                directory
            ).resolve()
        else:
            directory = directory.resolve()

        if not is_inside_root(
            directory
        ):
            return {
                "success":
                    False,

                "status":
                    "PUBLISHED_DIRECTORY_OUTSIDE_PROJECT",
            }

        if (
            not directory.exists()
            or
            not directory.is_dir()
        ):
            return {
                "success":
                    False,

                "status":
                    "PUBLISHED_DIRECTORY_NOT_FOUND",

                "published_directory":
                    str(
                        directory
                    ),
            }

        index = (
            directory
            /
            "index.html"
        )

        if (
            not index.exists()
            or
            not index.is_file()
            or
            index.stat().st_size <= 0
        ):
            return {
                "success":
                    False,

                "status":
                    "PUBLISHED_INDEX_INVALID",

                "index":
                    str(
                        index
                    ),
            }

        game_path = result.get(
            "game_path"
        )

        public_url = result.get(
            "public_url"
        )

        if not game_path:
            try:
                relative = directory.relative_to(
                    PUBLIC_DIR
                )

                game_path = (
                    "/"
                    +
                    str(
                        relative
                    ).replace(
                        os.sep,
                        "/",
                    )
                    +
                    "/index.html"
                )
            except Exception:
                game_path = None

        if not game_path:
            return {
                "success":
                    False,

                "status":
                    "GAME_PATH_MISSING",
            }

        return {
            "success":
                True,

            "status":
                "REAL_PUBLICATION_VERIFIED",

            "published_directory":
                str(
                    directory
                ),

            "index":
                str(
                    index
                ),

            "game_path":
                str(
                    game_path
                ),

            "public_url":
                public_url,
        }


# ============================================================
# COMMAND CLASSIFIER
# ============================================================

class CommandClassifier:

    GAME_WORDS = (
        "أنشئ لعبة",
        "انشئ لعبة",
        "اصنع لعبة",
        "ابني لعبة",
        "بناء لعبة",
        "لعبة جديدة",
        "create game",
        "build game",
        "make game",
    )

    CONTENT_WORDS = (
        "فيديو",
        "صورة",
        "صور",
        "فيلم",
        "مسلسل",
        "حلقة",
        "قصة",
        "بوستر",
        "ملصق",
        "thumbnail",
        "صوت",
        "تعليق صوتي",
        "موسيقى",
        "ترجمة",
        "دبلجة",
        "بث",
        "بث مباشر",
        "منشور",
        "محتوى",
        "سوشال",
        "سوشيال",
        "تيك توك",
        "tiktok",
        "سناب",
        "snapchat",
        "youtube",
        "يوتيوب",
        "twitter",
        "تويتر",
        "منصة x",
        "social",
        "content",
        "media",
        "shorts",
        "reels",
        "live stream",
        "channel",
    )

    DIAGNOSTIC_WORDS = (
        "افحص",
        "فحص",
        "راجع",
        "اختبر",
        "اختبار",
        "مشاكل",
        "مشكلة",
        "أخطاء",
        "اخطاء",
        "خطأ",
        "diagnose",
        "check",
        "test",
        "validate",
        "debug",
        "inspect",
    )

    REPAIR_WORDS = (
        "أصلح",
        "اصلح",
        "إصلاح",
        "اصلاح",
        "صحح",
        "تصحيح",
        "repair",
        "fix",
        "recover",
        "self repair",
    )

    STATUS_WORDS = (
        "الحالة",
        "حالة المنصة",
        "حالة النظام",
        "status",
        "health",
    )

    RUNTIME_WORDS = (
        "شغل المنصة",
        "شغل النظام",
        "شغّل المنصة",
        "شغّل النظام",
        "التشغيل",
        "runtime",
        "deploy",
        "deployment",
        "تشغيل تلقائي",
        "إدارة المنصة",
        "ادارة المنصة",
        "autonomous",
    )


    def classify(
        self,
        command: str,
        request: Dict[str, Any],
    ) -> str:
        explicit = str(
            request.get(
                "type"
            )
            or
            ""
        ).strip().upper()

        aliases = {
            "CREATE_GAME":
                "CREATE_GAME",

            "GAME":
                "CREATE_GAME",

            "CONTENT":
                "CONTENT",

            "MEDIA":
                "CONTENT",

            "SOCIAL":
                "CONTENT",

            "DIAGNOSE":
                "DIAGNOSE",

            "INSPECT":
                "DIAGNOSE",

            "REPAIR":
                "REPAIR",

            "STATUS":
                "STATUS",

            "RUNTIME":
                "RUNTIME",

            "PLATFORM":
                "RUNTIME",

            "AUTONOMOUS":
                "RUNTIME",
        }

        if explicit in aliases:
            return aliases[
                explicit
            ]

        lowered = str(
            command
            or
            ""
        ).lower()

        if any(
            phrase in lowered
            for phrase in self.GAME_WORDS
        ):
            return "CREATE_GAME"

        if any(
            phrase in lowered
            for phrase in self.CONTENT_WORDS
        ):
            return "CONTENT"

        if any(
            phrase in lowered
            for phrase in self.REPAIR_WORDS
        ):
            return "REPAIR"

        if any(
            phrase in lowered
            for phrase in self.DIAGNOSTIC_WORDS
        ):
            return "DIAGNOSE"

        if any(
            phrase in lowered
            for phrase in self.STATUS_WORDS
        ):
            return "STATUS"

        if any(
            phrase in lowered
            for phrase in self.RUNTIME_WORDS
        ):
            return "RUNTIME"

        return "OWNER_COMMAND"


# ============================================================
# PLANNER
# ============================================================

class AutonomousPlanner:

    def plan(
        self,
        route: str,
    ) -> List[
        Dict[str, Any]
    ]:
        routes = {
            "CREATE_GAME": (
                "INSPECT",
                "EXECUTE_03",
                "VERIFY_ARTIFACT",
                "PUBLISH_04",
                "VERIFY_PUBLICATION",
            ),

            "CONTENT": (
                "INSPECT",
                "EXECUTE_08",
                "VERIFY_RESULT",
            ),

            "DIAGNOSE": (
                "INSPECT",
                "DIAGNOSE",
                "REPORT",
            ),

            "REPAIR": (
                "INSPECT",
                "DIAGNOSE",
                "REPAIR",
                "RECHECK",
            ),

            "RUNTIME": (
                "INSPECT",
                "EXECUTE_06",
                "VERIFY_RESULT",
            ),

            "STATUS": (
                "INSPECT",
                "REPORT",
            ),

            "OWNER_COMMAND": (
                "OWNER_02",
                "ORCHESTRATE_05",
                "VERIFY_RESULT",
            ),
        }

        return [
            {
                "stage":
                    stage
            }
            for stage
            in routes.get(
                route,
                routes[
                    "OWNER_COMMAND"
                ],
            )
        ]


# ============================================================
# MASTERMIND
# ============================================================

class Mastermind:

    def __init__(
        self,
        owner: str = DEFAULT_OWNER,
        max_repair_attempts: int = MAX_REPAIR_ATTEMPTS,
    ):
        self.owner = owner

        self.max_repair_attempts = max(
            1,
            int(
                max_repair_attempts
            ),
        )

        self.operation_id = str(
            uuid.uuid4()
        )

        self.logger = (
            AuditLogger(
                self.operation_id
            )
        )

        self.executor = (
            ProcessExecutor()
        )

        self.inspector = (
            ProjectInspector()
        )

        self.python_checker = (
            PythonChecker(
                self.executor
            )
        )

        self.interface_checker = (
            InterfaceChecker()
        )

        self.classifier = (
            CommandClassifier()
        )

        self.planner = (
            AutonomousPlanner()
        )

        self.diagnostics = (
            DiagnosticEngine()
        )

        self.repair_engine = (
            AutonomousRepairEngine(
                self.operation_id,
                self.logger,
            )
        )

        self.owner_center = (
            OwnerCommandCenterBridge()
        )

        self.orchestrator = (
            OrchestratorBridge()
        )

        self.runtime = (
            FullRuntimeBridge()
        )

        self.content_factory = (
            ContentMediaBridge()
        )

        self.game_executor = (
            GameExecutorBridge()
        )

        self.artifact_verifier = (
            ArtifactVerifier()
        )

        self.platform = (
            PlatformBridge()
        )

        self.publication_verifier = (
            PublicationVerifier()
        )


    # ========================================================
    # STATE
    # ========================================================

    def _state_path(
        self,
    ) -> Path:
        return (
            MASTERMIND_STATE_DIR
            /
            f"{self.operation_id}.json"
        )


    def _save_state(
        self,
        state: MastermindState,
    ) -> None:
        state.updated_at = (
            utc_now()
        )

        write_json(
            self._state_path(),
            asdict(
                state
            ),
        )


    def _event(
        self,
        state: MastermindState,
        event_type: str,
        data: Dict[str, Any],
    ) -> None:
        event = {
            "time":
                utc_now(),

            "type":
                event_type,

            "data":
                data,
        }

        state.events.append(
            event
        )

        self._save_state(
            state
        )

        self.logger.log(
            event_type,
            data,
        )


    # ========================================================
    # REQUEST
    # ========================================================

    def normalize_request(
        self,
        command: str,
        request: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Dict[str, Any]:
        data = dict(
            request
            or
            {}
        )

        data.setdefault(
            "request",
            command,
        )

        data.setdefault(
            "description",
            command,
        )

        data.setdefault(
            "command",
            command,
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

        return data


    # ========================================================
    # INSPECTION
    # ========================================================

    def inspect_factory(
        self,
    ) -> Dict[str, Any]:
        core = (
            self.inspector
            .core_status()
        )

        compile_report = (
            self.python_checker
            .compile_project()
        )

        import_report = (
            self.python_checker
            .import_core()
        )

        interface_report = (
            self.interface_checker
            .check()
        )

        required = (
            "01",
            "02",
            "03",
            "04",
            "05",
            "06",
            "08",
            "agent",
        )

        missing = [
            core[number][
                "file"
            ]
            for number in required
            if (
                number not in core
                or
                not core[
                    number
                ].get(
                    "exists"
                )
            )
        ]

        result = {
            "system":
                SYSTEM_NAME,

            "mastermind":
                MASTERMIND_NAME,

            "version":
                VERSION,

            "core_files":
                core,

            "required_missing":
                missing,

            "stack":
                self.inspector
                .detect_stack(),

            "file_count":
                len(
                    self.inspector
                    .list_files()
                ),

            "python_compile":
                compile_report,

            "python_imports":
                import_report,

            "interfaces":
                interface_report,
        }

        result[
            "success"
        ] = bool(
            not missing
            and
            compile_report.get(
                "success"
            ) is True
            and
            import_report.get(
                "success"
            ) is True
            and
            interface_report.get(
                "success"
            ) is True
        )

        result[
            "status"
        ] = (
            "FACTORY_VERIFIED"
            if result[
                "success"
            ]
            else
            "FACTORY_CHECK_FAILED"
        )

        return result


    # ========================================================
    # DIAGNOSIS
    # ========================================================

    def diagnose_inspection(
        self,
        inspection: Dict[str, Any],
    ) -> Dict[str, Any]:
        if inspection.get(
            "success"
        ) is True:
            return {
                "success":
                    True,

                "status":
                    "NO_ENFORCED_FAILURE_DETECTED",

                "inspection":
                    inspection,
            }

        failure = {
            "stage":
                "FACTORY_INSPECTION",

            "inspection":
                inspection,
        }

        diagnosis = (
            self.diagnostics
            .diagnose(
                failure
            )
        )

        return {
            "success":
                False,

            "status":
                "FAILURE_DETECTED",

            "failure":
                failure,

            "diagnosis":
                diagnosis,
        }


    # ========================================================
    # REPAIR
    # ========================================================

    def repair_factory(
        self,
        state: MastermindState,
    ) -> Dict[str, Any]:
        attempts = []

        for attempt in range(
            1,
            self.max_repair_attempts + 1,
        ):
            state.attempts = attempt
            state.status = (
                "AUTONOMOUS_REPAIR"
            )

            self._save_state(
                state
            )

            inspection = (
                self.inspect_factory()
            )

            self._event(
                state,
                "REPAIR_INSPECTION",
                inspection,
            )

            if inspection.get(
                "success"
            ) is True:
                return {
                    "success":
                        True,

                    "status":
                        "FACTORY_REPAIR_VERIFIED",

                    "attempt":
                        attempt,

                    "attempts":
                        attempts,

                    "factory":
                        inspection,
                }

            diagnosis_result = (
                self.diagnose_inspection(
                    inspection
                )
            )

            diagnosis = (
                diagnosis_result.get(
                    "diagnosis"
                )
                or
                {
                    "type":
                        "UNKNOWN",

                    "repairable":
                        False,
                }
            )

            failure = (
                diagnosis_result.get(
                    "failure"
                )
                or
                {
                    "inspection":
                        inspection
                }
            )

            repair = (
                self.repair_engine
                .repair(
                    diagnosis,
                    failure,
                )
            )

            record = {
                "attempt":
                    attempt,

                "diagnosis":
                    diagnosis,

                "repair":
                    repair,
            }

            attempts.append(
                record
            )

            self._event(
                state,
                "AUTONOMOUS_REPAIR_ATTEMPT",
                record,
            )

            if repair.get(
                "success"
            ) is not True:
                return {
                    "success":
                        False,

                    "status":
                        repair.get(
                            "status",
                            "AUTONOMOUS_REPAIR_FAILED",
                        ),

                    "attempt":
                        attempt,

                    "attempts":
                        attempts,

                    "diagnosis":
                        diagnosis,

                    "repair":
                        repair,

                    "factory":
                        inspection,
                }

        final_inspection = (
            self.inspect_factory()
        )

        return {
            "success":
                final_inspection.get(
                    "success"
                ) is True,

            "status":
                (
                    "FACTORY_REPAIR_VERIFIED"
                    if final_inspection.get(
                        "success"
                    ) is True
                    else
                    "MAX_AUTONOMOUS_REPAIR_ATTEMPTS_REACHED"
                ),

            "attempts":
                attempts,

            "factory":
                final_inspection,
        }


    # ========================================================
    # GAME
    # ========================================================

    def _run_create_game(
        self,
        request: Dict[str, Any],
        state: MastermindState,
    ) -> Dict[str, Any]:
        inspection = (
            self.inspect_factory()
        )

        self._event(
            state,
            "GAME_PRE_INSPECTION",
            inspection,
        )

        if inspection.get(
            "success"
        ) is not True:
            repair = (
                self.repair_factory(
                    state
                )
            )

            if repair.get(
                "success"
            ) is not True:
                return {
                    "success":
                        False,

                    "status":
                        "FACTORY_NOT_READY",

                    "inspection":
                        inspection,

                    "repair":
                        repair,
                }

        executor_result = (
            self.game_executor
            .execute(
                request,
                self.operation_id,
            )
        )

        self._event(
            state,
            "GAME_EXECUTOR_RESULT",
            executor_result,
        )

        if executor_result.get(
            "success"
        ) is not True:
            return {
                "success":
                    False,

                "status":
                    "REAL_GAME_EXECUTION_FAILED",

                "executor":
                    executor_result,
            }

        artifact_result = (
            self.artifact_verifier
            .verify(
                executor_result
            )
        )

        self._event(
            state,
            "ARTIFACT_VERIFICATION",
            artifact_result,
        )

        if artifact_result.get(
            "success"
        ) is not True:
            return {
                "success":
                    False,

                "status":
                    "ARTIFACT_VERIFICATION_FAILED",

                "executor":
                    executor_result,

                "artifact_verification":
                    artifact_result,
            }

        artifact = str(
            artifact_result[
                "artifact"
            ]
        )

        platform_result = (
            self.platform
            .publish(
                artifact,
                request,
                self.operation_id,
            )
        )

        self._event(
            state,
            "PLATFORM_PUBLISH_RESULT",
            platform_result,
        )

        if platform_result.get(
            "success"
        ) is not True:
            return {
                "success":
                    False,

                "status":
                    "PLATFORM_PUBLISH_FAILED",

                "artifact":
                    artifact,

                "platform":
                    platform_result,
            }

        publication = (
            self.publication_verifier
            .verify(
                platform_result
            )
        )

        self._event(
            state,
            "PUBLICATION_VERIFICATION",
            publication,
        )

        if publication.get(
            "success"
        ) is not True:
            return {
                "success":
                    False,

                "status":
                    "FINAL_PUBLICATION_VALIDATION_FAILED",

                "artifact":
                    artifact,

                "platform":
                    platform_result,

                "publication":
                    publication,
            }

        return {
            "success":
                True,

            "status":
                "GAME_BUILT_AND_PUBLISHED",

            "operation_id":
                self.operation_id,

            "artifact":
                artifact,

            "executor":
                executor_result,

            "artifact_verification":
                artifact_result,

            "platform":
                platform_result,

            "publication":
                publication,

            "public_url":
                publication.get(
                    "public_url"
                ),

            "game_path":
                publication.get(
                    "game_path"
                ),
        }


    # ========================================================
    # CONTENT / MEDIA / SOCIAL
    # ========================================================

    def _run_content(
        self,
        command: str,
        request: Dict[str, Any],
        state: MastermindState,
    ) -> Dict[str, Any]:
        values = {
            "command":
                command,

            "request":
                request,

            "payload":
                request,

            "job_id":
                self.operation_id,

            "operation_id":
                self.operation_id,

            "owner":
                self.owner,

            "output_root":
                str(
                    OUTPUT_DIR
                ),
        }

        result = (
            self.content_factory
            .execute(
                values
            )
        )

        self._event(
            state,
            "CONTENT_MEDIA_RESULT",
            result,
        )

        if result.get(
            "success"
        ) is not True:
            return {
                "success":
                    False,

                "status":
                    "CONTENT_MEDIA_EXECUTION_FAILED",

                "component":
                    result,
            }

        return {
            "success":
                True,

            "status":
                "CONTENT_MEDIA_COMPLETED",

            "operation_id":
                self.operation_id,

            "result":
                result,
        }


    # ========================================================
    # RUNTIME
    # ========================================================

    def _run_runtime(
        self,
        command: str,
        request: Dict[str, Any],
        state: MastermindState,
    ) -> Dict[str, Any]:
        values = {
            "command":
                command,

            "request":
                request,

            "payload":
                request,

            "job_id":
                self.operation_id,

            "operation_id":
                self.operation_id,

            "owner":
                self.owner,
        }

        result = (
            self.runtime
            .execute(
                values
            )
        )

        self._event(
            state,
            "FULL_RUNTIME_RESULT",
            result,
        )

        if result.get(
            "success"
        ) is not True:
            return {
                "success":
                    False,

                "status":
                    "FULL_RUNTIME_EXECUTION_FAILED",

                "runtime":
                    result,
            }

        return {
            "success":
                True,

            "status":
                "FULL_RUNTIME_COMPLETED",

            "operation_id":
                self.operation_id,

            "runtime":
                result,
        }


    # ========================================================
    # OWNER COMMAND
    # ========================================================

    def _run_owner_command(
        self,
        command: str,
        request: Dict[str, Any],
        state: MastermindState,
    ) -> Dict[str, Any]:
        values = {
            "command":
                command,

            "request":
                request,

            "payload":
                request,

            "job_id":
                self.operation_id,

            "operation_id":
                self.operation_id,

            "owner":
                self.owner,
        }

        owner_result = (
            self.owner_center
            .execute(
                values
            )
        )

        self._event(
            state,
            "OWNER_COMMAND_CENTER_RESULT",
            owner_result,
        )

        if owner_result.get(
            "success"
        ) is True:
            return {
                "success":
                    True,

                "status":
                    "OWNER_COMMAND_COMPLETED",

                "operation_id":
                    self.operation_id,

                "owner_center":
                    owner_result,
            }

        orchestrator_result = (
            self.orchestrator
            .execute(
                values
            )
        )

        self._event(
            state,
            "ORCHESTRATOR_RESULT",
            orchestrator_result,
        )

        if orchestrator_result.get(
            "success"
        ) is True:
            return {
                "success":
                    True,

                "status":
                    "OWNER_COMMAND_ORCHESTRATED",

                "operation_id":
                    self.operation_id,

                "owner_center":
                    owner_result,

                "orchestrator":
                    orchestrator_result,
            }

        return {
            "success":
                False,

            "status":
                "OWNER_COMMAND_NOT_EXECUTED",

            "operation_id":
                self.operation_id,

            "owner_center":
                owner_result,

            "orchestrator":
                orchestrator_result,
        }


    # ========================================================
    # MAIN RUN
    # ========================================================

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
            self.owner = str(
                owner
            )

        if job_id:
            self.operation_id = str(
                job_id
            )

            self.logger = (
                AuditLogger(
                    self.operation_id
                )
            )

            self.repair_engine = (
                AutonomousRepairEngine(
                    self.operation_id,
                    self.logger,
                )
            )

        supplied_request = (
            request
            or
            payload
            or
            {}
        )

        if not command:
            command = str(
                supplied_request.get(
                    "command"
                )
                or
                supplied_request.get(
                    "request"
                )
                or
                supplied_request.get(
                    "description"
                )
                or
                ""
            ).strip()

        if not command:
            return {
                "success":
                    False,

                "status":
                    "EMPTY_OWNER_COMMAND",

                "system":
                    SYSTEM_NAME,

                "mastermind":
                    MASTERMIND_NAME,

                "version":
                    VERSION,
            }

        normalized = (
            self.normalize_request(
                command,
                supplied_request,
            )
        )

        route = (
            self.classifier
            .classify(
                command,
                normalized,
            )
        )

        normalized[
            "type"
        ] = route

        state = MastermindState(
            operation_id=
                self.operation_id,

            owner=
                self.owner,

            command=
                command,

            started_at=
                utc_now(),

            updated_at=
                utc_now(),

            status=
                "RECEIVED",

            route=
                route,
        )

        state.plan = (
            self.planner
            .plan(
                route
            )
        )

        self._save_state(
            state
        )

        self.logger.log(
            "OWNER_OBJECTIVE_RECEIVED",
            {
                "command":
                    command,

                "route":
                    route,

                "request":
                    normalized,
            },
        )

        try:
            state.status = (
                "EXECUTING"
            )

            self._save_state(
                state
            )

            if route == "CREATE_GAME":
                result = (
                    self._run_create_game(
                        normalized,
                        state,
                    )
                )

            elif route == "CONTENT":
                result = (
                    self._run_content(
                        command,
                        normalized,
                        state,
                    )
                )

            elif route == "STATUS":
                inspection = (
                    self.inspect_factory()
                )

                result = {
                    "success":
                        inspection.get(
                            "success"
                        ) is True,

                    "status":
                        (
                            "FACTORY_HEALTHY"
                            if inspection.get(
                                "success"
                            ) is True
                            else
                            "FACTORY_UNHEALTHY"
                        ),

                    "operation_id":
                        self.operation_id,

                    "factory":
                        inspection,
                }

            elif route == "DIAGNOSE":
                inspection = (
                    self.inspect_factory()
                )

                diagnosis = (
                    self.diagnose_inspection(
                        inspection
                    )
                )

                result = {
                    "success":
                        inspection.get(
                            "success"
                        ) is True,

                    "status":
                        (
                            "DIAGNOSIS_CLEAN"
                            if inspection.get(
                                "success"
                            ) is True
                            else
                            "DIAGNOSIS_FOUND_FAILURES"
                        ),

                    "operation_id":
                        self.operation_id,

                    "factory":
                        inspection,

                    "diagnosis":
                        diagnosis,
                }

            elif route == "REPAIR":
                result = (
                    self.repair_factory(
                        state
                    )
                )

                result.setdefault(
                    "operation_id",
                    self.operation_id,
                )

            elif route == "RUNTIME":
                result = (
                    self._run_runtime(
                        command,
                        normalized,
                        state,
                    )
                )

            else:
                result = (
                    self._run_owner_command(
                        command,
                        normalized,
                        state,
                    )
                )

            state.result = result

            state.success = (
                result.get(
                    "success"
                )
                is True
            )

            state.status = str(
                result.get(
                    "status"
                )
                or
                (
                    "COMPLETED"
                    if state.success
                    else
                    "FAILED"
                )
            )

            if not state.success:
                state.error = str(
                    result.get(
                        "error"
                    )
                    or
                    result.get(
                        "status"
                    )
                    or
                    "UNKNOWN_FAILURE"
                )

            self._save_state(
                state
            )

            self.logger.log(
                "MASTERMIND_FINAL_RESULT",
                result,
            )

            return result

        except Exception as error:
            result = {
                "success":
                    False,

                "status":
                    "MASTERMIND_EXCEPTION",

                "system":
                    SYSTEM_NAME,

                "mastermind":
                    MASTERMIND_NAME,

                "version":
                    VERSION,

                "operation_id":
                    self.operation_id,

                "route":
                    route,

                "error":
                    (
                        f"{type(error).__name__}: "
                        f"{error}"
                    ),

                "traceback":
                    traceback.format_exc(),
            }

            state.success = False
            state.status = "FAILED"
            state.error = result[
                "error"
            ]
            state.result = result

            self._save_state(
                state
            )

            self.logger.log(
                "MASTERMIND_EXCEPTION",
                result,
            )

            return result


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
    mastermind = (
        Mastermind(
            owner=owner
        )
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


# ============================================================
# COMPATIBILITY API
# ============================================================

def process_game_request(
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Compatibility with majd_ai_agent.py.

    Important:
    This function does NOT force CREATE_GAME unless
    the supplied request is actually a game request.
    """

    return execute_request(
        **kwargs
    )


def process_request(
    **kwargs: Any,
) -> Dict[str, Any]:
    return execute_request(
        **kwargs
    )


def execute_game_request(
    request: Dict[str, Any],
    job_id: Optional[str] = None,
    owner: str = DEFAULT_OWNER,
    **kwargs: Any,
) -> Dict[str, Any]:
    data = dict(
        request
    )

    data[
        "type"
    ] = "CREATE_GAME"

    command = str(
        data.get(
            "command"
        )
        or
        data.get(
            "request"
        )
        or
        data.get(
            "description"
        )
        or
        "CREATE GAME"
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


def execute(
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
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "MAJD SOVEREIGN "
            "AUTONOMOUS MASTERMIND"
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

    args = parser.parse_args()

    if args.status:
        result = {
            "success":
                True,

            "system":
                SYSTEM_NAME,

            "mastermind":
                MASTERMIND_NAME,

            "version":
                VERSION,

            "root":
                str(
                    ROOT_DIR
                ),

            "local_ai":
                bool(
                    LOCAL_AI_URL
                ),

            "core":
                ProjectInspector()
                .core_status(),
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

    if args.inspect:
        mastermind = (
            Mastermind(
                owner=args.owner
            )
        )

        try:
            result = (
                mastermind
                .inspect_factory()
            )
        except Exception as error:
            result = {
                "success":
                    False,

                "status":
                    "INSPECTION_EXCEPTION",

                "error":
                    (
                        f"{type(error).__name__}: "
                        f"{error}"
                    ),

                "traceback":
                    traceback.format_exc(),
            }

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
            if result.get(
                "success"
            ) is True
            else
            1
        )

    command = " ".join(
        args.command
    ).strip()

    if not command:
        command = input(
            "👑 OWNER > "
        ).strip()

    mastermind = (
        Mastermind(
            owner=args.owner
        )
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
        if result.get(
            "success"
        ) is True
        else
        1
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    raise SystemExit(
        main()
    )

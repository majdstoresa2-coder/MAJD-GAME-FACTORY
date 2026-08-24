#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-AI-MASTERMIND-01.py
============================================================

SOVEREIGN AUTONOMOUS MASTERMIND

العقل المدبر السيادي الشامل لمنصة ومصنع مجد.

المسؤوليات:
- استقبال أهداف وأوامر المالك.
- فهم الأوامر العربية والإنجليزية.
- التخطيط الذاتي.
- قراءة المشروع وفهم بنيته.
- اكتشاف الأخطاء البرمجية والتشغيلية.
- إصلاح الملفات تلقائياً.
- إنشاء ملفات وأكواد جديدة عند الحاجة.
- استبدال الأجزاء التالفة.
- إنشاء نسخ احتياطية قبل التعديل.
- إدارة متطلبات Python و Node.
- تشغيل الفحوصات.
- تشغيل الاختبارات.
- تشغيل البناء.
- إعادة المحاولة والإصلاح تلقائياً.
- تشغيل منفذ الألعاب الحقيقي 03.
- التحقق من Artifact حقيقي.
- تشغيل جسر المنصة الرسمي 04.
- حفظ سجل كامل لكل عملية.
- عدم إعلان نجاح وهمي.
- عدم طلب تدخل المالك في الأخطاء التقنية العادية.

السلسلة:

OWNER
  ↓
02 OWNER COMMAND CENTER
  ↓
06 FULL EXECUTION RUNTIME
  ↓
01 SOVEREIGN MASTERMIND
  ↓
DISCOVER
  ↓
PLAN
  ↓
DIAGNOSE
  ↓
CODE / REPAIR / DEPENDENCIES
  ↓
TEST
  ↓
RETRY
  ↓
03 REAL GAME EXECUTOR
  ↓
VERIFY ARTIFACT
  ↓
04 OFFICIAL PLATFORM BRIDGE
  ↓
VERIFY
  ↓
FINAL RESULT

قاعدة السيادة:
- العمل محصور داخل مجلد MAJD-GAME-FACTORY.
- لا تعديل خارج المشروع.
- لا نجاح بدون دليل فعلي.
- أي تعديل يحفظ نسخة احتياطية.
- أي فشل تقني يدخل حلقة إصلاح تلقائي.
"""

from __future__ import annotations

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
import time
import traceback
import urllib.error
import urllib.request
import uuid

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


# ============================================================
# IDENTITY
# ============================================================

SYSTEM_NAME = "MAJD-GAME-FACTORY"

MASTERMIND_NAME = "MAJD-SOVEREIGN-MASTERMIND"

VERSION = "2.0.0"

DEFAULT_OWNER = "MAJD"

MAX_REPAIR_ATTEMPTS = 5

COMMAND_TIMEOUT = 900

AI_TIMEOUT = 180


# ============================================================
# ROOT
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent

STATE_DIR = ROOT_DIR / "majd_factory_state"

MASTERMIND_STATE_DIR = (
    STATE_DIR / "mastermind"
)

LOG_DIR = (
    STATE_DIR / "logs"
)

BACKUP_DIR = (
    STATE_DIR / "backups"
)

WORK_DIR = (
    STATE_DIR / "work"
)

OUTPUT_DIR = (
    ROOT_DIR / "majd_game_output"
)


for directory in (
    STATE_DIR,
    MASTERMIND_STATE_DIR,
    LOG_DIR,
    BACKUP_DIR,
    WORK_DIR,
    OUTPUT_DIR,
):

    directory.mkdir(
        parents=True,
        exist_ok=True
    )


# ============================================================
# CORE FILES
# ============================================================

OWNER_COMMAND_CENTER_FILE = (
    ROOT_DIR
    /
    "MAJD-OWNER-COMMAND-CENTER-02.py"
)

REAL_GAME_EXECUTOR_FILE = (
    ROOT_DIR
    /
    "MAJD-REAL-GAME-EXECUTOR-03.py"
)

OFFICIAL_PLATFORM_BRIDGE_FILE = (
    ROOT_DIR
    /
    "MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py"
)

FULL_RUNTIME_FILE = (
    ROOT_DIR
    /
    "MAJD-FULL-EXECUTION-RUNTIME-06.py"
)


# ============================================================
# LOCAL AI
# ============================================================

LOCAL_AI_URL = (
    os.getenv(
        "MAJD_LOCAL_AI_URL",
        ""
    ).strip()
)

LOCAL_AI_MODEL = (
    os.getenv(
        "MAJD_LOCAL_AI_MODEL",
        "majd-sovereign"
    ).strip()
)


# ============================================================
# TIME
# ============================================================

def utc_now() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat()


# ============================================================
# JSON
# ============================================================

def write_json(
    path: Path,
    value: Any
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    temporary = path.with_suffix(
        path.suffix + ".tmp"
    )

    with temporary.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            value,
            file,
            ensure_ascii=False,
            indent=2,
            default=str
        )

    temporary.replace(
        path
    )


def read_json(
    path: Path,
    default: Optional[Any] = None
) -> Any:

    if not path.exists():

        return (
            default
            if default is not None
            else {}
        )

    try:

        with path.open(
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(
                file
            )

    except Exception:

        return (
            default
            if default is not None
            else {}
        )


# ============================================================
# FILE HELPERS
# ============================================================

def sha256_file(
    path: Path
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


def is_inside_root(
    path: Path
) -> bool:

    try:

        path.resolve().relative_to(
            ROOT_DIR.resolve()
        )

        return True

    except Exception:

        return False


def safe_project_path(
    value: str | Path
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
            "Mastermind refuses to modify paths outside MAJD-GAME-FACTORY."
        )

    return candidate


def read_text(
    path: Path
) -> str:

    return path.read_text(
        encoding="utf-8",
        errors="replace"
    )


def write_text(
    path: Path,
    content: str
) -> None:

    safe_path = safe_project_path(
        path
    )

    safe_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    safe_path.write_text(
        content,
        encoding="utf-8"
    )


# ============================================================
# COMMAND RESULT
# ============================================================

@dataclass
class CommandResult:

    command: List[str]

    returncode: int

    stdout: str

    stderr: str

    success: bool

    duration_seconds: float


# ============================================================
# EXECUTION STATE
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

    plan: List[Dict[str, Any]] = field(
        default_factory=list
    )

    events: List[Dict[str, Any]] = field(
        default_factory=list
    )

    result: Optional[
        Dict[str, Any]
    ] = None

    error: Optional[str] = None


# ============================================================
# LOGGER
# ============================================================

class AuditLogger:

    def __init__(
        self,
        operation_id: str
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
        ] = None
    ) -> None:

        record = {

            "time":
                utc_now(),

            "operation_id":
                self.operation_id,

            "event":
                event,

            "data":
                data or {}
        }

        with self.path.open(
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                    default=str
                )
            )

            file.write(
                "\n"
            )


# ============================================================
# BACKUP MANAGER
# ============================================================

class BackupManager:

    def __init__(
        self,
        operation_id: str
    ):

        self.root = (
            BACKUP_DIR
            /
            operation_id
        )

        self.root.mkdir(
            parents=True,
            exist_ok=True
        )


    def backup(
        self,
        path: Path
    ) -> Optional[str]:

        path = safe_project_path(
            path
        )

        if not path.exists():

            return None

        relative = path.relative_to(
            ROOT_DIR
        )

        target = (
            self.root
            /
            relative
        )

        target.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if path.is_dir():

            if target.exists():

                shutil.rmtree(
                    target
                )

            shutil.copytree(
                path,
                target
            )

        else:

            shutil.copy2(
                path,
                target
            )

        return str(
            target
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
    }


    def run(
        self,
        command: List[str],
        cwd: Optional[Path] = None,
        timeout: int = COMMAND_TIMEOUT
    ) -> CommandResult:

        if not command:

            return CommandResult(
                command=[],
                returncode=1,
                stdout="",
                stderr="Empty command",
                success=False,
                duration_seconds=0.0
            )

        executable = (
            Path(
                str(
                    command[0]
                )
            ).name
        )

        if executable in self.BLOCKED_COMMANDS:

            return CommandResult(
                command=command,
                returncode=126,
                stdout="",
                stderr=(
                    f"Blocked destructive command: "
                    f"{executable}"
                ),
                success=False,
                duration_seconds=0.0
            )

        working_directory = (
            safe_project_path(
                cwd or ROOT_DIR
            )
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
                env=os.environ.copy()
            )

            duration = (
                time.time()
                -
                started
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
                duration_seconds=duration
            )

        except subprocess.TimeoutExpired as error:

            return CommandResult(
                command=command,
                returncode=124,
                stdout=(
                    error.stdout
                    if isinstance(
                        error.stdout,
                        str
                    )
                    else ""
                ),
                stderr=(
                    "Command timed out."
                ),
                success=False,
                duration_seconds=(
                    time.time()
                    -
                    started
                )
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
                )
            )


# ============================================================
# PROJECT DISCOVERY
# ============================================================

class ProjectInspector:

    IGNORE = {

        ".git",
        "__pycache__",
        "node_modules",
        ".venv",
        "venv",
        "majd_factory_state",
        "majd_game_output"
    }


    def list_files(
        self,
        limit: int = 5000
    ) -> List[str]:

        files: List[str] = []

        for path in ROOT_DIR.rglob(
            "*"
        ):

            if len(
                files
            ) >= limit:

                break

            if any(
                part in self.IGNORE
                for part
                in path.parts
            ):

                continue

            if path.is_file():

                try:

                    files.append(
                        str(
                            path.relative_to(
                                ROOT_DIR
                            )
                        )
                    )

                except Exception:

                    pass

        return sorted(
            files
        )


    def detect_stack(
        self
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
                (
                    ROOT_DIR
                    /
                    "docker-compose.yml"
                ).exists()
                or
                (
                    ROOT_DIR
                    /
                    "compose.yml"
                ).exists(),
        }


    def core_status(
        self
    ) -> Dict[str, Any]:

        files = {

            "01":
                ROOT_DIR
                /
                "MAJD-AI-MASTERMIND-01.py",

            "02":
                OWNER_COMMAND_CENTER_FILE,

            "03":
                REAL_GAME_EXECUTOR_FILE,

            "04":
                OFFICIAL_PLATFORM_BRIDGE_FILE,

            "06":
                FULL_RUNTIME_FILE
        }

        result: Dict[str, Any] = {}

        for number, path in files.items():

            result[number] = {

                "file":
                    path.name,

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
                    )
            }

        return result


# ============================================================
# PYTHON CHECKER
# ============================================================

class PythonChecker:

    def __init__(
        self,
        executor: ProcessExecutor
    ):

        self.executor = executor


    def compile_file(
        self,
        path: Path
    ) -> CommandResult:

        return self.executor.run(
            [
                sys.executable,
                "-m",
                "py_compile",
                str(path)
            ],
            cwd=ROOT_DIR
        )


    def compile_project(
        self
    ) -> Dict[str, Any]:

        checked = []

        failed = []

        for path in ROOT_DIR.glob(
            "*.py"
        ):

            result = self.compile_file(
                path
            )

            item = {

                "file":
                    path.name,

                "success":
                    result.success,

                "stderr":
                    result.stderr[-4000:]
            }

            checked.append(
                item
            )

            if not result.success:

                failed.append(
                    item
                )

        return {

            "success":
                not failed,

            "checked":
                checked,

            "failed":
                failed
        }


# ============================================================
# DEPENDENCY MANAGER
# ============================================================

class DependencyManager:

    PYTHON_IMPORT_MAP = {

        "PIL":
            "pillow",

        "yaml":
            "pyyaml",

        "cv2":
            "opencv-python",

        "sklearn":
            "scikit-learn"
    }


    def __init__(
        self,
        executor: ProcessExecutor,
        logger: AuditLogger
    ):

        self.executor = executor

        self.logger = logger


    def module_installed(
        self,
        module_name: str
    ) -> bool:

        return (
            importlib.util.find_spec(
                module_name
            )
            is not None
        )


    def install_python_package(
        self,
        package_name: str
    ) -> Dict[str, Any]:

        self.logger.log(
            "PYTHON_DEPENDENCY_INSTALL",
            {
                "package":
                    package_name
            }
        )

        command = [
            sys.executable,
            "-m",
            "pip",
            "install",
            package_name
        ]

        result = self.executor.run(
            command,
            cwd=ROOT_DIR,
            timeout=600
        )

        if (
            not result.success
            and
            "externally-managed-environment"
            in (
                result.stderr
                +
                result.stdout
            ).lower()
        ):

            command.append(
                "--break-system-packages"
            )

            result = self.executor.run(
                command,
                cwd=ROOT_DIR,
                timeout=600
            )

        return asdict(
            result
        )


    def repair_missing_python_module(
        self,
        error_text: str
    ) -> Optional[
        Dict[str, Any]
    ]:

        match = re.search(
            r"No module named ['\"]([^'\"]+)['\"]",
            error_text
        )

        if not match:

            return None

        module_name = (
            match.group(1)
            .split(".")[0]
        )

        package_name = (
            self.PYTHON_IMPORT_MAP.get(
                module_name,
                module_name
            )
        )

        return self.install_python_package(
            package_name
        )


    def install_node_dependencies(
        self,
        project_dir: Path
    ) -> Dict[str, Any]:

        project_dir = safe_project_path(
            project_dir
        )

        package_json = (
            project_dir
            /
            "package.json"
        )

        if not package_json.exists():

            return {
                "success": False,
                "status": "PACKAGE_JSON_NOT_FOUND"
            }

        npm = shutil.which(
            "npm"
        )

        if not npm:

            return {
                "success": False,
                "status": "NPM_NOT_FOUND"
            }

        result = self.executor.run(
            [
                npm,
                "install",
                "--no-audit",
                "--no-fund"
            ],
            cwd=project_dir,
            timeout=900
        )

        return asdict(
            result
        )


# ============================================================
# LOCAL AI ADAPTER
# ============================================================

class LocalAIAdapter:

    """
    اختياري.

    إذا كان MAJD_LOCAL_AI_URL موجوداً، يمكن للعقل المدبر
    إرسال مهام إصلاح/كتابة كود إلى نموذج سيادي محلي.

    المتوقع endpoint متوافق تقريباً مع:
    POST /v1/chat/completions
    """


    def __init__(
        self,
        logger: AuditLogger
    ):

        self.logger = logger


    @property
    def available(
        self
    ) -> bool:

        return bool(
            LOCAL_AI_URL
        )


    def ask(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> Optional[str]:

        if not self.available:

            return None

        endpoint = (
            LOCAL_AI_URL.rstrip("/")
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
                        system_prompt
                },
                {
                    "role":
                        "user",

                    "content":
                        user_prompt
                }
            ]
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
                    "application/json"
            },
            method="POST"
        )

        try:

            with urllib.request.urlopen(
                request,
                timeout=AI_TIMEOUT
            ) as response:

                body = json.loads(
                    response.read().decode(
                        "utf-8"
                    )
                )

            choices = body.get(
                "choices"
            ) or []

            if not choices:

                return None

            content = (
                choices[0]
                .get(
                    "message",
                    {}
                )
                .get(
                    "content"
                )
            )

            if content:

                self.logger.log(
                    "LOCAL_AI_RESPONSE_RECEIVED",
                    {
                        "length":
                            len(
                                content
                            )
                    }
                )

            return content

        except Exception as error:

            self.logger.log(
                "LOCAL_AI_ERROR",
                {
                    "error":
                        str(
                            error
                        )
                }
            )

            return None


# ============================================================
# CODE MANAGER
# ============================================================

class CodeManager:

    def __init__(
        self,
        backup: BackupManager,
        logger: AuditLogger
    ):

        self.backup = backup

        self.logger = logger


    def replace_file(
        self,
        path: Path,
        content: str
    ) -> Dict[str, Any]:

        path = safe_project_path(
            path
        )

        backup_path = self.backup.backup(
            path
        )

        write_text(
            path,
            content
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
                    backup_path
            }
        )

        return {
            "success": True,
            "path": str(path),
            "backup": backup_path
        }


    def delete_broken_file(
        self,
        path: Path
    ) -> Dict[str, Any]:

        path = safe_project_path(
            path
        )

        if not path.exists():

            return {
                "success": True,
                "status": "ALREADY_ABSENT"
            }

        backup_path = self.backup.backup(
            path
        )

        if path.is_dir():

            shutil.rmtree(
                path
            )

        else:

            path.unlink()

        self.logger.log(
            "FILE_REMOVED",
            {
                "path":
                    str(
                        path.relative_to(
                            ROOT_DIR
                        )
                    ),

                "backup":
                    backup_path
            }
        )

        return {
            "success": True,
            "backup": backup_path
        }


# ============================================================
# MODULE LOADER
# ============================================================

def load_module(
    path: Path,
    name: str
) -> Any:

    path = safe_project_path(
        path
    )

    if not path.exists():

        raise FileNotFoundError(
            path.name
        )

    spec = importlib.util.spec_from_file_location(
        name,
        str(path)
    )

    if (
        spec is None
        or
        spec.loader is None
    ):

        raise ImportError(
            f"Unable to load {path.name}"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    sys.modules[name] = module

    spec.loader.exec_module(
        module
    )

    return module


# ============================================================
# SAFE CALL
# ============================================================

def call_supported(
    function: Callable[..., Any],
    values: Dict[str, Any]
) -> Any:

    signature = inspect.signature(
        function
    )

    parameters = (
        signature.parameters
    )

    accepts_kwargs = any(
        parameter.kind
        ==
        inspect.Parameter.VAR_KEYWORD
        for parameter
        in parameters.values()
    )

    kwargs: Dict[str, Any] = {}

    for key, value in values.items():

        if (
            accepts_kwargs
            or
            key in parameters
        ):

            kwargs[key] = value

    return function(
        **kwargs
    )


# ============================================================
# GAME EXECUTOR BRIDGE
# ============================================================

class GameExecutorBridge:

    def execute(
        self,
        request: Dict[str, Any],
        job_id: str
    ) -> Dict[str, Any]:

        module = load_module(
            REAL_GAME_EXECUTOR_FILE,
            "majd_real_game_executor_03"
        )

        function = getattr(
            module,
            "execute_game_request",
            None
        )

        if not callable(
            function
        ):

            return {
                "success": False,
                "status":
                    "REAL_EXECUTOR_INTERFACE_MISSING"
            }

        result = call_supported(
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
                    )
            }
        )

        if not isinstance(
            result,
            dict
        ):

            return {
                "success": False,
                "status":
                    "INVALID_REAL_EXECUTOR_RESULT"
            }

        return result


# ============================================================
# ARTIFACT VERIFIER
# ============================================================

class ArtifactVerifier:

    def verify(
        self,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:

        artifact = (
            result.get(
                "artifact"
            )
            or
            result.get(
                "build_path"
            )
            or
            result.get(
                "output_path"
            )
        )

        if not artifact:

            return {
                "success": False,
                "status":
                    "ARTIFACT_MISSING"
            }

        path = Path(
            str(
                artifact
            )
        )

        if not path.is_absolute():

            path = (
                ROOT_DIR
                /
                path
            ).resolve()

        if not path.exists():

            return {
                "success": False,
                "status":
                    "ARTIFACT_NOT_FOUND",
                "artifact":
                    str(path)
            }

        if path.is_dir():

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
                    "success": False,
                    "status":
                        "ARTIFACT_EMPTY"
                }

            index_files = [
                file
                for file
                in files
                if file.name.lower()
                ==
                "index.html"
            ]

            if not index_files:

                return {
                    "success": False,
                    "status":
                        "PLAYABLE_INDEX_NOT_FOUND",
                    "artifact":
                        str(path)
                }

        elif (
            path.is_file()
            and
            path.stat().st_size <= 0
        ):

            return {
                "success": False,
                "status":
                    "ARTIFACT_EMPTY"
            }

        return {
            "success": True,
            "status":
                "ARTIFACT_VERIFIED",
            "artifact":
                str(path)
        }


# ============================================================
# PLATFORM BRIDGE
# ============================================================

class PlatformBridge:

    def publish(
        self,
        artifact: str,
        request: Dict[str, Any],
        job_id: str
    ) -> Dict[str, Any]:

        module = load_module(
            OFFICIAL_PLATFORM_BRIDGE_FILE,
            "majd_official_platform_bridge_04"
        )

        functions = (
            "publish_game",
            "publish",
            "send_game",
            "send_to_majd",
            "execute"
        )

        function = None

        for name in functions:

            candidate = getattr(
                module,
                name,
                None
            )

            if callable(
                candidate
            ):

                function = candidate
                break

        if function is None:

            return {
                "success": False,
                "status":
                    "PLATFORM_INTERFACE_MISSING"
            }

        game_name = str(
            request.get(
                "name"
            )
            or
            "MAJD-GAME"
        )

        result = call_supported(
            function,
            {
                "game_dir":
                    Path(
                        artifact
                    ),

                "artifact":
                    artifact,

                "artifact_path":
                    artifact,

                "build_path":
                    artifact,

                "game_name":
                    game_name,

                "job_id":
                    job_id,

                "request":
                    request,

                "payload":
                    request
            }
        )

        if result is None:

            return {
                "success": True,
                "status":
                    "PLATFORM_EXECUTED"
            }

        if not isinstance(
            result,
            dict
        ):

            return {
                "success": True,
                "status":
                    "PLATFORM_EXECUTED",
                "result":
                    result
            }

        return result


# ============================================================
# AUTOMATIC DIAGNOSIS
# ============================================================

class DiagnosticEngine:

    def diagnose(
        self,
        failure: Dict[str, Any]
    ) -> Dict[str, Any]:

        text = json.dumps(
            failure,
            ensure_ascii=False,
            default=str
        )

        lowered = text.lower()

        diagnosis = {

            "type":
                "UNKNOWN",

            "repairable":
                False,

            "details":
                text[-8000:]
        }


        if (
            "no module named"
            in lowered
        ):

            diagnosis[
                "type"
            ] = (
                "MISSING_PYTHON_MODULE"
            )

            diagnosis[
                "repairable"
            ] = True


        elif (
            "modulenotfounderror"
            in lowered
        ):

            diagnosis[
                "type"
            ] = (
                "MISSING_PYTHON_MODULE"
            )

            diagnosis[
                "repairable"
            ] = True


        elif (
            "syntaxerror"
            in lowered
        ):

            diagnosis[
                "type"
            ] = (
                "PYTHON_SYNTAX_ERROR"
            )

            diagnosis[
                "repairable"
            ] = True


        elif (
            "interface"
            in lowered
            and
            "missing"
            in lowered
        ):

            diagnosis[
                "type"
            ] = (
                "INTERFACE_MISMATCH"
            )

            diagnosis[
                "repairable"
            ] = True


        elif (
            "interface_not_found"
            in lowered
        ):

            diagnosis[
                "type"
            ] = (
                "INTERFACE_MISMATCH"
            )

            diagnosis[
                "repairable"
            ] = True


        elif (
            "artifact"
            in lowered
        ):

            diagnosis[
                "type"
            ] = (
                "ARTIFACT_FAILURE"
            )

            diagnosis[
                "repairable"
            ] = True


        elif (
            "npm"
            in lowered
            or
            "vite"
            in lowered
            or
            "node_modules"
            in lowered
        ):

            diagnosis[
                "type"
            ] = (
                "NODE_BUILD_FAILURE"
            )

            diagnosis[
                "repairable"
            ] = True


        return diagnosis


# ============================================================
# AUTONOMOUS REPAIR ENGINE
# ============================================================

class AutonomousRepairEngine:

    def __init__(
        self,
        operation_id: str,
        logger: AuditLogger
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
                logger
            )
        )

        self.code = (
            CodeManager(
                self.backup,
                logger
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
        failure: Dict[str, Any]
    ) -> Dict[str, Any]:

        repair_type = diagnosis.get(
            "type"
        )


        # ----------------------------------------------------
        # MISSING PYTHON DEPENDENCY
        # ----------------------------------------------------

        if (
            repair_type
            ==
            "MISSING_PYTHON_MODULE"
        ):

            text = json.dumps(
                failure,
                ensure_ascii=False,
                default=str
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
                    "success": False,
                    "status":
                        "DEPENDENCY_NAME_NOT_DETECTED"
                }
            )


        # ----------------------------------------------------
        # SYNTAX CHECK
        # ----------------------------------------------------

        if (
            repair_type
            ==
            "PYTHON_SYNTAX_ERROR"
        ):

            checker = PythonChecker(
                self.executor
            )

            report = (
                checker
                .compile_project()
            )

            return {
                "success":
                    report.get(
                        "success",
                        False
                    ),

                "status":
                    (
                        "SYNTAX_VALID"
                        if report.get(
                            "success"
                        )
                        else
                        "SYNTAX_ERRORS_FOUND"
                    ),

                "report":
                    report
            }


        # ----------------------------------------------------
        # NODE DEPENDENCIES
        # ----------------------------------------------------

        if (
            repair_type
            ==
            "NODE_BUILD_FAILURE"
        ):

            candidates = []

            for package_json in ROOT_DIR.rglob(
                "package.json"
            ):

                if (
                    "node_modules"
                    in package_json.parts
                ):

                    continue

                candidates.append(
                    package_json.parent
                )

            reports = []

            for directory in candidates:

                report = (
                    self.dependencies
                    .install_node_dependencies(
                        directory
                    )
                )

                reports.append(
                    {
                        "directory":
                            str(
                                directory
                            ),
                        "result":
                            report
                    }
                )

            return {
                "success":
                    any(
                        report[
                            "result"
                        ].get(
                            "success",
                            False
                        )
                        for report
                        in reports
                    ),

                "status":
                    "NODE_DEPENDENCY_REPAIR",

                "reports":
                    reports
            }


        # ----------------------------------------------------
        # AI CODE REPAIR
        # ----------------------------------------------------

        if self.ai.available:

            project_files = (
                ProjectInspector()
                .list_files(
                    limit=300
                )
            )

            prompt = (
                "You are the sovereign software repair engine "
                "for MAJD-GAME-FACTORY.\n\n"
                "Failure:\n"
                f"{json.dumps(failure, ensure_ascii=False, default=str)}\n\n"
                "Diagnosis:\n"
                f"{json.dumps(diagnosis, ensure_ascii=False, default=str)}\n\n"
                "Project files:\n"
                f"{json.dumps(project_files, ensure_ascii=False)}\n\n"
                "Return JSON only with this structure:\n"
                "{"
                "\"success\": true,"
                "\"changes\": ["
                "{"
                "\"path\":\"relative/file.py\","
                "\"content\":\"complete replacement file content\""
                "}"
                "]"
                "}\n"
                "Only modify files inside MAJD-GAME-FACTORY. "
                "Return complete file contents for every changed file."
            )

            answer = self.ai.ask(
                (
                    "You are MAJD Sovereign Mastermind. "
                    "Repair software autonomously and conservatively. "
                    "Never modify outside the project."
                ),
                prompt
            )

            if answer:

                try:

                    cleaned = (
                        answer.strip()
                    )

                    if cleaned.startswith(
                        "```"
                    ):

                        cleaned = re.sub(
                            r"^```(?:json)?",
                            "",
                            cleaned
                        )

                        cleaned = re.sub(
                            r"```$",
                            "",
                            cleaned
                        )

                        cleaned = cleaned.strip()

                    data = json.loads(
                        cleaned
                    )

                    changes = data.get(
                        "changes"
                    ) or []

                    applied = []

                    for change in changes:

                        path = (
                            ROOT_DIR
                            /
                            str(
                                change.get(
                                    "path",
                                    ""
                                )
                            )
                        )

                        content = (
                            change.get(
                                "content"
                            )
                        )

                        if not content:

                            continue

                        applied.append(
                            self.code.replace_file(
                                path,
                                content
                            )
                        )

                    return {
                        "success":
                            bool(applied),

                        "status":
                            "AI_CODE_REPAIR_APPLIED",

                        "changes":
                            applied
                    }

                except Exception as error:

                    return {
                        "success": False,
                        "status":
                            "AI_REPAIR_RESPONSE_INVALID",
                        "error":
                            str(error)
                    }


        return {
            "success": False,

            "status":
                "AUTOMATIC_REPAIR_NOT_AVAILABLE",

            "diagnosis":
                diagnosis
        }


# ============================================================
# AUTONOMOUS PLANNER
# ============================================================

class AutonomousPlanner:

    def plan(
        self,
        command: str,
        request: Dict[str, Any]
    ) -> List[
        Dict[str, Any]
    ]:

        request_type = str(
            request.get(
                "type",
                ""
            )
        ).upper()

        if (
            request_type
            ==
            "CREATE_GAME"
        ):

            return [

                {
                    "stage":
                        "INSPECT",
                    "description":
                        "Inspect factory and core files."
                },

                {
                    "stage":
                        "VALIDATE",
                    "description":
                        "Validate Python and required interfaces."
                },

                {
                    "stage":
                        "BUILD",
                    "description":
                        "Execute real game executor."
                },

                {
                    "stage":
                        "VERIFY",
                    "description":
                        "Verify playable artifact."
                },

                {
                    "stage":
                        "PUBLISH",
                    "description":
                        "Publish to official MAJD platform."
                },

                {
                    "stage":
                        "FINAL_VERIFY",
                    "description":
                        "Verify final production result."
                }
            ]

        return [

            {
                "stage":
                    "INSPECT",
                "description":
                    "Inspect requested system area."
            },

            {
                "stage":
                    "EXECUTE",
                "description":
                    "Execute requested owner objective."
            },

            {
                "stage":
                    "VERIFY",
                "description":
                    "Verify the real result."
            }
        ]


# ============================================================
# SOVEREIGN MASTERMIND
# ============================================================

class Mastermind:

    def __init__(
        self,
        owner: str = DEFAULT_OWNER,
        max_repair_attempts: int = MAX_REPAIR_ATTEMPTS
    ):

        self.owner = (
            owner
        )

        self.max_repair_attempts = (
            max(
                1,
                int(
                    max_repair_attempts
                )
            )
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

        self.planner = (
            AutonomousPlanner()
        )

        self.diagnostics = (
            DiagnosticEngine()
        )

        self.repair_engine = (
            AutonomousRepairEngine(
                self.operation_id,
                self.logger
            )
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


    # ========================================================
    # STATE
    # ========================================================

    def _state_path(
        self
    ) -> Path:

        return (
            MASTERMIND_STATE_DIR
            /
            f"{self.operation_id}.json"
        )


    def _save_state(
        self,
        state: MastermindState
    ) -> None:

        state.updated_at = (
            utc_now()
        )

        write_json(
            self._state_path(),
            asdict(
                state
            )
        )


    # ========================================================
    # REQUEST NORMALIZATION
    # ========================================================

    def normalize_request(
        self,
        command: str,
        request: Optional[
            Dict[str, Any]
        ] = None
    ) -> Dict[str, Any]:

        data = dict(
            request or {}
        )

        if not data.get(
            "request"
        ):

            data[
                "request"
            ] = command

        if not data.get(
            "description"
        ):

            data[
                "description"
            ] = command

        if not data.get(
            "type"
        ):

            lowered = (
                command.lower()
            )

            if any(
                phrase in lowered
                for phrase
                in (
                    "أنشئ لعبة",
                    "انشئ لعبة",
                    "اصنع لعبة",
                    "ابني لعبة",
                    "create game",
                    "build game",
                    "make game"
                )
            ):

                data[
                    "type"
                ] = (
                    "CREATE_GAME"
                )

            else:

                data[
                    "type"
                ] = (
                    "GENERAL_OWNER_COMMAND"
                )

        data.setdefault(
            "owner",
            self.owner
        )

        data.setdefault(
            "autonomous",
            True
        )

        data.setdefault(
            "auto_repair",
            True
        )

        data.setdefault(
            "auto_test",
            True
        )

        data.setdefault(
            "auto_retry",
            True
        )

        return data


    # ========================================================
    # FACTORY INSPECTION
    # ========================================================

    def inspect_factory(
        self
    ) -> Dict[str, Any]:

        result = {

            "core_files":
                self.inspector.core_status(),

            "stack":
                self.inspector.detect_stack(),

            "file_count":
                len(
                    self.inspector.list_files()
                ),

            "python_compile":
                self.python_checker.compile_project()
        }

        result[
            "success"
        ] = all(

            item.get(
                "exists",
                False
            )

            for number, item
            in result[
                "core_files"
            ].items()

            if number
            in (
                "01",
                "02",
                "03",
                "04",
                "06"
            )
        )

        return result


    # ========================================================
    # FAILURE PROCESSING
    # ========================================================

    def _repair_failure(
        self,
        failure: Dict[str, Any],
        state: MastermindState
    ) -> Dict[str, Any]:

        diagnosis = (
            self.diagnostics
            .diagnose(
                failure
            )
        )

        self.logger.log(
            "FAILURE_DIAGNOSED",
            diagnosis
        )

        state.events.append(
            {
                "time":
                    utc_now(),

                "type":
                    "DIAGNOSIS",

                "data":
                    diagnosis
            }
        )

        self._save_state(
            state
        )

        if not diagnosis.get(
            "repairable"
        ):

            return {
                "success": False,
                "status":
                    "FAILURE_NOT_AUTOMATICALLY_REPAIRABLE",
                "diagnosis":
                    diagnosis
            }

        repair = (
            self.repair_engine
            .repair(
                diagnosis,
                failure
            )
        )

        self.logger.log(
            "REPAIR_RESULT",
            repair
        )

        state.events.append(
            {
                "time":
                    utc_now(),

                "type":
                    "REPAIR",

                "data":
                    repair
            }
        )

        self._save_state(
            state
        )

        return repair


    # ========================================================
    # CREATE GAME PIPELINE
    # ========================================================

    def _run_create_game(
        self,
        command: str,
        request: Dict[str, Any],
        state: MastermindState
    ) -> Dict[str, Any]:

        last_failure: Dict[
            str,
            Any
        ] = {}

        for attempt in range(
            1,
            self.max_repair_attempts + 1
        ):

            state.attempts = (
                attempt
            )

            state.status = (
                "EXECUTING"
            )

            self._save_state(
                state
            )

            self.logger.log(
                "EXECUTION_ATTEMPT",
                {
                    "attempt":
                        attempt
                }
            )


            # ------------------------------------------------
            # INSPECT
            # ------------------------------------------------

            inspection = (
                self.inspect_factory()
            )

            state.events.append(
                {
                    "time":
                        utc_now(),

                    "type":
                        "INSPECTION",

                    "data":
                        inspection
                }
            )

            self._save_state(
                state
            )


            if not inspection.get(
                "success"
            ):

                last_failure = {

                    "stage":
                        "INSPECTION",

                    "result":
                        inspection
                }

                repair = (
                    self._repair_failure(
                        last_failure,
                        state
                    )
                )

                if repair.get(
                    "success"
                ):

                    continue

                return {
                    "success": False,

                    "status":
                        "FACTORY_INSPECTION_FAILED",

                    "failure":
                        last_failure,

                    "repair":
                        repair
                }


            # ------------------------------------------------
            # EXECUTE 03
            # ------------------------------------------------

            executor_result = (
                self.game_executor
                .execute(
                    request,
                    self.operation_id
                )
            )

            state.events.append(
                {
                    "time":
                        utc_now(),

                    "type":
                        "GAME_EXECUTOR",

                    "data":
                        executor_result
                }
            )

            self._save_state(
                state
            )


            if not executor_result.get(
                "success"
            ):

                last_failure = {

                    "stage":
                        "REAL_GAME_EXECUTOR",

                    "result":
                        executor_result
                }

                repair = (
                    self._repair_failure(
                        last_failure,
                        state
                    )
                )

                if repair.get(
                    "success"
                ):

                    continue

                return {
                    "success": False,
                    "status":
                        "REAL_GAME_EXECUTION_FAILED",
                    "failure":
                        last_failure,
                    "repair":
                        repair
                }


            # ------------------------------------------------
            # VERIFY ARTIFACT
            # ------------------------------------------------

            artifact_result = (
                self.artifact_verifier
                .verify(
                    executor_result
                )
            )

            state.events.append(
                {
                    "time":
                        utc_now(),

                    "type":
                        "ARTIFACT_VERIFY",

                    "data":
                        artifact_result
                }
            )

            self._save_state(
                state
            )


            if not artifact_result.get(
                "success"
            ):

                last_failure = {

                    "stage":
                        "ARTIFACT",

                    "result":
                        artifact_result,

                    "executor":
                        executor_result
                }

                repair = (
                    self._repair_failure(
                        last_failure,
                        state
                    )
                )

                if repair.get(
                    "success"
                ):

                    continue

                return {
                    "success": False,
                    "status":
                        "ARTIFACT_VERIFICATION_FAILED",
                    "failure":
                        last_failure,
                    "repair":
                        repair
                }


            artifact = (
                artifact_result[
                    "artifact"
                ]
            )


            # ------------------------------------------------
            # PLATFORM 04
            # ------------------------------------------------

            platform_result = (
                self.platform
                .publish(
                    artifact=artifact,
                    request=request,
                    job_id=self.operation_id
                )
            )

            state.events.append(
                {
                    "time":
                        utc_now(),

                    "type":
                        "PLATFORM_PUBLISH",

                    "data":
                        platform_result
                }
            )

            self._save_state(
                state
            )


            if not platform_result.get(
                "success"
            ):

                last_failure = {

                    "stage":
                        "PLATFORM_BRIDGE",

                    "result":
                        platform_result
                }

                repair = (
                    self._repair_failure(
                        last_failure,
                        state
                    )
                )

                if repair.get(
                    "success"
                ):

                    continue

                return {
                    "success": False,
                    "status":
                        "PLATFORM_PUBLISH_FAILED",
                    "artifact":
                        artifact,
                    "failure":
                        last_failure,
                    "repair":
                        repair
                }


            # ------------------------------------------------
            # SUCCESS
            # ------------------------------------------------

            return {

                "success": True,

                "status":
                    "COMPLETED",

                "operation_id":
                    self.operation_id,

                "request":
                    request,

                "artifact":
                    artifact,

                "executor":
                    executor_result,

                "artifact_verification":
                    artifact_result,

                "platform":
                    platform_result,

                "attempt":
                    attempt
            }


        return {

            "success": False,

            "status":
                "MAX_AUTONOMOUS_REPAIR_ATTEMPTS_REACHED",

            "operation_id":
                self.operation_id,

            "failure":
                last_failure,

            "attempts":
                self.max_repair_attempts
        }


    # ========================================================
    # GENERAL OWNER COMMAND
    # ========================================================

    def _run_general_command(
        self,
        command: str,
        request: Dict[str, Any],
        state: MastermindState
    ) -> Dict[str, Any]:

        inspection = (
            self.inspect_factory()
        )

        return {

            "success": True,

            "status":
                "GENERAL_COMMAND_RECEIVED",

            "operation_id":
                self.operation_id,

            "command":
                command,

            "request":
                request,

            "factory":
                inspection,

            "message":
                (
                    "The sovereign mastermind received the owner "
                    "objective and is operational."
                )
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
        **kwargs: Any
    ) -> Dict[str, Any]:

        if owner:

            self.owner = (
                owner
            )

        if job_id:

            self.operation_id = (
                str(
                    job_id
                )
            )

            self.logger = (
                AuditLogger(
                    self.operation_id
                )
            )

            self.repair_engine = (
                AutonomousRepairEngine(
                    self.operation_id,
                    self.logger
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
                    "request"
                )
                or
                supplied_request.get(
                    "description"
                )
                or
                ""
            )

        normalized = (
            self.normalize_request(
                command,
                supplied_request
            )
        )

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
                "RECEIVED"
        )

        state.plan = (
            self.planner.plan(
                command,
                normalized
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

                "request":
                    normalized
            }
        )

        try:

            request_type = str(
                normalized.get(
                    "type",
                    ""
                )
            ).upper()

            if (
                request_type
                ==
                "CREATE_GAME"
            ):

                result = (
                    self._run_create_game(
                        command,
                        normalized,
                        state
                    )
                )

            else:

                result = (
                    self._run_general_command(
                        command,
                        normalized,
                        state
                    )
                )

            state.result = (
                result
            )

            state.success = bool(
                result.get(
                    "success"
                )
            )

            state.status = str(
                result.get(
                    "status",
                    (
                        "COMPLETED"
                        if state.success
                        else
                        "FAILED"
                    )
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
                result
            )

            return result

        except Exception as error:

            result = {

                "success": False,

                "status":
                    "MASTERMIND_EXCEPTION",

                "operation_id":
                    self.operation_id,

                "error":
                    (
                        f"{type(error).__name__}: "
                        f"{error}"
                    ),

                "traceback":
                    traceback.format_exc()
            }

            state.success = False

            state.status = (
                "FAILED"
            )

            state.error = (
                result[
                    "error"
                ]
            )

            state.result = (
                result
            )

            self._save_state(
                state
            )

            self.logger.log(
                "MASTERMIND_EXCEPTION",
                result
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
    **kwargs: Any
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

        **kwargs
    )


def process_request(
    **kwargs: Any
) -> Dict[str, Any]:

    return execute_request(
        **kwargs
    )


def execute_game_request(
    request: Dict[str, Any],
    job_id: Optional[str] = None,
    owner: str = DEFAULT_OWNER,
    **kwargs: Any
) -> Dict[str, Any]:

    command = str(
        request.get(
            "request"
        )
        or
        request.get(
            "description"
        )
        or
        ""
    )

    request = dict(
        request
    )

    request[
        "type"
    ] = (
        "CREATE_GAME"
    )

    return execute_request(

        command=command,

        request=request,

        job_id=job_id,

        owner=owner,

        **kwargs
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
    **kwargs: Any
) -> Dict[str, Any]:

    return execute_request(

        command=command,

        request=request,

        payload=payload,

        job_id=job_id,

        owner=owner,

        **kwargs
    )


# ============================================================
# CLI
# ============================================================

def main() -> int:

    import argparse

    parser = argparse.ArgumentParser(

        description=(
            "MAJD SOVEREIGN AUTONOMOUS MASTERMIND"
        )
    )

    parser.add_argument(

        "command",

        nargs="*",

        help="Owner objective"
    )

    parser.add_argument(

        "--owner",

        default=DEFAULT_OWNER
    )

    parser.add_argument(

        "--status",

        action="store_true"
    )

    args = parser.parse_args()

    if args.status:

        result = {

            "success": True,

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
                .core_status()
        }

        print(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=2
            )
        )

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
        owner=args.owner
    )

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
            default=str
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

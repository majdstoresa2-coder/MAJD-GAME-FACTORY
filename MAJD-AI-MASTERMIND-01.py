#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-AI-MASTERMIND-01.py
============================================================
SOVEREIGN AUTONOMOUS MASTERMIND

العقل المدبر السيادي لمنصة ومصنع مجد.

المسؤوليات:
- استقبال أوامر المالك.
- فهم أوامر إنشاء الألعاب والفحص والإصلاح.
- فحص ملفات المصنع الأساسية.
- فحص Python فعلياً.
- فحص الاستيراد والواجهات.
- اكتشاف الأخطاء.
- إصلاح الاعتماديات المفقودة.
- استخدام محرك AI محلي للإصلاح البرمجي إذا كان مفعلاً.
- حفظ نسخة احتياطية قبل أي تعديل.
- تشغيل منفذ الألعاب الحقيقي 03.
- التحقق من Artifact حقيقي قابل للتشغيل.
- تشغيل جسر المنصة الرسمي 04.
- تسجيل جميع العمليات.
- عدم إعلان نجاح وهمي.
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
from typing import Any, Callable, Dict, List, Optional


# ============================================================
# IDENTITY
# ============================================================

SYSTEM_NAME = "MAJD-GAME-FACTORY"
MASTERMIND_NAME = "MAJD-SOVEREIGN-MASTERMIND"
VERSION = "3.0.0"

DEFAULT_OWNER = "MAJD"

MAX_REPAIR_ATTEMPTS = 5
COMMAND_TIMEOUT = 900
AI_TIMEOUT = 180


# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent

STATE_DIR = ROOT_DIR / "majd_factory_state"
MASTERMIND_STATE_DIR = STATE_DIR / "mastermind"
LOG_DIR = STATE_DIR / "logs"
BACKUP_DIR = STATE_DIR / "backups"
OUTPUT_DIR = ROOT_DIR / "majd_game_output"

for directory in (
    STATE_DIR,
    MASTERMIND_STATE_DIR,
    LOG_DIR,
    BACKUP_DIR,
    OUTPUT_DIR,
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

FULL_RUNTIME_FILE = (
    ROOT_DIR / "MAJD-FULL-EXECUTION-RUNTIME-06.py"
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
# HELPERS
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

    temporary.replace(path)


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

            digest.update(chunk)

    return digest.hexdigest()


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

    candidate = Path(value)

    if not candidate.is_absolute():

        candidate = (
            ROOT_DIR / candidate
        )

    candidate = candidate.resolve()

    if not is_inside_root(
        candidate
    ):

        raise PermissionError(
            "Refusing path outside MAJD-GAME-FACTORY"
        )

    return candidate


def load_module(
    path: Path,
    name: str,
) -> Any:

    path = safe_project_path(
        path
    )

    if not path.exists():

        raise FileNotFoundError(
            path.name
        )

    spec = (
        importlib.util
        .spec_from_file_location(
            name,
            str(path),
        )
    )

    if (
        spec is None
        or spec.loader is None
    ):

        raise ImportError(
            f"Unable to load {path.name}"
        )

    module = (
        importlib.util
        .module_from_spec(spec)
    )

    sys.modules[name] = module

    spec.loader.exec_module(
        module
    )

    return module


def call_supported(
    function: Callable[..., Any],
    values: Dict[str, Any],
) -> Any:

    signature = inspect.signature(
        function
    )

    accepts_kwargs = any(
        parameter.kind
        ==
        inspect.Parameter.VAR_KEYWORD
        for parameter
        in signature.parameters.values()
    )

    kwargs: Dict[str, Any] = {}

    for key, value in values.items():

        if (
            accepts_kwargs
            or key in signature.parameters
        ):

            kwargs[key] = value

    return function(
        **kwargs
    )


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

            "time":
                utc_now(),

            "operation_id":
                self.operation_id,

            "event":
                event,

            "data":
                data or {},
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
            str(command[0])
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
                    if isinstance(
                        error.stdout,
                        str,
                    )
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

        "agent":
            "majd_ai_agent.py",
    }


    def list_files(
        self,
        limit: int = 5000,
    ) -> List[str]:

        result: List[str] = []

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
                for part
                in relative.parts
            ):

                continue

            if path.is_file():

                result.append(
                    str(relative)
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
                (
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
                    ).exists()
                    or
                    (
                        ROOT_DIR
                        /
                        "docker-compose.yaml"
                    ).exists()
                    or
                    (
                        ROOT_DIR
                        /
                        "compose.yaml"
                    ).exists()
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
            ROOT_DIR.glob(
                "*.py"
            )
        ):

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
                    result.stderr[-6000:],
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

        "PIL":
            "pillow",

        "yaml":
            "pyyaml",

        "cv2":
            "opencv-python",

        "sklearn":
            "scikit-learn",

        "fastapi":
            "fastapi",

        "uvicorn":
            "uvicorn",
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

        self.logger.log(
            "PYTHON_DEPENDENCY_INSTALL",
            {
                "module":
                    module,
                "package":
                    package,
            },
        )

        command = [

            sys.executable,
            "-m",
            "pip",
            "install",
            package,
        ]

        result = self.executor.run(
            command,
            cwd=ROOT_DIR,
            timeout=600,
        )

        if (
            not result.success
            and
            "externally-managed-environment"
            in (
                result.stdout
                +
                result.stderr
            ).lower()
        ):

            result = self.executor.run(
                command
                +
                [
                    "--break-system-packages"
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
                    response.read().decode(
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
                        str(error),
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

        backup = (
            self.backup
            .backup(
                path
            )
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            content,
            encoding="utf-8",
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
            },
        )

        return {

            "success":
                True,

            "path":
                str(path),

            "backup":
                backup,
        }


# ============================================================
# INTERFACE CHECKER
# ============================================================

class InterfaceChecker:

    def check(
        self,
    ) -> Dict[str, Any]:

        results = []
        failed = []

        checks = [

            (
                REAL_GAME_EXECUTOR_FILE,
                "03",
                (
                    "execute_game_request",
                ),
            ),

            (
                OFFICIAL_PLATFORM_BRIDGE_FILE,
                "04",
                (
                    "publish_game",
                    "publish",
                    "send_game",
                    "send_to_majd",
                    "execute",
                    "MajdPlatformClient",
                ),
            ),
        ]

        for (
            path,
            number,
            names,
        ) in checks:

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
                    for name
                    in names
                    if hasattr(
                        module,
                        name,
                    )
                ]

                item = {

                    "file":
                        path.name,

                    "number":
                        number,

                    "success":
                        bool(found),

                    "found":
                        found,

                    "expected_any":
                        list(names),
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
                    text[-8000:],
            }

        if (
            "syntaxerror"
            in lowered
            or
            "indentationerror"
            in lowered
            or
            "taberror"
            in lowered
        ):

            return {

                "type":
                    "PYTHON_SYNTAX_ERROR",

                "repairable":
                    True,

                "details":
                    text[-8000:],
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
                    text[-8000:],
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
                    text[-8000:],
            }

        return {

            "type":
                "UNKNOWN",

            "repairable":
                False,

            "details":
                text[-8000:],
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

        repair_type = (
            diagnosis.get(
                "type"
            )
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
                    limit=400
                )
            )

            prompt = (

                "Repair MAJD-GAME-FACTORY from the "
                "failure below.\n"

                "Return JSON only using this format:\n"

                "{"
                "\"success\":true,"
                "\"changes\":["
                "{"
                "\"path\":\"relative/path.py\","
                "\"content\":\"COMPLETE FILE\""
                "}"
                "]"
                "}\n"

                "Every changed file must contain its "
                "complete replacement contents.\n"

                "Never modify outside MAJD-GAME-FACTORY.\n\n"

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
                "\n\nFILES:\n"
                +
                json.dumps(
                    files,
                    ensure_ascii=False,
                )
            )

            answer = self.ai.ask(

                (
                    "You are MAJD Sovereign "
                    "code repair engine. "
                    "Never report success without "
                    "a real applied change."
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

                cleaned = (
                    answer.strip()
                )

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

                    content = (
                        change.get(
                            "content"
                        )
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

                    applied.append(
                        self.code.replace_file(
                            ROOT_DIR
                            /
                            relative,
                            content,
                        )
                    )

                return {

                    "success":
                        bool(applied),

                    "status":
                        (
                            "AI_CODE_REPAIR_APPLIED"
                            if applied
                            else
                            "AI_NO_CHANGES"
                        ),

                    "changes":
                        applied,
                }

            except Exception as error:

                return {

                    "success":
                        False,

                    "status":
                        "AI_REPAIR_RESPONSE_INVALID",

                    "error":
                        str(error),
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
# GAME EXECUTOR BRIDGE
# ============================================================

class GameExecutorBridge:

    def execute(
        self,
        request: Dict[str, Any],
        job_id: str,
    ) -> Dict[str, Any]:

        module = load_module(
            REAL_GAME_EXECUTOR_FILE,
            "majd_real_game_executor_03",
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
                    ),
            },
        )

        if not isinstance(
            result,
            dict,
        ):

            return {

                "success":
                    False,

                "status":
                    "INVALID_REAL_EXECUTOR_RESULT",
            }

        return result


# ============================================================
# ARTIFACT VERIFIER
# ============================================================

class ArtifactVerifier:

    def verify(
        self,
        result: Dict[str, Any],
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

                "success":
                    False,

                "status":
                    "ARTIFACT_MISSING",
            }

        path = Path(
            str(artifact)
        )

        if not path.is_absolute():

            path = (
                ROOT_DIR
                /
                path
            ).resolve()

        if not is_inside_root(
            path
        ):

            return {

                "success":
                    False,

                "status":
                    "ARTIFACT_OUTSIDE_PROJECT",

                "artifact":
                    str(path),
            }

        if not path.exists():

            return {

                "success":
                    False,

                "status":
                    "ARTIFACT_NOT_FOUND",

                "artifact":
                    str(path),
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

                    "success":
                        False,

                    "status":
                        "ARTIFACT_EMPTY",

                    "artifact":
                        str(path),
                }

            playable = any(

                item.name.lower()
                ==
                "index.html"

                for item
                in files
            )

            if not playable:

                return {

                    "success":
                        False,

                    "status":
                        "PLAYABLE_INDEX_NOT_FOUND",

                    "artifact":
                        str(path),
                }

        elif (
            path.stat().st_size
            <=
            0
        ):

            return {

                "success":
                    False,

                "status":
                    "ARTIFACT_EMPTY",

                "artifact":
                    str(path),
            }

        return {

            "success":
                True,

            "status":
                "ARTIFACT_VERIFIED",

            "artifact":
                str(path),
        }


# ============================================================
# PLATFORM BRIDGE
# ============================================================

class PlatformBridge:

    def publish(
        self,
        artifact: str,
        request: Dict[str, Any],
        job_id: str,
    ) -> Dict[str, Any]:

        module = load_module(
            OFFICIAL_PLATFORM_BRIDGE_FILE,
            "majd_official_platform_bridge_04",
        )

        for name in (

            "publish_game",
            "publish",
            "send_game",
            "send_to_majd",
            "execute",
        ):

            function = getattr(
                module,
                name,
                None,
            )

            if callable(
                function
            ):

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

                if result is None:

                    return {

                        "success":
                            True,

                        "status":
                            "PLATFORM_EXECUTED",
                    }

                if isinstance(
                    result,
                    dict,
                ):

                    return result

                return {

                    "success":
                        True,

                    "status":
                        "PLATFORM_EXECUTED",

                    "result":
                        str(result),
                }

        Client = getattr(
            module,
            "MajdPlatformClient",
            None,
        )

        ManifestBuilder = getattr(
            module,
            "ManifestBuilder",
            None,
        )

        PackageBuilder = getattr(
            module,
            "PackageBuilder",
            None,
        )

        if all(
            callable(item)
            for item
            in (
                Client,
                ManifestBuilder,
                PackageBuilder,
            )
        ):

            manifest = (
                ManifestBuilder()
                .build(
                    game_dir=Path(
                        artifact
                    ),
                    game_name=str(
                        request.get(
                            "name"
                        )
                        or
                        "MAJD-GAME"
                    ),
                    game_version="1.0.0",
                    metadata={
                        "job_id":
                            job_id,
                    },
                )
            )

            package = (
                PackageBuilder()
                .build(
                    game_dir=Path(
                        artifact
                    ),
                    manifest=manifest,
                )
            )

            receipt = (
                Client()
                .publish(
                    package_path=package,
                    manifest=manifest,
                )
            )

            return {

                "success":
                    True,

                "status":
                    "PLATFORM_EXECUTED",

                "package":
                    str(package),

                "receipt":
                    getattr(
                        receipt,
                        "__dict__",
                        str(receipt),
                    ),
            }

        return {

            "success":
                False,

            "status":
                "PLATFORM_INTERFACE_MISSING",
        }


# ============================================================
# PLANNER
# ============================================================

class AutonomousPlanner:

    def plan(
        self,
        command: str,
        request: Dict[str, Any],
    ) -> List[
        Dict[str, Any]
    ]:

        if (
            str(
                request.get(
                    "type",
                    "",
                )
            ).upper()
            ==
            "CREATE_GAME"
        ):

            stages = [

                "INSPECT",
                "VALIDATE",
                "BUILD",
                "VERIFY",
                "PUBLISH",
                "FINAL_VERIFY",
            ]

        else:

            stages = [

                "INSPECT",
                "DIAGNOSE",
                "REPAIR",
                "RECHECK",
                "VERIFY",
            ]

        return [

            {
                "stage":
                    stage,
            }

            for stage
            in stages
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


    # ========================================================
    # NORMALIZE REQUEST
    # ========================================================

    def normalize_request(
        self,
        command: str,
        request: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Dict[str, Any]:

        data = dict(
            request or {}
        )

        data.setdefault(
            "request",
            command,
        )

        data.setdefault(
            "description",
            command,
        )

        if not data.get(
            "type"
        ):

            lowered = (
                command.lower()
            )

            game_words = (

                "أنشئ لعبة",
                "انشئ لعبة",
                "اصنع لعبة",
                "ابني لعبة",
                "create game",
                "build game",
                "make game",
            )

            if any(
                phrase in lowered
                for phrase
                in game_words
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
            "06",
            "agent",
        )

        missing = [

            core[number][
                "file"
            ]

            for number
            in required

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
            )

            and

            import_report.get(
                "success"
            )

            and

            interface_report.get(
                "success"
            )
        )

        return result


    # ========================================================
    # FAILURE REPAIR
    # ========================================================

    def _repair_failure(
        self,
        failure: Dict[str, Any],
        state: MastermindState,
    ) -> Dict[str, Any]:

        diagnosis = (
            self.diagnostics
            .diagnose(
                failure
            )
        )

        self.logger.log(
            "FAILURE_DIAGNOSED",
            diagnosis,
        )

        state.events.append(
            {

                "time":
                    utc_now(),

                "type":
                    "DIAGNOSIS",

                "data":
                    diagnosis,
            }
        )

        self._save_state(
            state
        )

        if not diagnosis.get(
            "repairable"
        ):

            return {

                "success":
                    False,

                "status":
                    "FAILURE_NOT_AUTOMATICALLY_REPAIRABLE",

                "diagnosis":
                    diagnosis,
            }

        repair = (
            self.repair_engine
            .repair(
                diagnosis,
                failure,
            )
        )

        self.logger.log(
            "REPAIR_RESULT",
            repair,
        )

        state.events.append(
            {

                "time":
                    utc_now(),

                "type":
                    "REPAIR",

                "data":
                    repair,
            }
        )

        self._save_state(
            state
        )

        return repair


    # ========================================================
    # CREATE GAME
    # ========================================================

    def _run_create_game(
        self,
        command: str,
        request: Dict[str, Any],
        state: MastermindState,
    ) -> Dict[str, Any]:

        last_failure: Dict[
            str,
            Any
        ] = {}

        for attempt in range(
            1,
            self.max_repair_attempts + 1,
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
                        inspection,
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
                        inspection,
                }

                repair = (
                    self._repair_failure(
                        last_failure,
                        state,
                    )
                )

                if repair.get(
                    "success"
                ):

                    continue

                return {

                    "success":
                        False,

                    "status":
                        "FACTORY_INSPECTION_FAILED",

                    "failure":
                        last_failure,

                    "repair":
                        repair,
                }

            try:

                executor_result = (
                    self.game_executor
                    .execute(
                        request,
                        self.operation_id,
                    )
                )

            except Exception as error:

                executor_result = {

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

            if not executor_result.get(
                "success"
            ):

                last_failure = {

                    "stage":
                        "REAL_GAME_EXECUTOR",

                    "result":
                        executor_result,
                }

                repair = (
                    self._repair_failure(
                        last_failure,
                        state,
                    )
                )

                if repair.get(
                    "success"
                ):

                    continue

                return {

                    "success":
                        False,

                    "status":
                        "REAL_GAME_EXECUTION_FAILED",

                    "failure":
                        last_failure,

                    "repair":
                        repair,
                }

            artifact_result = (
                self.artifact_verifier
                .verify(
                    executor_result
                )
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
                        executor_result,
                }

                repair = (
                    self._repair_failure(
                        last_failure,
                        state,
                    )
                )

                if repair.get(
                    "success"
                ):

                    continue

                return {

                    "success":
                        False,

                    "status":
                        "ARTIFACT_VERIFICATION_FAILED",

                    "failure":
                        last_failure,

                    "repair":
                        repair,
                }

            artifact = (
                artifact_result[
                    "artifact"
                ]
            )

            try:

                platform_result = (
                    self.platform
                    .publish(
                        artifact,
                        request,
                        self.operation_id,
                    )
                )

            except Exception as error:

                platform_result = {

                    "success":
                        False,

                    "status":
                        "PLATFORM_EXCEPTION",

                    "error":
                        (
                            f"{type(error).__name__}: "
                            f"{error}"
                        ),

                    "traceback":
                        traceback.format_exc(),
                }

            if not platform_result.get(
                "success"
            ):

                last_failure = {

                    "stage":
                        "PLATFORM_BRIDGE",

                    "result":
                        platform_result,
                }

                repair = (
                    self._repair_failure(
                        last_failure,
                        state,
                    )
                )

                if repair.get(
                    "success"
                ):

                    continue

                return {

                    "success":
                        False,

                    "status":
                        "PLATFORM_PUBLISH_FAILED",

                    "artifact":
                        artifact,

                    "failure":
                        last_failure,

                    "repair":
                        repair,
                }

            return {

                "success":
                    True,

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
                    attempt,
            }

        return {

            "success":
                False,

            "status":
                "MAX_AUTONOMOUS_REPAIR_ATTEMPTS_REACHED",

            "operation_id":
                self.operation_id,

            "failure":
                last_failure,

            "attempts":
                self.max_repair_attempts,
        }


    # ========================================================
    # GENERAL OWNER COMMAND - REAL AUTONOMOUS EXECUTION
    # ========================================================

    def _run_general_command(
        self,
        command: str,
        request: Dict[str, Any],
        state: MastermindState,
    ) -> Dict[str, Any]:

        lowered = str(
            command or ""
        ).lower()

        repair_keywords = (

            "افحص",
            "فحص",
            "اصلح",
            "أصلح",
            "اصلاح",
            "إصلاح",
            "صحح",
            "تصحيح",
            "اختبر",
            "اختبار",
            "راجع",
            "مشاكل",
            "أخطاء",
            "اخطاء",
            "خطأ",
            "diagnose",
            "repair",
            "fix",
            "check",
            "test",
            "validate",
            "debug",
        )

        wants_repair = any(

            keyword in lowered

            for keyword
            in repair_keywords
        )

        inspection = (
            self.inspect_factory()
        )

        state.events.append(
            {

                "time":
                    utc_now(),

                "type":
                    "GENERAL_INSPECTION",

                "data":
                    inspection,
            }
        )

        self._save_state(
            state
        )

        self.logger.log(
            "GENERAL_OWNER_INSPECTION",
            inspection,
        )

        if not wants_repair:

            return {

                "success":
                    True,

                "status":
                    "GENERAL_COMMAND_COMPLETED",

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
                        "Owner command received and "
                        "factory inspection completed."
                    ),
            }

        attempts: List[
            Dict[str, Any]
        ] = []

        last_failure: Optional[
            Dict[str, Any]
        ] = None

        for attempt in range(
            1,
            self.max_repair_attempts + 1,
        ):

            state.attempts = (
                attempt
            )

            state.status = (
                "GENERAL_AUTONOMOUS_REPAIR"
            )

            self._save_state(
                state
            )

            current = (
                self.inspect_factory()
            )

            python_report = (
                current.get(
                    "python_compile",
                    {},
                )
            )

            import_report = (
                current.get(
                    "python_imports",
                    {},
                )
            )

            interface_report = (
                current.get(
                    "interfaces",
                    {},
                )
            )

            missing = (
                current.get(
                    "required_missing",
                    [],
                )
            )

            if current.get(
                "success"
            ):

                return {

                    "success":
                        True,

                    "status":
                        "GENERAL_REPAIR_COMPLETED",

                    "operation_id":
                        self.operation_id,

                    "command":
                        command,

                    "request":
                        request,

                    "attempts":
                        attempts,

                    "factory":
                        current,

                    "message":
                        (
                            "Factory inspection completed "
                            "and all enforced checks passed."
                        ),
                }

            if not python_report.get(
                "success",
                True,
            ):

                last_failure = {

                    "stage":
                        "PYTHON_COMPILE",

                    "status":
                        "PYTHON_SYNTAX_ERROR",

                    "result":
                        python_report,
                }

            elif not import_report.get(
                "success",
                True,
            ):

                import_text = json.dumps(
                    import_report,
                    ensure_ascii=False,
                    default=str,
                ).lower()

                import_status = (

                    "MISSING_PYTHON_MODULE"

                    if (
                        "no module named"
                        in import_text
                    )

                    else

                    "PYTHON_IMPORT_ERROR"
                )

                last_failure = {

                    "stage":
                        "PYTHON_IMPORT",

                    "status":
                        import_status,

                    "result":
                        import_report,
                }

            elif missing:

                last_failure = {

                    "stage":
                        "CORE_FILES",

                    "status":
                        "CORE_FILE_MISSING",

                    "missing":
                        missing,
                }

            elif not interface_report.get(
                "success",
                True,
            ):

                last_failure = {

                    "stage":
                        "INTERFACES",

                    "status":
                        "INTERFACE_MISMATCH",

                    "result":
                        interface_report,
                }

            else:

                last_failure = {

                    "stage":
                        "FACTORY_INSPECTION",

                    "status":
                        "FACTORY_INSPECTION_FAILED",

                    "result":
                        current,
                }

            diagnosis = (
                self.diagnostics
                .diagnose(
                    last_failure
                )
            )

            if (
                last_failure.get(
                    "status"
                )
                ==
                "PYTHON_SYNTAX_ERROR"
            ):

                diagnosis = {

                    "type":
                        "PYTHON_SYNTAX_ERROR",

                    "repairable":
                        True,

                    "details":
                        json.dumps(
                            last_failure,
                            ensure_ascii=False,
                            default=str,
                        )[-8000:],
                }

            elif (
                last_failure.get(
                    "status"
                )
                ==
                "INTERFACE_MISMATCH"
            ):

                diagnosis = {

                    "type":
                        "INTERFACE_MISMATCH",

                    "repairable":
                        True,

                    "details":
                        json.dumps(
                            last_failure,
                            ensure_ascii=False,
                            default=str,
                        )[-8000:],
                }

            elif (
                last_failure.get(
                    "status"
                )
                ==
                "MISSING_PYTHON_MODULE"
            ):

                diagnosis = {

                    "type":
                        "MISSING_PYTHON_MODULE",

                    "repairable":
                        True,

                    "details":
                        json.dumps(
                            last_failure,
                            ensure_ascii=False,
                            default=str,
                        )[-8000:],
                }

            repair = (
                self.repair_engine
                .repair(
                    diagnosis,
                    last_failure,
                )
            )

            attempt_record = {

                "attempt":
                    attempt,

                "failure":
                    last_failure,

                "diagnosis":
                    diagnosis,

                "repair":
                    repair,
            }

            attempts.append(
                attempt_record
            )

            state.events.append(
                {

                    "time":
                        utc_now(),

                    "type":
                        "GENERAL_REPAIR_ATTEMPT",

                    "data":
                        attempt_record,
                }
            )

            self._save_state(
                state
            )

            self.logger.log(
                "GENERAL_REPAIR_ATTEMPT",
                attempt_record,
            )

            recheck = (
                self.inspect_factory()
            )

            state.events.append(
                {

                    "time":
                        utc_now(),

                    "type":
                        "GENERAL_REPAIR_RECHECK",

                    "data":
                        recheck,
                }
            )

            self._save_state(
                state
            )

            if recheck.get(
                "success"
            ):

                return {

                    "success":
                        True,

                    "status":
                        "GENERAL_REPAIR_COMPLETED",

                    "operation_id":
                        self.operation_id,

                    "command":
                        command,

                    "request":
                        request,

                    "attempt":
                        attempt,

                    "attempts":
                        attempts,

                    "factory":
                        recheck,

                    "message":
                        (
                            "Factory repaired and "
                            "verified successfully."
                        ),
                }

            if not repair.get(
                "success"
            ):

                return {

                    "success":
                        False,

                    "status":
                        repair.get(
                            "status",
                            "AUTONOMOUS_REPAIR_FAILED",
                        ),

                    "operation_id":
                        self.operation_id,

                    "command":
                        command,

                    "request":
                        request,

                    "failure":
                        last_failure,

                    "diagnosis":
                        diagnosis,

                    "repair":
                        repair,

                    "attempts":
                        attempts,

                    "factory":
                        recheck,

                    "message":
                        (
                            "A real failure remains. "
                            "No fake success was returned."
                        ),
                }

        final_inspection = (
            self.inspect_factory()
        )

        return {

            "success":
                False,

            "status":
                "MAX_AUTONOMOUS_REPAIR_ATTEMPTS_REACHED",

            "operation_id":
                self.operation_id,

            "command":
                command,

            "request":
                request,

            "attempts":
                attempts,

            "failure":
                last_failure,

            "factory":
                final_inspection,

            "message":
                (
                    "Autonomous repair attempts "
                    "were exhausted. "
                    "No fake success was returned."
                ),
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

            self.owner = (
                owner
            )

        if job_id:

            self.operation_id = (
                str(job_id)
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
                supplied_request,
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
                "RECEIVED",
        )

        state.plan = (
            self.planner
            .plan(
                command,
                normalized,
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
                    normalized,
            },
        )

        try:

            request_type = str(
                normalized.get(
                    "type",
                    "",
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
                        state,
                    )
                )

            else:

                result = (
                    self._run_general_command(
                        command,
                        normalized,
                        state,
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

                "operation_id":
                    self.operation_id,

                "error":
                    (
                        f"{type(error).__name__}: "
                        f"{error}"
                    ),

                "traceback":
                    traceback.format_exc(),
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
# COMPATIBILITY API FOR AGENT
# ============================================================

def process_game_request(
    **kwargs: Any,
) -> Dict[str, Any]:

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
    ] = (
        "CREATE_GAME"
    )

    command = str(

        data.get(
            "request"
        )

        or

        data.get(
            "description"
        )

        or

        ""
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

    args = (
        parser.parse_args()
    )

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
            )
        )

        return 0

    if args.inspect:

        mastermind = (
            Mastermind(
                owner=args.owner
            )
        )

        result = (
            mastermind
            .inspect_factory()
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
            )
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
        )
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

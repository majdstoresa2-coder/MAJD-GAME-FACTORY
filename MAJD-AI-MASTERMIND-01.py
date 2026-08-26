#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-AI-MASTERMIND-01.py
============================================================
MAJD SOVEREIGN AUTONOMOUS MASTERMIND
COMPLETE REPLACEMENT BUILD — VERSION 4.1.0

Central sovereign brain for MAJD-GAME-FACTORY.

Core rules:
- Discover MAJD components 01–10 from the real repository.
- Do not mark a capability operational because a word appears in a file.
- A capability becomes operational only when a real callable contract exists.
- Receive owner objectives in Arabic or English.
- Plan, route, execute, verify, diagnose, repair, retest and monitor.
- Use real 06 runtime repair/verification capabilities when available.
- Auto-discover a local AI engine, discover a real model, run a real prompt test,
  save the verified connection, and reconnect automatically when it fails.
- Never use --break-system-packages.
- Backup before code changes and rollback on syntax regression.
- Never manufacture success.
- Maintain owner dashboard state, security events and continuous monitoring.
- Enforce content-safety policy for explicit sexual content and sensitive /
  prohibited government-site or government-vehicle content.
- Provide an electronic legal-assistance layer without pretending to be a
  licensed human lawyer.

No external capability is reported CONNECTED/OPERATIONAL until a real check
proves it.
"""

from __future__ import annotations

import argparse
import ast
import asyncio
import hashlib
import html
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
import urllib.error
import urllib.parse
import urllib.request
import uuid

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple


# ============================================================
# IDENTITY
# ============================================================

SYSTEM_NAME = "MAJD-GAME-FACTORY"
MASTERMIND_NAME = "MAJD-SOVEREIGN-MASTERMIND"
VERSION = "4.1.0"
DEFAULT_OWNER = "MAJD"

MAX_REPAIR_ATTEMPTS = max(
    1,
    int(
        os.getenv(
            "MAJD_MAX_REPAIR_ATTEMPTS",
            "5",
        )
    ),
)

COMMAND_TIMEOUT = max(
    30,
    int(
        os.getenv(
            "MAJD_COMMAND_TIMEOUT",
            "900",
        )
    ),
)

AI_TIMEOUT = max(
    5,
    int(
        os.getenv(
            "MAJD_AI_TIMEOUT",
            "180",
        )
    ),
)

AI_PROBE_TIMEOUT = max(
    1,
    int(
        os.getenv(
            "MAJD_AI_PROBE_TIMEOUT",
            "3",
        )
    ),
)

MONITOR_INTERVAL = max(
    30,
    int(
        os.getenv(
            "MAJD_MONITOR_INTERVAL",
            "300",
        )
    ),
)

REQUIRE_AI = (
    os.getenv(
        "MAJD_REQUIRE_AI",
        "1",
    )
    .strip()
    .lower()
    not in {
        "0",
        "false",
        "no",
    }
)


# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent
THIS_FILE = Path(__file__).resolve()

STATE_DIR = ROOT_DIR / "majd_factory_state"

MASTERMIND_STATE_DIR = (
    STATE_DIR
    /
    "mastermind"
)

LOG_DIR = (
    STATE_DIR
    /
    "logs"
)

BACKUP_DIR = (
    STATE_DIR
    /
    "backups"
)

DASHBOARD_DIR = (
    STATE_DIR
    /
    "dashboard"
)

SECURITY_DIR = (
    STATE_DIR
    /
    "security"
)

LEGAL_DIR = (
    STATE_DIR
    /
    "legal"
)

MONITOR_DIR = (
    STATE_DIR
    /
    "monitor"
)

REGISTRY_DIR = (
    STATE_DIR
    /
    "registry"
)

AI_STATE_DIR = (
    STATE_DIR
    /
    "ai"
)

OUTPUT_DIR = (
    ROOT_DIR
    /
    "majd_game_output"
)

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
    AI_STATE_DIR,
    OUTPUT_DIR,
):
    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

AI_CONNECTION_FILE = (
    AI_STATE_DIR
    /
    "connection.json"
)

OFFICIAL_NUMBERS = tuple(
    f"{number:02d}"
    for number
    in range(
        1,
        11,
    )
)

KNOWN_CORE_FILES: Dict[
    str,
    str,
] = {
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
}

AGENT_FILE = (
    ROOT_DIR
    /
    "majd_ai_agent.py"
)


# ============================================================
# GENERIC HELPERS
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
        path.suffix
        +
        ".tmp"
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


def read_json(
    path: Path,
    default: Any = None,
) -> Any:

    try:

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(
                file
            )

    except Exception:

        return default


def sha256_file(
    path: Path,
) -> str:

    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as file:

        while True:

            chunk = file.read(
                1024
                *
                1024
            )

            if not chunk:

                break

            digest.update(
                chunk
            )

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

    candidate = Path(
        value
    )

    if not candidate.is_absolute():

        candidate = (
            ROOT_DIR
            /
            candidate
        )

    candidate = (
        candidate.resolve()
    )

    if not is_inside_root(
        candidate
    ):

        raise PermissionError(
            "Refusing path outside MAJD-GAME-FACTORY"
        )

    return candidate


def truncate(
    value: Any,
    limit: int = 6000,
) -> str:

    text = str(
        value
        or
        ""
    )

    if len(
        text
    ) <= limit:

        return text

    return text[
        -limit:
    ]


def load_module(
    path: Path,
    name: Optional[str] = None,
) -> Any:

    path = safe_project_path(
        path
    )

    if not path.exists():

        raise FileNotFoundError(
            path.name
        )

    module_name = (
        name
        or
        (
            "_majd_dynamic_"
            +
            uuid.uuid4().hex
        )
    )

    specification = (
        importlib.util
        .spec_from_file_location(
            module_name,
            str(path),
        )
    )

    if (
        specification is None
        or
        specification.loader is None
    ):

        raise ImportError(
            f"Unable to load {path.name}"
        )

    module = (
        importlib.util
        .module_from_spec(
            specification
        )
    )

    sys.modules[
        module_name
    ] = module

    specification.loader.exec_module(
        module
    )

    return module


def _resolve_awaitable(
    value: Any,
) -> Any:

    if not inspect.isawaitable(
        value
    ):

        return value

    try:

        asyncio.get_running_loop()

    except RuntimeError:

        return asyncio.run(
            value
        )

    result_box: Dict[
        str,
        Any
    ] = {}

    error_box: Dict[
        str,
        BaseException
    ] = {}

    def runner() -> None:

        try:

            result_box[
                "value"
            ] = asyncio.run(
                value
            )

        except BaseException as error:

            error_box[
                "error"
            ] = error

    thread = threading.Thread(
        target=runner,
        daemon=True,
    )

    thread.start()
    thread.join()

    if "error" in error_box:

        raise error_box[
            "error"
        ]

    return result_box.get(
        "value"
    )


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

        return _resolve_awaitable(
            function(
                **values
            )
        )

    accepts_kwargs = any(
        parameter.kind
        ==
        inspect.Parameter.VAR_KEYWORD
        for parameter
        in signature.parameters.values()
    )

    kwargs = {
        key:
            value

        for key, value
        in values.items()

        if (
            accepts_kwargs
            or
            key in signature.parameters
        )
    }

    return _resolve_awaitable(
        function(
            **kwargs
        )
    )


def normalize_result(
    value: Any,
    component: Optional[str] = None,
) -> Dict[str, Any]:

    if value is None:

        result = {
            "success":
                False,

            "status":
                "COMPONENT_RETURNED_NONE",
        }

    elif isinstance(
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

    else:

        result = {
            "success":
                False,

            "status":
                "UNVERIFIED_COMPONENT_RESULT",

            "result_type":
                type(
                    value
                ).__name__,

            "result":
                truncate(
                    value
                ),
        }

    if component:

        result.setdefault(
            "component",
            component,
        )

    return result


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
        "dd",
    }

    def run(
        self,
        command: List[str],
        cwd: Optional[Path] = None,
        timeout: int = COMMAND_TIMEOUT,
        allow_outside_root: bool = False,
    ) -> CommandResult:

        if not command:

            return CommandResult(
                [],
                1,
                "",
                "Empty command",
                False,
                0.0,
            )

        executable = Path(
            str(
                command[0]
            )
        ).name.lower()

        if executable in self.BLOCKED_COMMANDS:

            return CommandResult(
                command,
                126,
                "",
                (
                    "Blocked destructive command: "
                    f"{executable}"
                ),
                False,
                0.0,
            )

        if allow_outside_root:

            working_directory = Path(
                cwd
                or
                ROOT_DIR
            ).resolve()

        else:

            working_directory = (
                safe_project_path(
                    cwd
                    or
                    ROOT_DIR
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
                stdout=completed.stdout
                or
                "",
                stderr=completed.stderr
                or
                "",
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
                    else
                    ""
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
# AUDIT
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
                data
                or
                {},
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
# BACKUP / ROLLBACK
# ============================================================

class BackupManager:

    def __init__(
        self,
        operation_id: str,
    ):

        self.operation_id = (
            operation_id
        )

        self.root = (
            BACKUP_DIR
            /
            operation_id
        )

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.manifest_file = (
            self.root
            /
            "manifest.json"
        )

        self.manifest: Dict[
            str,
            str
        ] = (
            read_json(
                self.manifest_file,
                {},
            )
            or
            {}
        )

    def _save_manifest(
        self,
    ) -> None:

        write_json(
            self.manifest_file,
            self.manifest,
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

        self.manifest[
            str(relative)
        ] = str(
            target
        )

        self._save_manifest()

        return str(
            target
        )

    def restore(
        self,
        path: Path,
    ) -> Dict[str, Any]:

        path = safe_project_path(
            path
        )

        relative = str(
            path.relative_to(
                ROOT_DIR
            )
        )

        backup_value = (
            self.manifest.get(
                relative
            )
        )

        if not backup_value:

            return {
                "success":
                    False,

                "status":
                    "BACKUP_NOT_FOUND",

                "path":
                    relative,
            }

        backup = Path(
            backup_value
        )

        if not backup.exists():

            return {
                "success":
                    False,

                "status":
                    "BACKUP_NOT_FOUND",

                "path":
                    relative,
            }

        if backup.is_dir():

            if path.exists():

                shutil.rmtree(
                    path
                )

            shutil.copytree(
                backup,
                path,
            )

        else:

            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            shutil.copy2(
                backup,
                path,
            )

        return {
            "success":
                True,

            "status":
                "ROLLBACK_COMPLETED",

            "path":
                relative,
        }


# ============================================================
# STATIC DISCOVERY
# ============================================================

class StaticPythonDiscovery:

    @staticmethod
    def discover(
        path: Path,
    ) -> Dict[str, Any]:

        result: Dict[
            str,
            Any
        ] = {
            "functions":
                [],

            "async_functions":
                [],

            "classes":
                [],

            "imports":
                [],

            "constants":
                {},
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

                    result[
                        "functions"
                    ].append(
                        node.name
                    )

                elif isinstance(
                    node,
                    ast.AsyncFunctionDef,
                ):

                    result[
                        "async_functions"
                    ].append(
                        node.name
                    )

                elif isinstance(
                    node,
                    ast.ClassDef,
                ):

                    result[
                        "classes"
                    ].append(
                        node.name
                    )

                elif isinstance(
                    node,
                    ast.Import,
                ):

                    result[
                        "imports"
                    ].extend(
                        item.name
                        for item
                        in node.names
                    )

                elif (
                    isinstance(
                        node,
                        ast.ImportFrom,
                    )
                    and
                    node.module
                ):

                    result[
                        "imports"
                    ].append(
                        node.module
                    )

                elif isinstance(
                    node,
                    ast.Assign,
                ):

                    for target in (
                        node.targets
                    ):

                        if (
                            isinstance(
                                target,
                                ast.Name,
                            )
                            and
                            target.id
                            in {
                                "CAPABILITIES",
                                "MAJD_CAPABILITIES",
                                "COMPONENT_CAPABILITIES",
                            }
                        ):

                            try:

                                result[
                                    "constants"
                                ][
                                    target.id
                                ] = ast.literal_eval(
                                    node.value
                                )

                            except Exception:

                                pass

            result[
                "success"
            ] = True

        except Exception as error:

            result[
                "success"
            ] = False

            result[
                "error"
            ] = (
                f"{type(error).__name__}: "
                f"{error}"
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

    sha256: Optional[
        str
    ] = None

    importable: bool = False

    static_functions: List[
        str
    ] = field(
        default_factory=list
    )

    static_async_functions: List[
        str
    ] = field(
        default_factory=list
    )

    static_classes: List[
        str
    ] = field(
        default_factory=list
    )

    runtime_callables: List[
        str
    ] = field(
        default_factory=list
    )

    declared_capabilities: List[
        str
    ] = field(
        default_factory=list
    )

    detected_capabilities: List[
        str
    ] = field(
        default_factory=list
    )

    error: Optional[
        str
    ] = None


# ============================================================
# COMPONENT DISCOVERY 01–10
# ============================================================

class ComponentDiscovery:

    FILE_NUMBER_PATTERN = (
        re.compile(
            (
                r"(?:^|[-_])"
                r"([0-9]{2})"
                r"(?:\.py$|[-_])"
            ),
            re.IGNORECASE,
        )
    )

    def discover_files(
        self,
    ) -> Dict[
        str,
        List[Path]
    ]:

        discovered: Dict[
            str,
            List[Path]
        ] = {
            number:
                []

            for number
            in OFFICIAL_NUMBERS
        }

        for path in ROOT_DIR.glob(
            "*.py"
        ):

            if not path.is_file():

                continue

            match = (
                self.FILE_NUMBER_PATTERN
                .search(
                    path.name
                )
            )

            if (
                match
                and
                match.group(
                    1
                )
                in discovered
            ):

                discovered[
                    match.group(
                        1
                    )
                ].append(
                    path.resolve()
                )

        for number, filename in (
            KNOWN_CORE_FILES.items()
        ):

            path = (
                ROOT_DIR
                /
                filename
            ).resolve()

            if (
                number
                in discovered
                and
                path.exists()
                and
                path
                not in discovered[
                    number
                ]
            ):

                discovered[
                    number
                ].insert(
                    0,
                    path,
                )

        for number in discovered:

            discovered[
                number
            ] = sorted(
                discovered[
                    number
                ],
                key=lambda path: (
                    0
                    if path.name
                    ==
                    KNOWN_CORE_FILES.get(
                        number
                    )
                    else
                    1,
                    path.name,
                ),
            )

        return discovered

    @staticmethod
    def _capabilities_from_declaration(
        value: Any,
    ) -> List[str]:

        if isinstance(
            value,
            dict,
        ):

            values = (
                value.keys()
            )

        elif isinstance(
            value,
            (
                list,
                tuple,
                set,
            ),
        ):

            values = value

        else:

            return []

        return sorted(
            {
                str(
                    item
                )
                .strip()
                .upper()

                for item
                in values

                if str(
                    item
                ).strip()
            }
        )

    def inspect_file(
        self,
        number: str,
        path: Path,
        runtime_import: bool = True,
    ) -> ComponentRecord:

        static = (
            StaticPythonDiscovery
            .discover(
                path
            )
        )

        record = ComponentRecord(
            number=number,
            filename=path.name,
            path=str(path),
            exists=path.exists(),
            size=(
                path.stat().st_size
                if path.exists()
                else
                0
            ),
            sha256=(
                sha256_file(
                    path
                )
                if path.exists()
                else
                None
            ),
        )

        record.static_functions = list(
            static.get(
                "functions",
                [],
            )
        )

        record.static_async_functions = list(
            static.get(
                "async_functions",
                [],
            )
        )

        record.static_classes = list(
            static.get(
                "classes",
                [],
            )
        )

        for value in (
            static.get(
                "constants"
            )
            or
            {}
        ).values():

            record.declared_capabilities.extend(
                self._capabilities_from_declaration(
                    value
                )
            )

        record.declared_capabilities = sorted(
            set(
                record.declared_capabilities
            )
        )

        if not static.get(
            "success"
        ):

            record.error = (
                static.get(
                    "error"
                )
            )

        if number == "01":

            record.importable = True

            record.runtime_callables = sorted(
                set(
                    record.static_functions
                    +
                    record.static_async_functions
                )
            )

            return record

        if (
            runtime_import
            and
            static.get(
                "success"
            )
        ):

            try:

                module = load_module(
                    path,
                    (
                        "_majd_discovery_"
                        +
                        number
                        +
                        "_"
                        +
                        uuid.uuid4().hex
                    ),
                )

                record.importable = True

                record.runtime_callables = sorted(
                    name

                    for name
                    in dir(
                        module
                    )

                    if (
                        not name.startswith(
                            "_"
                        )
                        and
                        callable(
                            getattr(
                                module,
                                name,
                                None,
                            )
                        )
                    )
                )

                for constant_name in (
                    "CAPABILITIES",
                    "MAJD_CAPABILITIES",
                    "COMPONENT_CAPABILITIES",
                ):

                    if hasattr(
                        module,
                        constant_name,
                    ):

                        record.declared_capabilities.extend(
                            self._capabilities_from_declaration(
                                getattr(
                                    module,
                                    constant_name,
                                )
                            )
                        )

                record.declared_capabilities = sorted(
                    set(
                        record.declared_capabilities
                    )
                )

            except Exception as error:

                record.importable = False

                record.error = (
                    f"{type(error).__name__}: "
                    f"{error}"
                )

        return record

    def discover(
        self,
        runtime_import: bool = True,
    ) -> Dict[str, Any]:

        files = (
            self.discover_files()
        )

        components: Dict[
            str,
            List[Dict[str, Any]]
        ] = {}

        for number in OFFICIAL_NUMBERS:

            components[
                number
            ] = [
                asdict(
                    self.inspect_file(
                        number,
                        path,
                        runtime_import=
                            runtime_import,
                    )
                )

                for path
                in files[
                    number
                ]
            ]

        missing = [
            number

            for number
            in OFFICIAL_NUMBERS

            if not components[
                number
            ]
        ]

        result = {
            "success":
                not missing,

            "generated_at":
                utc_now(),

            "components":
                components,

            "missing_numbers":
                missing,
        }

        write_json(
            REGISTRY_DIR
            /
            "components.json",
            result,
        )

        return result


# ============================================================
# TRUSTED CAPABILITY REGISTRY
# ============================================================

class CapabilityRegistry:

    """
    No keyword/filename inference.

    Capability becomes registered only through:
    1. explicit component declaration, or
    2. an exact callable contract.

    run()/execute() alone does NOT turn an audit file into
    PAYMENTS, ADS, SOCIAL, etc.
    """

    GENERIC_ENTRYPOINTS = (
        "execute_request",
        "process_request",
        "process_command",
        "run_command",
        "execute",
        "run",
    )

    CAPABILITY_CONTRACTS: Dict[
        str,
        Tuple[str, ...]
    ] = {
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
            "render_media",
        ),

        "VIDEO": (
            "create_video",
            "generate_video",
            "render_video",
            "process_video",
        ),

        "IMAGE": (
            "create_image",
            "generate_image",
            "render_image",
            "process_image",
        ),

        "AUDIO": (
            "create_audio",
            "generate_audio",
            "process_audio",
        ),

        "VOICE": (
            "create_voice",
            "generate_voice",
            "synthesize_voice",
        ),

        "MUSIC": (
            "create_music",
            "generate_music",
        ),

        "SOCIAL": (
            "publish_social",
            "process_social",
            "social_publish",
            "publish_post",
        ),

        "LIVE": (
            "start_live",
            "process_live",
            "live_stream",
            "stream_live",
        ),

        "PAYMENTS": (
            "process_payment",
            "execute_payment",
            "create_payment",
            "payment_status",
        ),

        "WALLET": (
            "wallet_balance",
            "wallet_credit",
            "wallet_debit",
            "process_wallet",
        ),

        "ADS": (
            "process_ad",
            "publish_ad",
            "create_ad",
            "serve_ad",
        ),

        "LEGAL": (
            "review_contract",
            "generate_contract",
            "legal_review",
        ),

        "SECURITY": (
            "security_check",
            "scan_security",
            "security_status",
        ),

        "CONTENT_SAFETY": (
            "moderate_content",
            "content_safety_check",
            "moderate_media",
            "moderate_live",
        ),

        "MONITORING": (
            "health",
            "health_check",
            "status",
            "monitor",
            "capability_snapshot",
        ),

        "REPAIR": (
            "repair",
            "repair_system",
            "auto_repair",
            "repair_dependencies",
            "recover_docker",
        ),

        "DIAGNOSTICS": (
            "diagnose",
            "inspect_company_direct",
            "inspect_platform",
            "dependency_state",
        ),

        "TESTING": (
            "verify_syntax",
            "verify_core",
            "run_tests",
            "test",
        ),

        "VERIFICATION": (
            "verify_artifact",
            "verify_published",
            "verify_mastermind_result",
            "verify",
        ),

        "BUILD": (
            "build",
            "build_queue",
            "select_batch",
        ),

        "PLATFORM": (
            "inspect_platform",
            "publish_game",
            "send_to_majd",
        ),

        "RUNTIME": (
            "runtime_status",
            "runtime_execute",
            "run_process",
            "recover_docker",
        ),

        "OWNER_COMMAND": (
            "execute_owner_command",
            "process_owner_command",
            "owner_command",
        ),

        "ORCHESTRATION": (
            "orchestrate",
            "plan_and_execute",
            "execute_objective",
        ),

        "DASHBOARD": (
            "dashboard_status",
            "owner_dashboard",
            "dashboard_snapshot",
        ),

        "HEALTH": (
            "health",
            "health_check",
            "capability_status",
        ),

        "DOCKER": (
            "docker_state",
            "recover_docker",
        ),
    }

    def __init__(
        self,
        discovery: ComponentDiscovery,
    ):

        self.discovery = (
            discovery
        )

        self.registry: Dict[
            str,
            List[Dict[str, Any]]
        ] = {}

        self.report: Dict[
            str,
            Any
        ] = {}

    @staticmethod
    def _safe_capability_snapshot(
        module: Any,
    ) -> List[str]:

        for name in (
            "capability_snapshot",
            "get_capabilities",
            "capabilities",
        ):

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
                    {},
                )

            except Exception:

                continue

            if isinstance(
                value,
                dict,
            ):

                if "capabilities" in value:

                    value = (
                        value[
                            "capabilities"
                        ]
                    )

                elif "available" in value:

                    value = (
                        value[
                            "available"
                        ]
                    )

                else:

                    value = list(
                        value.keys()
                    )

            if isinstance(
                value,
                (
                    list,
                    tuple,
                    set,
                ),
            ):

                return sorted(
                    {
                        str(
                            item
                        )
                        .strip()
                        .upper()

                        for item
                        in value

                        if str(
                            item
                        ).strip()
                    }
                )

        return []

    def build(
        self,
    ) -> Dict[str, Any]:

        report = (
            self.discovery
            .discover(
                runtime_import=True
            )
        )

        registry: Dict[
            str,
            List[Dict[str, Any]]
        ] = {}

        detected: Set[
            str
        ] = set()

        operational: Set[
            str
        ] = set()

        for number, records in (
            report[
                "components"
            ].items()
        ):

            for record in records:

                callables = set(
                    record.get(
                        "runtime_callables"
                    )
                    or
                    record.get(
                        "static_functions"
                    )
                    or
                    []
                )

                declared = set(
                    record.get(
                        "declared_capabilities"
                    )
                    or
                    []
                )

                if (
                    record.get(
                        "importable"
                    )
                    and
                    number != "01"
                ):

                    try:

                        module = load_module(
                            Path(
                                record[
                                    "path"
                                ]
                            ),
                            (
                                "_majd_caps_"
                                +
                                number
                                +
                                "_"
                                +
                                uuid.uuid4().hex
                            ),
                        )

                        declared.update(
                            self._safe_capability_snapshot(
                                module
                            )
                        )

                    except Exception:

                        pass

                exact_matches: Dict[
                    str,
                    List[str]
                ] = {}

                for capability, contract_names in (
                    self.CAPABILITY_CONTRACTS.items()
                ):

                    matches = [
                        name

                        for name
                        in contract_names

                        if name
                        in callables
                    ]

                    if matches:

                        exact_matches[
                            capability
                        ] = matches

                        detected.add(
                            capability
                        )

                for capability in sorted(
                    declared
                    |
                    set(
                        exact_matches.keys()
                    )
                ):

                    capability = (
                        capability.upper()
                    )

                    preferred = list(
                        exact_matches.get(
                            capability,
                            [],
                        )
                    )

                    generic = [
                        name

                        for name
                        in self.GENERIC_ENTRYPOINTS

                        if name
                        in callables
                    ]

                    entrypoints = (
                        preferred
                        or
                        (
                            generic
                            if capability
                            in declared
                            else
                            []
                        )
                    )

                    provider = {
                        "number":
                            number,

                        "filename":
                            record[
                                "filename"
                            ],

                        "path":
                            record[
                                "path"
                            ],

                        "entrypoints":
                            entrypoints,

                        "exact_contracts":
                            preferred,

                        "declared":
                            capability
                            in declared,

                        "importable":
                            bool(
                                record.get(
                                    "importable"
                                )
                            ),

                        "operational":
                            bool(
                                record.get(
                                    "importable"
                                )
                                and
                                entrypoints
                            ),
                    }

                    registry.setdefault(
                        capability,
                        [],
                    ).append(
                        provider
                    )

                    detected.add(
                        capability
                    )

                    if provider[
                        "operational"
                    ]:

                        operational.add(
                            capability
                        )

        self.registry = (
            registry
        )

        self.report = {
            "success":
                True,

            "generated_at":
                utc_now(),

            "capabilities":
                registry,

            "detected":
                sorted(
                    detected
                ),

            "operational":
                sorted(
                    operational
                ),

            "unavailable":
                sorted(
                    detected
                    -
                    operational
                ),

            "missing_component_numbers":
                report.get(
                    "missing_numbers",
                    [],
                ),
        }

        write_json(
            REGISTRY_DIR
            /
            "capabilities.json",
            self.report,
        )

        return self.report

    def providers(
        self,
        capability: str,
        operational_only: bool = True,
    ) -> List[Dict[str, Any]]:

        providers = list(
            self.registry.get(
                capability.upper(),
                [],
            )
        )

        if operational_only:

            providers = [
                provider

                for provider
                in providers

                if provider.get(
                    "operational"
                )
            ]

        return providers

    def generic_providers(
        self,
        numbers: Sequence[str] = (
            "02",
            "05",
            "06",
        ),
    ) -> List[Dict[str, Any]]:

        report = (
            self.discovery
            .discover(
                runtime_import=True
            )
        )

        providers: List[
            Dict[str, Any]
        ] = []

        for number in numbers:

            for record in (
                report[
                    "components"
                ].get(
                    number,
                    [],
                )
            ):

                callables = set(
                    record.get(
                        "runtime_callables"
                    )
                    or
                    []
                )

                entrypoints = [
                    name

                    for name
                    in self.GENERIC_ENTRYPOINTS

                    if name
                    in callables
                ]

                if (
                    record.get(
                        "importable"
                    )
                    and
                    entrypoints
                ):

                    providers.append(
                        {
                            "number":
                                number,

                            "filename":
                                record[
                                    "filename"
                                ],

                            "path":
                                record[
                                    "path"
                                ],

                            "entrypoints":
                                entrypoints,

                            "importable":
                                True,

                            "operational":
                                True,

                            "generic":
                                True,
                        }
                    )

        return providers


# ============================================================
# PYTHON ENVIRONMENT
# ============================================================

class PythonEnvironment:

    @staticmethod
    def project_python(
        self=None,
    ) -> Optional[Path]:

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

            ROOT_DIR
            /
            ".venv"
            /
            "Scripts"
            /
            "python.exe",

            ROOT_DIR
            /
            "venv"
            /
            "Scripts"
            /
            "python.exe",
        )

        for candidate in candidates:

            if (
                candidate.exists()
                and
                candidate.is_file()
            ):

                return candidate

        return None


# ============================================================
# PYTHON CHECKER
# ============================================================

class PythonChecker:

    def __init__(
        self,
        executor: ProcessExecutor,
    ):

        self.executor = (
            executor
        )

    def python_binary(
        self,
    ) -> str:

        return str(
            PythonEnvironment
            .project_python()
            or
            Path(
                sys.executable
            )
        )

    def compile_file(
        self,
        path: Path,
    ) -> CommandResult:

        return self.executor.run(
            [
                self.python_binary(),
                "-m",
                "py_compile",
                str(path),
            ],
            cwd=ROOT_DIR,
        )

    def compile_project(
        self,
    ) -> Dict[str, Any]:

        checked: List[
            Dict[str, Any]
        ] = []

        failed: List[
            Dict[str, Any]
        ] = []

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
                    truncate(
                        result.stderr
                    ),
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
    ) -> Dict[str, Any]:

        match = re.search(
            (
                r"No module named "
                r"['\"]([^'\"]+)['\"]"
            ),
            error_text,
            re.IGNORECASE,
        )

        if not match:

            return {
                "success":
                    False,

                "status":
                    "DEPENDENCY_NAME_NOT_DETECTED",
            }

        module = (
            match.group(
                1
            )
            .split(
                "."
            )[
                0
            ]
        )

        package = (
            self.PYTHON_IMPORT_MAP
            .get(
                module,
                module,
            )
        )

        python_binary = (
            PythonEnvironment
            .project_python()
        )

        if python_binary is None:

            return {
                "success":
                    False,

                "status":
                    "VIRTUAL_ENVIRONMENT_REQUIRED",

                "module":
                    module,

                "package":
                    package,
            }

        self.logger.log(
            "DEPENDENCY_REPAIR_STARTED",
            {
                "module":
                    module,

                "package":
                    package,
            },
        )

        result = self.executor.run(
            [
                str(
                    python_binary
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

        path = safe_project_path(
            path
        )

        if (
            path.suffix.lower()
            !=
            ".py"
        ):

            return {
                "success":
                    False,

                "status":
                    "NON_PYTHON_REPAIR_REFUSED",

                "path":
                    str(
                        path
                    ),
            }

        temporary = (
            path.with_name(
                path.name
                +
                f".{uuid.uuid4().hex}.majd-new.py"
            )
        )

        temporary.write_text(
            content,
            encoding="utf-8",
        )

        compile_new = (
            self.checker
            .compile_file(
                temporary
            )
        )

        if not compile_new.success:

            temporary.unlink(
                missing_ok=True
            )

            return {
                "success":
                    False,

                "status":
                    "REPLACEMENT_SYNTAX_INVALID",

                "stderr":
                    truncate(
                        compile_new.stderr
                    ),
            }

        backup_path = (
            self.backup
            .backup(
                path
            )
        )

        before_hash = (
            sha256_file(
                path
            )
            if path.exists()
            else
            None
        )

        temporary.replace(
            path
        )

        compile_live = (
            self.checker
            .compile_file(
                path
            )
        )

        if not compile_live.success:

            rollback = (
                self.backup
                .restore(
                    path
                )
            )

            return {
                "success":
                    False,

                "status":
                    "REPAIR_REGRESSION_ROLLED_BACK",

                "compile":
                    asdict(
                        compile_live
                    ),

                "rollback":
                    rollback,
            }

        result = {
            "success":
                True,

            "status":
                "FILE_REPLACED_AND_COMPILED",

            "path":
                str(path),

            "backup":
                backup_path,

            "before_sha256":
                before_hash,

            "after_sha256":
                sha256_file(
                    path
                ),
        }

        self.logger.log(
            "FILE_REPLACED",
            result,
        )

        return result


# ============================================================
# AUTO AI DISCOVERY / CONNECTION
# ============================================================

@dataclass
class AIConnection:

    protocol: str

    base_url: str

    model: str

    verified_at: str

    test_response: str


class AutoAIConnector:

    """
    Discovers local OpenAI-compatible or Ollama engines.
    Connection is accepted only after:
    - endpoint responds,
    - model list is real,
    - model selected,
    - real MAJD_OK prompt succeeds.
    """

    def __init__(
        self,
        logger: AuditLogger,
        executor: ProcessExecutor,
    ):

        self.logger = logger
        self.executor = executor

        self.attempts: List[
            Dict[str, Any]
        ] = []

        self.connection: Optional[
            AIConnection
        ] = None

        self.api_key = (
            os.getenv(
                "MAJD_LOCAL_AI_API_KEY",
                "",
            ).strip()
        )

        saved = (
            read_json(
                AI_CONNECTION_FILE,
                {},
            )
            or
            {}
        )

        if (
            saved.get(
                "base_url"
            )
            and
            saved.get(
                "model"
            )
            and
            saved.get(
                "protocol"
            )
        ):

            try:

                self.connection = (
                    AIConnection(
                        protocol=str(
                            saved[
                                "protocol"
                            ]
                        ),
                        base_url=str(
                            saved[
                                "base_url"
                            ]
                        ),
                        model=str(
                            saved[
                                "model"
                            ]
                        ),
                        verified_at=str(
                            saved.get(
                                "verified_at"
                            )
                            or
                            ""
                        ),
                        test_response=str(
                            saved.get(
                                "test_response"
                            )
                            or
                            ""
                        ),
                    )
                )

            except Exception:

                self.connection = None

    def _headers(
        self,
    ) -> Dict[str, str]:

        headers = {
            "Content-Type":
                "application/json",
        }

        if self.api_key:

            headers[
                "Authorization"
            ] = (
                "Bearer "
                +
                self.api_key
            )

        return headers

    def _request_json(
        self,
        url: str,
        method: str = "GET",
        payload: Optional[
            Dict[str, Any]
        ] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:

        data = (
            None
            if payload is None
            else
            json.dumps(
                payload
            ).encode(
                "utf-8"
            )
        )

        request = urllib.request.Request(
            url,
            data=data,
            headers=self._headers(),
            method=method,
        )

        with urllib.request.urlopen(
            request,
            timeout=(
                timeout
                or
                AI_PROBE_TIMEOUT
            ),
        ) as response:

            body = (
                response.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

            if not body.strip():

                return {}

            return json.loads(
                body
            )

    @staticmethod
    def _normalize_base(
        url: str,
    ) -> str:

        return str(
            url
            or
            ""
        ).strip().rstrip(
            "/"
        )

    def _docker_ports(
        self,
    ) -> List[int]:

        result = self.executor.run(
            [
                "docker",
                "ps",
                "--format",
                "{{.Ports}}",
            ],
            cwd=ROOT_DIR,
            timeout=10,
            allow_outside_root=True,
        )

        if not result.success:

            return []

        ports: Set[
            int
        ] = set()

        for match in re.finditer(
            (
                r"(?:"
                r"0\.0\.0\.0:"
                r"|"
                r"127\.0\.0\.1:"
                r"|"
                r":::"
                r")"
                r"(\d+)"
                r"->"
            ),
            result.stdout,
        ):

            try:

                ports.add(
                    int(
                        match.group(
                            1
                        )
                    )
                )

            except ValueError:

                pass

        return sorted(
            ports
        )

    def candidate_endpoints(
        self,
    ) -> List[
        Tuple[str, str]
    ]:

        candidates: List[
            Tuple[str, str]
        ] = []

        def add(
            protocol: str,
            base: str,
        ) -> None:

            base = (
                self._normalize_base(
                    base
                )
            )

            if (
                base
                and
                (
                    protocol,
                    base,
                )
                not in candidates
            ):

                candidates.append(
                    (
                        protocol,
                        base,
                    )
                )

        env_url = (
            os.getenv(
                "MAJD_LOCAL_AI_URL",
                "",
            ).strip()
        )

        if env_url:

            lowered = (
                env_url.lower()
            )

            if (
                "/api"
                in lowered
                and
                "/v1"
                not in lowered
            ):

                add(
                    "ollama",
                    env_url.split(
                        "/api",
                        1,
                    )[
                        0
                    ],
                )

            else:

                base = (
                    env_url[
                        :-3
                    ]
                    if env_url.endswith(
                        "/v1"
                    )
                    else
                    env_url
                )

                add(
                    "openai",
                    base,
                )

        if self.connection:

            add(
                self.connection.protocol,
                self.connection.base_url,
            )

        add(
            "ollama",
            "http://127.0.0.1:11434",
        )

        for port in (
            1234,
            8001,
            8080,
            5000,
            3001,
            9000,
        ):

            add(
                "openai",
                (
                    "http://127.0.0.1:"
                    +
                    str(
                        port
                    )
                ),
            )

        for port in (
            self._docker_ports()
        ):

            if (
                1
                <=
                port
                <=
                65535
            ):

                base = (
                    "http://127.0.0.1:"
                    +
                    str(
                        port
                    )
                )

                add(
                    "openai",
                    base,
                )

                add(
                    "ollama",
                    base,
                )

        return candidates

    def _openai_models(
        self,
        base: str,
    ) -> List[str]:

        body = (
            self._request_json(
                base.rstrip(
                    "/"
                )
                +
                "/v1/models"
            )
        )

        data = (
            body.get(
                "data"
            )
            or
            []
        )

        models = []

        for item in data:

            if (
                isinstance(
                    item,
                    dict,
                )
                and
                item.get(
                    "id"
                )
            ):

                models.append(
                    str(
                        item[
                            "id"
                        ]
                    )
                )

        return models

    def _ollama_models(
        self,
        base: str,
    ) -> List[str]:

        body = (
            self._request_json(
                base.rstrip(
                    "/"
                )
                +
                "/api/tags"
            )
        )

        models = []

        for item in (
            body.get(
                "models"
            )
            or
            []
        ):

            if isinstance(
                item,
                dict,
            ):

                model = (
                    item.get(
                        "model"
                    )
                    or
                    item.get(
                        "name"
                    )
                )

                if model:

                    models.append(
                        str(
                            model
                        )
                    )

        return models

    def _openai_test(
        self,
        base: str,
        model: str,
    ) -> str:

        body = (
            self._request_json(
                (
                    base.rstrip(
                        "/"
                    )
                    +
                    "/v1/chat/completions"
                ),
                method="POST",
                timeout=min(
                    AI_TIMEOUT,
                    30,
                ),
                payload={
                    "model":
                        model,

                    "temperature":
                        0,

                    "max_tokens":
                        32,

                    "messages": [
                        {
                            "role":
                                "system",

                            "content":
                                (
                                    "You are the MAJD "
                                    "local AI health checker."
                                ),
                        },
                        {
                            "role":
                                "user",

                            "content":
                                "Reply exactly MAJD_OK",
                        },
                    ],
                },
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

            return ""

        return str(
            choices[
                0
            ]
            .get(
                "message",
                {},
            )
            .get(
                "content"
            )
            or
            ""
        ).strip()

    def _ollama_test(
        self,
        base: str,
        model: str,
    ) -> str:

        body = (
            self._request_json(
                (
                    base.rstrip(
                        "/"
                    )
                    +
                    "/api/chat"
                ),
                method="POST",
                timeout=min(
                    AI_TIMEOUT,
                    30,
                ),
                payload={
                    "model":
                        model,

                    "stream":
                        False,

                    "messages": [
                        {
                            "role":
                                "system",

                            "content":
                                (
                                    "You are the MAJD "
                                    "local AI health checker."
                                ),
                        },
                        {
                            "role":
                                "user",

                            "content":
                                "Reply exactly MAJD_OK",
                        },
                    ],
                },
            )
        )

        return str(
            body.get(
                "message",
                {},
            ).get(
                "content"
            )
            or
            ""
        ).strip()

    def _choose_model(
        self,
        models: List[str],
    ) -> Optional[str]:

        requested = (
            os.getenv(
                "MAJD_LOCAL_AI_MODEL",
                "",
            ).strip()
        )

        if (
            requested
            and
            requested
            in models
        ):

            return requested

        if requested:

            for model in models:

                if (
                    requested.lower()
                    in
                    model.lower()
                ):

                    return model

        if models:

            return models[
                0
            ]

        return None

    def _verify_candidate(
        self,
        protocol: str,
        base: str,
    ) -> Optional[
        AIConnection
    ]:

        started = time.time()

        attempt: Dict[
            str,
            Any
        ] = {
            "protocol":
                protocol,

            "base_url":
                base,

            "time":
                utc_now(),
        }

        try:

            if protocol == "openai":

                models = (
                    self._openai_models(
                        base
                    )
                )

            else:

                models = (
                    self._ollama_models(
                        base
                    )
                )

            attempt[
                "models"
            ] = models[
                :20
            ]

            model = (
                self._choose_model(
                    models
                )
            )

            if not model:

                attempt.update(
                    {
                        "success":
                            False,

                        "status":
                            "NO_MODELS",
                    }
                )

                self.attempts.append(
                    attempt
                )

                return None

            if protocol == "openai":

                response = (
                    self._openai_test(
                        base,
                        model,
                    )
                )

            else:

                response = (
                    self._ollama_test(
                        base,
                        model,
                    )
                )

            verified = (
                "MAJD_OK"
                in
                response.upper()
            )

            attempt.update(
                {
                    "success":
                        verified,

                    "status":
                        (
                            "VERIFIED"
                            if verified
                            else
                            "REAL_PROMPT_TEST_FAILED"
                        ),

                    "model":
                        model,

                    "response":
                        truncate(
                            response,
                            300,
                        ),

                    "duration_seconds":
                        round(
                            (
                                time.time()
                                -
                                started
                            ),
                            3,
                        ),
                }
            )

            self.attempts.append(
                attempt
            )

            if not verified:

                return None

            return AIConnection(
                protocol=protocol,
                base_url=base,
                model=model,
                verified_at=utc_now(),
                test_response=response,
            )

        except Exception as error:

            attempt.update(
                {
                    "success":
                        False,

                    "status":
                        "PROBE_FAILED",

                    "error":
                        (
                            f"{type(error).__name__}: "
                            f"{error}"
                        ),

                    "duration_seconds":
                        round(
                            (
                                time.time()
                                -
                                started
                            ),
                            3,
                        ),
                }
            )

            self.attempts.append(
                attempt
            )

            return None

    def ensure_connected(
        self,
        force: bool = False,
    ) -> Dict[str, Any]:

        self.attempts = []

        if (
            self.connection
            and
            not force
        ):

            verified = (
                self._verify_candidate(
                    self.connection.protocol,
                    self.connection.base_url,
                )
            )

            if (
                verified
                and
                verified.model
                ==
                self.connection.model
            ):

                self.connection = (
                    verified
                )

                self._save()

                return self.status()

        for protocol, base in (
            self.candidate_endpoints()
        ):

            connection = (
                self._verify_candidate(
                    protocol,
                    base,
                )
            )

            if connection:

                self.connection = (
                    connection
                )

                self._save()

                self.logger.log(
                    "AI_CONNECTED",
                    {
                        "protocol":
                            connection.protocol,

                        "base_url":
                            connection.base_url,

                        "model":
                            connection.model,
                    },
                )

                return self.status()

        self.connection = None

        write_json(
            AI_CONNECTION_FILE,
            {
                "status":
                    "NOT_CONNECTED",

                "updated_at":
                    utc_now(),

                "attempts":
                    self.attempts[
                        -20:
                    ],
            },
        )

        return self.status()

    def _save(
        self,
    ) -> None:

        if not self.connection:

            return

        write_json(
            AI_CONNECTION_FILE,
            {
                **asdict(
                    self.connection
                ),

                "status":
                    "CONNECTED",

                "updated_at":
                    utc_now(),
            },
        )

    def status(
        self,
    ) -> Dict[str, Any]:

        if not self.connection:

            return {
                "configured":
                    False,

                "connected":
                    False,

                "model":
                    None,

                "protocol":
                    None,

                "base_url":
                    None,

                "status":
                    "NOT_CONNECTED",

                "attempts":
                    self.attempts[
                        -20:
                    ],
            }

        return {
            "configured":
                True,

            "connected":
                True,

            "model":
                self.connection.model,

            "protocol":
                self.connection.protocol,

            "base_url":
                self.connection.base_url,

            "verified_at":
                self.connection.verified_at,

            "status":
                "CONNECTED",

            "attempts":
                self.attempts[
                    -20:
                ],
        }

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> Optional[str]:

        if not self.connection:

            self.ensure_connected(
                force=False
            )

        if not self.connection:

            return None

        try:

            if (
                self.connection.protocol
                ==
                "openai"
            ):

                body = self._request_json(
                    (
                        self.connection.base_url
                        .rstrip(
                            "/"
                        )
                        +
                        "/v1/chat/completions"
                    ),
                    method="POST",
                    timeout=AI_TIMEOUT,
                    payload={
                        "model":
                            self.connection.model,

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
                    },
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

                return str(
                    choices[
                        0
                    ]
                    .get(
                        "message",
                        {},
                    )
                    .get(
                        "content"
                    )
                    or
                    ""
                )

            body = self._request_json(
                (
                    self.connection.base_url
                    .rstrip(
                        "/"
                    )
                    +
                    "/api/chat"
                ),
                method="POST",
                timeout=AI_TIMEOUT,
                payload={
                    "model":
                        self.connection.model,

                    "stream":
                        False,

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
                },
            )

            return str(
                body.get(
                    "message",
                    {},
                ).get(
                    "content"
                )
                or
                ""
            ) or None

        except Exception as error:

            self.logger.log(
                "AI_CHAT_ERROR",
                {
                    "error":
                        (
                            f"{type(error).__name__}: "
                            f"{error}"
                        )
                },
            )

            self.connection = None

            status = (
                self.ensure_connected(
                    force=True
                )
            )

            if not status.get(
                "connected"
            ):

                return None

            try:

                if (
                    self.connection
                    and
                    self.connection.protocol
                    ==
                    "openai"
                ):

                    body = (
                        self._request_json(
                            (
                                self.connection.base_url
                                .rstrip(
                                    "/"
                                )
                                +
                                "/v1/chat/completions"
                            ),
                            method="POST",
                            timeout=AI_TIMEOUT,
                            payload={
                                "model":
                                    self.connection.model,

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
                            },
                        )
                    )

                    choices = (
                        body.get(
                            "choices"
                        )
                        or
                        []
                    )

                    if choices:

                        return str(
                            choices[
                                0
                            ]
                            .get(
                                "message",
                                {},
                            )
                            .get(
                                "content"
                            )
                            or
                            ""
                        )

                elif self.connection:

                    body = self._request_json(
                        (
                            self.connection.base_url
                            .rstrip(
                                "/"
                            )
                            +
                            "/api/chat"
                        ),
                        method="POST",
                        timeout=AI_TIMEOUT,
                        payload={
                            "model":
                                self.connection.model,

                            "stream":
                                False,

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
                        },
                    )

                    return str(
                        body.get(
                            "message",
                            {},
                        ).get(
                            "content"
                        )
                        or
                        ""
                    ) or None

            except Exception:

                return None

        return None


# ============================================================
# LOCAL AI ADAPTER
# ============================================================

class LocalAIAdapter:

    def __init__(
        self,
        connector: AutoAIConnector,
        logger: AuditLogger,
    ):

        self.connector = (
            connector
        )

        self.logger = (
            logger
        )

    @property
    def available(
        self,
    ) -> bool:

        return bool(
            self.connector.connection
        )

    def ensure_connected(
        self,
        force: bool = False,
    ) -> Dict[str, Any]:

        return (
            self.connector
            .ensure_connected(
                force=force
            )
        )

    def status(
        self,
    ) -> Dict[str, Any]:

        return (
            self.connector
            .status()
        )

    def ask(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> Optional[str]:

        return (
            self.connector
            .chat(
                system_prompt,
                user_prompt,
            )
        )


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
        owner: str = DEFAULT_OWNER,
    ) -> Dict[str, Any]:

        path = Path(
            provider[
                "path"
            ]
        )

        try:

            module = load_module(
                path,
                (
                    "_majd_execute_"
                    +
                    uuid.uuid4().hex
                ),
            )

        except Exception as error:

            return {
                "success":
                    False,

                "status":
                    "COMPONENT_LOAD_FAILED",

                "component":
                    provider,

                "error":
                    (
                        f"{type(error).__name__}: "
                        f"{error}"
                    ),

                "traceback":
                    truncate(
                        traceback.format_exc()
                    ),
            }

        for name in (
            provider.get(
                "entrypoints"
            )
            or
            []
        ):

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
                    {
                        "command":
                            command,

                        "request":
                            request,

                        "payload":
                            request,

                        "job_id":
                            job_id,

                        "operation_id":
                            job_id,

                        "owner":
                            owner,

                        "output_root":
                            str(
                                OUTPUT_DIR
                            ),
                    },
                )

                result = normalize_result(
                    value,
                    provider.get(
                        "filename"
                    ),
                )

                result.setdefault(
                    "entrypoint",
                    name,
                )

                return result

            except Exception as error:

                return {
                    "success":
                        False,

                    "status":
                        "COMPONENT_EXECUTION_FAILED",

                    "component":
                        provider.get(
                            "filename"
                        ),

                    "entrypoint":
                        name,

                    "error":
                        (
                            f"{type(error).__name__}: "
                            f"{error}"
                        ),

                    "traceback":
                        truncate(
                            traceback.format_exc()
                        ),
                }

        return {
            "success":
                False,

            "status":
                "COMPONENT_ENTRYPOINT_MISSING",

            "component":
                provider.get(
                    "filename"
                ),
        }


# ============================================================
# REAL RUNTIME 06 BRIDGE
# ============================================================

class Runtime06Bridge:

    def __init__(
        self,
        discovery: ComponentDiscovery,
        logger: AuditLogger,
    ):

        self.discovery = (
            discovery
        )

        self.logger = (
            logger
        )

    def _modules(
        self,
    ) -> List[
        Tuple[
            Dict[str, Any],
            Any,
        ]
    ]:

        report = (
            self.discovery
            .discover(
                runtime_import=True
            )
        )

        result: List[
            Tuple[
                Dict[str, Any],
                Any,
            ]
        ] = []

        for record in (
            report[
                "components"
            ].get(
                "06",
                [],
            )
        ):

            if not record.get(
                "importable"
            ):

                continue

            try:

                module = load_module(
                    Path(
                        record[
                            "path"
                        ]
                    ),
                    (
                        "_majd_runtime06_"
                        +
                        uuid.uuid4().hex
                    ),
                )

                result.append(
                    (
                        record,
                        module,
                    )
                )

            except Exception:

                continue

        return result

    def call_first(
        self,
        names: Sequence[str],
        values: Dict[str, Any],
    ) -> Dict[str, Any]:

        for record, module in (
            self._modules()
        ):

            for name in names:

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

                    result = (
                        normalize_result(
                            value,
                            record[
                                "filename"
                            ],
                        )
                    )

                    result.setdefault(
                        "entrypoint",
                        name,
                    )

                    self.logger.log(
                        "RUNTIME06_RESULT",
                        result,
                    )

                    return result

                except Exception as error:

                    return {
                        "success":
                            False,

                        "status":
                            "RUNTIME06_EXCEPTION",

                        "entrypoint":
                            name,

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
                "RUNTIME06_INTERFACE_NOT_FOUND",

            "expected":
                list(
                    names
                ),
        }

    def repair(
        self,
        failure: Dict[str, Any],
        diagnosis: Dict[str, Any],
    ) -> Dict[str, Any]:

        repair_type = str(
            diagnosis.get(
                "type"
            )
            or
            ""
        )

        if (
            repair_type
            ==
            "MISSING_PYTHON_MODULE"
        ):

            names = (
                "repair_dependencies",
            )

        elif (
            "DOCKER"
            in
            json.dumps(
                failure,
                default=str,
            ).upper()
        ):

            names = (
                "recover_docker",
            )

        else:

            names = (
                "execute",
                "run",
            )

        return self.call_first(
            names,
            {
                "command":
                    (
                        "Repair this verified MAJD "
                        "failure and return a real result"
                    ),

                "request":
                    failure,

                "payload":
                    failure,

                "failure":
                    failure,

                "diagnosis":
                    diagnosis,

                "owner":
                    DEFAULT_OWNER,
            },
        )

    def verification(
        self,
    ) -> Dict[str, Any]:

        checks: Dict[
            str,
            Any
        ] = {}

        for key, names in {
            "core": (
                "verify_core",
            ),

            "syntax": (
                "verify_syntax",
            ),

            "platform": (
                "inspect_platform",
            ),

            "capabilities": (
                "capability_snapshot",
            ),
        }.items():

            checks[
                key
            ] = self.call_first(
                names,
                {},
            )

        success = all(
            (
                item.get(
                    "success"
                )
                is True
            )
            or
            (
                item.get(
                    "status"
                )
                ==
                "RUNTIME06_INTERFACE_NOT_FOUND"
            )

            for item
            in checks.values()
        )

        return {
            "success":
                success,

            "checks":
                checks,
        }


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

        lowered = (
            text.lower()
        )

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
                        -10000:
                    ],
            }

        if any(
            token in lowered

            for token in (
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
                        -10000:
                    ],
            }

        if "interface" in lowered:

            return {
                "type":
                    "INTERFACE_MISMATCH",

                "repairable":
                    True,

                "details":
                    text[
                        -10000:
                    ],
            }

        if "artifact" in lowered:

            return {
                "type":
                    "ARTIFACT_FAILURE",

                "repairable":
                    True,

                "details":
                    text[
                        -10000:
                    ],
            }

        if (
            "publish"
            in lowered
            or
            "publication"
            in lowered
        ):

            return {
                "type":
                    "PUBLICATION_FAILURE",

                "repairable":
                    True,

                "details":
                    text[
                        -10000:
                    ],
            }

        if (
            "docker"
            in lowered
            or
            "container"
            in lowered
        ):

            return {
                "type":
                    "DOCKER_FAILURE",

                "repairable":
                    True,

                "details":
                    text[
                        -10000:
                    ],
            }

        return {
            "type":
                "UNKNOWN",

            "repairable":
                True,

            "details":
                text[
                    -10000:
                ],
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
        ai: LocalAIAdapter,
        runtime06: Runtime06Bridge,
    ):

        self.operation_id = (
            operation_id
        )

        self.logger = (
            logger
        )

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

        self.ai = (
            ai
        )

        self.runtime06 = (
            runtime06
        )

        self.code = (
            CodeManager(
                self.backup,
                logger,
                checker,
            )
        )

    def _ai_code_repair(
        self,
        diagnosis: Dict[str, Any],
        failure: Dict[str, Any],
    ) -> Dict[str, Any]:

        if not self.ai.available:

            self.ai.ensure_connected(
                force=False
            )

        if not self.ai.available:

            return {
                "success":
                    False,

                "status":
                    "CODE_REPAIR_ENGINE_UNAVAILABLE",

                "ai":
                    self.ai.status(),
            }

        relevant_files = [
            {
                "path":
                    path.name,

                "sha256":
                    sha256_file(
                        path
                    ),

                "size":
                    path.stat().st_size,
            }

            for path in ROOT_DIR.glob(
                "*.py"
            )

            if path.is_file()
        ]

        prompt = (
            "Repair the verified MAJD-GAME-FACTORY failure. "
            "Return JSON only.\n"
            "{\"success\":true,\"changes\":["
            "{\"path\":\"relative.py\","
            "\"content\":\"COMPLETE FILE CONTENT\"}]}\n"
            "Rules: complete-file replacement only; "
            "stay inside project root; preserve working interfaces; "
            "never claim success without a real applied change; "
            "do not rewrite MAJD-AI-MASTERMIND-01.py while it is executing.\n\n"
            "FAILURE:\n"
            +
            json.dumps(
                failure,
                ensure_ascii=False,
                default=str,
            )
            +
            "\nDIAGNOSIS:\n"
            +
            json.dumps(
                diagnosis,
                ensure_ascii=False,
                default=str,
            )
            +
            "\nFILES:\n"
            +
            json.dumps(
                relevant_files,
                ensure_ascii=False,
            )
        )

        answer = self.ai.ask(
            (
                "You are the MAJD sovereign code repair engine. "
                "Be conservative and return JSON only."
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

            cleaned = re.sub(
                r"^```(?:json)?\s*",
                "",
                answer.strip(),
            )

            cleaned = re.sub(
                r"\s*```$",
                "",
                cleaned,
            )

            data = json.loads(
                cleaned
            )

        except Exception as error:

            return {
                "success":
                    False,

                "status":
                    "AI_REPAIR_RESPONSE_INVALID",

                "error":
                    str(
                        error
                    ),
            }

        applied: List[
            Dict[str, Any]
        ] = []

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

            target = safe_project_path(
                ROOT_DIR
                /
                relative
            )

            if (
                target.resolve()
                ==
                THIS_FILE
            ):

                applied.append(
                    {
                        "success":
                            False,

                        "status":
                            "SELF_REWRITE_REQUIRES_CONTROLLED_RESTART",

                        "path":
                            relative,
                    }
                )

                continue

            applied.append(
                self.code
                .replace_python_file(
                    target,
                    content,
                )
            )

        success = (
            bool(
                applied
            )
            and
            all(
                item.get(
                    "success"
                )

                for item
                in applied
            )
        )

        return {
            "success":
                success,

            "status":
                (
                    "AI_CODE_REPAIR_APPLIED"
                    if success
                    else
                    "AI_REPAIR_INCOMPLETE"
                ),

            "changes":
                applied,
        }

    def repair(
        self,
        diagnosis: Dict[str, Any],
        failure: Dict[str, Any],
    ) -> Dict[str, Any]:

        repair_type = str(
            diagnosis.get(
                "type"
            )
            or
            ""
        )

        runtime_result = (
            self.runtime06
            .repair(
                failure,
                diagnosis,
            )
        )

        if (
            runtime_result.get(
                "success"
            )
            is True
        ):

            return {
                "success":
                    True,

                "status":
                    "RUNTIME06_REPAIR_COMPLETED",

                "runtime06":
                    runtime_result,
            }

        if (
            repair_type
            ==
            "MISSING_PYTHON_MODULE"
        ):

            dependency = (
                self.dependencies
                .repair_missing_python_module(
                    json.dumps(
                        failure,
                        ensure_ascii=False,
                        default=str,
                    )
                )
            )

            if dependency.get(
                "success"
            ):

                return {
                    "success":
                        True,

                    "status":
                        "DEPENDENCY_REPAIRED",

                    "dependency":
                        dependency,
                }

        ai_result = (
            self._ai_code_repair(
                diagnosis,
                failure,
            )
        )

        return {
            "success":
                (
                    ai_result.get(
                        "success"
                    )
                    is True
                ),

            "status":
                ai_result.get(
                    "status",
                    "AUTONOMOUS_REPAIR_FAILED",
                ),

            "runtime06":
                runtime_result,

            "ai_repair":
                ai_result,
        }


# ============================================================
# CONTENT SAFETY
# ============================================================

class ContentSafetyPolicy:

    EXPLICIT_SEXUAL_TERMS = {
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
        "تصوير موقع حكومي محظور",
        "تصوير سيارة حكومية محظور",
    }

    def inspect_text(
        self,
        text: str,
    ) -> Dict[str, Any]:

        normalized = str(
            text
            or
            ""
        ).lower()

        violations: List[
            Dict[str, str]
        ] = []

        if any(
            term.lower()
            in normalized

            for term
            in self.EXPLICIT_SEXUAL_TERMS
        ):

            violations.append(
                {
                    "policy":
                        "EXPLICIT_SEXUAL_CONTENT",

                    "action":
                        "BLOCK",
                }
            )

        if any(
            term.lower()
            in normalized

            for term
            in self.SENSITIVE_GOVERNMENT_TERMS
        ):

            violations.append(
                {
                    "policy":
                        "SENSITIVE_GOVERNMENT_CONTENT",

                    "action":
                        "BLOCK",
                }
            )

        return {
            "success":
                not violations,

            "status":
                (
                    "CONTENT_ALLOWED"
                    if not violations
                    else
                    "CONTENT_BLOCKED"
                ),

            "violations":
                violations,
        }

    def inspect_request(
        self,
        command: str,
        request_type: str,
        payload: Dict[str, Any],
        registry: CapabilityRegistry,
        executor: ComponentExecutor,
        job_id: str,
        owner: str,
    ) -> Dict[str, Any]:

        text_result = (
            self.inspect_text(
                command
                +
                "\n"
                +
                json.dumps(
                    payload,
                    ensure_ascii=False,
                    default=str,
                )
            )
        )

        if not text_result.get(
            "success"
        ):

            return text_result

        needs_media_moderation = (
            request_type
            in {
                "SOCIAL",
                "LIVE",
            }
            or
            any(
                payload.get(
                    key
                )

                for key in (
                    "image",
                    "image_path",
                    "video",
                    "video_path",
                    "media",
                    "asset",
                    "stream_url",
                )
            )
        )

        if not needs_media_moderation:

            return {
                "success":
                    True,

                "status":
                    "CONTENT_ALLOWED",

                "text":
                    text_result,
            }

        providers = (
            registry.providers(
                "CONTENT_SAFETY"
            )
        )

        if not providers:

            return {
                "success":
                    False,

                "status":
                    "CONTENT_SAFETY_ADAPTER_REQUIRED",

                "message":
                    (
                        "Visual/live publication is blocked until "
                        "a real moderation adapter is operational."
                    ),
            }

        failures = []

        for provider in providers:

            result = (
                executor.execute_provider(
                    provider,
                    command,
                    payload,
                    job_id,
                    owner,
                )
            )

            if (
                result.get(
                    "success"
                )
                is True
            ):

                return {
                    "success":
                        True,

                    "status":
                        "CONTENT_SAFETY_VERIFIED",

                    "provider":
                        provider,

                    "result":
                        result,
                }

            failures.append(
                {
                    "provider":
                        provider,

                    "result":
                        result,
                }
            )

        return {
            "success":
                False,

            "status":
                "CONTENT_SAFETY_CHECK_FAILED",

            "failures":
                failures,
        }


# ============================================================
# SECURITY CENTER
# ============================================================

class SecurityCenter:

    SUSPICIOUS_PATTERNS = (
        re.compile(
            r"failed password",
            re.IGNORECASE,
        ),

        re.compile(
            r"invalid user",
            re.IGNORECASE,
        ),

        re.compile(
            r"authentication failure",
            re.IGNORECASE,
        ),

        re.compile(
            r"\b401\b"
        ),

        re.compile(
            r"\b403\b"
        ),

        re.compile(
            r"sql injection",
            re.IGNORECASE,
        ),

        re.compile(
            r"path traversal",
            re.IGNORECASE,
        ),

        re.compile(
            r"\.\./\.\./"
        ),
    )

    def __init__(
        self,
        logger: AuditLogger,
        executor: ProcessExecutor,
    ):

        self.logger = (
            logger
        )

        self.executor = (
            executor
        )

        self.events_file = (
            SECURITY_DIR
            /
            "events.jsonl"
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
            "id":
                str(
                    uuid.uuid4()
                ),

            "time":
                utc_now(),

            "event_type":
                event_type,

            "severity":
                severity.upper(),

            "source":
                source,

            "target":
                target,

            "action":
                action,

            "result":
                result,

            "details":
                details
                or
                {},
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
                +
                "\n"
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

        result: List[
            Dict[str, Any]
        ] = []

        for line in (
            self.events_file
            .read_text(
                encoding="utf-8",
                errors="replace",
            )
            .splitlines()[
                -limit:
            ]
        ):

            try:

                result.append(
                    json.loads(
                        line
                    )
                )

            except Exception:

                pass

        return result

    def _read_auth_log(
        self,
    ) -> str:

        path = Path(
            "/var/log/auth.log"
        )

        if (
            not path.exists()
            or
            not os.access(
                path,
                os.R_OK,
            )
        ):

            return ""

        try:

            lines = (
                path.read_text(
                    encoding="utf-8",
                    errors="replace",
                )
                .splitlines()
            )

            return "\n".join(
                lines[
                    -1000:
                ]
            )

        except Exception:

            return ""

    def scan(
        self,
    ) -> Dict[str, Any]:

        sources: Dict[
            str,
            str
        ] = {}

        auth = (
            self._read_auth_log()
        )

        if auth:

            sources[
                "auth.log"
            ] = auth

        journal = (
            self.executor.run(
                [
                    "journalctl",
                    "--since",
                    "-10 minutes",
                    "-n",
                    "700",
                    "--no-pager",
                ],
                cwd=ROOT_DIR,
                timeout=15,
                allow_outside_root=True,
            )
        )

        if (
            journal.success
            and
            journal.stdout
        ):

            sources[
                "journalctl"
            ] = journal.stdout

        findings: List[
            Dict[str, Any]
        ] = []

        seen_lines: Set[
            str
        ] = set()

        for source_name, text in (
            sources.items()
        ):

            for line in text.splitlines():

                if line in seen_lines:

                    continue

                for pattern in (
                    self.SUSPICIOUS_PATTERNS
                ):

                    if pattern.search(
                        line
                    ):

                        seen_lines.add(
                            line
                        )

                        findings.append(
                            {
                                "source":
                                    source_name,

                                "pattern":
                                    pattern.pattern,

                                "line":
                                    truncate(
                                        line,
                                        800,
                                    ),
                            }
                        )

                        break

        listeners = (
            self.executor.run(
                [
                    "ss",
                    "-ltnp",
                ],
                cwd=ROOT_DIR,
                timeout=10,
                allow_outside_root=True,
            )
        )

        result = {
            "success":
                True,

            "status":
                "SECURITY_SCAN_COMPLETED",

            "time":
                utc_now(),

            "suspicious_count":
                len(
                    findings
                ),

            "findings":
                findings[
                    -100:
                ],

            "listeners":
                (
                    truncate(
                        listeners.stdout,
                        12000,
                    )
                    if listeners.success
                    else
                    None
                ),
        }

        if findings:

            self.record(
                "SUSPICIOUS_ACTIVITY_DETECTED",
                (
                    "HIGH"
                    if len(
                        findings
                    ) >= 10
                    else
                    "MEDIUM"
                ),
                action=(
                    "LOG_AND_ISOLATE_AT_EDGE_IF_"
                    "SECURITY_PROVIDER_SUPPORTS_IT"
                ),
                result="DETECTED",
                details={
                    "count":
                        len(
                            findings
                        ),

                    "findings":
                        findings[
                            -20:
                        ],
                },
            )

        write_json(
            SECURITY_DIR
            /
            "latest-scan.json",
            result,
        )

        return result


# ============================================================
# LEGAL ASSISTANT
# ============================================================

class ElectronicLegalAssistant:

    DISCLAIMER = (
        "MAJD Electronic Legal Assistant provides AI drafting/review "
        "assistance. It is not a human licensed lawyer and does not "
        "replace formal legal approval where required."
    )

    def __init__(
        self,
        ai: LocalAIAdapter,
        logger: AuditLogger,
    ):

        self.ai = (
            ai
        )

        self.logger = (
            logger
        )

    def execute(
        self,
        command: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:

        if not self.ai.available:

            self.ai.ensure_connected(
                force=False
            )

        if not self.ai.available:

            return {
                "success":
                    False,

                "status":
                    "LEGAL_AI_NOT_CONNECTED",

                "disclaimer":
                    self.DISCLAIMER,
            }

        prompt = (
            "Assist MAJD with contract drafting/review, terms, privacy, "
            "developer/creator/agency agreements, advertising, sponsorship "
            "and intellectual-property review. Flag items needing formal "
            "legal approval.\n\n"
            f"COMMAND:\n{command}\n\n"
            "PAYLOAD:\n"
            +
            json.dumps(
                payload,
                ensure_ascii=False,
                default=str,
            )
        )

        answer = self.ai.ask(
            (
                "You are the MAJD electronic legal assistance system. "
                "Do not claim to be a licensed human lawyer."
            ),
            prompt,
        )

        if not answer:

            return {
                "success":
                    False,

                "status":
                    "LEGAL_AI_EMPTY",

                "disclaimer":
                    self.DISCLAIMER,
            }

        result = {
            "success":
                True,

            "status":
                "LEGAL_ASSISTANCE_COMPLETED",

            "result":
                answer,

            "disclaimer":
                self.DISCLAIMER,
        }

        self.logger.log(
            "LEGAL_ASSISTANCE",
            {
                "command":
                    command,

                "status":
                    result[
                        "status"
                    ],
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
            result
        ]

        for key in (
            "result",
            "build",
            "output",
            "game",
        ):

            nested = (
                result.get(
                    key
                )
            )

            if isinstance(
                nested,
                dict,
            ):

                containers.append(
                    nested
                )

        for container in containers:

            for key in self.KEYS:

                value = (
                    container.get(
                        key
                    )
                )

                if not value:

                    continue

                path = Path(
                    str(
                        value
                    )
                )

                if not path.is_absolute():

                    path = (
                        ROOT_DIR
                        /
                        path
                    ).resolve()

                else:

                    path = (
                        path.resolve()
                    )

                if is_inside_root(
                    path
                ):

                    return path

        return None

    def verify(
        self,
        result: Dict[str, Any],
    ) -> Dict[str, Any]:

        artifact = (
            self.extract(
                result
            )
        )

        if artifact is None:

            return {
                "success":
                    False,

                "status":
                    "ARTIFACT_MISSING",
            }

        if not artifact.exists():

            return {
                "success":
                    False,

                "status":
                    "ARTIFACT_NOT_FOUND",

                "artifact":
                    str(
                        artifact
                    ),
            }

        if not artifact.is_dir():

            return {
                "success":
                    False,

                "status":
                    "ARTIFACT_NOT_DIRECTORY",

                "artifact":
                    str(
                        artifact
                    ),
            }

        files = [
            item

            for item
            in artifact.rglob(
                "*"
            )

            if item.is_file()
        ]

        index = (
            artifact
            /
            "index.html"
        )

        if not files:

            return {
                "success":
                    False,

                "status":
                    "ARTIFACT_EMPTY",

                "artifact":
                    str(
                        artifact
                    ),
            }

        if (
            not index.exists()
            or
            not index.is_file()
            or
            index.stat().st_size
            <=
            0
        ):

            return {
                "success":
                    False,

                "status":
                    "PLAYABLE_INDEX_NOT_FOUND",

                "artifact":
                    str(
                        artifact
                    ),
            }

        return {
            "success":
                True,

            "status":
                "ARTIFACT_VERIFIED",

            "artifact":
                str(
                    artifact
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
# PUBLICATION VERIFIER
# ============================================================

class PublicationVerifier:

    def verify(
        self,
        published: Dict[str, Any],
    ) -> Dict[str, Any]:

        if (
            published.get(
                "success"
            )
            is not True
        ):

            return {
                "success":
                    False,

                "status":
                    "PUBLISHER_REPORTED_FAILURE",
            }

        directory_value = (
            published.get(
                "published_directory"
            )
            or
            published.get(
                "publish_dir"
            )
            or
            published.get(
                "destination"
            )
        )

        directory_result: Optional[
            Dict[str, Any]
        ] = None

        if directory_value:

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

                directory = (
                    directory.resolve()
                )

            if (
                is_inside_root(
                    directory
                )
                and
                directory.exists()
                and
                directory.is_dir()
            ):

                index = (
                    directory
                    /
                    "index.html"
                )

                if (
                    index.exists()
                    and
                    index.is_file()
                    and
                    index.stat().st_size
                    >
                    0
                ):

                    directory_result = {
                        "published_directory":
                            str(
                                directory
                            ),

                        "index":
                            str(
                                index
                            ),
                    }

        url = (
            published.get(
                "public_url"
            )
        )

        url_result: Optional[
            Dict[str, Any]
        ] = None

        if url:

            try:

                parsed = (
                    urllib.parse
                    .urlparse(
                        str(
                            url
                        )
                    )
                )

                if parsed.scheme in {
                    "http",
                    "https",
                }:

                    request = (
                        urllib.request.Request(
                            str(
                                url
                            ),
                            method="GET",
                            headers={
                                "User-Agent":
                                    "MAJD-Publication-Verifier/4.1",
                            },
                        )
                    )

                    with urllib.request.urlopen(
                        request,
                        timeout=10,
                    ) as response:

                        status = int(
                            getattr(
                                response,
                                "status",
                                200,
                            )
                        )

                        body = response.read(
                            4096
                        )

                    if (
                        200
                        <=
                        status
                        <
                        400
                        and
                        body
                    ):

                        url_result = {
                            "public_url":
                                str(
                                    url
                                ),

                            "http_status":
                                status,

                            "body_bytes_checked":
                                len(
                                    body
                                ),
                        }

            except Exception as error:

                url_result = {
                    "public_url":
                        str(
                            url
                        ),

                    "error":
                        (
                            f"{type(error).__name__}: "
                            f"{error}"
                        ),
                }

        success = (
            bool(
                directory_result
            )
            or
            bool(
                url_result
                and
                url_result.get(
                    "http_status"
                )
            )
        )

        return {
            "success":
                success,

            "status":
                (
                    "REAL_PUBLICATION_VERIFIED"
                    if success
                    else
                    "PUBLICATION_NOT_VERIFIED"
                ),

            "filesystem":
                directory_result,

            "http":
                url_result,

            "game_path":
                published.get(
                    "game_path"
                ),
        }


# ============================================================
# COMMAND CLASSIFIER
# ============================================================

class CommandClassifier:

    RULES: Tuple[
        Tuple[
            str,
            Tuple[str, ...]
        ],
        ...
    ] = (
        (
            "CONNECT_AI",
            (
                "اربط الذكاء",
                "ربط الذكاء",
                "اكتشف محرك الذكاء",
                "connect ai",
                "discover ai engine",
            ),
        ),

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
                "منصة x",
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
            command
            or
            ""
        ).lower()

        scores: Dict[
            str,
            int
        ] = {}

        for command_type, phrases in (
            self.RULES
        ):

            score = sum(
                1

                for phrase
                in phrases

                if phrase.lower()
                in lowered
            )

            if score:

                scores[
                    command_type
                ] = score

        selected = (
            max(
                scores,
                key=scores.get,
            )
            if scores
            else
            "GENERAL_OWNER_COMMAND"
        )

        return {
            "type":
                selected,

            "scores":
                scores,
        }


# ============================================================
# ROUTER
# ============================================================

class CapabilityRouter:

    TYPE_TO_CAPABILITIES = {
        "CREATE_GAME":
            [
                "GAME",
            ],

        "CONTENT":
            [
                "CONTENT",
                "MEDIA",
            ],

        "SOCIAL":
            [
                "SOCIAL",
                "CONTENT",
            ],

        "LIVE":
            [
                "LIVE",
                "MEDIA",
            ],

        "PAYMENTS":
            [
                "PAYMENTS",
                "WALLET",
            ],

        "ADS":
            [
                "ADS",
            ],

        "SECURITY":
            [
                "SECURITY",
            ],

        "REPAIR":
            [
                "REPAIR",
                "DIAGNOSTICS",
            ],

        "INSPECT":
            [
                "HEALTH",
                "TESTING",
                "VERIFICATION",
            ],

        "STATUS":
            [
                "DASHBOARD",
                "MONITORING",
                "HEALTH",
            ],
    }

    def __init__(
        self,
        registry: CapabilityRegistry,
    ):

        self.registry = (
            registry
        )

    def route(
        self,
        command_type: str,
    ) -> Dict[str, Any]:

        desired = (
            self.TYPE_TO_CAPABILITIES
            .get(
                command_type,
                [],
            )
        )

        candidates: List[
            Dict[str, Any]
        ] = []

        seen: Set[
            Tuple[
                str,
                Tuple[str, ...]
            ]
        ] = set()

        for capability in desired:

            for provider in (
                self.registry.providers(
                    capability
                )
            ):

                key = (
                    provider[
                        "path"
                    ],
                    tuple(
                        provider.get(
                            "entrypoints"
                        )
                        or
                        []
                    ),
                )

                if key in seen:

                    continue

                seen.add(
                    key
                )

                candidates.append(
                    {
                        "capability":
                            capability,

                        **provider,
                    }
                )

        return {
            "success":
                bool(
                    candidates
                ),

            "desired_capabilities":
                desired,

            "candidates":
                candidates,

            "status":
                (
                    "ROUTE_FOUND"
                    if candidates
                    else
                    "NO_OPERATIONAL_CAPABILITY_ROUTE"
                ),
        }


# ============================================================
# GAME PIPELINE
# ============================================================

class GamePipeline:

    def __init__(
        self,
        registry: CapabilityRegistry,
        executor: ComponentExecutor,
    ):

        self.registry = (
            registry
        )

        self.executor = (
            executor
        )

        self.artifact_verifier = (
            ArtifactVerifier()
        )

        self.publication_verifier = (
            PublicationVerifier()
        )

    @staticmethod
    def _prefer_number(
        providers: List[
            Dict[str, Any]
        ],
        number: str,
    ) -> List[Dict[str, Any]]:

        return sorted(
            providers,
            key=lambda item: (
                0
                if item.get(
                    "number"
                )
                ==
                number
                else
                1,
                item.get(
                    "filename",
                    "",
                ),
            ),
        )

    def run(
        self,
        command: str,
        request: Dict[str, Any],
        job_id: str,
        owner: str,
    ) -> Dict[str, Any]:

        executors = (
            self._prefer_number(
                self.registry.providers(
                    "GAME"
                ),
                "03",
            )
        )

        if not executors:

            return {
                "success":
                    False,

                "status":
                    "REAL_GAME_EXECUTOR_UNAVAILABLE",
            }

        build = (
            self.executor
            .execute_provider(
                executors[
                    0
                ],
                command,
                request,
                job_id,
                owner,
            )
        )

        if not build.get(
            "success"
        ):

            return {
                "success":
                    False,

                "status":
                    "REAL_GAME_EXECUTION_FAILED",

                "executor":
                    build,
            }

        artifact = (
            self.artifact_verifier
            .verify(
                build
            )
        )

        if not artifact.get(
            "success"
        ):

            return {
                "success":
                    False,

                "status":
                    "ARTIFACT_VERIFICATION_FAILED",

                "executor":
                    build,

                "artifact_verification":
                    artifact,
            }

        publishers = (
            self._prefer_number(
                self.registry.providers(
                    "PUBLISH"
                ),
                "04",
            )
        )

        if not publishers:

            return {
                "success":
                    False,

                "status":
                    "OFFICIAL_PLATFORM_BRIDGE_UNAVAILABLE",

                "artifact":
                    artifact,
            }

        publish_request = dict(
            request
        )

        publish_request.update(
            {
                "artifact":
                    artifact[
                        "artifact"
                    ],

                "artifact_path":
                    artifact[
                        "artifact"
                    ],

                "game_dir":
                    artifact[
                        "artifact"
                    ],

                "build_path":
                    artifact[
                        "artifact"
                    ],
            }
        )

        published = (
            self.executor
            .execute_provider(
                publishers[
                    0
                ],
                command,
                publish_request,
                job_id,
                owner,
            )
        )

        if not published.get(
            "success"
        ):

            return {
                "success":
                    False,

                "status":
                    "OFFICIAL_PLATFORM_PUBLISH_FAILED",

                "artifact":
                    artifact,

                "publisher":
                    published,
            }

        publication = (
            self.publication_verifier
            .verify(
                published
            )
        )

        if not publication.get(
            "success"
        ):

            return {
                "success":
                    False,

                "status":
                    "FINAL_PUBLICATION_VALIDATION_FAILED",

                "artifact":
                    artifact,

                "publisher":
                    published,

                "publication":
                    publication,
            }

        return {
            "success":
                True,

            "status":
                "GAME_BUILT_AND_PUBLISHED",

            "artifact":
                artifact,

            "executor":
                build,

            "publisher":
                published,

            "publication":
                publication,
        }


# ============================================================
# OWNER DASHBOARD
# ============================================================

class OwnerDashboard:

    def __init__(
        self,
        security: SecurityCenter,
    ):

        self.security = (
            security
        )

        self.path = (
            DASHBOARD_DIR
            /
            "owner-status.json"
        )

    def update(
        self,
        **values: Any,
    ) -> Dict[str, Any]:

        current = (
            read_json(
                self.path,
                {},
            )
            or
            {}
        )

        current.update(
            values
        )

        current[
            "updated_at"
        ] = utc_now()

        write_json(
            self.path,
            current,
        )

        return current

    def snapshot(
        self,
    ) -> Dict[str, Any]:

        data = (
            read_json(
                self.path,
                {},
            )
            or
            {}
        )

        data[
            "security_events"
        ] = self.security.recent(
            100
        )

        data[
            "security_latest_scan"
        ] = (
            read_json(
                SECURITY_DIR
                /
                "latest-scan.json",
                {},
            )
            or
            {}
        )

        data[
            "monitor_latest"
        ] = (
            read_json(
                MONITOR_DIR
                /
                "latest.json",
                {},
            )
            or
            {}
        )

        data[
            "ai_connection"
        ] = (
            read_json(
                AI_CONNECTION_FILE,
                {},
            )
            or
            {}
        )

        data[
            "capability_registry"
        ] = (
            read_json(
                REGISTRY_DIR
                /
                "capabilities.json",
                {},
            )
            or
            {}
        )

        data[
            "updated_at"
        ] = utc_now()

        return data


# ============================================================
# DASHBOARD HTML
# ============================================================

DASHBOARD_HTML = """
<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MAJD Sovereign Owner Dashboard</title>
<style>
body{
    font-family:system-ui,-apple-system,sans-serif;
    background:#0b1020;
    color:#eef2ff;
    margin:0;
    padding:20px
}
h1{margin-top:0}
.grid{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(260px,1fr));
    gap:12px
}
.card{
    background:#151c32;
    border:1px solid #2a365f;
    border-radius:14px;
    padding:14px
}
.ok{color:#51e39b}
.bad{color:#ff7d8d}
.warn{color:#ffd166}
pre{
    white-space:pre-wrap;
    word-break:break-word;
    font-size:12px
}
.muted{color:#9aa7c7}
</style>
</head>
<body>
<h1>لوحة مالك مجد السيادية</h1>
<div id="updated" class="muted"></div>

<div class="grid">

<div class="card">
<h3>حالة العقل</h3>
<pre id="brain"></pre>
</div>

<div class="card">
<h3>الذكاء الاصطناعي</h3>
<pre id="ai"></pre>
</div>

<div class="card">
<h3>القدرات التشغيلية</h3>
<pre id="caps"></pre>
</div>

<div class="card">
<h3>الأمن</h3>
<pre id="security"></pre>
</div>

<div class="card">
<h3>آخر نتيجة</h3>
<pre id="result"></pre>
</div>

<div class="card">
<h3>المراقبة</h3>
<pre id="monitor"></pre>
</div>

</div>

<script>
async function refresh(){
    try{
        const r=await fetch('/api/status',{cache:'no-store'});
        const d=await r.json();

        document.getElementById('updated').textContent=
            'آخر تحديث: '+(d.updated_at||'');

        document.getElementById('brain').textContent=
            JSON.stringify({
                status:d.status,
                operation_id:d.operation_id,
                command:d.command,
                command_type:d.command_type
            },null,2);

        document.getElementById('ai').textContent=
            JSON.stringify(d.ai_connection||{},null,2);

        const c=d.capability_registry||{};

        document.getElementById('caps').textContent=
            JSON.stringify({
                operational:c.operational,
                unavailable:c.unavailable,
                missing_component_numbers:c.missing_component_numbers
            },null,2);

        document.getElementById('security').textContent=
            JSON.stringify({
                latest_scan:d.security_latest_scan,
                events:(d.security_events||[]).slice(-10)
            },null,2);

        document.getElementById('result').textContent=
            JSON.stringify(d.result||{},null,2);

        document.getElementById('monitor').textContent=
            JSON.stringify(d.monitor_latest||{},null,2);

    }catch(e){
        document.getElementById('brain').textContent=String(e)
    }
}
refresh();
setInterval(refresh,3000);
</script>
</body>
</html>
"""


# ============================================================
# DASHBOARD HTTP SERVER
# ============================================================

class DashboardServer:

    def __init__(
        self,
        dashboard: OwnerDashboard,
        host: str = "127.0.0.1",
        port: int = 8765,
    ):

        self.dashboard = (
            dashboard
        )

        self.host = (
            host
        )

        self.port = int(
            port
        )

    def serve_forever(
        self,
    ) -> None:

        dashboard = (
            self.dashboard
        )

        class Handler(
            BaseHTTPRequestHandler
        ):

            def _send(
                self,
                status: int,
                content_type: str,
                body: bytes,
            ) -> None:

                self.send_response(
                    status
                )

                self.send_header(
                    "Content-Type",
                    content_type,
                )

                self.send_header(
                    "Cache-Control",
                    "no-store",
                )

                self.send_header(
                    "Content-Length",
                    str(
                        len(
                            body
                        )
                    ),
                )

                self.end_headers()

                self.wfile.write(
                    body
                )

            def do_GET(
                self,
            ) -> None:

                if (
                    self.path
                    ==
                    "/"
                    or
                    self.path.startswith(
                        "/?"
                    )
                ):

                    self._send(
                        200,
                        "text/html; charset=utf-8",
                        DASHBOARD_HTML.encode(
                            "utf-8"
                        ),
                    )

                    return

                if self.path == "/health":

                    body = json.dumps(
                        {
                            "success":
                                True,

                            "status":
                                "healthy",

                            "service":
                                "majd-owner-dashboard",

                            "version":
                                VERSION,
                        }
                    ).encode(
                        "utf-8"
                    )

                    self._send(
                        200,
                        "application/json; charset=utf-8",
                        body,
                    )

                    return

                if self.path == "/api/status":

                    body = json.dumps(
                        dashboard.snapshot(),
                        ensure_ascii=False,
                        default=str,
                    ).encode(
                        "utf-8"
                    )

                    self._send(
                        200,
                        "application/json; charset=utf-8",
                        body,
                    )

                    return

                self._send(
                    404,
                    "application/json; charset=utf-8",
                    (
                        b'{"success":false,'
                        b'"status":"NOT_FOUND"}'
                    ),
                )

            def log_message(
                self,
                format: str,
                *args: Any,
            ) -> None:

                return

        server = (
            ThreadingHTTPServer(
                (
                    self.host,
                    self.port,
                ),
                Handler,
            )
        )

        server.serve_forever()


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

    error: Optional[
        str
    ] = None


# ============================================================
# MASTERMIND
# ============================================================

class Mastermind:

    def __init__(
        self,
        owner: str = DEFAULT_OWNER,
        max_repair_attempts: int = MAX_REPAIR_ATTEMPTS,
        auto_connect_ai: bool = True,
    ):

        self.owner = (
            owner
        )

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

        self.process = (
            ProcessExecutor()
        )

        self.python_checker = (
            PythonChecker(
                self.process
            )
        )

        self.discovery = (
            ComponentDiscovery()
        )

        self.registry = (
            CapabilityRegistry(
                self.discovery
            )
        )

        self.registry.build()

        self.router = (
            CapabilityRouter(
                self.registry
            )
        )

        self.component_executor = (
            ComponentExecutor()
        )

        self.game_pipeline = (
            GamePipeline(
                self.registry,
                self.component_executor,
            )
        )

        self.classifier = (
            CommandClassifier()
        )

        self.diagnostics = (
            DiagnosticEngine()
        )

        self.ai_connector = (
            AutoAIConnector(
                self.logger,
                self.process,
            )
        )

        self.ai = (
            LocalAIAdapter(
                self.ai_connector,
                self.logger,
            )
        )

        if auto_connect_ai:

            self.ai.ensure_connected(
                force=False
            )

        self.runtime06 = (
            Runtime06Bridge(
                self.discovery,
                self.logger,
            )
        )

        self.repair_engine = (
            AutonomousRepairEngine(
                self.operation_id,
                self.logger,
                self.python_checker,
                self.ai,
                self.runtime06,
            )
        )

        self.security = (
            SecurityCenter(
                self.logger,
                self.process,
            )
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

        self.dashboard = (
            OwnerDashboard(
                self.security
            )
        )

    # --------------------------------------------------------
    # STATE
    # --------------------------------------------------------

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

        self.logger.log(
            event_type,
            data,
        )

        self._save_state(
            state
        )

    # --------------------------------------------------------
    # REGISTRY
    # --------------------------------------------------------

    def refresh_registry(
        self,
    ) -> Dict[str, Any]:

        result = (
            self.registry
            .build()
        )

        self.router = (
            CapabilityRouter(
                self.registry
            )
        )

        self.game_pipeline = (
            GamePipeline(
                self.registry,
                self.component_executor,
            )
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

        components = (
            self.discovery
            .discover(
                runtime_import=True
            )
        )

        registry = (
            self.refresh_registry()
        )

        ai_status = (
            self.ai.status()
        )

        runtime06 = (
            self.runtime06
            .verification()
        )

        import_failures: List[
            Dict[str, Any]
        ] = []

        for number in OFFICIAL_NUMBERS:

            records = (
                components[
                    "components"
                ].get(
                    number,
                    [],
                )
            )

            if (
                records
                and
                not any(
                    record.get(
                        "importable"
                    )
                    for record
                    in records
                )
            ):

                import_failures.append(
                    {
                        "number":
                            number,

                        "files":
                            [
                                record.get(
                                    "filename"
                                )
                                for record
                                in records
                            ],

                        "errors":
                            [
                                record.get(
                                    "error"
                                )
                                for record
                                in records
                                if record.get(
                                    "error"
                                )
                            ],
                    }
                )

        missing = (
            components.get(
                "missing_numbers",
                [],
            )
        )

        ai_ok = (
            ai_status.get(
                "connected"
            )
            is True
            or
            not REQUIRE_AI
        )

        success = bool(
            not missing
            and
            compile_report.get(
                "success"
            )
            is True
            and
            not import_failures
            and
            ai_ok
        )

        if missing:

            status = (
                "FACTORY_COMPONENTS_MISSING"
            )

        elif not compile_report.get(
            "success"
        ):

            status = (
                "FACTORY_PYTHON_INVALID"
            )

        elif import_failures:

            status = (
                "FACTORY_IMPORT_FAILURE"
            )

        elif not ai_ok:

            status = (
                "FACTORY_AI_NOT_CONNECTED"
            )

        else:

            status = (
                "FACTORY_VERIFIED"
            )

        return {
            "success":
                success,

            "status":
                status,

            "python_compile":
                compile_report,

            "components":
                components,

            "capability_registry":
                registry,

            "import_failures":
                import_failures,

            "ai":
                ai_status,

            "runtime06":
                runtime06,
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

        classification = (
            self.classifier
            .classify(
                command
            )
        )

        data.setdefault(
            "type",
            classification[
                "type"
            ],
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

        data[
            "classification"
        ] = classification

        return data

    # --------------------------------------------------------
    # PLAN
    # --------------------------------------------------------

    def build_plan(
        self,
        request: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        request_type = str(
            request.get(
                "type"
            )
            or
            "GENERAL_OWNER_COMMAND"
        ).upper()

        common = [
            "DISCOVER",
            "VALIDATE",
            "PLAN",
        ]

        if (
            request_type
            ==
            "CONNECT_AI"
        ):

            stages = [
                "DISCOVER_AI",
                "HEALTH_CHECK",
                "DISCOVER_MODELS",
                "REAL_PROMPT_TEST",
                "SAVE_CONNECTION",
            ]

        elif (
            request_type
            ==
            "CREATE_GAME"
        ):

            stages = (
                common
                +
                [
                    "BUILD",
                    "VERIFY_ARTIFACT",
                    "PUBLISH",
                    "VERIFY_PUBLICATION",
                ]
            )

        elif request_type in {
            "REPAIR",
            "INSPECT",
        }:

            stages = (
                common
                +
                [
                    "DIAGNOSE",
                    "BACKUP",
                    "REPAIR",
                    "TEST",
                    "VERIFY",
                    "RETRY_IF_REQUIRED",
                ]
            )

        else:

            stages = (
                common
                +
                [
                    "ROUTE",
                    "EXECUTE",
                    "VERIFY",
                    "REPAIR_IF_REQUIRED",
                    "FINAL_VERIFY",
                ]
            )

        return [
            {
                "stage":
                    stage,

                "status":
                    "PENDING",
            }

            for stage
            in stages
        ]

    # --------------------------------------------------------
    # REPAIR FAILURE
    # --------------------------------------------------------

    def repair_failure(
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

        self._event(
            state,
            "DIAGNOSIS",
            diagnosis,
        )

        self.dashboard.update(
            status="REPAIRING",
            operation_id=self.operation_id,
            diagnosis=diagnosis,
        )

        repair = (
            self.repair_engine
            .repair(
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
    # REPAIR CYCLE
    # --------------------------------------------------------

    def run_repair_cycle(
        self,
        state: MastermindState,
    ) -> Dict[str, Any]:

        attempts: List[
            Dict[str, Any]
        ] = []

        for attempt in range(
            1,
            self.max_repair_attempts
            +
            1,
        ):

            state.attempts = (
                attempt
            )

            state.status = (
                "DIAGNOSING"
            )

            self._save_state(
                state
            )

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

            if inspection.get(
                "success"
            ):

                return {
                    "success":
                        True,

                    "status":
                        "FACTORY_VERIFIED",

                    "attempt":
                        attempt,

                    "inspection":
                        inspection,

                    "attempts":
                        attempts,
                }

            failure = {
                "stage":
                    "FACTORY_INSPECTION",

                "result":
                    inspection,
            }

            repair = (
                self.repair_failure(
                    failure,
                    state,
                )
            )

            attempts.append(
                {
                    "attempt":
                        attempt,

                    "failure":
                        failure,

                    "repair":
                        repair,
                }
            )

            self.dashboard.update(
                status="TESTING",
                operation_id=self.operation_id,
                attempt=attempt,
            )

            if (
                inspection.get(
                    "ai",
                    {},
                ).get(
                    "connected"
                )
                is not True
            ):

                self.ai.ensure_connected(
                    force=True
                )

            self.refresh_registry()

            recheck = (
                self.inspect_factory()
            )

            self._event(
                state,
                "REPAIR_RECHECK",
                recheck,
            )

            if recheck.get(
                "success"
            ):

                return {
                    "success":
                        True,

                    "status":
                        "REPAIR_VERIFIED",

                    "attempt":
                        attempt,

                    "repair":
                        repair,

                    "inspection":
                        recheck,

                    "attempts":
                        attempts,
                }

        return {
            "success":
                False,

            "status":
                "MAX_AUTONOMOUS_REPAIR_ATTEMPTS_REACHED",

            "attempts":
                attempts,

            "inspection":
                self.inspect_factory(),
        }

    # --------------------------------------------------------
    # ROUTED CAPABILITY
    # --------------------------------------------------------

    def execute_routed(
        self,
        command: str,
        request: Dict[str, Any],
        state: MastermindState,
    ) -> Dict[str, Any]:

        command_type = str(
            request.get(
                "type"
            )
            or
            "GENERAL_OWNER_COMMAND"
        ).upper()

        route = (
            self.router
            .route(
                command_type
            )
        )

        self._event(
            state,
            "CAPABILITY_ROUTE",
            route,
        )

        if not route.get(
            "success"
        ):

            return {
                "success":
                    False,

                "status":
                    "CAPABILITY_NOT_CONNECTED",

                "command_type":
                    command_type,

                "route":
                    route,
            }

        failures: List[
            Dict[str, Any]
        ] = []

        for provider in (
            route[
                "candidates"
            ]
        ):

            result = (
                self.component_executor
                .execute_provider(
                    provider,
                    command,
                    request,
                    self.operation_id,
                    self.owner,
                )
            )

            self._event(
                state,
                "COMPONENT_RESULT",
                result,
            )

            if result.get(
                "success"
            ):

                return {
                    "success":
                        True,

                    "status":
                        "COMMAND_EXECUTED_AND_VERIFIED",

                    "provider":
                        provider,

                    "result":
                        result,
                }

            failures.append(
                {
                    "provider":
                        provider,

                    "result":
                        result,
                }
            )

        return {
            "success":
                False,

            "status":
                "ALL_CAPABILITY_PROVIDERS_FAILED",

            "failures":
                failures,
        }

    # --------------------------------------------------------
    # AI PLAN FOR UNKNOWN OWNER COMMAND
    # --------------------------------------------------------

    def _ai_plan_general_command(
        self,
        command: str,
    ) -> Optional[
        Dict[str, Any]
    ]:

        if not self.ai.available:

            self.ai.ensure_connected(
                force=False
            )

        if not self.ai.available:

            return None

        available = sorted(
            self.registry.report.get(
                "operational",
                [],
            )
        )

        answer = self.ai.ask(
            (
                "You are the MAJD sovereign command planner. "
                "Return JSON only."
            ),
            (
                "Choose one operational capability for the owner objective. "
                "Return exactly: "
                "{\"capability\":\"NAME\","
                "\"rewritten_command\":\"...\","
                "\"reason\":\"...\"}. "
                f"Allowed capabilities: {json.dumps(available)}\n"
                f"Owner objective: {command}"
            ),
        )

        if not answer:

            return None

        try:

            cleaned = re.sub(
                r"^```(?:json)?\s*",
                "",
                answer.strip(),
            )

            cleaned = re.sub(
                r"\s*```$",
                "",
                cleaned,
            )

            data = json.loads(
                cleaned
            )

            capability = str(
                data.get(
                    "capability"
                )
                or
                ""
            ).upper()

            if capability not in available:

                return None

            return data

        except Exception:

            return None

    # --------------------------------------------------------
    # GENERAL OWNER COMMAND
    # --------------------------------------------------------

    def execute_general_owner_command(
        self,
        command: str,
        request: Dict[str, Any],
        state: MastermindState,
    ) -> Dict[str, Any]:

        plan = (
            self._ai_plan_general_command(
                command
            )
        )

        if plan:

            providers = (
                self.registry.providers(
                    str(
                        plan[
                            "capability"
                        ]
                    )
                )
            )

            for provider in providers:

                result = (
                    self.component_executor
                    .execute_provider(
                        provider,
                        str(
                            plan.get(
                                "rewritten_command"
                            )
                            or
                            command
                        ),
                        request,
                        self.operation_id,
                        self.owner,
                    )
                )

                self._event(
                    state,
                    "AI_PLANNED_PROVIDER_RESULT",
                    result,
                )

                if result.get(
                    "success"
                ):

                    return {
                        "success":
                            True,

                        "status":
                            "GENERAL_COMMAND_COMPLETED",

                        "plan":
                            plan,

                        "provider":
                            provider,

                        "result":
                            result,
                    }

        providers = (
            self.registry
            .generic_providers(
                (
                    "02",
                    "05",
                    "06",
                )
            )
        )

        failures: List[
            Dict[str, Any]
        ] = []

        for provider in providers:

            result = (
                self.component_executor
                .execute_provider(
                    provider,
                    command,
                    request,
                    self.operation_id,
                    self.owner,
                )
            )

            self._event(
                state,
                "GENERAL_COMMAND_PROVIDER",
                result,
            )

            if result.get(
                "success"
            ):

                return {
                    "success":
                        True,

                    "status":
                        "GENERAL_COMMAND_COMPLETED",

                    "provider":
                        provider,

                    "result":
                        result,
                }

            failures.append(
                {
                    "provider":
                        provider,

                    "result":
                        result,
                }
            )

        return {
            "success":
                False,

            "status":
                "OWNER_COMMAND_NOT_EXECUTABLE",

            "failures":
                failures,

            "ai":
                self.ai.status(),

            "operational_capabilities":
                sorted(
                    self.registry.report.get(
                        "operational",
                        [],
                    )
                ),
        }

    # --------------------------------------------------------
    # REBIND OPERATION
    # --------------------------------------------------------

    def _rebind_operation(
        self,
        job_id: str,
    ) -> None:

        self.operation_id = str(
            job_id
        )

        self.logger = (
            AuditLogger(
                self.operation_id
            )
        )

        self.ai_connector = (
            AutoAIConnector(
                self.logger,
                self.process,
            )
        )

        self.ai = (
            LocalAIAdapter(
                self.ai_connector,
                self.logger,
            )
        )

        self.ai.ensure_connected(
            force=False
        )

        self.runtime06 = (
            Runtime06Bridge(
                self.discovery,
                self.logger,
            )
        )

        self.repair_engine = (
            AutonomousRepairEngine(
                self.operation_id,
                self.logger,
                self.python_checker,
                self.ai,
                self.runtime06,
            )
        )

        self.security = (
            SecurityCenter(
                self.logger,
                self.process,
            )
        )

        self.legal = (
            ElectronicLegalAssistant(
                self.ai,
                self.logger,
            )
        )

        self.dashboard = (
            OwnerDashboard(
                self.security
            )
        )

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

            self.owner = str(
                owner
            )

        if job_id:

            self._rebind_operation(
                str(
                    job_id
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
                    "EMPTY_COMMAND",
            }

        normalized = (
            self.normalize_request(
                command,
                supplied_request,
            )
        )

        request_type = str(
            normalized.get(
                "type"
            )
            or
            "GENERAL_OWNER_COMMAND"
        ).upper()

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

            command_type=
                request_type,
        )

        state.plan = (
            self.build_plan(
                normalized
            )
        )

        self._save_state(
            state
        )

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
            ai=self.ai.status(),
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

            self.refresh_registry()

            if request_type in {
                "CONTENT",
                "SOCIAL",
                "LIVE",
                "ADS",
            }:

                safety = (
                    self.content_policy
                    .inspect_request(
                        command,
                        request_type,
                        normalized,
                        self.registry,
                        self.component_executor,
                        self.operation_id,
                        self.owner,
                    )
                )

                self._event(
                    state,
                    "CONTENT_SAFETY_CHECK",
                    safety,
                )

                if not safety.get(
                    "success"
                ):

                    result = {
                        "success":
                            False,

                        "status":
                            "CONTENT_POLICY_BLOCKED",

                        "policy":
                            safety,
                    }

                    state.result = (
                        result
                    )

                    state.status = (
                        result[
                            "status"
                        ]
                    )

                    self._save_state(
                        state
                    )

                    self.dashboard.update(
                        status="FAILED",
                        operation_id=self.operation_id,
                        result=result,
                    )

                    return result

            # ------------------------------------------------
            # CONNECT AI
            # ------------------------------------------------

            if (
                request_type
                ==
                "CONNECT_AI"
            ):

                ai_result = (
                    self.ai
                    .ensure_connected(
                        force=True
                    )
                )

                result = {
                    "success":
                        (
                            ai_result.get(
                                "connected"
                            )
                            is True
                        ),

                    "status":
                        (
                            "AI_CONNECTED_AND_VERIFIED"
                            if ai_result.get(
                                "connected"
                            )
                            else
                            "AI_ENGINE_NOT_FOUND"
                        ),

                    "ai":
                        ai_result,
                }

            # ------------------------------------------------
            # STATUS
            # ------------------------------------------------

            elif (
                request_type
                ==
                "STATUS"
            ):

                result = {
                    "success":
                        True,

                    "status":
                        "STATUS_RETRIEVED",

                    "dashboard":
                        self.dashboard.snapshot(),

                    "factory":
                        self.inspect_factory(),
                }

            # ------------------------------------------------
            # INSPECT / REPAIR
            # ------------------------------------------------

            elif request_type in {
                "REPAIR",
                "INSPECT",
            }:

                result = (
                    self.run_repair_cycle(
                        state
                    )
                )

            # ------------------------------------------------
            # LEGAL
            # ------------------------------------------------

            elif (
                request_type
                ==
                "LEGAL"
            ):

                result = (
                    self.legal
                    .execute(
                        command,
                        normalized,
                    )
                )

            # ------------------------------------------------
            # SECURITY
            # ------------------------------------------------

            elif (
                request_type
                ==
                "SECURITY"
            ):

                result = {
                    "success":
                        True,

                    "status":
                        "SECURITY_STATUS_RETRIEVED",

                    "scan":
                        self.security.scan(),

                    "recent_events":
                        self.security.recent(
                            100
                        ),

                    "factory":
                        self.inspect_factory(),
                }

            # ------------------------------------------------
            # GAME
            # ------------------------------------------------

            elif (
                request_type
                ==
                "CREATE_GAME"
            ):

                self.dashboard.update(
                    status="RUNNING",
                    stage="BUILD",
                    operation_id=self.operation_id,
                )

                result = (
                    self.game_pipeline
                    .run(
                        command,
                        normalized,
                        self.operation_id,
                        self.owner,
                    )
                )

                if not result.get(
                    "success"
                ):

                    repair = (
                        self.repair_failure(
                            result,
                            state,
                        )
                    )

                    if repair.get(
                        "success"
                    ):

                        self.refresh_registry()

                        result = (
                            self.game_pipeline
                            .run(
                                command,
                                normalized,
                                self.operation_id,
                                self.owner,
                            )
                        )

            # ------------------------------------------------
            # KNOWN ROUTED CAPABILITIES
            # ------------------------------------------------

            elif request_type in {
                "CONTENT",
                "SOCIAL",
                "LIVE",
                "PAYMENTS",
                "ADS",
            }:

                result = (
                    self.execute_routed(
                        command,
                        normalized,
                        state,
                    )
                )

                if not result.get(
                    "success"
                ):

                    repair = (
                        self.repair_failure(
                            result,
                            state,
                        )
                    )

                    if repair.get(
                        "success"
                    ):

                        self.refresh_registry()

                        result = (
                            self.execute_routed(
                                command,
                                normalized,
                                state,
                            )
                        )

            # ------------------------------------------------
            # GENERAL OWNER OBJECTIVE
            # ------------------------------------------------

            else:

                result = (
                    self.execute_general_owner_command(
                        command,
                        normalized,
                        state,
                    )
                )

            state.result = (
                result
            )

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
                    "VERIFIED"
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

            self.dashboard.update(
                status=(
                    "VERIFIED"
                    if state.success
                    else
                    "FAILED"
                ),
                operation_id=self.operation_id,
                command=command,
                command_type=request_type,
                result=result,
                finished_at=utc_now(),
                ai=self.ai.status(),
                operational_capabilities=
                    sorted(
                        self.registry.report.get(
                            "operational",
                            [],
                        )
                    ),
                unavailable_capabilities=
                    sorted(
                        self.registry.report.get(
                            "unavailable",
                            [],
                        )
                    ),
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
                    truncate(
                        traceback.format_exc()
                    ),
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

            self.dashboard.update(
                status="FAILED",
                operation_id=self.operation_id,
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

        self.owner = (
            owner
        )

        self.interval = max(
            30,
            int(
                interval
            ),
        )

        self.stop_event = (
            threading.Event()
        )

    def stop(
        self,
    ) -> None:

        self.stop_event.set()

    def run_forever(
        self,
    ) -> None:

        while not self.stop_event.is_set():

            mastermind = (
                Mastermind(
                    owner=self.owner,
                    auto_connect_ai=True,
                )
            )

            security = (
                mastermind.security
                .scan()
            )

            inspection = (
                mastermind
                .inspect_factory()
            )

            snapshot = {
                "time":
                    utc_now(),

                "inspection":
                    inspection,

                "security":
                    security,

                "ai":
                    mastermind.ai.status(),
            }

            write_json(
                MONITOR_DIR
                /
                "latest.json",
                snapshot,
            )

            mastermind.dashboard.update(
                status="MONITORING",
                monitor=snapshot,
                ai=mastermind.ai.status(),
                operational_capabilities=
                    sorted(
                        mastermind.registry.report.get(
                            "operational",
                            [],
                        )
                    ),
            )

            if not inspection.get(
                "success"
            ):

                repair_state = (
                    MastermindState(
                        operation_id=
                            mastermind.operation_id,

                        owner=
                            self.owner,

                        command=
                            "AUTONOMOUS_MONITOR_REPAIR",

                        started_at=
                            utc_now(),

                        updated_at=
                            utc_now(),

                        status=
                            "DIAGNOSING",

                        command_type=
                            "REPAIR",
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

    parser = argparse.ArgumentParser(
        description=(
            "MAJD SOVEREIGN AUTONOMOUS MASTERMIND"
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
        "--connect-ai",
        action="store_true",
    )

    parser.add_argument(
        "--ai-status",
        action="store_true",
    )

    parser.add_argument(
        "--security-scan",
        action="store_true",
    )

    parser.add_argument(
        "--monitor",
        action="store_true",
    )

    parser.add_argument(
        "--dashboard-server",
        action="store_true",
    )

    parser.add_argument(
        "--dashboard-host",
        default=os.getenv(
            "MAJD_DASHBOARD_HOST",
            "127.0.0.1",
        ),
    )

    parser.add_argument(
        "--dashboard-port",
        type=int,
        default=int(
            os.getenv(
                "MAJD_DASHBOARD_PORT",
                "8765",
            )
        ),
    )

    args = (
        parser.parse_args()
    )

    # --------------------------------------------------------
    # DISCOVERY
    # --------------------------------------------------------

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

        return (
            0
            if result.get(
                "success"
            )
            else
            1
        )

    # --------------------------------------------------------
    # CAPABILITIES
    # --------------------------------------------------------

    if args.capabilities:

        registry = (
            CapabilityRegistry(
                ComponentDiscovery()
            )
        )

        result = (
            registry.build()
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

    mastermind = (
        Mastermind(
            owner=args.owner,
            auto_connect_ai=(
                not args.connect_ai
            ),
        )
    )

    # --------------------------------------------------------
    # CONNECT AI
    # --------------------------------------------------------

    if args.connect_ai:

        result = (
            mastermind.ai
            .ensure_connected(
                force=True
            )
        )

        output = {
            "success":
                (
                    result.get(
                        "connected"
                    )
                    is True
                ),

            "status":
                (
                    "AI_CONNECTED_AND_VERIFIED"
                    if result.get(
                        "connected"
                    )
                    else
                    "AI_ENGINE_NOT_FOUND"
                ),

            "ai":
                result,
        }

        print(
            json.dumps(
                output,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )

        return (
            0
            if output[
                "success"
            ]
            else
            1
        )

    # --------------------------------------------------------
    # AI STATUS
    # --------------------------------------------------------

    if args.ai_status:

        result = (
            mastermind.ai
            .ensure_connected(
                force=False
            )
        )

        output = {
            "success":
                (
                    result.get(
                        "connected"
                    )
                    is True
                ),

            "ai":
                result,
        }

        print(
            json.dumps(
                output,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )

        return (
            0
            if result.get(
                "connected"
            )
            else
            1
        )

    # --------------------------------------------------------
    # SECURITY SCAN
    # --------------------------------------------------------

    if args.security_scan:

        result = (
            mastermind.security
            .scan()
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

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

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

            "ai":
                mastermind.ai.status(),

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

    # --------------------------------------------------------
    # INSPECT
    # --------------------------------------------------------

    if args.inspect:

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

    # --------------------------------------------------------
    # DASHBOARD SERVER
    # --------------------------------------------------------

    if args.dashboard_server:

        mastermind.dashboard.update(
            system=SYSTEM_NAME,
            mastermind=MASTERMIND_NAME,
            version=VERSION,
            status="DASHBOARD_RUNNING",
            ai=mastermind.ai.status(),
        )

        print(
            json.dumps(
                {
                    "success":
                        True,

                    "status":
                        "OWNER_DASHBOARD_SERVER_STARTED",

                    "host":
                        args.dashboard_host,

                    "port":
                        args.dashboard_port,
                },
                ensure_ascii=False,
                indent=2,
            )
        )

        DashboardServer(
            mastermind.dashboard,
            args.dashboard_host,
            args.dashboard_port,
        ).serve_forever()

        return 0

    # --------------------------------------------------------
    # MONITOR
    # --------------------------------------------------------

    if args.monitor:

        print(
            json.dumps(
                {
                    "success":
                        True,

                    "status":
                        "CONTINUOUS_MONITOR_STARTED",

                    "interval_seconds":
                        MONITOR_INTERVAL,
                },
                ensure_ascii=False,
                indent=2,
            )
        )

        monitor = (
            ContinuousMonitor(
                owner=args.owner
            )
        )

        try:

            monitor.run_forever()

        except KeyboardInterrupt:

            monitor.stop()

        return 0

    # --------------------------------------------------------
    # OWNER COMMAND
    # --------------------------------------------------------

    command = " ".join(
        args.command
    ).strip()

    if not command:

        command = input(
            "👑 OWNER > "
        ).strip()

    result = (
        mastermind.run(
            command=command,
            owner=args.owner,
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

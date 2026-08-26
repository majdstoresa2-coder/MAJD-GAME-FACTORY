#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MAJD-FULL-EXECUTION-RUNTIME-06.py
01 mastermind, 02 sovereign company/owner center, 03 real executor, 04 platform bridge.
06 runs permanently, reads Company-02 directly, queues every real unavailable capability,
verifies BEFORE/AFTER, repairs safe dependencies, and rolls back only real regressions.
"""

from __future__ import annotations

import argparse
import ast
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
import urllib.request
import uuid

from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping


ROOT = Path(__file__).resolve().parent

F01 = ROOT / "MAJD-AI-MASTERMIND-01.py"
F02C = ROOT / "MAJD-AI-SOVEREIGN-COMPANY-02.py"
F02O = ROOT / "MAJD-OWNER-COMMAND-CENTER-02.py"
F03 = ROOT / "MAJD-REAL-GAME-EXECUTOR-03.py"
F04 = ROOT / "MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py"

STATE = ROOT / "majd_factory_state"
RUNTIME_DIR = STATE / "runtime"
AUTO = STATE / "autonomous"
AUDIT = STATE / "audit"
REPORT = STATE / "reports"
BACKUP = STATE / "runtime_backups"
QUEUE = STATE / "work_queue"
OUTPUT = ROOT / "majd_game_output"

for path in (
    STATE,
    RUNTIME_DIR,
    AUTO,
    AUDIT,
    REPORT,
    BACKUP,
    QUEUE,
    OUTPUT,
):
    path.mkdir(
        parents=True,
        exist_ok=True,
    )

STATE_FILE = AUTO / "state.json"
REPORT_FILE = REPORT / "autonomous-latest.json"
AUDIT_FILE = AUDIT / "autonomous-runtime.jsonl"
QUEUE_FILE = QUEUE / "capabilities.json"
PID_FILE = AUTO / "majd-autonomous-runtime.pid"

SERVICE_NAME = "majd-autonomous.service"
SERVICE_FILE = Path("/etc/systemd/system") / SERVICE_NAME

SYSTEM = "MAJD-GAME-FACTORY"
RUNTIME = "MAJD-FULL-EXECUTION-RUNTIME"
VERSION = "8.1.0-DIRECT-COMPANY-SMART-VERIFY"
OWNER = "MAJD"

PLATFORM = os.getenv(
    "MAJD_OFFICIAL_PLATFORM",
    "https://majd.shop",
).rstrip("/")

LOCAL_HEALTH = os.getenv(
    "MAJD_LOCAL_API_HEALTH_URL",
    "http://127.0.0.1:8000/health",
)

CYCLE_SECONDS = max(
    30,
    int(
        os.getenv(
            "MAJD_AUTONOMOUS_CYCLE_SECONDS",
            "300",
        )
    ),
)

MAX_BATCH = max(
    1,
    int(
        os.getenv(
            "MAJD_MAX_CAPABILITIES_PER_CYCLE",
            "12",
        )
    ),
)

MAX_ATTEMPTS = max(
    1,
    int(
        os.getenv(
            "MAJD_MAX_REPAIR_ATTEMPTS",
            "3",
        )
    ),
)

HTTP_TIMEOUT = max(
    2,
    int(
        os.getenv(
            "MAJD_HTTP_TIMEOUT",
            "12",
        )
    ),
)

ALLOW_DEP_INSTALL = (
    os.getenv(
        "MAJD_ALLOW_PYTHON_PACKAGE_INSTALL",
        "true",
    ).lower()
    in {
        "1",
        "true",
        "yes",
        "on",
    }
)

PROACTIVE = (
    os.getenv(
        "MAJD_PROACTIVE_WORK_ENABLED",
        "true",
    ).lower()
    in {
        "1",
        "true",
        "yes",
        "on",
    }
)

STOP = False

OPERATIONAL = {
    "AVAILABLE",
    "CONFIGURED",
    "OPERATIONAL",
    "HEALTHY",
    "READY",
    "ACTIVE",
}

SAFE_DEPS = {
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "pydantic": "pydantic",
    "starlette": "starlette",
    "requests": "requests",
    "httpx": "httpx",
    "aiohttp": "aiohttp",
    "psutil": "psutil",
    "yaml": "PyYAML",
    "dotenv": "python-dotenv",
    "PIL": "Pillow",
    "numpy": "numpy",
    "schedule": "schedule",
}

SOURCE_EXTENSIONS = {
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
}

IGNORE_DIRS = {
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

SECRET_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    "credentials.json",
    "secrets.json",
}

EXTERNAL_BLOCKERS = (
    "api key",
    "api_key",
    "credential",
    "credentials",
    "oauth",
    "merchant approval",
    "merchant account",
    "bank approval",
    "identity verification",
    "legal approval",
    "government approval",
    "domain verification",
    "dns ownership",
    "phone verification",
    "sms verification",
    "external account",
    "billing account",
    "payment account",
    "access token",
    "secret token",
)


def now():
    return datetime.now(
        timezone.utc
    ).isoformat()


def jsonable(value):
    if is_dataclass(value):
        return {
            str(key): jsonable(child)
            for key, child
            in asdict(value).items()
        }

    if isinstance(value, Mapping):
        return {
            str(key): jsonable(child)
            for key, child
            in value.items()
        }

    if isinstance(
        value,
        (
            list,
            tuple,
            set,
        ),
    ):
        return [
            jsonable(child)
            for child
            in value
        ]

    if isinstance(value, Path):
        return str(value)

    if (
        hasattr(
            value,
            "value",
        )
        and
        not isinstance(
            value,
            (
                str,
                bytes,
            ),
        )
    ):
        try:
            return jsonable(
                value.value
            )
        except Exception:
            pass

    return value


def save_json(
    path,
    data,
):
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
            jsonable(
                dict(data)
            ),
            file,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

    temporary.replace(path)


def load_json(
    path,
    default=None,
):
    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            value = json.load(file)

        if isinstance(
            value,
            dict,
        ):
            return value

    except Exception:
        pass

    return dict(
        default or {}
    )


def audit(
    event,
    data=None,
):
    with AUDIT_FILE.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(
                {
                    "time": now(),
                    "event": event,
                    "data": jsonable(
                        data or {}
                    ),
                },
                ensure_ascii=False,
                default=str,
            )
            + "\n"
        )


def run_process(
    command,
    timeout=120,
):
    started = time.time()

    try:
        process = subprocess.run(
            list(command),
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env=os.environ.copy(),
        )

        return {
            "success":
                process.returncode == 0,

            "returncode":
                process.returncode,

            "stdout":
                (
                    process.stdout
                    or ""
                )[-12000:],

            "stderr":
                (
                    process.stderr
                    or ""
                )[-12000:],

            "command":
                list(command),

            "duration_seconds":
                round(
                    time.time()
                    -
                    started,
                    3,
                ),
        }

    except Exception as error:
        return {
            "success":
                False,

            "error":
                f"{type(error).__name__}: {error}",

            "command":
                list(command),

            "duration_seconds":
                round(
                    time.time()
                    -
                    started,
                    3,
                ),
        }


def http_probe(
    url,
):
    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                    f"{RUNTIME}/{VERSION}"
            },
        )

        with urllib.request.urlopen(
            request,
            timeout=HTTP_TIMEOUT,
        ) as response:
            status_code = int(
                getattr(
                    response,
                    "status",
                    200,
                )
            )

            body = response.read(
                65536
            ).decode(
                "utf-8",
                "replace",
            )

            return {
                "success":
                    200
                    <= status_code
                    < 400,

                "status_code":
                    status_code,

                "url":
                    url,

                "body":
                    body[:3000],
            }

    except Exception as error:
        return {
            "success":
                False,

            "url":
                url,

            "error":
                f"{type(error).__name__}: {error}",
        }


def load_module(
    path,
    name,
):
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
        or
        spec.loader is None
    ):
        raise ImportError(
            path.name
        )

    module = (
        importlib.util
        .module_from_spec(
            spec
        )
    )

    sys.modules[
        name
    ] = module

    spec.loader.exec_module(
        module
    )

    return module


def find_callable(
    obj,
    names,
):
    for name in names:
        function = getattr(
            obj,
            name,
            None,
        )

        if callable(function):
            return function

    return None


def call_supported(
    function,
    values,
):
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

    return function(
        **{
            key: value
            for key, value
            in values.items()
            if (
                accepts_kwargs
                or
                key
                in signature.parameters
            )
        }
    )


def source_files():
    result = []

    for path in ROOT.rglob("*"):
        if (
            not path.is_file()
            or
            path.suffix.lower()
            not in SOURCE_EXTENSIONS
            or
            path.name in SECRET_NAMES
        ):
            continue

        try:
            relative = path.relative_to(
                ROOT
            )
        except ValueError:
            continue

        if any(
            part in IGNORE_DIRS
            for part
            in relative.parts
        ):
            continue

        result.append(path)

    return sorted(result)


def sha256_file(
    path,
):
    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as file:
        for chunk in iter(
            lambda:
                file.read(
                    1024 * 1024
                ),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def backup(
    cycle_id,
):
    base = BACKUP / cycle_id

    base.mkdir(
        parents=True,
        exist_ok=True,
    )

    manifest = {
        "files": {}
    }

    for path in source_files():
        relative = path.relative_to(
            ROOT
        )

        destination = (
            base
            /
            relative
        )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            path,
            destination,
        )

        manifest[
            "files"
        ][
            str(relative)
        ] = {
            "sha256":
                sha256_file(path),

            "size":
                path.stat().st_size,
        }

    save_json(
        base
        /
        "manifest.json",
        manifest,
    )

    return {
        "success": True,
        "status":
            "SOURCE_BACKUP_CREATED",
        "file_count":
            len(
                manifest[
                    "files"
                ]
            ),
    }


def source_changes(
    cycle_id,
):
    before = load_json(
        BACKUP
        /
        cycle_id
        /
        "manifest.json",
        {},
    ).get(
        "files",
        {},
    )

    current = {
        str(
            path.relative_to(
                ROOT
            )
        ): {
            "sha256":
                sha256_file(path)
        }
        for path
        in source_files()
    }

    changed = sorted(
        name
        for name
        in before
        if (
            name in current
            and
            before[
                name
            ].get(
                "sha256"
            )
            !=
            current[
                name
            ].get(
                "sha256"
            )
        )
    )

    created = sorted(
        set(current)
        -
        set(before)
    )

    deleted = sorted(
        set(before)
        -
        set(current)
    )

    return {
        "success": True,
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


def rollback(
    cycle_id,
):
    base = BACKUP / cycle_id

    before = load_json(
        base
        /
        "manifest.json",
        {},
    ).get(
        "files",
        {},
    )

    if not before:
        return {
            "success": False,
            "status":
                "ROLLBACK_MANIFEST_MISSING",
        }

    original = set(before)

    for relative in original:
        source = (
            base
            /
            relative
        )

        destination = (
            ROOT
            /
            relative
        )

        if source.exists():
            destination.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            shutil.copy2(
                source,
                destination,
            )

    current = {
        str(
            path.relative_to(
                ROOT
            )
        )
        for path
        in source_files()
    }

    for relative in (
        current
        -
        original
    ):
        try:
            (
                ROOT
                /
                relative
            ).unlink()
        except Exception:
            pass

    return {
        "success": True,
        "status":
            "SOURCE_ROLLBACK_COMPLETED",
    }


def verify_core():
    required = {
        "01":
            F01,

        "02_company":
            F02C,

        "02_owner":
            F02O,

        "03":
            F03,

        "04":
            F04,
    }

    missing = []
    files = {}

    for name, path in required.items():
        exists = (
            path.exists()
            and
            path.is_file()
            and
            path.stat().st_size > 0
        )

        files[
            name
        ] = {
            "file":
                path.name,

            "exists":
                exists,

            "size":
                (
                    path.stat().st_size
                    if path.exists()
                    else 0
                ),
        }

        if not exists:
            missing.append(
                path.name
            )

    return {
        "success":
            not missing,

        "missing":
            missing,

        "files":
            files,
    }


def verify_syntax():
    checked = []
    failed = []

    for path in source_files():
        if (
            path.suffix.lower()
            != ".py"
        ):
            continue

        result = run_process(
            [
                sys.executable,
                "-m",
                "py_compile",
                str(path),
            ],
            45,
        )

        item = {
            "file":
                str(
                    path.relative_to(
                        ROOT
                    )
                ),

            "success":
                bool(
                    result.get(
                        "success"
                    )
                ),

            "stderr":
                result.get(
                    "stderr",
                    "",
                ),
        }

        checked.append(item)

        if not item[
            "success"
        ]:
            failed.append(item)

    return {
        "success":
            not failed,

        "checked_count":
            len(checked),

        "failed":
            failed,

        "checked":
            checked,
    }


def imported_roots(
    path,
):
    try:
        tree = ast.parse(
            path.read_text(
                encoding="utf-8"
            ),
            filename=str(path),
        )
    except Exception:
        return set()

    result = set()

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.Import,
        ):
            result |= {
                alias.name.split(
                    "."
                )[0]
                for alias
                in node.names
            }

        elif (
            isinstance(
                node,
                ast.ImportFrom,
            )
            and
            node.module
        ):
            result.add(
                node.module.split(
                    "."
                )[0]
            )

    return result


def dependency_state():
    roots = set()

    for path in source_files():
        if (
            path.suffix.lower()
            == ".py"
        ):
            roots |= imported_roots(
                path
            )

    missing = []

    for module, package in SAFE_DEPS.items():
        if module not in roots:
            continue

        try:
            available = (
                importlib.util
                .find_spec(
                    module
                )
                is not None
            )
        except Exception:
            available = False

        if not available:
            missing.append(
                {
                    "module":
                        module,

                    "package":
                        package,
                }
            )

    return {
        "success":
            not missing,

        "missing":
            missing,
    }


def pip_install(
    package,
):
    if not ALLOW_DEP_INSTALL:
        return {
            "success": False,
            "status":
                "DEPENDENCY_INSTALL_DISABLED",
        }

    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        package,
    ]

    result = run_process(
        command,
        600,
    )

    text = (
        result.get(
            "stdout",
            "",
        )
        +
        result.get(
            "stderr",
            "",
        )
    ).lower()

    if (
        not result.get(
            "success"
        )
        and
        (
            "externally-managed-environment"
            in text
            or
            "pep 668"
            in text
        )
    ):
        result = run_process(
            command
            +
            [
                "--break-system-packages"
            ],
            600,
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
                "INSTALLED"
                if result.get(
                    "success"
                )
                else
                "INSTALL_FAILED"
            ),

        "process":
            result,
    }


def repair_dependencies():
    before = dependency_state()

    if before[
        "success"
    ]:
        return {
            "success": True,
            "status":
                "DEPENDENCIES_HEALTHY",
            "before":
                before,
            "after":
                before,
            "installed": [],
            "failed": [],
        }

    installed = []
    failed = []

    for item in before[
        "missing"
    ]:
        result = pip_install(
            item[
                "package"
            ]
        )

        record = {
            "module":
                item[
                    "module"
                ],

            "package":
                item[
                    "package"
                ],

            "result":
                result,
        }

        if result[
            "success"
        ]:
            installed.append(
                record
            )
        else:
            failed.append(
                record
            )

    after = dependency_state()

    return {
        "success":
            after[
                "success"
            ],

        "status":
            (
                "DEPENDENCIES_REPAIRED"
                if after[
                    "success"
                ]
                else
                "DEPENDENCY_REPAIR_INCOMPLETE"
            ),

        "before":
            before,

        "after":
            after,

        "installed":
            installed,

        "failed":
            failed,
    }


def disk_state():
    try:
        stat = os.statvfs(ROOT)

        total = (
            stat.f_blocks
            *
            stat.f_frsize
        )

        available = (
            stat.f_bavail
            *
            stat.f_frsize
        )

        percent = (
            (
                total
                -
                available
            )
            /
            total
            *
            100
            if total
            else 0
        )

        return {
            "success":
                percent < 90,

            "used_percent":
                round(
                    percent,
                    2,
                ),

            "available_bytes":
                available,
        }

    except Exception as error:
        return {
            "success": False,
            "error":
                str(error),
        }


def docker_state():
    if (
        shutil.which(
            "docker"
        )
        is None
    ):
        return {
            "success": False,
            "status":
                "DOCKER_COMMAND_MISSING",
        }

    result = run_process(
        [
            "docker",
            "ps",
            "-a",
            "--format",
            "{{.Names}}|{{.State}}|{{.Status}}|{{.Ports}}",
        ],
        45,
    )

    if not result.get(
        "success"
    ):
        return {
            "success": False,
            "status":
                "DOCKER_QUERY_FAILED",
            "process":
                result,
        }

    containers = []

    for line in result.get(
        "stdout",
        "",
    ).splitlines():
        if not line.strip():
            continue

        parts = line.split(
            "|",
            3,
        )

        containers.append(
            {
                "name":
                    (
                        parts[0]
                        if len(parts) > 0
                        else ""
                    ),

                "state":
                    (
                        parts[1]
                        if len(parts) > 1
                        else ""
                    ),

                "status":
                    (
                        parts[2]
                        if len(parts) > 2
                        else ""
                    ),

                "ports":
                    (
                        parts[3]
                        if len(parts) > 3
                        else ""
                    ),
            }
        )

    by_name = {
        item[
            "name"
        ]:
            item
        for item
        in containers
    }

    expected = {
        "majd-ai-core",
        "majd-web-ui",
    }

    missing = sorted(
        expected
        -
        set(by_name)
    )

    stopped = sorted(
        name
        for name
        in (
            expected
            &
            set(by_name)
        )
        if (
            by_name[
                name
            ][
                "state"
            ].lower()
            != "running"
        )
    )

    return {
        "success":
            not missing
            and
            not stopped,

        "containers":
            containers,

        "missing_expected":
            missing,

        "stopped_expected":
            stopped,
    }


def recover_docker():
    before = docker_state()
    actions = []

    for name in before.get(
        "stopped_expected",
        [],
    ):
        result = run_process(
            [
                "docker",
                "start",
                name,
            ],
            90,
        )

        actions.append(
            {
                "container":
                    name,

                "success":
                    bool(
                        result.get(
                            "success"
                        )
                    ),
            }
        )

    after = docker_state()

    return {
        "success":
            after.get(
                "success",
                False,
            ),

        "before":
            before,

        "actions":
            actions,

        "after":
            after,
    }


def normalize_status(
    value,
):
    if value is None:
        return "UNKNOWN"

    if (
        hasattr(
            value,
            "value",
        )
        and
        not isinstance(
            value,
            str,
        )
    ):
        try:
            value = value.value
        except Exception:
            pass

    text = str(
        value
    ).strip().upper()

    aliases = {
        "OPERATIONAL":
            "AVAILABLE",

        "HEALTHY":
            "AVAILABLE",

        "READY":
            "AVAILABLE",

        "ACTIVE":
            "AVAILABLE",

        "OK":
            "AVAILABLE",

        "CONNECTED":
            "CONFIGURED",

        "ENABLED":
            "CONFIGURED",

        "NOT AVAILABLE":
            "UNAVAILABLE",

        "NOT_AVAILABLE":
            "UNAVAILABLE",

        "NOT CONFIGURED":
            "NOT_CONFIGURED",

        "ERROR":
            "FAILED",

        "BROKEN":
            "FAILED",
    }

    return aliases.get(
        text,
        text or "UNKNOWN",
    )


def capability_id(
    value,
    fallback="",
):
    if isinstance(
        value,
        Mapping,
    ):
        return str(
            value.get(
                "capability_id"
            )
            or
            value.get(
                "id"
            )
            or
            value.get(
                "name"
            )
            or
            fallback
        )

    for attribute in (
        "capability_id",
        "id",
        "name",
    ):
        candidate = getattr(
            value,
            attribute,
            None,
        )

        if candidate:
            return str(candidate)

    return str(fallback)


def capability_status(
    value,
):
    if isinstance(
        value,
        Mapping,
    ):
        for key in (
            "status",
            "state",
            "availability",
        ):
            if key in value:
                return normalize_status(
                    value[key]
                )

        health = value.get(
            "health"
        )

        if health is not None:
            return capability_status(
                health
            )

        return "UNKNOWN"

    for attribute in (
        "status",
        "state",
        "availability",
    ):
        candidate = getattr(
            value,
            attribute,
            None,
        )

        if candidate is not None:
            return normalize_status(
                candidate
            )

    health = getattr(
        value,
        "health",
        None,
    )

    if health is not None:
        return capability_status(
            health
        )

    return "UNKNOWN"


def capability_reason(
    value,
):
    if isinstance(
        value,
        Mapping,
    ):
        for key in (
            "reason",
            "message",
            "error",
            "detail",
            "details",
        ):
            if value.get(key):
                return str(
                    value[key]
                )

        health = value.get(
            "health"
        )

        if health is not None:
            return capability_reason(
                health
            )

        return ""

    for attribute in (
        "reason",
        "message",
        "error",
        "detail",
        "details",
    ):
        candidate = getattr(
            value,
            attribute,
            None,
        )

        if candidate:
            return str(candidate)

    health = getattr(
        value,
        "health",
        None,
    )

    if health is not None:
        return capability_reason(
            health
        )

    return ""


def capability_snapshot(
    value,
    fallback="",
):
    status = capability_status(
        value
    )

    if isinstance(
        value,
        Mapping,
    ):
        adapter = (
            value.get(
                "adapter"
            )
            or
            value.get(
                "adapter_name"
            )
            or
            value.get(
                "engine"
            )
        )

        required = bool(
            value.get(
                "required",
                False,
            )
        )

    else:
        adapter = (
            getattr(
                value,
                "adapter_name",
                None,
            )
            or
            getattr(
                value,
                "adapter",
                None,
            )
            or
            getattr(
                value,
                "engine_name",
                None,
            )
        )

        required = bool(
            getattr(
                value,
                "required",
                False,
            )
        )

    return {
        "capability_id":
            capability_id(
                value,
                fallback,
            ),

        "status":
            status,

        "operational":
            status
            in OPERATIONAL,

        "required":
            required,

        "reason":
            capability_reason(
                value
            ),

        "adapter":
            (
                str(adapter)
                if adapter
                else None
            ),

        "raw":
            jsonable(value),
    }


def inspect_company_direct():
    module_name = (
        "majd_company_"
        +
        uuid.uuid4().hex
    )

    try:
        company_module = load_module(
            F02C,
            module_name,
        )

        getter = getattr(
            company_module,
            "get_company",
            None,
        )

        if not callable(getter):
            raise RuntimeError(
                "get_company() missing in Company 02"
            )

        company = call_supported(
            getter,
            {
                "root_dir":
                    str(ROOT),

                "owner":
                    OWNER,
            },
        )

        refresh = find_callable(
            company,
            (
                "refresh_health",
                "refresh",
                "health_check",
                "check_health",
            ),
        )

        refresh_result = (
            call_supported(
                refresh,
                {},
            )
            if refresh
            else None
        )

        raw = getattr(
            company,
            "capabilities",
            {},
        )

        if isinstance(
            raw,
            Mapping,
        ):
            capabilities = [
                capability_snapshot(
                    value,
                    str(key),
                )
                for key, value
                in raw.items()
            ]

        else:
            capabilities = [
                capability_snapshot(
                    value,
                    f"CAPABILITY_{index + 1}",
                )
                for index, value
                in enumerate(
                    raw or []
                )
            ]

        unavailable = [
            item
            for item
            in capabilities
            if not item[
                "operational"
            ]
        ]

        operational = [
            item
            for item
            in capabilities
            if item[
                "operational"
            ]
        ]

        required_unavailable = [
            item
            for item
            in unavailable
            if item[
                "required"
            ]
        ]

        return {
            "success": True,
            "company_loaded": True,
            "status":
                "COMPANY_INSPECTED_DIRECTLY",

            "refresh":
                jsonable(
                    refresh_result
                ),

            "capability_count":
                len(
                    capabilities
                ),

            "operational_count":
                len(
                    operational
                ),

            "unavailable_count":
                len(
                    unavailable
                ),

            "required_unavailable_count":
                len(
                    required_unavailable
                ),

            "all_capabilities_operational":
                (
                    bool(
                        capabilities
                    )
                    and
                    not unavailable
                ),

            "required_capabilities_operational":
                not required_unavailable,

            "capabilities":
                capabilities,
        }

    except Exception as error:
        return {
            "success": False,
            "company_loaded": False,
            "status":
                "COMPANY_DIRECT_INSPECTION_EXCEPTION",

            "error":
                f"{type(error).__name__}: {error}",

            "traceback":
                traceback.format_exc(),

            "capabilities": [],

            "unavailable_count": 0,
        }

    finally:
        sys.modules.pop(
            module_name,
            None,
        )


def owner_action_required(
    item,
):
    text = (
        str(
            item.get(
                "reason",
                "",
            )
        )
        +
        " "
        +
        json.dumps(
            jsonable(
                item.get(
                    "raw",
                    {},
                )
            ),
            ensure_ascii=False,
            default=str,
        )
    ).lower()

    return any(
        keyword in text
        for keyword
        in EXTERNAL_BLOCKERS
    )


def capability_priority(
    item,
):
    identifier = str(
        item.get(
            "capability_id",
            "",
        )
    ).upper()

    priority = (
        10
        if item.get(
            "required"
        )
        else 50
    )

    important = (
        "OWNER",
        "AUTHORITY",
        "SECURITY",
        "AUDIT",
        "DATABASE",
        "EXECUTOR",
        "BUILD",
        "TEST",
        "QA",
        "DEPLOY",
        "BRIDGE",
        "PUBLISH",
        "PLATFORM",
        "API",
        "ORIGINALITY",
        "IP_",
        "MONITOR",
        "RECOVERY",
        "BACKUP",
    )

    if any(
        keyword
        in identifier
        for keyword
        in important
    ):
        priority -= 5

    return max(
        1,
        priority,
    )


def build_queue(
    company,
):
    old = load_json(
        QUEUE_FILE,
        {},
    )

    previous = {
        str(
            item.get(
                "capability_id"
            )
        ):
            item
        for item
        in old.get(
            "items",
            [],
        )
        if isinstance(
            item,
            dict,
        )
    }

    items = []

    for capability in company.get(
        "capabilities",
        [],
    ):
        if capability.get(
            "operational"
        ):
            continue

        item = dict(
            capability
        )

        old_item = previous.get(
            str(
                capability.get(
                    "capability_id"
                )
            ),
            {},
        )

        item.update(
            {
                "owner_required":
                    owner_action_required(
                        capability
                    ),

                "priority":
                    capability_priority(
                        capability
                    ),

                "attempts":
                    int(
                        old_item.get(
                            "attempts",
                            0,
                        )
                        or 0
                    ),

                "last_attempt_at":
                    old_item.get(
                        "last_attempt_at"
                    ),

                "last_result":
                    old_item.get(
                        "last_result"
                    ),
            }
        )

        items.append(item)

    items.sort(
        key=lambda item: (
            item[
                "owner_required"
            ],
            item[
                "priority"
            ],
            item[
                "attempts"
            ],
            str(
                item.get(
                    "capability_id",
                    "",
                )
            ),
        )
    )

    queue = {
        "updated_at":
            now(),

        "total":
            len(items),

        "autonomous":
            sum(
                not item[
                    "owner_required"
                ]
                for item
                in items
            ),

        "owner_required":
            sum(
                item[
                    "owner_required"
                ]
                for item
                in items
            ),

        "required_total":
            sum(
                bool(
                    item.get(
                        "required"
                    )
                )
                for item
                in items
            ),

        "items":
            items,
    }

    save_json(
        QUEUE_FILE,
        queue,
    )

    return queue


def select_batch(
    queue,
):
    return [
        dict(item)
        for item
        in queue.get(
            "items",
            [],
        )
        if not item.get(
            "owner_required"
        )
    ][:MAX_BATCH]


def mark_attempts(
    selected,
    result,
):
    queue = load_json(
        QUEUE_FILE,
        {},
    )

    identifiers = {
        str(
            item.get(
                "capability_id"
            )
        )
        for item
        in selected
    }

    for item in queue.get(
        "items",
        [],
    ):
        if (
            str(
                item.get(
                    "capability_id"
                )
            )
            in identifiers
        ):
            item[
                "attempts"
            ] = (
                int(
                    item.get(
                        "attempts",
                        0,
                    )
                    or 0
                )
                +
                1
            )

            item[
                "last_attempt_at"
            ] = now()

            item[
                "last_result"
            ] = {
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
            }

    save_json(
        QUEUE_FILE,
        queue,
    )


class OwnerBridge:

    def __init__(
        self,
    ):
        self.module = load_module(
            F02O,
            (
                "majd_owner_"
                +
                uuid.uuid4().hex
            ),
        )

    def parse(
        self,
        command,
    ):
        parser = getattr(
            self.module,
            "OwnerCommandParser",
            None,
        )

        if parser is None:
            return {
                "type":
                    "GENERAL_OWNER_COMMAND",
                "raw":
                    command,
            }

        try:
            result = parser().parse(
                command
            )

            if not isinstance(
                result,
                dict,
            ):
                result = {
                    "type":
                        "GENERAL_OWNER_COMMAND",
                    "raw":
                        command,
                }

            if str(
                result.get(
                    "type",
                    "",
                )
            ).upper() in {
                "",
                "UNKNOWN",
            }:
                result[
                    "type"
                ] = (
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
                    str(error),
            }

    def execute(
        self,
        command,
        owner,
    ):
        function = getattr(
            self.module,
            "execute_owner_command",
            None,
        )

        if not callable(
            function
        ):
            return {
                "success": False,
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

            if isinstance(
                result,
                dict,
            ):
                return result

            return {
                "success": False,
                "status":
                    "INVALID_OWNER_COMMAND_RESULT",
            }

        except Exception as error:
            return {
                "success": False,

                "status":
                    "OWNER_COMMAND_EXCEPTION",

                "error":
                    str(error),

                "traceback":
                    traceback.format_exc(),
            }


class Mastermind:

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
    ):
        self.dependencies = (
            repair_dependencies()
        )

        self.module = load_module(
            F01,
            (
                "majd_master_"
                +
                uuid.uuid4().hex
            ),
        )

    def execute(
        self,
        command,
        request,
        runtime_id,
        owner,
    ):
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

            if mastermind_class:
                instance = call_supported(
                    mastermind_class,
                    {
                        "owner":
                            owner
                    },
                )

                function = find_callable(
                    instance,
                    self.FUNCTION_NAMES,
                )

        if function is None:
            return {
                "success": False,
                "status":
                    "MASTERMIND_INTERFACE_MISSING",
            }

        try:
            result = call_supported(
                function,
                {
                    "command":
                        command,

                    "request":
                        dict(request),

                    "payload":
                        dict(request),

                    "job_id":
                        runtime_id,

                    "runtime_id":
                        runtime_id,

                    "owner":
                        owner,

                    "output_root":
                        str(OUTPUT),
                },
            )

            if isinstance(
                result,
                dict,
            ):
                return result

            return {
                "success": False,
                "status":
                    "INVALID_MASTERMIND_RESULT",
            }

        except Exception as error:
            return {
                "success": False,

                "status":
                    "MASTERMIND_EXECUTION_EXCEPTION",

                "error":
                    f"{type(error).__name__}: {error}",

                "traceback":
                    traceback.format_exc(),

                "dependency_repair":
                    self.dependencies,
            }


def verify_artifact(
    value,
):
    if not value:
        return {
            "success": False,
            "status":
                "PLAYABLE_ARTIFACT_MISSING",
        }

    path = Path(
        str(value)
    )

    if not path.is_absolute():
        path = (
            ROOT
            /
            path
        ).resolve()
    else:
        path = path.resolve()

    if (
        not path.exists()
        or
        not path.is_dir()
    ):
        return {
            "success": False,
            "status":
                "PLAYABLE_ARTIFACT_NOT_FOUND",
        }

    index = (
        path
        /
        "index.html"
    )

    files = [
        item
        for item
        in path.rglob("*")
        if item.is_file()
    ]

    if (
        not index.exists()
        or
        index.stat().st_size
        <= 0
    ):
        return {
            "success": False,
            "status":
                "PLAYABLE_INDEX_NOT_FOUND_OR_EMPTY",
        }

    if not any(
        item.suffix.lower()
        in {
            ".js",
            ".mjs",
        }
        for item
        in files
    ):
        return {
            "success": False,
            "status":
                "PLAYABLE_JAVASCRIPT_NOT_FOUND",
        }

    return {
        "success": True,

        "status":
            "PLAYABLE_ARTIFACT_VERIFIED",

        "artifact":
            str(path),

        "index":
            str(index),

        "file_count":
            len(files),
    }


def verify_published(
    value,
):
    if (
        not isinstance(
            value,
            Mapping,
        )
        or
        not value.get(
            "success"
        )
    ):
        return {
            "success": False,
            "status":
                "PLATFORM_RESULT_INVALID_OR_FAILED",
        }

    directory = value.get(
        "published_directory"
    )

    public_url = value.get(
        "public_url"
    )

    game_path = value.get(
        "game_path"
    )

    if (
        not directory
        or
        not public_url
        or
        not game_path
    ):
        return {
            "success": False,
            "status":
                "PUBLISHED_RESULT_INCOMPLETE",
        }

    path = Path(
        str(directory)
    )

    if not path.is_absolute():
        path = (
            ROOT
            /
            path
        ).resolve()

    if (
        not path.exists()
        or
        not (
            path
            /
            "index.html"
        ).exists()
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
            str(path),

        "public_url":
            str(public_url),

        "game_path":
            str(game_path),
    }


def verify_mastermind_result(
    command_type,
    result,
):
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
        }

    if (
        command_type
        != "CREATE_GAME"
    ):
        return {
            "success": True,
            "status":
                "MASTERMIND_RESULT_VERIFIED",
        }

    artifact = verify_artifact(
        result.get(
            "artifact"
        )
    )

    publication = verify_published(
        result.get(
            "platform"
        )
    )

    success = (
        artifact[
            "success"
        ]
        and
        publication[
            "success"
        ]
    )

    return {
        "success":
            success,

        "status":
            (
                "FULL_EXECUTION_VERIFIED"
                if success
                else
                (
                    artifact[
                        "status"
                    ]
                    if not artifact[
                        "success"
                    ]
                    else
                    publication[
                        "status"
                    ]
                )
            ),

        "artifact":
            artifact,

        "publication":
            publication,
    }


def inspect_platform():
    dependencies = (
        repair_dependencies()
    )

    docker_recovery = (
        recover_docker()
    )

    company = (
        inspect_company_direct()
    )

    queue = (
        build_queue(
            company
        )
        if company.get(
            "success"
        )
        else
        {
            "total": 0,
            "autonomous": 0,
            "owner_required": 0,
            "required_total": 0,
            "items": [],
        }
    )

    return {
        "time":
            now(),

        "core_files":
            verify_core(),

        "python_syntax":
            verify_syntax(),

        "dependencies":
            dependencies,

        "local_api":
            http_probe(
                LOCAL_HEALTH
            ),

        "official_platform":
            http_probe(
                PLATFORM
            ),

        "docker_recovery":
            docker_recovery,

        "docker":
            docker_state(),

        "disk":
            disk_state(),

        "sovereign_company":
            company,

        "work_queue":
            queue,
    }


def infrastructure_map(
    inspection,
):
    return {
        "core_files":
            bool(
                inspection.get(
                    "core_files",
                    {},
                ).get(
                    "success"
                )
            ),

        "python_syntax":
            bool(
                inspection.get(
                    "python_syntax",
                    {},
                ).get(
                    "success"
                )
            ),

        "dependencies":
            bool(
                inspection.get(
                    "dependencies",
                    {},
                ).get(
                    "success"
                )
            ),

        "local_api":
            bool(
                inspection.get(
                    "local_api",
                    {},
                ).get(
                    "success"
                )
            ),

        "official_platform":
            bool(
                inspection.get(
                    "official_platform",
                    {},
                ).get(
                    "success"
                )
            ),

        "docker":
            bool(
                inspection.get(
                    "docker",
                    {},
                ).get(
                    "success"
                )
            ),

        "disk":
            bool(
                inspection.get(
                    "disk",
                    {},
                ).get(
                    "success"
                )
            ),

        "company_loaded":
            bool(
                inspection.get(
                    "sovereign_company",
                    {},
                ).get(
                    "success"
                )
            ),
    }


def infrastructure_findings(
    inspection,
):
    return [
        {
            "id":
                key.upper()
                +
                "_UNHEALTHY",

            "component":
                key,
        }
        for key, value
        in infrastructure_map(
            inspection
        ).items()
        if not value
    ]


def regression_check(
    before,
    after,
):
    before_map = infrastructure_map(
        before
    )

    after_map = infrastructure_map(
        after
    )

    regressions = [
        key
        for key, value
        in before_map.items()
        if (
            value
            and
            not after_map.get(
                key,
                False,
            )
        )
    ]

    return {
        "success":
            not regressions,

        "regressions":
            regressions,

        "before":
            before_map,

        "after":
            after_map,
    }


def capability_map(
    company,
):
    return {
        str(
            item.get(
                "capability_id"
            )
        ):
            str(
                item.get(
                    "status",
                    "UNKNOWN",
                )
            ).upper()
        for item
        in company.get(
            "capabilities",
            [],
        )
        if item.get(
            "capability_id"
        )
    }


def capability_progress(
    before,
    after,
    selected,
):
    before_company = before.get(
        "sovereign_company",
        {},
    )

    after_company = after.get(
        "sovereign_company",
        {},
    )

    before_map = capability_map(
        before_company
    )

    after_map = capability_map(
        after_company
    )

    identifiers = [
        str(
            item.get(
                "capability_id"
            )
        )
        for item
        in selected
        if item.get(
            "capability_id"
        )
    ]

    became_operational = [
        identifier
        for identifier
        in identifiers
        if (
            before_map.get(
                identifier
            )
            not in OPERATIONAL
            and
            after_map.get(
                identifier
            )
            in OPERATIONAL
        )
    ]

    before_unavailable = int(
        before_company.get(
            "unavailable_count",
            0,
        )
        or 0
    )

    after_unavailable = int(
        after_company.get(
            "unavailable_count",
            0,
        )
        or 0
    )

    return {
        "success":
            bool(
                became_operational
                or
                after_unavailable
                <
                before_unavailable
            ),

        "before_unavailable":
            before_unavailable,

        "after_unavailable":
            after_unavailable,

        "became_operational":
            became_operational,

        "selected_status_before":
            {
                identifier:
                    before_map.get(
                        identifier
                    )
                for identifier
                in identifiers
            },

        "selected_status_after":
            {
                identifier:
                    after_map.get(
                        identifier
                    )
                for identifier
                in identifiers
            },
    }


def build_objective(
    cycle_id,
    inspection,
    selected,
    findings,
    proactive,
):
    request = {
        "type":
            (
                "AUTONOMOUS_CONTINUOUS_COMPANY_OPERATION"
                if proactive
                else
                "AUTONOMOUS_REPAIR_AND_CAPABILITY_COMPLETION"
            ),

        "cycle_id":
            cycle_id,

        "autonomous":
            True,

        "proactive":
            proactive,

        "findings":
            list(findings),

        "work_items":
            list(selected),

        "policy": {
            "routine_owner_approval_required":
                False,

            "allow_code_generation":
                True,

            "allow_code_repair":
                True,

            "allow_adapter_generation":
                True,

            "allow_integration":
                True,

            "allow_ui_development":
                True,

            "allow_testing":
                True,

            "allow_build":
                True,

            "allow_routine_deployment":
                True,

            "require_real_verification":
                True,

            "never_fake_operational":
                True,

            "rollback_only_on_real_regression":
                True,

            "protect_owner_authority":
                True,

            "protect_platform_secrets":
                True,

            "do_not_ask_owner_for_code":
                True,
        },
    }

    command = (
        "MAJD SOVEREIGN AUTONOMOUS OPERATION / "
        "تشغيل مجد السيادي الذاتي. "
        "Inspect diagnose repair test and improve the supplied real work items. "
        "For NO_REAL_ADAPTER inspect Company 02 and existing MAJD code, "
        "build and persist a real adapter only when a real implementation exists, "
        "run its health check, never create a placeholder or fake AVAILABLE state. "
        "Continue unrelated work when an external credential/account/legal/"
        "identity/financial blocker exists. Return structured proof."
    )

    return (
        command,
        request,
    )


def notify(
    cycle,
):
    queue = cycle.get(
        "queue_summary",
        {},
    )

    progress = cycle.get(
        "capability_progress",
        {},
    )

    report_ar = (
        "تقرير مجد\n"
        f"الحالة: {cycle.get('status')}\n"
        f"الوضع: {cycle.get('mode_executed')}\n"
        f"النجاح: {cycle.get('success')}\n"
        f"قائمة العمل: {queue.get('total', 0)}\n"
        f"يحتاج المالك: {queue.get('owner_required', 0)}\n"
        f"تحولت لتشغيلية: "
        f"{','.join(progress.get('became_operational', [])) or 'لا يوجد'}"
    )

    report_en = (
        "MAJD Report\n"
        f"Status: {cycle.get('status')}\n"
        f"Mode: {cycle.get('mode_executed')}\n"
        f"Success: {cycle.get('success')}\n"
        f"Work queue: {queue.get('total', 0)}\n"
        f"Owner required: {queue.get('owner_required', 0)}\n"
        f"Became operational: "
        f"{','.join(progress.get('became_operational', [])) or 'none'}"
    )

    return {
        "report_ar":
            report_ar,

        "report_en":
            report_en,

        "email": {
            "success": False,
            "status":
                "NOT_CONFIGURED",
        },

        "whatsapp": {
            "success": False,
            "status":
                "NOT_CONFIGURED",
        },
    }


class AutonomousRuntime:

    def __init__(
        self,
        owner=OWNER,
        cycle_seconds=CYCLE_SECONDS,
    ):
        self.owner = owner

        self.cycle_seconds = max(
            30,
            int(
                cycle_seconds
            ),
        )

        old = load_json(
            STATE_FILE,
            {},
        )

        self.total = int(
            old.get(
                "total_cycles",
                0,
            )
            or 0
        )

        self.good = int(
            old.get(
                "successful_cycles",
                0,
            )
            or 0
        )

        self.bad = int(
            old.get(
                "failed_cycles",
                0,
            )
            or 0
        )

    def save_state(
        self,
        status,
        cycle=None,
    ):
        save_json(
            STATE_FILE,
            {
                "system":
                    SYSTEM,

                "runtime":
                    RUNTIME,

                "version":
                    VERSION,

                "owner":
                    self.owner,

                "pid":
                    os.getpid(),

                "status":
                    status,

                "updated_at":
                    now(),

                "cycle_seconds":
                    self.cycle_seconds,

                "total_cycles":
                    self.total,

                "successful_cycles":
                    self.good,

                "failed_cycles":
                    self.bad,

                "last_cycle":
                    cycle,
            },
        )

    def execute_mastermind(
        self,
        cycle_id,
        command,
        request,
        kind,
    ):
        attempts = []

        for attempt in range(
            1,
            MAX_ATTEMPTS + 1,
        ):
            result = (
                Mastermind()
                .execute(
                    command,
                    request,
                    (
                        f"AUTO-"
                        f"{cycle_id}-"
                        f"{kind}-"
                        f"{attempt}"
                    ),
                    self.owner,
                )
            )

            attempts.append(
                {
                    "attempt":
                        attempt,

                    "result":
                        result,
                }
            )

            if result.get(
                "success"
            ):
                return {
                    "success": True,
                    "status":
                        "MASTERMIND_EXECUTED",
                    "attempts":
                        attempts,
                    "result":
                        result,
                }

            if attempt < MAX_ATTEMPTS:
                time.sleep(2)

        return {
            "success": False,
            "status":
                "MASTERMIND_ATTEMPTS_EXHAUSTED",
            "attempts":
                attempts,
        }

    def cycle(
        self,
    ):
        cycle_id = str(
            uuid.uuid4()
        )

        self.total += 1

        cycle = {
            "cycle_id":
                cycle_id,

            "started_at":
                now(),

            "success":
                False,

            "status":
                "INSPECTING",

            "mode_executed":
                None,
        }

        audit(
            "CYCLE_STARTED",
            {
                "cycle_id":
                    cycle_id
            },
        )

        try:
            before = (
                inspect_platform()
            )

            findings = (
                infrastructure_findings(
                    before
                )
            )

            queue = before[
                "work_queue"
            ]

            selected = (
                select_batch(
                    queue
                )
            )

            if findings:
                mode = "REPAIR"

            elif selected:
                mode = (
                    "CAPABILITY_COMPLETION"
                )

            elif PROACTIVE:
                mode = "PROACTIVE"

            else:
                mode = "HEALTH_ONLY"

            cycle.update(
                {
                    "inspection_before":
                        before,

                    "findings":
                        findings,

                    "selected_work":
                        selected,

                    "mode_executed":
                        mode,

                    "queue_summary": {
                        key:
                            queue.get(
                                key,
                                0,
                            )
                        for key
                        in (
                            "total",
                            "autonomous",
                            "owner_required",
                            "required_total",
                        )
                    },
                }
            )

            if mode == "HEALTH_ONLY":
                cycle[
                    "success"
                ] = all(
                    infrastructure_map(
                        before
                    ).values()
                )

                cycle[
                    "status"
                ] = (
                    "PLATFORM_HEALTHY"
                    if cycle[
                        "success"
                    ]
                    else
                    "PLATFORM_DEGRADED"
                )

            else:
                cycle[
                    "backup"
                ] = backup(
                    cycle_id
                )

                (
                    command,
                    request,
                ) = build_objective(
                    cycle_id,
                    before,
                    selected,
                    findings,
                    mode
                    ==
                    "PROACTIVE",
                )

                mastermind = (
                    self.execute_mastermind(
                        cycle_id,
                        command,
                        request,
                        mode,
                    )
                )

                cycle[
                    "mastermind"
                ] = mastermind

                mark_attempts(
                    selected,
                    mastermind,
                )

                after = (
                    inspect_platform()
                )

                regressions = (
                    regression_check(
                        before,
                        after,
                    )
                )

                progress = (
                    capability_progress(
                        before,
                        after,
                        selected,
                    )
                )

                changes = (
                    source_changes(
                        cycle_id
                    )
                )

                cycle.update(
                    {
                        "inspection_after":
                            after,

                        "regression_check":
                            regressions,

                        "capability_progress":
                            progress,

                        "source_changes":
                            changes,
                    }
                )

                infrastructure_progress = (
                    len(
                        infrastructure_findings(
                            after
                        )
                    )
                    <
                    len(
                        findings
                    )
                )

                if mode == "REPAIR":
                    real_progress = (
                        infrastructure_progress
                        or
                        progress[
                            "success"
                        ]
                    )

                elif (
                    mode
                    ==
                    "CAPABILITY_COMPLETION"
                ):
                    real_progress = (
                        progress[
                            "success"
                        ]
                    )

                else:
                    real_progress = bool(
                        mastermind.get(
                            "success"
                        )
                    )

                if (
                    regressions[
                        "success"
                    ]
                    and
                    real_progress
                ):
                    cycle[
                        "success"
                    ] = True

                    cycle[
                        "status"
                    ] = (
                        "REPAIRED_AND_VERIFIED"
                        if mode
                        ==
                        "REPAIR"
                        else
                        "CAPABILITY_PROGRESS_VERIFIED"
                        if mode
                        ==
                        "CAPABILITY_COMPLETION"
                        else
                        "PROACTIVE_WORK_VERIFIED"
                    )

                    cycle[
                        "rollback"
                    ] = {
                        "success": True,
                        "status":
                            "NOT_REQUIRED",
                    }

                else:
                    should_rollback = (
                        changes[
                            "has_changes"
                        ]
                        and
                        not regressions[
                            "success"
                        ]
                    )

                    cycle[
                        "rollback"
                    ] = (
                        rollback(
                            cycle_id
                        )
                        if should_rollback
                        else
                        {
                            "success": True,
                            "status":
                                "NOT_REQUIRED_NO_REAL_REGRESSION",
                        }
                    )

                    if not regressions[
                        "success"
                    ]:
                        cycle[
                            "status"
                        ] = (
                            "REGRESSION_DETECTED"
                        )

                    elif (
                        mastermind.get(
                            "success"
                        )
                        and
                        not real_progress
                    ):
                        cycle[
                            "status"
                        ] = (
                            "NO_REAL_PROGRESS_VERIFIED"
                        )

                    else:
                        cycle[
                            "status"
                        ] = (
                            "DEGRADED_AFTER_REPAIR"
                        )

            self.good += int(
                cycle[
                    "success"
                ]
            )

            self.bad += int(
                not cycle[
                    "success"
                ]
            )

            cycle[
                "finished_at"
            ] = now()

            cycle[
                "notification"
            ] = notify(
                cycle
            )

            save_json(
                REPORT_FILE,
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
            cycle.update(
                {
                    "success":
                        False,

                    "status":
                        "AUTONOMOUS_CYCLE_EXCEPTION",

                    "error":
                        f"{type(error).__name__}: {error}",

                    "traceback":
                        traceback.format_exc(),

                    "finished_at":
                        now(),
                }
            )

            self.bad += 1

            save_json(
                REPORT_FILE,
                cycle,
            )

            self.save_state(
                "RUNNING_DEGRADED",
                cycle,
            )

            return cycle

    def once(
        self,
    ):
        self.save_state(
            "RUNNING"
        )

        return self.cycle()

    def forever(
        self,
    ):
        global STOP

        PID_FILE.write_text(
            str(
                os.getpid()
            ),
            encoding="utf-8",
        )

        self.save_state(
            "STARTING"
        )

        try:
            while not STOP:
                cycle = (
                    self.cycle()
                )

                print(
                    json.dumps(
                        {
                            "time":
                                now(),

                            "mode":
                                "AUTONOMOUS_COMPANY_WIDE",

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

                            "queue":
                                cycle.get(
                                    "queue_summary"
                                ),

                            "became_operational":
                                cycle.get(
                                    "capability_progress",
                                    {},
                                ).get(
                                    "became_operational",
                                    [],
                                ),

                            "regressions":
                                cycle.get(
                                    "regression_check",
                                    {},
                                ).get(
                                    "regressions",
                                    [],
                                ),
                        },
                        ensure_ascii=False,
                    ),
                    flush=True,
                )

                deadline = (
                    time.monotonic()
                    +
                    self.cycle_seconds
                )

                while (
                    not STOP
                    and
                    time.monotonic()
                    <
                    deadline
                ):
                    time.sleep(
                        min(
                            1,
                            max(
                                .05,
                                deadline
                                -
                                time.monotonic(),
                            ),
                        )
                    )

            self.save_state(
                "STOPPED"
            )

            return 0

        finally:
            try:
                PID_FILE.unlink(
                    missing_ok=True
                )
            except Exception:
                pass


class FullRuntime:

    def __init__(
        self,
    ):
        self.runtime_id = str(
            uuid.uuid4()
        )

    def execute(
        self,
        command,
        owner=OWNER,
    ):
        command = str(
            command
            or ""
        ).strip()

        state = {
            "runtime_id":
                self.runtime_id,

            "system":
                SYSTEM,

            "runtime":
                RUNTIME,

            "version":
                VERSION,

            "owner":
                owner,

            "command":
                command,

            "started_at":
                now(),

            "success":
                False,

            "status":
                "STARTING",

            "stages":
                {},
        }

        state_path = (
            RUNTIME_DIR
            /
            f"{self.runtime_id}.json"
        )

        save_json(
            state_path,
            state,
        )

        try:
            if not command:
                state[
                    "status"
                ] = (
                    "EMPTY_OWNER_COMMAND"
                )

                return state

            state[
                "stages"
            ][
                "core_files"
            ] = verify_core()

            if not state[
                "stages"
            ][
                "core_files"
            ][
                "success"
            ]:
                state[
                    "status"
                ] = (
                    "REQUIRED_FILES_MISSING"
                )

                return state

            owner_bridge = (
                OwnerBridge()
            )

            request = (
                owner_bridge.parse(
                    command
                )
            )

            command_type = str(
                request.get(
                    "type",
                    "GENERAL_OWNER_COMMAND",
                )
            ).upper()

            state[
                "stages"
            ][
                "command"
            ] = {
                "type":
                    command_type,

                "request":
                    request,
            }

            if command_type in {
                "STATUS",
                "SYSTEM_STATUS",
            }:
                result = (
                    owner_bridge.execute(
                        command,
                        owner,
                    )
                )

                state.update(
                    {
                        "result":
                            result,

                        "success":
                            bool(
                                result.get(
                                    "success"
                                )
                            ),

                        "status":
                            str(
                                result.get(
                                    "status"
                                )
                                or
                                (
                                    "COMPLETED"
                                    if result.get(
                                        "success"
                                    )
                                    else
                                    "FAILED"
                                )
                            ),
                    }
                )

                return state

            result = (
                Mastermind()
                .execute(
                    command,
                    request,
                    self.runtime_id,
                    owner,
                )
            )

            verification = (
                verify_mastermind_result(
                    command_type,
                    result,
                )
            )

            state[
                "stages"
            ][
                "mastermind"
            ] = result

            state[
                "stages"
            ][
                "verification"
            ] = verification

            state.update(
                {
                    "result":
                        result,

                    "success":
                        bool(
                            verification.get(
                                "success"
                            )
                        ),

                    "status":
                        str(
                            verification.get(
                                "status",
                                "FAILED",
                            )
                        ),
                }
            )

            if (
                command_type
                ==
                "CREATE_GAME"
                and
                verification.get(
                    "success"
                )
            ):
                state.update(
                    {
                        "artifact":
                            verification.get(
                                "artifact",
                                {},
                            ).get(
                                "artifact"
                            ),

                        "game_path":
                            verification.get(
                                "publication",
                                {},
                            ).get(
                                "game_path"
                            ),

                        "public_url":
                            verification.get(
                                "publication",
                                {},
                            ).get(
                                "public_url"
                            ),

                        "published":
                            True,
                    }
                )

            return state

        except Exception as error:
            state.update(
                {
                    "success":
                        False,

                    "status":
                        "RUNTIME_EXCEPTION",

                    "error":
                        f"{type(error).__name__}: {error}",

                    "traceback":
                        traceback.format_exc(),
                }
            )

            return state

        finally:
            state[
                "finished_at"
            ] = now()

            save_json(
                state_path,
                state,
            )


def execute_full_factory(
    command,
    owner=OWNER,
    **kwargs,
):
    return FullRuntime().execute(
        command,
        owner,
    )


def execute_owner_runtime(
    command,
    owner=OWNER,
    **kwargs,
):
    return execute_full_factory(
        command,
        owner,
    )


def execute(
    command,
    owner=OWNER,
    **kwargs,
):
    return execute_full_factory(
        command,
        owner,
    )


def run(
    command,
    owner=OWNER,
    **kwargs,
):
    return execute_full_factory(
        command,
        owner,
    )


def autonomous_status():
    state = load_json(
        STATE_FILE,
        {},
    )

    pid = state.get(
        "pid"
    )

    alive = False

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

            alive = True

        except Exception:
            pass

    state[
        "process_alive"
    ] = alive

    return state


def install_service():
    if os.geteuid() != 0:
        return {
            "success": False,
            "status":
                "ROOT_REQUIRED",
        }

    python_path = (
        shutil.which(
            "python3"
        )
        or
        sys.executable
    )

    service_text = f"""[Unit]
Description=MAJD Sovereign Autonomous Runtime
After=network-online.target docker.service
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory={ROOT}
ExecStart={python_path} {Path(__file__).resolve()} --autonomous
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
"""

    SERVICE_FILE.write_text(
        service_text,
        encoding="utf-8",
    )

    daemon_reload = run_process(
        [
            "systemctl",
            "daemon-reload",
        ],
        30,
    )

    enable = run_process(
        [
            "systemctl",
            "enable",
            "--now",
            SERVICE_NAME,
        ],
        60,
    )

    service_status = run_process(
        [
            "systemctl",
            "--no-pager",
            "--full",
            "status",
            SERVICE_NAME,
        ],
        30,
    )

    return {
        "success":
            daemon_reload.get(
                "success"
            )
            and
            enable.get(
                "success"
            ),

        "daemon_reload":
            daemon_reload,

        "enable":
            enable,

        "service_status":
            service_status,
    }


def shutdown_signal(
    signum,
    frame,
):
    global STOP

    STOP = True

    audit(
        "SHUTDOWN_SIGNAL",
        {
            "signal":
                signum
        },
    )


def main():
    signal.signal(
        signal.SIGTERM,
        shutdown_signal,
    )

    signal.signal(
        signal.SIGINT,
        shutdown_signal,
    )

    parser = (
        argparse.ArgumentParser()
    )

    parser.add_argument(
        "command",
        nargs="*",
    )

    parser.add_argument(
        "--owner",
        default=
            OWNER,
    )

    parser.add_argument(
        "--autonomous",
        action=
            "store_true",
    )

    parser.add_argument(
        "--once",
        action=
            "store_true",
    )

    parser.add_argument(
        "--autonomous-status",
        action=
            "store_true",
    )

    parser.add_argument(
        "--install-service",
        action=
            "store_true",
    )

    parser.add_argument(
        "--service-status",
        action=
            "store_true",
    )

    parser.add_argument(
        "--cycle-seconds",
        type=
            int,
        default=
            CYCLE_SECONDS,
    )

    args = (
        parser.parse_args()
    )

    if args.install_service:
        result = (
            install_service()
        )

    elif args.service_status:
        result = run_process(
            [
                "systemctl",
                "--no-pager",
                "--full",
                "status",
                SERVICE_NAME,
            ],
            30,
        )

    elif args.autonomous_status:
        result = (
            autonomous_status()
        )

    elif args.once:
        result = (
            AutonomousRuntime(
                args.owner,
                args.cycle_seconds,
            ).once()
        )

    elif (
        args.autonomous
        or
        not args.command
    ):
        return (
            AutonomousRuntime(
                args.owner,
                args.cycle_seconds,
            ).forever()
        )

    else:
        result = (
            execute_full_factory(
                " ".join(
                    args.command
                ).strip(),
                args.owner,
            )
        )

    print(
        json.dumps(
            jsonable(
                result
            ),
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


if __name__ == "__main__":
    raise SystemExit(
        main()
    )

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
import smtplib
import subprocess
import sys
import time
import traceback
import urllib.request
import uuid
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple

ROOT = Path(__file__).resolve().parent
F01 = ROOT / "MAJD-AI-MASTERMIND-01.py"
F02C = ROOT / "MAJD-AI-SOVEREIGN-COMPANY-02.py"
F02O = ROOT / "MAJD-OWNER-COMMAND-CENTER-02.py"
F03 = ROOT / "MAJD-REAL-GAME-EXECUTOR-03.py"
F04 = ROOT / "MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py"

STATE = ROOT / "majd_factory_state"
AUTO = STATE / "autonomous"
AUDIT = STATE / "audit"
REPORT = STATE / "reports"
BACKUP = STATE / "backups"
QUEUE = STATE / "work_queue"
OUTPUT = ROOT / "majd_game_output"

for p in (
    STATE,
    AUTO,
    AUDIT,
    REPORT,
    BACKUP,
    QUEUE,
    OUTPUT,
):
    p.mkdir(
        parents=True,
        exist_ok=True,
    )

STATE_FILE = AUTO / "state.json"
REPORT_FILE = REPORT / "latest.json"
AUDIT_FILE = AUDIT / "runtime.jsonl"
QUEUE_FILE = QUEUE / "capabilities.json"

SERVICE = (
    "/etc/systemd/system/"
    "majd-autonomous.service"
)

SYSTEM = "MAJD-GAME-FACTORY"
RUNTIME = "MAJD-FULL-EXECUTION-RUNTIME"

VERSION = (
    "6.0.0-"
    "SOVEREIGN-AUTONOMOUS"
)

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

STOP = False


# ============================================================
# SAFE DEPENDENCIES
# ============================================================

SAFE_DEPS = {
    "fastapi":
        "fastapi>=0.115,<1",

    "uvicorn":
        "uvicorn[standard]>=0.30,<1",

    "pydantic":
        "pydantic>=2.7,<3",

    "starlette":
        "starlette>=0.37,<1",

    "requests":
        "requests>=2.31,<3",

    "httpx":
        "httpx>=0.27,<1",

    "aiohttp":
        "aiohttp>=3.9,<4",

    "psutil":
        "psutil>=5.9,<8",

    "yaml":
        "PyYAML>=6,<7",

    "dotenv":
        "python-dotenv>=1,<2",
}


SOURCE_EXT = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".json",
    ".html",
    ".css",
    ".scss",
    ".yml",
    ".yaml",
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
}


SECRET_FILES = {
    ".env",
    ".env.local",
    ".env.production",
    "credentials.json",
    "secrets.json",
}


# ============================================================
# BASIC HELPERS
# ============================================================

def now() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat()


def save_json(
    path: Path,
    data: Dict[str, Any],
) -> None:

    tmp = path.with_suffix(
        path.suffix + ".tmp"
    )

    with tmp.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

    tmp.replace(
        path
    )


def load_json(
    path: Path,
    default: Optional[
        Dict[str, Any]
    ] = None,
) -> Dict[str, Any]:

    default = default or {}

    try:

        with path.open(
            "r",
            encoding="utf-8",
        ) as f:

            value = json.load(
                f
            )

        return (
            value
            if isinstance(
                value,
                dict,
            )
            else dict(
                default
            )
        )

    except Exception:

        return dict(
            default
        )


def audit(
    event: str,
    data: Optional[
        Dict[str, Any]
    ] = None,
) -> None:

    with AUDIT_FILE.open(
        "a",
        encoding="utf-8",
    ) as f:

        f.write(
            json.dumps(
                {
                    "time":
                        now(),

                    "event":
                        event,

                    "data":
                        data or {},
                },
                ensure_ascii=False,
                default=str,
            )
            +
            "\n"
        )


def run_process(
    cmd: List[str],
    timeout: int = 120,
) -> Dict[str, Any]:

    try:

        process = subprocess.run(
            cmd,
            cwd=str(
                ROOT
            ),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

        return {
            "success":
                process.returncode == 0,

            "returncode":
                process.returncode,

            "stdout":
                process.stdout[
                    -12000:
                ],

            "stderr":
                process.stderr[
                    -12000:
                ],

            "command":
                cmd,
        }

    except Exception as error:

        return {
            "success":
                False,

            "error":
                (
                    f"{type(error).__name__}: "
                    f"{error}"
                ),

            "command":
                cmd,
        }


def http_probe(
    url: str,
) -> Dict[str, Any]:

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent":
                f"{RUNTIME}/{VERSION}"
        },
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=12,
        ) as response:

            body = response.read(
                65536
            ).decode(
                "utf-8",
                "replace",
            )

            code = int(
                getattr(
                    response,
                    "status",
                    200,
                )
            )

            return {
                "success":
                    200 <= code < 400,

                "status_code":
                    code,

                "url":
                    url,

                "body":
                    body[:4000],
            }

    except Exception as error:

        return {
            "success":
                False,

            "url":
                url,

            "error":
                (
                    f"{type(error).__name__}: "
                    f"{error}"
                ),
        }


# ============================================================
# SOURCE DISCOVERY
# ============================================================

def source_files() -> List[Path]:

    result = []

    for path in ROOT.rglob(
        "*"
    ):

        if (
            not path.is_file()
            or
            path.suffix.lower()
            not in SOURCE_EXT
            or
            path.name
            in SECRET_FILES
        ):

            continue

        try:

            relative = (
                path.relative_to(
                    ROOT
                )
            )

        except ValueError:

            continue

        if any(
            part in IGNORE_DIRS
            for part
            in relative.parts
        ):

            continue

        result.append(
            path
        )

    return sorted(
        result
    )


def sha(
    path: Path,
) -> str:

    digest = (
        hashlib.sha256()
    )

    with path.open(
        "rb"
    ) as f:

        for chunk in iter(
            lambda:
                f.read(
                    1024 * 1024
                ),
            b"",
        ):

            digest.update(
                chunk
            )

    return digest.hexdigest()


# ============================================================
# BACKUP / ROLLBACK
# ============================================================

def backup(
    cycle: str,
) -> Dict[str, Any]:

    base = (
        BACKUP
        /
        cycle
    )

    base.mkdir(
        parents=True,
        exist_ok=True,
    )

    manifest = {
        "files":
            {}
    }

    for path in source_files():

        relative = str(
            path.relative_to(
                ROOT
            )
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
            relative
        ] = {
            "sha256":
                sha(
                    path
                )
        }

    save_json(
        base
        /
        "manifest.json",

        manifest,
    )

    return {
        "success":
            True,

        "path":
            str(
                base
            ),

        "count":
            len(
                manifest[
                    "files"
                ]
            ),
    }


def rollback(
    cycle: str,
) -> Dict[str, Any]:

    base = (
        BACKUP
        /
        cycle
    )

    manifest = load_json(
        base
        /
        "manifest.json",
        {},
    )

    originals = set(
        manifest.get(
            "files",
            {},
        )
    )

    if not originals:

        return {
            "success":
                False,

            "status":
                "NO_BACKUP",
        }

    for relative in originals:

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
        originals
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
        "success":
            True,

        "status":
            "ROLLED_BACK",
    }


# ============================================================
# CORE VERIFICATION
# ============================================================

def verify_core() -> Dict[str, Any]:

    required = [
        F01,
        F02O,
        F03,
        F04,
    ]

    important = [
        F02C,
    ]

    missing = [
        path.name

        for path
        in required

        if (
            not path.exists()
            or
            path.stat().st_size
            ==
            0
        )
    ]

    return {
        "success":
            not missing,

        "missing":
            missing,

        "files":
            [
                {
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
                }

                for path
                in (
                    required
                    +
                    important
                )
            ],
    }


# ============================================================
# PYTHON SYNTAX
# ============================================================

def verify_syntax() -> Dict[str, Any]:

    failed = []
    checked = []

    for path in source_files():

        if (
            path.suffix.lower()
            !=
            ".py"
        ):

            continue

        result = run_process(
            [
                sys.executable,
                "-m",
                "py_compile",
                str(
                    path
                ),
            ],
            30,
        )

        relative = str(
            path.relative_to(
                ROOT
            )
        )

        checked.append(
            {
                "file":
                    relative,

                "success":
                    result[
                        "success"
                    ],

                "stderr":
                    result.get(
                        "stderr",
                        "",
                    ),
            }
        )

        if not result[
            "success"
        ]:

            failed.append(
                relative
            )

    return {
        "success":
            not failed,

        "failed":
            failed,

        "checked":
            checked,
    }


# ============================================================
# DEPENDENCY DISCOVERY / REPAIR
# ============================================================

def import_roots(
    path: Path,
) -> Set[str]:

    try:

        tree = ast.parse(
            path.read_text(
                encoding="utf-8"
            )
        )

    except Exception:

        return set()

    roots = set()

    for node in ast.walk(
        tree
    ):

        if isinstance(
            node,
            ast.Import,
        ):

            roots.update(
                alias.name.split(
                    "."
                )[0]

                for alias
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

            roots.add(
                node.module.split(
                    "."
                )[0]
            )

    return roots


def dependency_state() -> Dict[str, Any]:

    roots = set()

    for path in source_files():

        if (
            path.suffix.lower()
            ==
            ".py"
        ):

            roots |= (
                import_roots(
                    path
                )
            )

    missing = []

    for (
        root,
        package,
    ) in SAFE_DEPS.items():

        if (
            root in roots
            and
            importlib.util.find_spec(
                root
            )
            is None
        ):

            missing.append(
                {
                    "module":
                        root,

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


def repair_dependencies() -> Dict[str, Any]:

    before = (
        dependency_state()
    )

    if before[
        "success"
    ]:

        return {
            "success":
                True,

            "status":
                "HEALTHY",

            "installed":
                [],
        }

    installed = []
    failed = []

    for item in before[
        "missing"
    ]:

        result = run_process(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                item[
                    "package"
                ],
            ],
            300,
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

            "success":
                result[
                    "success"
                ],

            "stderr":
                result.get(
                    "stderr",
                    "",
                ),
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

    after = (
        dependency_state()
    )

    return {
        "success":
            (
                not failed
                and
                after[
                    "success"
                ]
            ),

        "status":
            (
                "REPAIRED"
                if (
                    not failed
                    and
                    after[
                        "success"
                    ]
                )
                else
                "INCOMPLETE"
            ),

        "installed":
            installed,

        "failed":
            failed,

        "after":
            after,
    }


# ============================================================
# DOCKER
# ============================================================

def docker_state() -> Dict[str, Any]:

    result = run_process(
        [
            "docker",
            "ps",
            "--format",
            "{{.Names}}|"
            "{{.Status}}|"
            "{{.Ports}}",
        ],
        30,
    )

    if not result[
        "success"
    ]:

        return {
            "success":
                False,

            "error":
                (
                    result.get(
                        "stderr"
                    )
                    or
                    result.get(
                        "error"
                    )
                ),
        }

    containers = []

    for line in result[
        "stdout"
    ].splitlines():

        parts = line.split(
            "|",
            2,
        )

        if line.strip():

            containers.append(
                {
                    "name":
                        parts[
                            0
                        ],

                    "status":
                        (
                            parts[
                                1
                            ]
                            if len(
                                parts
                            )
                            > 1
                            else ""
                        ),

                    "ports":
                        (
                            parts[
                                2
                            ]
                            if len(
                                parts
                            )
                            > 2
                            else ""
                        ),
                }
            )

    names = {
        item[
            "name"
        ]

        for item
        in containers
    }

    missing = sorted(
        {
            "majd-ai-core",
            "majd-web-ui",
        }
        -
        names
    )

    return {
        "success":
            not missing,

        "containers":
            containers,

        "missing_expected":
            missing,
    }


def recover_docker() -> Dict[str, Any]:

    before = (
        docker_state()
    )

    if before[
        "success"
    ]:

        return {
            "success":
                True,

            "status":
                "HEALTHY",
        }

    actions = []

    for name in before.get(
        "missing_expected",
        [],
    ):

        result = run_process(
            [
                "docker",
                "start",
                name,
            ],
            60,
        )

        actions.append(
            {
                "name":
                    name,

                "success":
                    result[
                        "success"
                    ],
            }
        )

    after = (
        docker_state()
    )

    return {
        "success":
            after[
                "success"
            ],

        "actions":
            actions,

        "after":
            after,
    }


# ============================================================
# COMPANY INSPECTION
# ============================================================

def parse_json_output(
    text: str,
) -> Optional[
    Dict[str, Any]
]:

    text = text.strip()

    try:

        value = json.loads(
            text
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

    start = text.find(
        "{"
    )

    end = text.rfind(
        "}"
    )

    if (
        start >= 0
        and
        end > start
    ):

        try:

            value = json.loads(
                text[
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

            pass

    return None


def inspect_company() -> Dict[str, Any]:

    if not F02C.exists():

        return {
            "success":
                False,

            "status":
                "COMPANY_FILE_MISSING",
        }

    health = run_process(
        [
            sys.executable,
            str(
                F02C
            ),
            "--health",
        ],
        180,
    )

    self_test = run_process(
        [
            sys.executable,
            str(
                F02C
            ),
            "--self-test",
        ],
        240,
    )

    health_json = (
        parse_json_output(
            health.get(
                "stdout",
                "",
            )
        )
    )

    self_test_json = (
        parse_json_output(
            self_test.get(
                "stdout",
                "",
            )
        )
    )

    return {
        "success":
            bool(
                health[
                    "success"
                ]
                and
                self_test[
                    "success"
                ]
                and
                health_json
                and
                self_test_json
            ),

        "health":
            health_json,

        "self_test":
            self_test_json,

        "health_process":
            health,

        "self_test_process":
            self_test,
    }


# ============================================================
# CAPABILITY GAP DISCOVERY
# ============================================================

def extract_gaps(
    company: Dict[str, Any],
) -> List[
    Dict[str, Any]
]:

    gaps = []

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

            capability_id = (
                value.get(
                    "capability_id"
                )
                or
                value.get(
                    "capability"
                )
                or
                value.get(
                    "id"
                )
                or
                value.get(
                    "name"
                )
            )

            if (
                capability_id
                and
                status
                in {
                    "UNAVAILABLE",
                    "FAILED",
                    "MISSING",
                    "DEGRADED",
                    "NOT_CONFIGURED",
                }
            ):

                reason = str(
                    value.get(
                        "reason"
                    )
                    or
                    value.get(
                        "message"
                    )
                    or
                    (
                        value.get(
                            "health"
                        )
                        or
                        {}
                    ).get(
                        "message"
                    )
                    or
                    ""
                )

                owner_required = any(
                    item
                    in reason.lower()

                    for item
                    in (
                        "api key",
                        "credential",
                        "oauth",
                        "identity verification",
                        "merchant approval",
                        "legal approval",
                        "bank approval",
                    )
                )

                priority = (
                    10
                    if bool(
                        value.get(
                            "required"
                        )
                    )
                    else 50
                )

                if any(
                    item
                    in str(
                        capability_id
                    ).upper()

                    for item
                    in (
                        "OWNER",
                        "AUTHORITY",
                        "AUDIT",
                        "SECURITY",
                        "BUILD",
                        "DEPLOY",
                        "TEST",
                        "EXECUTOR",
                        "BRIDGE",
                        "PUBLISH",
                    )
                ):

                    priority -= 5

                gaps.append(
                    {
                        "capability_id":
                            str(
                                capability_id
                            ),

                        "status":
                            status,

                        "required":
                            bool(
                                value.get(
                                    "required"
                                )
                            ),

                        "reason":
                            reason,

                        "adapter":
                            value.get(
                                "adapter"
                            ),

                        "engine":
                            value.get(
                                "engine"
                            ),

                        "owner_required":
                            owner_required,

                        "priority":
                            max(
                                1,
                                priority,
                            ),
                    }
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

    unique = {}

    for gap in gaps:

        unique[
            (
                gap[
                    "capability_id"
                ],
                gap[
                    "status"
                ],
            )
        ] = gap

    return sorted(
        unique.values(),
        key=lambda item: (
            item[
                "owner_required"
            ],
            item[
                "priority"
            ],
            item[
                "capability_id"
            ],
        ),
    )


# ============================================================
# CAPABILITY WORK QUEUE
# ============================================================

def update_queue(
    gaps: List[
        Dict[str, Any]
    ],
) -> Dict[str, Any]:

    old = load_json(
        QUEUE_FILE,
        {},
    )

    old_map = {
        item.get(
            "capability_id"
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

    for gap in gaps:

        previous = old_map.get(
            gap[
                "capability_id"
            ],
            {},
        )

        item = dict(
            gap
        )

        item[
            "attempts"
        ] = int(
            previous.get(
                "attempts",
                0,
            )
            or
            0
        )

        item[
            "last_result"
        ] = previous.get(
            "last_result"
        )

        item[
            "last_attempt_at"
        ] = previous.get(
            "last_attempt_at"
        )

        items.append(
            item
        )

    data = {
        "updated_at":
            now(),

        "total":
            len(
                items
            ),

        "owner_required":
            sum(
                1
                for item
                in items
                if item[
                    "owner_required"
                ]
            ),

        "autonomous":
            sum(
                1
                for item
                in items
                if not item[
                    "owner_required"
                ]
            ),

        "items":
            items,
    }

    save_json(
        QUEUE_FILE,
        data,
    )

    return data


def select_batch(
    queue: Dict[str, Any],
) -> List[
    Dict[str, Any]
]:

    items = [
        item

        for item
        in queue.get(
            "items",
            [],
        )

        if not item.get(
            "owner_required"
        )
    ]

    items.sort(
        key=lambda item: (
            int(
                item.get(
                    "priority",
                    50,
                )
            ),
            int(
                item.get(
                    "attempts",
                    0,
                )
            ),
            item.get(
                "capability_id",
                "",
            ),
        )
    )

    return items[
        :MAX_BATCH
    ]


# ============================================================
# MODULE LOADER
# ============================================================

def load_module(
    path: Path,
    name: str,
) -> Any:

    spec = (
        importlib.util
        .spec_from_file_location(
            name,
            str(
                path
            ),
        )
    )

    if (
        spec is None
        or
        spec.loader is None
    ):

        raise RuntimeError(
            f"cannot load "
            f"{path.name}"
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

        if callable(
            value
        ):

            return value

    return None


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

    return function(
        **{
            key:
                value

            for (
                key,
                value,
            )
            in values.items()

            if (
                accepts_kwargs
                or
                key
                in signature.parameters
            )
        }
    )


# ============================================================
# MASTERMIND
# ============================================================

class Mastermind:

    def __init__(
        self,
    ):

        self.dep = (
            repair_dependencies()
        )

        self.module = (
            load_module(
                F01,
                (
                    "majd_mastermind_"
                    +
                    uuid.uuid4().hex
                ),
            )
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
            (
                "execute_request",
                "process_request",
                "execute_game_request",
                "run_request",
                "run",
                "execute",
            ),
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
                            owner,
                    },
                )

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
                    "MASTERMIND_INTERFACE_MISSING",

                "dependency_repair":
                    self.dep,
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
                            OUTPUT
                        ),
                },
            )

            return (
                result
                if isinstance(
                    result,
                    dict,
                )
                else
                {
                    "success":
                        False,

                    "status":
                        "INVALID_MASTERMIND_RESULT",
                }
            )

        except ModuleNotFoundError as error:

            dependency_repair = (
                repair_dependencies()
            )

            if dependency_repair[
                "success"
            ]:

                try:

                    self.module = (
                        load_module(
                            F01,
                            (
                                "majd_mastermind_retry_"
                                +
                                uuid.uuid4().hex
                            ),
                        )
                    )

                    function = find_callable(
                        self.module,
                        (
                            "execute_request",
                            "process_request",
                            "execute_game_request",
                            "run_request",
                            "run",
                            "execute",
                        ),
                    )

                    if function:

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
                                        OUTPUT
                                    ),
                            },
                        )

                        return (
                            result
                            if isinstance(
                                result,
                                dict,
                            )
                            else
                            {
                                "success":
                                    False,

                                "status":
                                    "INVALID_MASTERMIND_RESULT",
                            }
                        )

                except Exception as retry_error:

                    return {
                        "success":
                            False,

                        "status":
                            "MASTERMIND_RETRY_FAILED",

                        "error":
                            (
                                f"{type(retry_error).__name__}: "
                                f"{retry_error}"
                            ),

                        "traceback":
                            traceback.format_exc(),
                    }

            return {
                "success":
                    False,

                "status":
                    "DEPENDENCY_REPAIR_FAILED",

                "error":
                    str(
                        error
                    ),

                "dependency_repair":
                    dependency_repair,
            }

        except Exception as error:

            return {
                "success":
                    False,

                "status":
                    "MASTERMIND_EXCEPTION",

                "error":
                    (
                        f"{type(error).__name__}: "
                        f"{error}"
                    ),

                "traceback":
                    traceback.format_exc(),
            }


# ============================================================
# AUTONOMOUS POLICY
# ============================================================

def policy() -> Dict[str, Any]:

    return {
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

        "allow_tests":
            True,

        "allow_build":
            True,

        "allow_routine_deployment":
            True,

        "allow_safe_dependency_repair":
            True,

        "require_real_verification":
            True,

        "never_fake_operational":
            True,

        "rollback_on_failed_change":
            True,

        "protect_owner_authority":
            True,

        "protect_platform_secrets":
            True,

        "do_not_ask_owner_for_code":
            True,

        "owner_only_for_true_external_blockers":
            True,
    }


# ============================================================
# OBJECTIVE
# ============================================================

def objective(
    cycle: str,
    inspection: Dict[str, Any],
    batch: List[
        Dict[str, Any]
    ],
    proactive: bool = False,
) -> Tuple[
    str,
    Dict[str, Any],
]:

    kind = (
        "AUTONOMOUS_CONTINUOUS_IMPROVEMENT"
        if proactive
        else
        "AUTONOMOUS_REPAIR_AND_COMPLETION"
    )

    request = {
        "type":
            kind,

        "cycle_id":
            cycle,

        "owner":
            OWNER,

        "autonomous":
            True,

        "work_items":
            batch,

        "policy":
            policy(),

        "snapshot": {
            "local_api":
                inspection[
                    "local_api"
                ],

            "official_platform":
                inspection[
                    "official_platform"
                ],

            "docker":
                inspection[
                    "docker"
                ],

            "company_summary":
                inspection[
                    "company_summary"
                ],
        },
    }

    command = (
        "MAJD SOVEREIGN AUTONOMOUS OPERATION. "
        "تشغيل مجد السيادي تلقائياً. "
        "Inspect the repository and supplied capability work items. "
        "Build and register real internal adapters where possible, "
        "repair broken code, connect disconnected integrations, "
        "complete UI/runtime/tests/build/deploy work, test every "
        "change and verify real runtime evidence. Never return fake "
        "success. Do not ask the owner for code or routine approvals. "
        "If a capability truly requires an external credential, "
        "account, legal, financial or identity action, mark only that "
        "capability OWNER_ACTION_REQUIRED and continue the rest. "
        "Return structured Arabic and English proof of changed files, "
        "adapters activated, tests, blockers and final status."
    )

    return (
        command,
        request,
    )


# ============================================================
# OWNER REPORT / EMAIL / WHATSAPP
# ============================================================

def notify(
    cycle: Dict[str, Any],
) -> Dict[str, Any]:

    ar = (
        "تقرير مجد\n"
        f"الحالة: "
        f"{cycle.get('status')}\n"
        f"الوضع: "
        f"{cycle.get('mode_executed')}\n"
        f"النجاح: "
        f"{cycle.get('success')}\n"
        f"قائمة العمل: "
        f"{cycle.get('queue_summary', {}).get('total', 0)}\n"
        f"متطلبات خارجية: "
        f"{cycle.get('queue_summary', {}).get('owner_required', 0)}"
    )

    en = (
        "MAJD Report\n"
        f"Status: "
        f"{cycle.get('status')}\n"
        f"Mode: "
        f"{cycle.get('mode_executed')}\n"
        f"Success: "
        f"{cycle.get('success')}\n"
        f"Work queue: "
        f"{cycle.get('queue_summary', {}).get('total', 0)}\n"
        f"External blockers: "
        f"{cycle.get('queue_summary', {}).get('owner_required', 0)}"
    )

    output = {
        "report_ar":
            ar,

        "report_en":
            en,

        "email": {
            "success":
                False,

            "status":
                "NOT_CONFIGURED",
        },

        "whatsapp": {
            "success":
                False,

            "status":
                "NOT_CONFIGURED",
        },
    }

    host = os.getenv(
        "MAJD_SMTP_HOST",
        "",
    ).strip()

    recipient = os.getenv(
        "MAJD_OWNER_EMAIL",
        "",
    ).strip()

    sender = os.getenv(
        "MAJD_REPORT_FROM_EMAIL",
        os.getenv(
            "MAJD_SMTP_USERNAME",
            "",
        ),
    ).strip()

    if (
        host
        and
        recipient
        and
        sender
    ):

        try:

            message = (
                EmailMessage()
            )

            message[
                "Subject"
            ] = (
                "MAJD Autonomous Report "
                "| تقرير مجد"
            )

            message[
                "From"
            ] = sender

            message[
                "To"
            ] = recipient

            message.set_content(
                ar
                +
                "\n\n"
                +
                en
            )

            with smtplib.SMTP(
                host,
                int(
                    os.getenv(
                        "MAJD_SMTP_PORT",
                        "587",
                    )
                ),
                timeout=20,
            ) as smtp:

                if os.getenv(
                    "MAJD_SMTP_STARTTLS",
                    "true",
                ).lower() in (
                    "1",
                    "true",
                    "yes",
                    "on",
                ):

                    smtp.starttls()

                username = os.getenv(
                    "MAJD_SMTP_USERNAME",
                    "",
                )

                if username:

                    smtp.login(
                        username,
                        os.getenv(
                            "MAJD_SMTP_PASSWORD",
                            "",
                        ),
                    )

                smtp.send_message(
                    message
                )

            output[
                "email"
            ] = {
                "success":
                    True,

                "status":
                    "SENT",
            }

        except Exception as error:

            output[
                "email"
            ] = {
                "success":
                    False,

                "status":
                    "FAILED",

                "error":
                    str(
                        error
                    ),
            }

    token = os.getenv(
        "MAJD_WHATSAPP_TOKEN",
        "",
    ).strip()

    phone_id = os.getenv(
        "MAJD_WHATSAPP_PHONE_NUMBER_ID",
        "",
    ).strip()

    to_number = os.getenv(
        "MAJD_OWNER_WHATSAPP",
        "",
    ).strip()

    if (
        token
        and
        phone_id
        and
        to_number
    ):

        try:

            url = (
                "https://graph.facebook.com/"
                f"{os.getenv('MAJD_WHATSAPP_API_VERSION', 'v23.0')}/"
                f"{phone_id}/messages"
            )

            payload = {
                "messaging_product":
                    "whatsapp",

                "to":
                    to_number,

                "type":
                    "text",

                "text": {
                    "preview_url":
                        False,

                    "body":
                        ar
                        +
                        "\n\n"
                        +
                        en,
                },
            }

            request = urllib.request.Request(
                url,
                data=json.dumps(
                    payload
                ).encode(),
                method="POST",
                headers={
                    "Authorization":
                        f"Bearer {token}",

                    "Content-Type":
                        "application/json",
                },
            )

            with urllib.request.urlopen(
                request,
                timeout=20,
            ) as response:

                response.read()

            output[
                "whatsapp"
            ] = {
                "success":
                    True,

                "status":
                    "SENT",
            }

        except Exception as error:

            output[
                "whatsapp"
            ] = {
                "success":
                    False,

                "status":
                    "FAILED",

                "error":
                    str(
                        error
                    ),
            }

    return output


# ============================================================
# AUTONOMOUS RUNTIME
# ============================================================

class AutonomousRuntime:

    def __init__(
        self,
        owner: str = OWNER,
        cycle_seconds: int = CYCLE_SECONDS,
    ):

        self.owner = owner

        self.cycle_seconds = max(
            30,
            cycle_seconds,
        )

        self.session_id = str(
            uuid.uuid4()
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
            or
            0
        )

        self.good = int(
            old.get(
                "successful_cycles",
                0,
            )
            or
            0
        )

        self.bad = int(
            old.get(
                "failed_cycles",
                0,
            )
            or
            0
        )

    def inspect(
        self,
    ) -> Dict[str, Any]:

        dependencies = (
            repair_dependencies()
        )

        docker_before = (
            docker_state()
        )

        docker_recovery = (
            recover_docker()
            if not docker_before[
                "success"
            ]
            else
            {
                "success":
                    True,

                "status":
                    "HEALTHY",
            }
        )

        company = (
            inspect_company()
        )

        gaps = (
            extract_gaps(
                company
            )
        )

        queue = (
            update_queue(
                gaps
            )
        )

        return {
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

            "sovereign_company":
                company,

            "company_summary": {
                "gaps":
                    len(
                        gaps
                    ),

                "required":
                    sum(
                        1
                        for gap
                        in gaps
                        if gap[
                            "required"
                        ]
                    ),

                "owner_required":
                    sum(
                        1
                        for gap
                        in gaps
                        if gap[
                            "owner_required"
                        ]
                    ),
            },

            "work_queue":
                queue,
        }

    def save_state(
        self,
        status: str,
        cycle: Optional[
            Dict[str, Any]
        ] = None,
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

                "mode":
                    "AUTONOMOUS_COMPANY_WIDE",

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

    def verify(
        self,
    ) -> Dict[str, Any]:

        inspection = (
            self.inspect()
        )

        success = all(
            inspection[
                key
            ].get(
                "success"
            )

            for key
            in (
                "core_files",
                "python_syntax",
                "dependencies",
                "local_api",
                "official_platform",
                "docker",
                "sovereign_company",
            )
        )

        return {
            "success":
                success,

            "status":
                (
                    "VERIFIED"
                    if success
                    else
                    "VERIFICATION_FAILED"
                ),

            "inspection":
                inspection,
        }

    def execute_objective(
        self,
        cycle: str,
        command: str,
        request: Dict[str, Any],
        kind: str,
    ) -> Dict[str, Any]:

        attempts = []

        for number in range(
            1,
            MAX_ATTEMPTS + 1,
        ):

            try:

                result = (
                    Mastermind()
                    .execute(
                        command,
                        request,
                        (
                            f"AUTO-"
                            f"{cycle}-"
                            f"{kind}-"
                            f"{number}"
                        ),
                        self.owner,
                    )
                )

            except Exception as error:

                result = {
                    "success":
                        False,

                    "status":
                        "MASTER_EXCEPTION",

                    "error":
                        str(
                            error
                        ),
                }

            attempts.append(
                {
                    "attempt":
                        number,

                    "result":
                        result,
                }
            )

            if result.get(
                "success"
            ):

                return {
                    "success":
                        True,

                    "status":
                        "EXECUTED",

                    "attempts":
                        attempts,

                    "result":
                        result,
                }

            time.sleep(
                2
            )

        return {
            "success":
                False,

            "status":
                "FAILED",

            "attempts":
                attempts,
        }

    def cycle(
        self,
    ) -> Dict[str, Any]:

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

            inspection = (
                self.inspect()
            )

            queue = inspection[
                "work_queue"
            ]

            batch = (
                select_batch(
                    queue
                )
            )

            cycle[
                "inspection"
            ] = inspection

            cycle[
                "queue_summary"
            ] = {
                key:
                    queue[
                        key
                    ]

                for key
                in (
                    "total",
                    "owner_required",
                    "autonomous",
                )
            }

            cycle[
                "selected_work"
            ] = batch

            infrastructure_ok = all(
                inspection[
                    key
                ].get(
                    "success"
                )

                for key
                in (
                    "core_files",
                    "python_syntax",
                    "dependencies",
                    "local_api",
                    "official_platform",
                    "docker",
                    "sovereign_company",
                )
            )

            proactive = (
                not batch
                and
                infrastructure_ok
            )

            cycle[
                "mode_executed"
            ] = (
                "PROACTIVE"
                if proactive
                else
                "REPAIR"
            )

            backup_result = (
                backup(
                    cycle_id
                )
            )

            cycle[
                "backup"
            ] = backup_result

            (
                command,
                request,
            ) = objective(
                cycle_id,
                inspection,
                batch,
                proactive=
                    proactive,
            )

            mastermind = (
                self.execute_objective(
                    cycle_id,
                    command,
                    request,
                    cycle[
                        "mode_executed"
                    ],
                )
            )

            cycle[
                "mastermind"
            ] = mastermind

            verification = (
                self.verify()
            )

            cycle[
                "verification"
            ] = verification

            if (
                mastermind.get(
                    "success"
                )
                and
                verification.get(
                    "success"
                )
            ):

                cycle[
                    "success"
                ] = True

                cycle[
                    "status"
                ] = (
                    "PROACTIVE_WORK_COMPLETED"
                    if proactive
                    else
                    "REPAIRED_AND_VERIFIED"
                )

                self.good += 1

            else:

                cycle[
                    "rollback"
                ] = rollback(
                    cycle_id
                )

                cycle[
                    "status"
                ] = (
                    "DEGRADED_AFTER_REPAIR"
                )

                self.bad += 1

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

            audit(
                "CYCLE_FINISHED",
                {
                    "cycle_id":
                        cycle_id,

                    "status":
                        cycle[
                            "status"
                        ],

                    "success":
                        cycle[
                            "success"
                        ],
                },
            )

            return cycle

        except Exception as error:

            cycle[
                "status"
            ] = (
                "CYCLE_EXCEPTION"
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
            ] = now()

            self.bad += 1

            if cycle.get(
                "backup",
                {},
            ).get(
                "success"
            ):

                cycle[
                    "rollback"
                ] = rollback(
                    cycle_id
                )

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
                "RUNNING_DEGRADED",
                cycle,
            )

            return cycle

    def once(
        self,
    ) -> Dict[str, Any]:

        self.save_state(
            "RUNNING"
        )

        return self.cycle()

    def forever(
        self,
    ) -> int:

        global STOP

        self.save_state(
            "STARTING"
        )

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

                        "selected":
                            [
                                item.get(
                                    "capability_id"
                                )

                                for item
                                in cycle.get(
                                    "selected_work",
                                    [],
                                )
                            ],
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
                            (
                                deadline
                                -
                                time.monotonic()
                            ),
                        ),
                    )
                )

        self.save_state(
            "STOPPED"
        )

        return 0


# ============================================================
# SYSTEMD SERVICE
# ============================================================

def install_service() -> Dict[str, Any]:

    if os.geteuid() != 0:

        return {
            "success":
                False,

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

    Path(
        SERVICE
    ).write_text(
        service_text,
        encoding="utf-8",
    )

    daemon_reload = (
        run_process(
            [
                "systemctl",
                "daemon-reload",
            ],
            30,
        )
    )

    enable = (
        run_process(
            [
                "systemctl",
                "enable",
                "--now",
                "majd-autonomous.service",
            ],
            60,
        )
    )

    status = (
        run_process(
            [
                "systemctl",
                "--no-pager",
                "--full",
                "status",
                "majd-autonomous.service",
            ],
            30,
        )
    )

    return {
        "success":
            (
                daemon_reload[
                    "success"
                ]
                and
                enable[
                    "success"
                ]
            ),

        "daemon_reload":
            daemon_reload,

        "enable":
            enable,

        "status":
            status,
    }


# ============================================================
# SIGNALS
# ============================================================

def sig(
    signum: int,
    frame: Any,
):

    global STOP

    STOP = True

    audit(
        "SHUTDOWN",
        {
            "signal":
                signum
        },
    )


# ============================================================
# CLI
# ============================================================

def main() -> int:

    signal.signal(
        signal.SIGTERM,
        sig,
    )

    signal.signal(
        signal.SIGINT,
        sig,
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
            else
            1
        )

    if args.service_status:

        result = run_process(
            [
                "systemctl",
                "--no-pager",
                "--full",
                "status",
                "majd-autonomous.service",
            ],
            30,
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
            else
            1
        )

    if args.autonomous_status:

        print(
            json.dumps(
                load_json(
                    STATE_FILE,
                    {},
                ),
                ensure_ascii=False,
                indent=2,
            )
        )

        return 0

    if args.once:

        result = (
            AutonomousRuntime(
                args.owner,
                args.cycle_seconds,
            ).once()
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

    if (
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

    command = " ".join(
        args.command
    ).strip()

    dependencies = (
        repair_dependencies()
    )

    try:

        result = (
            Mastermind()
            .execute(
                command,
                {
                    "type":
                        "GENERAL_OWNER_COMMAND",

                    "raw":
                        command,
                },
                str(
                    uuid.uuid4()
                ),
                args.owner,
            )
        )

    except Exception as error:

        result = {
            "success":
                False,

            "status":
                "OWNER_RUNTIME_EXCEPTION",

            "error":
                str(
                    error
                ),
        }

    output = {
        "success":
            bool(
                result.get(
                    "success"
                )
            ),

        "dependencies":
            dependencies,

        "result":
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


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )

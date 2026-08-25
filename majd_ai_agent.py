#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
majd_ai_agent.py
============================================================

MAJD AI AGENT — REAL EXECUTION ORCHESTRATOR
VERSION 3.0.0

السلسلة الحقيقية:

USER / MAJD API
      ↓
MAJD AI AGENT
      ↓
01 MAJD AI MASTERMIND
      ↓
03 REAL GAME EXECUTOR
      ↓
PLAYABLE ARTIFACT
      ↓
04 OFFICIAL PLATFORM BRIDGE
      ↓
publish_game()
      ↓
PUBLIC /artifacts/<game_id>/index.html
      ↓
https://majd.shop/artifacts/<game_id>/index.html

القواعد:
- لا نجاح وهمي.
- فشل 01 = توقف.
- فشل 03 = توقف.
- Artifact غير صالح = توقف.
- فشل 04 = توقف.
- لا ManifestBuilder داخل Agent.
- لا PackageBuilder داخل Agent.
- لا MajdPlatformClient داخل Agent.
- المسؤول الوحيد عن النشر هو 04 عبر publish_game().
- لا يعتبر النشر ناجحاً إلا بعد التحقق من النسخة المنشورة.
"""

from __future__ import annotations

import importlib.util
import inspect
import json
import os
import re
import sys
import traceback
import uuid

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

import uvicorn


# ============================================================
# IDENTITY
# ============================================================

SYSTEM_NAME = "MAJD-GAME-FACTORY"
AGENT_NAME = "MAJD-AI-AGENT"
VERSION = "3.0.0"

OFFICIAL_PLATFORM_URL = os.getenv(
    "MAJD_OFFICIAL_PLATFORM_URL",
    "https://majd.shop",
).rstrip("/")


# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = ROOT_DIR / "majd_game_output"
STATE_DIR = ROOT_DIR / "majd_factory_state"
AGENT_STATE_DIR = STATE_DIR / "agent"
PUBLIC_DIR = ROOT_DIR / "public"
ARTIFACTS_DIR = PUBLIC_DIR / "artifacts"

MASTERMIND_FILE = ROOT_DIR / "MAJD-AI-MASTERMIND-01.py"
REAL_GAME_EXECUTOR_FILE = ROOT_DIR / "MAJD-REAL-GAME-EXECUTOR-03.py"
OFFICIAL_PLATFORM_BRIDGE_FILE = ROOT_DIR / "MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py"

for directory in (
    OUTPUT_DIR,
    STATE_DIR,
    AGENT_STATE_DIR,
    PUBLIC_DIR,
    ARTIFACTS_DIR,
):
    directory.mkdir(
        parents=True,
        exist_ok=True,
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

        file.flush()
        os.fsync(
            file.fileno()
        )

    temporary.replace(
        path
    )


# ============================================================
# SAFE VALUES
# ============================================================

def safe_name(
    value: str,
) -> str:
    value = str(
        value
        or
        "MAJD-GAME"
    ).strip()

    value = re.sub(
        r"[^\w\u0600-\u06FF\- ]+",
        "",
        value,
        flags=re.UNICODE,
    )

    value = re.sub(
        r"\s+",
        "-",
        value,
    ).strip(
        "-_"
    )

    if not value:
        value = "MAJD-GAME"

    return value[:100]


def build_job_id(
    value: Optional[str] = None,
) -> str:
    raw = str(
        value
        or
        uuid.uuid4()
    ).strip()

    raw = (
        raw
        .replace(
            "/",
            "-",
        )
        .replace(
            "\\",
            "-",
        )
    )

    raw = re.sub(
        r"[^A-Za-z0-9._-]+",
        "-",
        raw,
    ).strip(
        ".-_"
    )

    if not raw:
        raw = str(
            uuid.uuid4()
        )

    return raw[:120]


# ============================================================
# MODULE LOADER
# ============================================================

def load_python_module(
    path: Path,
    module_name: str,
) -> Any:
    if not path.exists():
        raise FileNotFoundError(
            f"Required file not found: {path}"
        )

    specification = (
        importlib.util.spec_from_file_location(
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
            f"Unable to load module: {path}"
        )

    module = (
        importlib.util.module_from_spec(
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


# ============================================================
# RESULT NORMALIZATION
# ============================================================

def normalize_result(
    value: Any,
    default_success: bool = True,
) -> Dict[str, Any]:
    if isinstance(
        value,
        dict,
    ):
        result = dict(
            value
        )

        if "success" not in result:
            result[
                "success"
            ] = default_success

        return result

    if value is None:
        return {
            "success":
                False,
            "error":
                "COMPONENT_RETURNED_NONE",
        }

    return {
        "success":
            default_success,
        "result":
            value,
    }


# ============================================================
# SAFE FUNCTION CALL
# ============================================================

def call_with_supported_kwargs(
    function: Any,
    **kwargs: Any,
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
            **kwargs
        )

    parameters = signature.parameters

    accepts_var_kwargs = any(
        parameter.kind
        ==
        inspect.Parameter.VAR_KEYWORD
        for parameter
        in parameters.values()
    )

    if accepts_var_kwargs:
        return function(
            **kwargs
        )

    supported = {
        key:
            value
        for key, value
        in kwargs.items()
        if key
        in parameters
    }

    return function(
        **supported
    )


# ============================================================
# COMMAND PARSER
# ============================================================

def extract_game_name(
    command: str,
) -> str:
    text = str(
        command
        or
        ""
    ).strip()

    patterns = (
        (
            r"(?:اسمها|اسم اللعبة)"
            r"\s*[:：]?\s*"
            r"[\"']?"
            r"([^\"'\n،,.]+)"
        ),
        (
            r"(?:أنشئ|انشئ|اصنع|ابن|سوي|سوِ)"
            r"\s+(?:لي\s+)?"
            r"(?:لعبة\s+)?"
            r"[\"']?"
            r"([^\"'\n،,.]+)"
        ),
    )

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            value = (
                match
                .group(1)
                .strip()
            )

            if value:
                return safe_name(
                    value
                )

    return safe_name(
        text[:80]
        or
        "MAJD GENERATED GAME"
    )


def detect_dimension(
    command: str,
) -> str:
    lowered = command.lower()

    if (
        "3d" in lowered
        or
        "ثلاثية" in command
        or
        "ثلاثي" in command
    ):
        return "3D"

    if (
        "2d" in lowered
        or
        "ثنائية" in command
        or
        "ثنائي" in command
    ):
        return "2D"

    return "2D"


def detect_genre(
    command: str,
) -> str:
    lowered = command.lower()

    if (
        "استراتيجية" in command
        or
        "strategy" in lowered
    ):
        return "STRATEGY"

    if (
        "سباق" in command
        or
        "race" in lowered
        or
        "racing" in lowered
    ):
        return "RACING"

    if (
        "مغامرات" in command
        or
        "مغامرة" in command
        or
        "adventure" in lowered
    ):
        return "ADVENTURE"

    return "ADVENTURE"


def parse_command(
    command: str,
) -> Dict[str, Any]:
    text = str(
        command
        or
        ""
    ).strip()

    if not text:
        return {
            "success":
                False,
            "error":
                "EMPTY_COMMAND",
        }

    return {
        "success":
            True,

        "type":
            "CREATE_GAME",

        "name":
            extract_game_name(
                text
            ),

        "genre":
            detect_genre(
                text
            ),

        "dimension":
            detect_dimension(
                text
            ),

        "platform":
            [
                "WEB"
            ],

        "request":
            text,

        "command":
            text,

        "requested_at":
            utc_now(),

        "source":
            AGENT_NAME,
    }


# ============================================================
# MASTERMIND 01
# ============================================================

def call_mastermind(
    command: str,
    parsed_request: Dict[str, Any],
    job_id: str,
) -> Dict[str, Any]:
    try:
        module = load_python_module(
            MASTERMIND_FILE,
            "majd_ai_mastermind_01",
        )

    except Exception as error:
        return {
            "success":
                False,

            "status":
                "MASTERMIND_LOAD_FAILED",

            "error":
                (
                    f"{type(error).__name__}: "
                    f"{error}"
                ),

            "traceback":
                traceback.format_exc(),
        }

    function = (
        getattr(
            module,
            "process_game_request",
            None,
        )
        or
        getattr(
            module,
            "execute_request",
            None,
        )
        or
        getattr(
            module,
            "process_request",
            None,
        )
        or
        getattr(
            module,
            "execute",
            None,
        )
        or
        getattr(
            module,
            "run",
            None,
        )
    )

    if not callable(
        function
    ):
        return {
            "success":
                False,

            "status":
                "MASTERMIND_INTERFACE_MISSING",

            "file":
                str(
                    MASTERMIND_FILE
                ),
        }

    try:
        value = (
            call_with_supported_kwargs(
                function,

                command=
                    command,

                request=
                    parsed_request,

                job_id=
                    job_id,

                owner=
                    "MAJD",

                output_root=
                    str(
                        OUTPUT_DIR
                    ),
            )
        )

        return normalize_result(
            value
        )

    except Exception as error:
        return {
            "success":
                False,

            "status":
                "MASTERMIND_FAILED",

            "error":
                (
                    f"{type(error).__name__}: "
                    f"{error}"
                ),

            "traceback":
                traceback.format_exc(),
        }


# ============================================================
# PREPARED REQUEST
# ============================================================

def build_prepared_request(
    parsed_request: Dict[str, Any],
    mastermind_result: Dict[str, Any],
) -> Dict[str, Any]:
    candidates = (
        mastermind_result.get(
            "request"
        ),
        mastermind_result.get(
            "prepared_request"
        ),
        mastermind_result.get(
            "game_request"
        ),
    )

    for candidate in candidates:
        if isinstance(
            candidate,
            dict,
        ):
            prepared = dict(
                parsed_request
            )

            prepared.update(
                candidate
            )

            prepared[
                "success"
            ] = True

            return prepared

    nested_result = (
        mastermind_result.get(
            "result"
        )
    )

    if isinstance(
        nested_result,
        dict,
    ):
        prepared = dict(
            parsed_request
        )

        prepared.update(
            nested_result
        )

        prepared[
            "success"
        ] = True

        return prepared

    return dict(
        parsed_request
    )


# ============================================================
# REAL GAME EXECUTOR 03
# ============================================================

def call_real_executor(
    prepared_request: Dict[str, Any],
    job_id: str,
) -> Dict[str, Any]:
    try:
        module = load_python_module(
            REAL_GAME_EXECUTOR_FILE,
            "majd_real_game_executor_03",
        )

    except Exception as error:
        return {
            "success":
                False,

            "status":
                "EXECUTOR_LOAD_FAILED",

            "error":
                (
                    f"{type(error).__name__}: "
                    f"{error}"
                ),

            "traceback":
                traceback.format_exc(),
        }

    function = (
        getattr(
            module,
            "execute_game_request",
            None,
        )
        or
        getattr(
            module,
            "execute",
            None,
        )
        or
        getattr(
            module,
            "run",
            None,
        )
    )

    if not callable(
        function
    ):
        return {
            "success":
                False,

            "status":
                "EXECUTOR_INTERFACE_MISSING",

            "file":
                str(
                    REAL_GAME_EXECUTOR_FILE
                ),
        }

    try:
        value = (
            call_with_supported_kwargs(
                function,

                request=
                    prepared_request,

                job_id=
                    job_id,

                output_root=
                    str(
                        OUTPUT_DIR
                    ),
            )
        )

        return normalize_result(
            value
        )

    except Exception as error:
        return {
            "success":
                False,

            "status":
                "EXECUTOR_FAILED",

            "error":
                (
                    f"{type(error).__name__}: "
                    f"{error}"
                ),

            "traceback":
                traceback.format_exc(),
        }


# ============================================================
# ARTIFACT
# ============================================================

def candidate_path(
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

    if path.exists():
        return path

    return None


def extract_artifact(
    executor_result: Dict[str, Any],
) -> Optional[Path]:
    keys = (
        "artifact",
        "artifact_path",
        "build_path",
        "game_dir",
        "output_path",
        "playable_artifact",
    )

    for key in keys:
        path = candidate_path(
            executor_result.get(
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
        nested = (
            executor_result.get(
                nested_key
            )
        )

        if not isinstance(
            nested,
            dict,
        ):
            continue

        for key in keys:
            path = candidate_path(
                nested.get(
                    key
                )
            )

            if path is not None:
                return path

    return None


def verify_source_artifact(
    artifact: Path,
) -> Dict[str, Any]:
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

    index_file = (
        artifact
        /
        "index.html"
    )

    if (
        not index_file.exists()
        or
        not index_file.is_file()
    ):
        return {
            "success":
                False,

            "status":
                "ARTIFACT_INDEX_NOT_FOUND",

            "artifact":
                str(
                    artifact
                ),
        }

    if (
        index_file.stat().st_size
        <=
        0
    ):
        return {
            "success":
                False,

            "status":
                "ARTIFACT_INDEX_EMPTY",

            "artifact":
                str(
                    artifact
                ),
        }

    files = [
        path
        for path
        in artifact.rglob(
            "*"
        )
        if path.is_file()
    ]

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
                index_file
            ),

        "file_count":
            len(
                files
            ),
    }


# ============================================================
# OFFICIAL PLATFORM BRIDGE 04
# ============================================================

def call_platform_bridge(
    artifact: Path,
    prepared_request: Dict[str, Any],
    job_id: str,
) -> Dict[str, Any]:
    try:
        module = load_python_module(
            OFFICIAL_PLATFORM_BRIDGE_FILE,
            "majd_official_platform_bridge_04",
        )

    except Exception as error:
        return {
            "success":
                False,

            "status":
                "PLATFORM_BRIDGE_LOAD_FAILED",

            "error":
                (
                    f"{type(error).__name__}: "
                    f"{error}"
                ),

            "traceback":
                traceback.format_exc(),
        }

    publish_function = (
        getattr(
            module,
            "publish_game",
            None,
        )
    )

    if not callable(
        publish_function
    ):
        return {
            "success":
                False,

            "status":
                "PLATFORM_BRIDGE_INTERFACE_MISSING",

            "required_interface":
                "publish_game",

            "file":
                str(
                    OFFICIAL_PLATFORM_BRIDGE_FILE
                ),
        }

    try:
        value = (
            call_with_supported_kwargs(
                publish_function,

                game_dir=
                    artifact,

                artifact=
                    artifact,

                game_name=
                    str(
                        prepared_request.get(
                            "name"
                        )
                        or
                        "MAJD GENERATED GAME"
                    ),

                job_id=
                    job_id,

                request=
                    prepared_request,

                payload=
                    prepared_request,
            )
        )

        result = (
            normalize_result(
                value,
                default_success=False,
            )
        )

        return result

    except Exception as error:
        return {
            "success":
                False,

            "status":
                "PLATFORM_BRIDGE_FAILED",

            "error":
                (
                    f"{type(error).__name__}: "
                    f"{error}"
                ),

            "traceback":
                traceback.format_exc(),
        }


# ============================================================
# PUBLICATION VALIDATION
# ============================================================

def validate_publication(
    bridge_result: Dict[str, Any],
) -> Dict[str, Any]:
    if (
        bridge_result.get(
            "success"
        )
        is not True
    ):
        return {
            "success":
                False,

            "status":
                "BRIDGE_REPORTED_FAILURE",
        }

    published_directory_value = (
        bridge_result.get(
            "published_directory"
        )
    )

    game_path = (
        bridge_result.get(
            "game_path"
        )
    )

    public_url = (
        bridge_result.get(
            "public_url"
        )
    )

    if not published_directory_value:
        return {
            "success":
                False,

            "status":
                "PUBLISHED_DIRECTORY_MISSING",
        }

    published_directory = Path(
        str(
            published_directory_value
        )
    )

    if not published_directory.is_absolute():
        published_directory = (
            ROOT_DIR
            /
            published_directory
        ).resolve()

    if (
        not published_directory.exists()
        or
        not published_directory.is_dir()
    ):
        return {
            "success":
                False,

            "status":
                "PUBLISHED_DIRECTORY_NOT_FOUND",

            "published_directory":
                str(
                    published_directory
                ),
        }

    index_file = (
        published_directory
        /
        "index.html"
    )

    if (
        not index_file.exists()
        or
        index_file.stat().st_size
        <=
        0
    ):
        return {
            "success":
                False,

            "status":
                "PUBLISHED_INDEX_INVALID",

            "index":
                str(
                    index_file
                ),
        }

    if not game_path:
        return {
            "success":
                False,

            "status":
                "GAME_PATH_MISSING",
        }

    if not public_url:
        public_url = (
            OFFICIAL_PLATFORM_URL
            +
            "/"
            +
            str(
                game_path
            ).lstrip(
                "/"
            )
        )

    return {
        "success":
            True,

        "status":
            "REAL_PUBLICATION_VERIFIED",

        "published_directory":
            str(
                published_directory
            ),

        "index":
            str(
                index_file
            ),

        "game_path":
            str(
                game_path
            ),

        "public_url":
            str(
                public_url
            ),
    }


# ============================================================
# RECEIPT
# ============================================================

def save_agent_receipt(
    job_id: str,
    result: Dict[str, Any],
) -> Path:
    receipt_file = (
        AGENT_STATE_DIR
        /
        f"{job_id}.json"
    )

    write_json(
        receipt_file,
        result,
    )

    return receipt_file


# ============================================================
# MAIN EXECUTION
# ============================================================

def execute_command(
    command: str,
    job_id: Optional[str] = None,
) -> Dict[str, Any]:
    started_at = utc_now()

    actual_job_id = (
        build_job_id(
            job_id
        )
    )

    try:
        parsed_request = (
            parse_command(
                command
            )
        )

        if (
            parsed_request.get(
                "success"
            )
            is not True
        ):
            result = {
                "success":
                    False,

                "status":
                    "COMMAND_PARSE_FAILED",

                "system":
                    SYSTEM_NAME,

                "agent":
                    AGENT_NAME,

                "version":
                    VERSION,

                "job_id":
                    actual_job_id,

                "error":
                    parsed_request.get(
                        "error"
                    ),

                "started_at":
                    started_at,

                "finished_at":
                    utc_now(),
            }

            save_agent_receipt(
                actual_job_id,
                result,
            )

            return result

        mastermind_result = (
            call_mastermind(
                command=
                    command,

                parsed_request=
                    parsed_request,

                job_id=
                    actual_job_id,
            )
        )

        if (
            mastermind_result.get(
                "success"
            )
            is not True
        ):
            result = {
                "success":
                    False,

                "status":
                    "MASTERMIND_STAGE_FAILED",

                "system":
                    SYSTEM_NAME,

                "agent":
                    AGENT_NAME,

                "version":
                    VERSION,

                "job_id":
                    actual_job_id,

                "request":
                    parsed_request,

                "mastermind":
                    mastermind_result,

                "started_at":
                    started_at,

                "finished_at":
                    utc_now(),
            }

            save_agent_receipt(
                actual_job_id,
                result,
            )

            return result

        prepared_request = (
            build_prepared_request(
                parsed_request,
                mastermind_result,
            )
        )

        executor_result = (
            call_real_executor(
                prepared_request=
                    prepared_request,

                job_id=
                    actual_job_id,
            )
        )

        if (
            executor_result.get(
                "success"
            )
            is not True
        ):
            result = {
                "success":
                    False,

                "status":
                    "REAL_GAME_EXECUTION_FAILED",

                "system":
                    SYSTEM_NAME,

                "agent":
                    AGENT_NAME,

                "version":
                    VERSION,

                "job_id":
                    actual_job_id,

                "request":
                    prepared_request,

                "mastermind":
                    mastermind_result,

                "executor":
                    executor_result,

                "started_at":
                    started_at,

                "finished_at":
                    utc_now(),
            }

            save_agent_receipt(
                actual_job_id,
                result,
            )

            return result

        artifact = (
            extract_artifact(
                executor_result
            )
        )

        if artifact is None:
            result = {
                "success":
                    False,

                "status":
                    "REAL_ARTIFACT_NOT_FOUND",

                "system":
                    SYSTEM_NAME,

                "agent":
                    AGENT_NAME,

                "version":
                    VERSION,

                "job_id":
                    actual_job_id,

                "executor":
                    executor_result,

                "started_at":
                    started_at,

                "finished_at":
                    utc_now(),
            }

            save_agent_receipt(
                actual_job_id,
                result,
            )

            return result

        artifact_check = (
            verify_source_artifact(
                artifact
            )
        )

        if (
            artifact_check.get(
                "success"
            )
            is not True
        ):
            result = {
                "success":
                    False,

                "status":
                    "REAL_ARTIFACT_INVALID",

                "system":
                    SYSTEM_NAME,

                "agent":
                    AGENT_NAME,

                "version":
                    VERSION,

                "job_id":
                    actual_job_id,

                "artifact":
                    str(
                        artifact
                    ),

                "artifact_check":
                    artifact_check,

                "started_at":
                    started_at,

                "finished_at":
                    utc_now(),
            }

            save_agent_receipt(
                actual_job_id,
                result,
            )

            return result

        bridge_result = (
            call_platform_bridge(
                artifact=
                    artifact,

                prepared_request=
                    prepared_request,

                job_id=
                    actual_job_id,
            )
        )

        if (
            bridge_result.get(
                "success"
            )
            is not True
        ):
            result = {
                "success":
                    False,

                "status":
                    "OFFICIAL_PLATFORM_PUBLISH_FAILED",

                "system":
                    SYSTEM_NAME,

                "agent":
                    AGENT_NAME,

                "version":
                    VERSION,

                "job_id":
                    actual_job_id,

                "request":
                    prepared_request,

                "artifact":
                    str(
                        artifact
                    ),

                "bridge":
                    bridge_result,

                "started_at":
                    started_at,

                "finished_at":
                    utc_now(),
            }

            save_agent_receipt(
                actual_job_id,
                result,
            )

            return result

        publication_validation = (
            validate_publication(
                bridge_result
            )
        )

        if (
            publication_validation.get(
                "success"
            )
            is not True
        ):
            result = {
                "success":
                    False,

                "status":
                    "FINAL_PUBLICATION_VALIDATION_FAILED",

                "system":
                    SYSTEM_NAME,

                "agent":
                    AGENT_NAME,

                "version":
                    VERSION,

                "job_id":
                    actual_job_id,

                "artifact":
                    str(
                        artifact
                    ),

                "bridge":
                    bridge_result,

                "publication_validation":
                    publication_validation,

                "started_at":
                    started_at,

                "finished_at":
                    utc_now(),
            }

            save_agent_receipt(
                actual_job_id,
                result,
            )

            return result

        result = {
            "success":
                True,

            "status":
                "GAME_BUILT_AND_PUBLISHED",

            "message":
                (
                    "Game built and published successfully "
                    "through MAJD Official Platform Bridge."
                ),

            "system":
                SYSTEM_NAME,

            "agent":
                AGENT_NAME,

            "version":
                VERSION,

            "job_id":
                actual_job_id,

            "game_id":
                bridge_result.get(
                    "game_id"
                ),

            "game_name":
                (
                    bridge_result.get(
                        "game_name"
                    )
                    or
                    prepared_request.get(
                        "name"
                    )
                ),

            "artifact":
                str(
                    artifact
                ),

            "published_directory":
                publication_validation.get(
                    "published_directory"
                ),

            "game_path":
                publication_validation.get(
                    "game_path"
                ),

            "public_url":
                publication_validation.get(
                    "public_url"
                ),

            "metadata":
                bridge_result.get(
                    "metadata"
                ),

            "request":
                prepared_request,

            "mastermind":
                mastermind_result,

            "executor":
                executor_result,

            "bridge":
                bridge_result,

            "publication_validation":
                publication_validation,

            "started_at":
                started_at,

            "finished_at":
                utc_now(),
        }

        receipt_file = (
            save_agent_receipt(
                actual_job_id,
                result,
            )
        )

        result[
            "agent_receipt"
        ] = str(
            receipt_file
        )

        return result

    except Exception as error:
        result = {
            "success":
                False,

            "status":
                "AGENT_SYSTEM_CRASH",

            "system":
                SYSTEM_NAME,

            "agent":
                AGENT_NAME,

            "version":
                VERSION,

            "job_id":
                actual_job_id,

            "error":
                (
                    f"{type(error).__name__}: "
                    f"{error}"
                ),

            "traceback":
                traceback.format_exc(),

            "started_at":
                started_at,

            "finished_at":
                utc_now(),
        }

        try:
            save_agent_receipt(
                actual_job_id,
                result,
            )

        except Exception:
            pass

        return result


# ============================================================
# COMPATIBILITY
# ============================================================

def run_game_creation(
    command: str,
) -> Dict[str, Any]:
    return execute_command(
        command
    )


def run_command(
    command: str,
    job_id: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    return execute_command(
        command,
        job_id=job_id,
    )


def process_command(
    command: str,
    job_id: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    return execute_command(
        command,
        job_id=job_id,
    )


def execute(
    command: str,
    job_id: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    return execute_command(
        command,
        job_id=job_id,
    )


def run(
    command: str,
    job_id: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    return execute_command(
        command,
        job_id=job_id,
    )


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title=
        "MAJD AI AGENT - Sovereign Game Factory",

    version=
        VERSION,
)


# ============================================================
# UI
# ============================================================

@app.get(
    "/",
    response_class=HTMLResponse,
)
async def ui() -> HTMLResponse:
    html = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">

<head>

<meta charset="utf-8">

<title>
MAJD AI Agent
</title>

<style>

body {
    background: #0b0f1c;
    color: white;
    font-family: Arial, sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    margin: 0;
}

.box {
    background: #151e2e;
    padding: 40px;
    border-radius: 20px;
    text-align: center;
    width: min(520px, 88vw);
    border: 1px solid #2b3a55;
}

h1 {
    color: #f0c84b;
}

textarea {
    width: 100%;
    min-height: 100px;
    box-sizing: border-box;
    background: #0b0f1c;
    border: 1px solid #2b3a55;
    color: white;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 15px;
}

button {
    width: 100%;
    padding: 15px;
    background: #f0c84b;
    border: none;
    border-radius: 12px;
    font-weight: bold;
    font-size: 18px;
    cursor: pointer;
}

#status {
    margin-top: 15px;
    color: #aab7d6;
    word-break: break-word;
}

a {
    color: #f0c84b;
}

</style>

</head>

<body>

<div class="box">

<h1>
MAJD AI Agent
</h1>

<p>
الوكيل السيادي لبناء الألعاب ونشرها على منصة مجد.
</p>

<textarea id="cmd">
أنشئ لعبة مغامرات ثلاثية الأبعاد كاملة
</textarea>

<button onclick="runAI()">
تشغيل
</button>

<div id="status">
في انتظار الأمر...
</div>

</div>

<script>

async function runAI() {

    const cmd =
        document.getElementById('cmd').value;

    const status =
        document.getElementById('status');

    status.textContent =
        'جاري التنفيذ...';

    try {

        const response =
            await fetch(
                '/run',
                {
                    method: 'POST',
                    headers: {
                        'Content-Type':
                            'application/json'
                    },
                    body:
                        JSON.stringify({
                            command: cmd
                        })
                }
            );

        const data =
            await response.json();

        if (data.success) {

            let html =
                'تم البناء والنشر بنجاح.';

            if (data.job_id) {

                html +=
                    '<br>Job ID: '
                    +
                    data.job_id;
            }

            if (data.public_url) {

                html +=
                    '<br><a target="_blank" href="'
                    +
                    data.public_url
                    +
                    '">فتح اللعبة</a>';
            }

            status.innerHTML =
                html;

        } else {

            status.textContent =
                'فشل: '
                +
                (
                    data.status
                    ||
                    data.error
                    ||
                    'UNKNOWN_ERROR'
                );
        }

    } catch (error) {

        status.textContent =
            'خطأ في الاتصال بالوكيل.';
    }
}

</script>

</body>
</html>
"""

    return HTMLResponse(
        content=html
    )


# ============================================================
# HEALTH
# ============================================================

@app.get(
    "/health"
)
async def api_health() -> Dict[str, Any]:
    return {
        "success":
            True,

        "status":
            "healthy",

        "service":
            "majd-ai-core",

        "api":
            "online",

        "game_factory":
            "ready",

        "agent":
            AGENT_NAME,

        "version":
            VERSION,

        "components": {
            "mastermind":
                MASTERMIND_FILE.exists(),

            "executor":
                REAL_GAME_EXECUTOR_FILE.exists(),

            "bridge":
                OFFICIAL_PLATFORM_BRIDGE_FILE.exists(),
        },

        "time":
            utc_now(),
    }


# ============================================================
# API EXECUTION
# ============================================================

async def execute_request(
    request: Request,
) -> JSONResponse:
    try:
        body = (
            await request.json()
        )

    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "success":
                    False,

                "status":
                    "INVALID_JSON",
            },
        )

    command = str(
        body.get(
            "command"
        )
        or
        body.get(
            "prompt"
        )
        or
        ""
    ).strip()

    if not command:
        return JSONResponse(
            status_code=400,
            content={
                "success":
                    False,

                "status":
                    "EMPTY_COMMAND",
            },
        )

    supplied_job_id = (
        body.get(
            "job_id"
        )
    )

    result = (
        execute_command(
            command=
                command,

            job_id=
                (
                    str(
                        supplied_job_id
                    )
                    if supplied_job_id
                    else None
                ),
        )
    )

    return JSONResponse(
        status_code=
            (
                200
                if result.get(
                    "success"
                )
                else 500
            ),

        content=
            result,
    )


@app.post(
    "/run"
)
async def execute_run(
    request: Request,
) -> JSONResponse:
    return await execute_request(
        request
    )


@app.post(
    "/api/run"
)
async def execute_api_run(
    request: Request,
) -> JSONResponse:
    return await execute_request(
        request
    )


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    port = int(
        os.getenv(
            "PORT",
            "8000",
        )
    )

    print(
        f"{AGENT_NAME} "
        f"{VERSION} "
        f"running on port "
        f"{port}..."
    )

    uvicorn.run(
        app,
        host=
            "0.0.0.0",
        port=
            port,
    )

    return 0


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    raise SystemExit(
        main()
    )

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
majd_ai_agent.py
============================================================

MAJD AI AGENT — REAL EXECUTION ORCHESTRATOR

السلسلة الحقيقية:

USER / MAJD API
      ↓
MAJD AI AGENT
      ↓
01 MASTERMIND
      ↓
03 REAL GAME EXECUTOR
      ↓
PLAYABLE ARTIFACT
      ↓
04 OFFICIAL PLATFORM BRIDGE
      ↓
PUBLIC /artifacts/<game_id>/index.html
      ↓
https://majd.shop/artifacts/<game_id>/index.html

القواعد:
- لا نجاح وهمي.
- لا ManifestBuilder غير موجود.
- لا PackageBuilder غير موجود.
- لا MajdPlatformClient غير موجود.
- الربط مع 04 يتم فقط عبر الواجهة الحقيقية publish_game.
- إذا فشل 01 أو 03 أو 04 تظهر حالة الفشل الحقيقية.
- HTTP 200 لا يعني أن العملية نجحت؛ success داخل JSON هو الحكم.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
import traceback
import uuid

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


# ============================================================
# IDENTITY
# ============================================================

SYSTEM_NAME = "MAJD-GAME-FACTORY"
AGENT_NAME = "MAJD-AI-AGENT"
VERSION = "3.0.0"

OFFICIAL_PLATFORM_URL = os.getenv(
    "MAJD_OFFICIAL_PLATFORM_URL",
    "https://majd.shop"
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

for directory in (
    OUTPUT_DIR,
    STATE_DIR,
    AGENT_STATE_DIR,
    PUBLIC_DIR,
    ARTIFACTS_DIR,
):
    directory.mkdir(
        parents=True,
        exist_ok=True
    )


# ============================================================
# OFFICIAL COMPONENT FILES
# ============================================================

MASTERMIND_CANDIDATES = (
    ROOT_DIR / "MAJD-AI-MASTERMIND-01.py",
    ROOT_DIR / "MAJD-MASTERMIND-01.py",
    ROOT_DIR / "majd_ai_mastermind.py",
)

REAL_GAME_EXECUTOR_FILE = (
    ROOT_DIR / "MAJD-REAL-GAME-EXECUTOR-03.py"
)

OFFICIAL_PLATFORM_BRIDGE_FILE = (
    ROOT_DIR / "MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py"
)


# ============================================================
# TIME
# ============================================================

def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


# ============================================================
# JSON HELPERS
# ============================================================

def write_json(
    path: Path,
    data: Dict[str, Any]
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
            data,
            file,
            ensure_ascii=False,
            indent=2,
            default=str
        )

    temporary.replace(path)


# ============================================================
# SAFE JOB ID
# ============================================================

def build_job_id(
    value: Optional[str] = None
) -> str:

    raw = str(
        value or uuid.uuid4()
    ).strip()

    raw = raw.replace(
        "/",
        "-"
    ).replace(
        "\\",
        "-"
    )

    raw = re.sub(
        r"[^A-Za-z0-9._-]+",
        "-",
        raw
    )

    raw = raw.strip(
        ".-_"
    )

    if not raw:
        raw = str(
            uuid.uuid4()
        )

    return raw[:120]


# ============================================================
# DYNAMIC PYTHON MODULE LOADER
# ============================================================

def load_python_module(
    path: Path,
    module_name: str
) -> Any:

    if not path.exists():

        raise FileNotFoundError(
            f"MODULE_FILE_NOT_FOUND: {path}"
        )

    specification = (
        importlib.util.spec_from_file_location(
            module_name,
            str(path)
        )
    )

    if (
        specification is None
        or
        specification.loader is None
    ):

        raise ImportError(
            f"MODULE_SPEC_FAILED: {path}"
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
# MASTERMIND DISCOVERY
# ============================================================

def find_mastermind_file() -> Optional[Path]:

    for candidate in MASTERMIND_CANDIDATES:

        if candidate.exists():
            return candidate

    matches = sorted(
        ROOT_DIR.glob(
            "*MASTERMIND*01*.py"
        )
    )

    if matches:
        return matches[0]

    return None


# ============================================================
# REQUEST PARSER
# ============================================================

def parse_command(
    command: str
) -> Dict[str, Any]:

    command = str(
        command or ""
    ).strip()

    if not command:

        return {
            "success": False,
            "error": "EMPTY_COMMAND"
        }

    game_name = extract_game_name(
        command
    )

    request = {
        "success": True,
        "command": command,
        "name": game_name,
        "type": detect_game_type(
            command
        ),
        "requested_at": utc_now(),
        "source": AGENT_NAME,
    }

    return request


def extract_game_name(
    command: str
) -> str:

    text = command.strip()

    patterns = (
        r"(?:اسمها|اسم اللعبة)\s*[:：]?\s*[\"']?([^\"'\n،,.]+)",
        r"(?:أنشئ|انشئ|اصنع|ابن|سوي|سوِ)\s+(?:لي\s+)?(?:لعبة\s+)?[\"']?([^\"'\n،,.]+)",
    )

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:

            value = (
                match.group(1)
                .strip()
            )

            if value:
                return value[:100]

    return (
        "MAJD GENERATED GAME"
    )


def detect_game_type(
    command: str
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

    if (
        "استراتيجية" in command
        or
        "strategy" in lowered
    ):
        return "STRATEGY"

    if (
        "سباق" in command
        or
        "racing" in lowered
        or
        "race" in lowered
    ):
        return "RACING"

    if (
        "مغامرات" in command
        or
        "adventure" in lowered
    ):
        return "ADVENTURE"

    return "GAME"


# ============================================================
# RESULT NORMALIZATION
# ============================================================

def normalize_result(
    value: Any
) -> Dict[str, Any]:

    if isinstance(
        value,
        dict
    ):
        return value

    if value is None:

        return {
            "success": False,
            "error": "COMPONENT_RETURNED_NONE"
        }

    return {
        "success": True,
        "result": value
    }


# ============================================================
# MASTERMIND CALL
# ============================================================

def call_mastermind(
    command: str,
    request: Dict[str, Any],
    job_id: str
) -> Dict[str, Any]:

    mastermind_file = (
        find_mastermind_file()
    )

    if mastermind_file is None:

        return {
            "success": True,
            "status": "MASTERMIND_NOT_PRESENT_PASSTHROUGH",
            "request": request
        }

    try:

        module = load_python_module(
            mastermind_file,
            "majd_mastermind_01"
        )

        function = (
            getattr(
                module,
                "process_game_request",
                None
            )
            or
            getattr(
                module,
                "execute_request",
                None
            )
            or
            getattr(
                module,
                "process_request",
                None
            )
            or
            getattr(
                module,
                "execute",
                None
            )
            or
            getattr(
                module,
                "run",
                None
            )
        )

        if function is None:

            return {
                "success": False,
                "status": "MASTERMIND_INTERFACE_MISSING",
                "file": str(
                    mastermind_file
                )
            }

        attempts = (
            lambda: function(
                command=command,
                request=request,
                job_id=job_id,
                owner="MAJD",
                output_root=str(
                    OUTPUT_DIR
                )
            ),
            lambda: function(
                request=request,
                job_id=job_id,
                output_root=str(
                    OUTPUT_DIR
                )
            ),
            lambda: function(
                command=command
            ),
            lambda: function(
                request
            ),
        )

        last_type_error = None

        for attempt in attempts:

            try:

                result = attempt()

                normalized = normalize_result(
                    result
                )

                if "success" not in normalized:
                    normalized[
                        "success"
                    ] = True

                return normalized

            except TypeError as error:

                last_type_error = error
                continue

        return {
            "success": False,
            "status": "MASTERMIND_SIGNATURE_MISMATCH",
            "error": str(
                last_type_error
            )
        }

    except Exception as error:

        return {
            "success": False,
            "status": "MASTERMIND_FAILED",
            "error": (
                f"{type(error).__name__}: "
                f"{error}"
            ),
            "traceback": traceback.format_exc()
        }


# ============================================================
# PREPARED REQUEST
# ============================================================

def build_prepared_request(
    parsed_request: Dict[str, Any],
    mastermind_result: Dict[str, Any]
) -> Dict[str, Any]:

    if mastermind_result.get(
        "success"
    ) is False:

        return parsed_request

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
        mastermind_result.get(
            "result"
        ),
    )

    for candidate in candidates:

        if isinstance(
            candidate,
            dict
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

    return parsed_request


# ============================================================
# REAL EXECUTOR
# ============================================================

def call_real_executor(
    request: Dict[str, Any],
    job_id: str
) -> Dict[str, Any]:

    if not REAL_GAME_EXECUTOR_FILE.exists():

        return {
            "success": False,
            "status": "REAL_GAME_EXECUTOR_NOT_FOUND",
            "file": str(
                REAL_GAME_EXECUTOR_FILE
            )
        }

    try:

        module = load_python_module(
            REAL_GAME_EXECUTOR_FILE,
            "majd_real_game_executor_03"
        )

        function = (
            getattr(
                module,
                "execute_game_request",
                None
            )
            or
            getattr(
                module,
                "execute",
                None
            )
            or
            getattr(
                module,
                "run",
                None
            )
        )

        if function is None:

            return {
                "success": False,
                "status": "EXECUTOR_INTERFACE_MISSING",
                "file": str(
                    REAL_GAME_EXECUTOR_FILE
                )
            }

        attempts = (
            lambda: function(
                request=request,
                job_id=job_id,
                output_root=str(
                    OUTPUT_DIR
                )
            ),
            lambda: function(
                request=request,
                job_id=job_id
            ),
            lambda: function(
                request
            ),
        )

        last_type_error = None

        for attempt in attempts:

            try:

                result = attempt()

                normalized = normalize_result(
                    result
                )

                if "success" not in normalized:
                    normalized[
                        "success"
                    ] = True

                return normalized

            except TypeError as error:

                last_type_error = error
                continue

        return {
            "success": False,
            "status": "EXECUTOR_SIGNATURE_MISMATCH",
            "error": str(
                last_type_error
            )
        }

    except Exception as error:

        return {
            "success": False,
            "status": "EXECUTOR_FAILED",
            "error": (
                f"{type(error).__name__}: "
                f"{error}"
            ),
            "traceback": traceback.format_exc()
        }


# ============================================================
# ARTIFACT EXTRACTION
# ============================================================

def extract_artifact(
    executor_result: Dict[str, Any]
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

        value = executor_result.get(
            key
        )

        if value:

            path = Path(
                str(value)
            )

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

    nested_keys = (
        "result",
        "build",
        "output",
        "game",
    )

    for nested_key in nested_keys:

        nested = executor_result.get(
            nested_key
        )

        if not isinstance(
            nested,
            dict
        ):
            continue

        for key in keys:

            value = nested.get(
                key
            )

            if not value:
                continue

            path = Path(
                str(value)
            )

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


# ============================================================
# PLATFORM BRIDGE
# ============================================================

def call_platform_bridge(
    artifact: Path,
    request: Dict[str, Any],
    job_id: str
) -> Dict[str, Any]:

    if not OFFICIAL_PLATFORM_BRIDGE_FILE.exists():

        return {
            "success": False,
            "status": "OFFICIAL_PLATFORM_BRIDGE_NOT_FOUND",
            "file": str(
                OFFICIAL_PLATFORM_BRIDGE_FILE
            )
        }

    try:

        module = load_python_module(
            OFFICIAL_PLATFORM_BRIDGE_FILE,
            "majd_official_platform_bridge_04"
        )

        publish_function = getattr(
            module,
            "publish_game",
            None
        )

        if publish_function is None:

            return {
                "success": False,
                "status": "PLATFORM_BRIDGE_INTERFACE_MISSING",
                "required_interface": "publish_game",
                "file": str(
                    OFFICIAL_PLATFORM_BRIDGE_FILE
                )
            }

        result = publish_function(
            game_dir=artifact,
            game_name=str(
                request.get(
                    "name"
                )
                or
                "MAJD GENERATED GAME"
            ),
            job_id=job_id,
            request=request
        )

        normalized = normalize_result(
            result
        )

        if "success" not in normalized:
            normalized[
                "success"
            ] = False

        return normalized

    except Exception as error:

        return {
            "success": False,
            "status": "PLATFORM_BRIDGE_FAILED",
            "error": (
                f"{type(error).__name__}: "
                f"{error}"
            ),
            "traceback": traceback.format_exc()
        }


# ============================================================
# FINAL PUBLICATION VALIDATION
# ============================================================

def validate_publication(
    bridge_result: Dict[str, Any]
) -> Dict[str, Any]:

    if bridge_result.get(
        "success"
    ) is not True:

        return {
            "success": False,
            "status": "BRIDGE_REPORTED_FAILURE",
            "bridge_result": bridge_result
        }

    published_directory_value = (
        bridge_result.get(
            "published_directory"
        )
    )

    game_path = bridge_result.get(
        "game_path"
    )

    public_url = bridge_result.get(
        "public_url"
    )

    if not published_directory_value:

        return {
            "success": False,
            "status": "PUBLISHED_DIRECTORY_MISSING"
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

    if not published_directory.exists():

        return {
            "success": False,
            "status": "PUBLISHED_DIRECTORY_NOT_FOUND",
            "published_directory": str(
                published_directory
            )
        }

    index_file = (
        published_directory
        /
        "index.html"
    )

    if not index_file.exists():

        return {
            "success": False,
            "status": "PUBLISHED_INDEX_NOT_FOUND",
            "index": str(
                index_file
            )
        }

    if index_file.stat().st_size <= 0:

        return {
            "success": False,
            "status": "PUBLISHED_INDEX_EMPTY",
            "index": str(
                index_file
            )
        }

    if not game_path:

        return {
            "success": False,
            "status": "GAME_PATH_MISSING"
        }

    if not public_url:

        public_url = (
            OFFICIAL_PLATFORM_URL
            +
            "/"
            +
            str(
                game_path
            ).lstrip("/")
        )

    return {
        "success": True,
        "status": "REAL_PUBLICATION_VERIFIED",
        "published_directory": str(
            published_directory
        ),
        "index": str(
            index_file
        ),
        "game_path": str(
            game_path
        ),
        "public_url": str(
            public_url
        )
    }


# ============================================================
# SAVE AGENT RECEIPT
# ============================================================

def save_agent_receipt(
    job_id: str,
    result: Dict[str, Any]
) -> Path:

    receipt_file = (
        AGENT_STATE_DIR
        /
        f"{job_id}.json"
    )

    write_json(
        receipt_file,
        result
    )

    return receipt_file


# ============================================================
# MAIN EXECUTION PIPELINE
# ============================================================

def execute_command(
    command: str,
    job_id: Optional[str] = None
) -> Dict[str, Any]:

    started_at = utc_now()

    actual_job_id = build_job_id(
        job_id
    )

    try:

        # ====================================================
        # 1. PARSE USER COMMAND
        # ====================================================

        parsed_request = parse_command(
            command
        )

        if parsed_request.get(
            "success"
        ) is not True:

            result = {
                "success": False,
                "status": "COMMAND_PARSE_FAILED",
                "system": SYSTEM_NAME,
                "agent": AGENT_NAME,
                "version": VERSION,
                "job_id": actual_job_id,
                "error": parsed_request.get(
                    "error"
                ),
                "started_at": started_at,
                "finished_at": utc_now()
            }

            save_agent_receipt(
                actual_job_id,
                result
            )

            return result

        # ====================================================
        # 2. MASTERMIND 01
        # ====================================================

        mastermind_result = call_mastermind(
            command=command,
            request=parsed_request,
            job_id=actual_job_id
        )

        if mastermind_result.get(
            "success"
        ) is False:

            result = {
                "success": False,
                "status": "MASTERMIND_STAGE_FAILED",
                "system": SYSTEM_NAME,
                "agent": AGENT_NAME,
                "version": VERSION,
                "job_id": actual_job_id,
                "request": parsed_request,
                "mastermind": mastermind_result,
                "started_at": started_at,
                "finished_at": utc_now()
            }

            save_agent_receipt(
                actual_job_id,
                result
            )

            return result

        prepared_request = build_prepared_request(
            parsed_request,
            mastermind_result
        )

        # ====================================================
        # 3. REAL GAME EXECUTOR 03
        # ====================================================

        executor_result = call_real_executor(
            request=prepared_request,
            job_id=actual_job_id
        )

        if executor_result.get(
            "success"
        ) is not True:

            result = {
                "success": False,
                "status": "REAL_GAME_EXECUTION_FAILED",
                "system": SYSTEM_NAME,
                "agent": AGENT_NAME,
                "version": VERSION,
                "job_id": actual_job_id,
                "request": prepared_request,
                "mastermind": mastermind_result,
                "executor": executor_result,
                "started_at": started_at,
                "finished_at": utc_now()
            }

            save_agent_receipt(
                actual_job_id,
                result
            )

            return result

        # ====================================================
        # 4. FIND REAL PLAYABLE ARTIFACT
        # ====================================================

        artifact = extract_artifact(
            executor_result
        )

        if artifact is None:

            result = {
                "success": False,
                "status": "REAL_ARTIFACT_NOT_FOUND",
                "system": SYSTEM_NAME,
                "agent": AGENT_NAME,
                "version": VERSION,
                "job_id": actual_job_id,
                "request": prepared_request,
                "mastermind": mastermind_result,
                "executor": executor_result,
                "started_at": started_at,
                "finished_at": utc_now()
            }

            save_agent_receipt(
                actual_job_id,
                result
            )

            return result

        if not artifact.is_dir():

            result = {
                "success": False,
                "status": "REAL_ARTIFACT_NOT_DIRECTORY",
                "system": SYSTEM_NAME,
                "agent": AGENT_NAME,
                "version": VERSION,
                "job_id": actual_job_id,
                "artifact": str(
                    artifact
                ),
                "started_at": started_at,
                "finished_at": utc_now()
            }

            save_agent_receipt(
                actual_job_id,
                result
            )

            return result

        source_index = (
            artifact
            /
            "index.html"
        )

        if (
            not source_index.exists()
            or
            source_index.stat().st_size <= 0
        ):

            result = {
                "success": False,
                "status": "REAL_ARTIFACT_INDEX_INVALID",
                "system": SYSTEM_NAME,
                "agent": AGENT_NAME,
                "version": VERSION,
                "job_id": actual_job_id,
                "artifact": str(
                    artifact
                ),
                "index": str(
                    source_index
                ),
                "started_at": started_at,
                "finished_at": utc_now()
            }

            save_agent_receipt(
                actual_job_id,
                result
            )

            return result

        # ====================================================
        # 5. OFFICIAL PLATFORM BRIDGE 04
        #
        # IMPORTANT:
        # لا ManifestBuilder
        # لا PackageBuilder
        # لا MajdPlatformClient
        #
        # الملف 04 الذي أرسلته يوفّر publish_game مباشرة.
        # ====================================================

        bridge_result = call_platform_bridge(
            artifact=artifact,
            request=prepared_request,
            job_id=actual_job_id
        )

        if bridge_result.get(
            "success"
        ) is not True:

            result = {
                "success": False,
                "status": "OFFICIAL_PLATFORM_PUBLISH_FAILED",
                "system": SYSTEM_NAME,
                "agent": AGENT_NAME,
                "version": VERSION,
                "job_id": actual_job_id,
                "request": prepared_request,
                "artifact": str(
                    artifact
                ),
                "mastermind": mastermind_result,
                "executor": executor_result,
                "bridge": bridge_result,
                "started_at": started_at,
                "finished_at": utc_now()
            }

            save_agent_receipt(
                actual_job_id,
                result
            )

            return result

        # ====================================================
        # 6. VERIFY REAL PUBLICATION
        # ====================================================

        publication_validation = (
            validate_publication(
                bridge_result
            )
        )

        if publication_validation.get(
            "success"
        ) is not True:

            result = {
                "success": False,
                "status": "FINAL_PUBLICATION_VALIDATION_FAILED",
                "system": SYSTEM_NAME,
                "agent": AGENT_NAME,
                "version": VERSION,
                "job_id": actual_job_id,
                "request": prepared_request,
                "artifact": str(
                    artifact
                ),
                "mastermind": mastermind_result,
                "executor": executor_result,
                "bridge": bridge_result,
                "publication_validation":
                    publication_validation,
                "started_at": started_at,
                "finished_at": utc_now()
            }

            save_agent_receipt(
                actual_job_id,
                result
            )

            return result

        # ====================================================
        # 7. FINAL REAL SUCCESS
        # ====================================================

        result = {
            "success": True,
            "status": "GAME_BUILT_AND_PUBLISHED",
            "message": (
                "Game built and published successfully "
                "through MAJD Official Platform Bridge."
            ),
            "system": SYSTEM_NAME,
            "agent": AGENT_NAME,
            "version": VERSION,
            "job_id": actual_job_id,
            "game_id": bridge_result.get(
                "game_id"
            ),
            "game_name": bridge_result.get(
                "game_name"
            )
            or
            prepared_request.get(
                "name"
            ),
            "artifact": str(
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
                utc_now()
        }

        receipt_file = save_agent_receipt(
            actual_job_id,
            result
        )

        result[
            "agent_receipt"
        ] = str(
            receipt_file
        )

        return result

    except Exception as error:

        result = {
            "success": False,
            "status": "AGENT_SYSTEM_CRASH",
            "system": SYSTEM_NAME,
            "agent": AGENT_NAME,
            "version": VERSION,
            "job_id": actual_job_id,
            "error": (
                f"{type(error).__name__}: "
                f"{error}"
            ),
            "traceback": traceback.format_exc(),
            "started_at": started_at,
            "finished_at": utc_now()
        }

        try:
            save_agent_receipt(
                actual_job_id,
                result
            )
        except Exception:
            pass

        return result


# ============================================================
# COMPATIBILITY INTERFACES
# ============================================================

def run_command(
    command: str,
    job_id: Optional[str] = None,
    **kwargs: Any
) -> Dict[str, Any]:

    return execute_command(
        command=command,
        job_id=job_id
    )


def process_command(
    command: str,
    job_id: Optional[str] = None,
    **kwargs: Any
) -> Dict[str, Any]:

    return execute_command(
        command=command,
        job_id=job_id
    )


def execute(
    command: str,
    job_id: Optional[str] = None,
    **kwargs: Any
) -> Dict[str, Any]:

    return execute_command(
        command=command,
        job_id=job_id
    )


def run(
    command: str,
    job_id: Optional[str] = None,
    **kwargs: Any
) -> Dict[str, Any]:

    return execute_command(
        command=command,
        job_id=job_id
    )


# ============================================================
# OPTIONAL FASTAPI APPLICATION
# ============================================================

try:

    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    FASTAPI_AVAILABLE = True

except Exception:

    FastAPI = None
    JSONResponse = None
    FASTAPI_AVAILABLE = False


if FASTAPI_AVAILABLE:

    app = FastAPI(
        title="MAJD AI Agent",
        version=VERSION
    )

    @app.get("/")
    def root() -> Dict[str, Any]:

        return {
            "success": True,
            "system": SYSTEM_NAME,
            "agent": AGENT_NAME,
            "version": VERSION,
            "status": "ONLINE"
        }

    @app.get("/health")
    def health() -> Dict[str, Any]:

        mastermind_file = (
            find_mastermind_file()
        )

        return {
            "success": True,
            "system": SYSTEM_NAME,
            "agent": AGENT_NAME,
            "version": VERSION,
            "status": "ONLINE",
            "components": {
                "mastermind": {
                    "present":
                        mastermind_file is not None,
                    "file":
                        str(
                            mastermind_file
                        )
                        if mastermind_file
                        else None
                },
                "real_game_executor": {
                    "present":
                        REAL_GAME_EXECUTOR_FILE.exists(),
                    "file":
                        str(
                            REAL_GAME_EXECUTOR_FILE
                        )
                },
                "official_platform_bridge": {
                    "present":
                        OFFICIAL_PLATFORM_BRIDGE_FILE.exists(),
                    "file":
                        str(
                            OFFICIAL_PLATFORM_BRIDGE_FILE
                        )
                }
            },
            "time": utc_now()
        }

    @app.post("/api/run")
    def api_run(
        payload: Dict[str, Any]
    ) -> Any:

        command = str(
            payload.get(
                "command"
            )
            or
            payload.get(
                "prompt"
            )
            or
            ""
        ).strip()

        supplied_job_id = (
            payload.get(
                "job_id"
            )
        )

        result = execute_command(
            command=command,
            job_id=(
                str(
                    supplied_job_id
                )
                if supplied_job_id
                else None
            )
        )

        status_code = (
            200
            if result.get(
                "success"
            )
            else 500
        )

        return JSONResponse(
            content=result,
            status_code=status_code
        )


# ============================================================
# CLI
# ============================================================

def main() -> int:

    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "MAJD AI AGENT — REAL GAME "
            "BUILD AND PUBLICATION PIPELINE"
        )
    )

    parser.add_argument(
        "command",
        nargs="?",
        default="",
        help="MAJD AI command"
    )

    parser.add_argument(
        "--job-id",
        default=None
    )

    parser.add_argument(
        "--health",
        action="store_true"
    )

    args = parser.parse_args()

    if args.health:

        mastermind_file = (
            find_mastermind_file()
        )

        health_result = {
            "success": True,
            "system": SYSTEM_NAME,
            "agent": AGENT_NAME,
            "version": VERSION,
            "components": {
                "mastermind": (
                    str(
                        mastermind_file
                    )
                    if mastermind_file
                    else None
                ),
                "executor": {
                    "file":
                        str(
                            REAL_GAME_EXECUTOR_FILE
                        ),
                    "exists":
                        REAL_GAME_EXECUTOR_FILE.exists()
                },
                "bridge": {
                    "file":
                        str(
                            OFFICIAL_PLATFORM_BRIDGE_FILE
                        ),
                    "exists":
                        OFFICIAL_PLATFORM_BRIDGE_FILE.exists()
                }
            }
        }

        print(
            json.dumps(
                health_result,
                ensure_ascii=False,
                indent=2,
                default=str
            )
        )

        return 0

    command = str(
        args.command
        or ""
    ).strip()

    if not command:

        try:
            command = input(
                "MAJD COMMAND: "
            ).strip()
        except EOFError:
            command = ""

    result = execute_command(
        command=command,
        job_id=args.job_id
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import importlib.util
import inspect
import json
import os
import re
import sys
import traceback
import uuid

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Callable

try:
    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse, JSONResponse
    import uvicorn
except Exception:
    FastAPI = None
    Request = Any
    HTMLResponse = None
    JSONResponse = None
    uvicorn = None


# ============================================================
# IDENTITY
# ============================================================

SYSTEM_NAME = "MAJD-GAME-FACTORY"
AGENT_NAME = "MAJD-AI-AGENT"
VERSION = "4.0.0"

OWNER_ID = os.getenv(
    "MAJD_OWNER_ID",
    "OWNER",
).strip() or "OWNER"


# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent

STATE_DIR = (
    ROOT_DIR
    / "majd_factory_state"
    / "agent"
)

STATE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_DIR = (
    ROOT_DIR
    / "majd_game_output"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

FILES = {
    "01":
        ROOT_DIR
        / "MAJD-AI-MASTERMIND-01.py",

    "02":
        ROOT_DIR
        / "MAJD-OWNER-COMMAND-CENTER-02.py",

    "03":
        ROOT_DIR
        / "MAJD-REAL-GAME-EXECUTOR-03.py",

    "04":
        ROOT_DIR
        / "MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py",

    "06":
        ROOT_DIR
        / "MAJD-FULL-EXECUTION-RUNTIME-06.py",

    "08":
        ROOT_DIR
        / "MAJD-AI-CONTENT-MEDIA-FACTORY-08.py",
}


# ============================================================
# ROUTES
# ============================================================

class Route(str, Enum):
    STATUS = "STATUS"
    AUTONOMOUS = "AUTONOMOUS"
    REPAIR = "REPAIR"
    CREATE_GAME = "CREATE_GAME"
    CONTENT = "CONTENT"
    PLATFORM = "PLATFORM"
    GENERAL = "GENERAL"


# ============================================================
# UTILITIES
# ============================================================

def now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def build_job_id(
    value: Optional[str] = None,
) -> str:

    raw = str(
        value
        or
        uuid.uuid4()
    )

    raw = re.sub(
        r"[^A-Za-z0-9._-]+",
        "-",
        raw,
    ).strip(
        ".-_"
    )

    return (
        raw
        or
        str(uuid.uuid4())
    )[:120]


def save_receipt(
    job_id: str,
    data: Dict[str, Any],
) -> str:

    path = (
        STATE_DIR
        / f"{job_id}.json"
    )

    temporary = path.with_suffix(
        ".json.tmp"
    )

    temporary.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    temporary.replace(
        path
    )

    return str(
        path
    )


# ============================================================
# MODULE LOADER
# ============================================================

def load_module(
    path: Path,
    name: str,
) -> Any:

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
            str(path)
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
    **kwargs: Any,
) -> Any:

    try:
        signature = (
            inspect.signature(
                function
            )
        )
    except Exception:
        return function(
            **kwargs
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

    if accepts_kwargs:
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


def normalize(
    value: Any,
    default_success: bool = False,
    status: str = "RESULT",
) -> Dict[str, Any]:

    if isinstance(
        value,
        dict,
    ):
        result = dict(
            value
        )

        result.setdefault(
            "success",
            default_success,
        )

        result.setdefault(
            "status",
            status,
        )

        return result

    if value is None:
        return {
            "success":
                False,

            "status":
                "COMPONENT_RETURNED_NONE",
        }

    return {
        "success":
            default_success,

        "status":
            status,

        "result":
            value,
    }


def call_first(
    component: Any,
    names: Sequence[str],
    **kwargs: Any,
) -> Dict[str, Any]:

    for name in names:

        function = getattr(
            component,
            name,
            None,
        )

        if not callable(
            function
        ):
            continue

        try:
            value = (
                call_supported(
                    function,
                    **kwargs,
                )
            )

            result = (
                normalize(
                    value,
                    False,
                    name.upper()
                    + "_RESULT",
                )
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
                    "COMPONENT_CALL_FAILED",

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
            "INTERFACE_MISSING",

        "expected_any":
            list(names),
    }


# ============================================================
# ROUTING
# ============================================================

def contains_any(
    text: str,
    words: Sequence[str],
) -> bool:

    lowered = (
        text.lower()
    )

    return any(
        word.lower()
        in lowered

        for word
        in words
    )


def detect_content_type(
    command: str,
) -> Optional[str]:

    lowered = (
        command.lower()
    )

    mappings = [
        (
            "movie",
            (
                "فيلم",
                "movie",
            ),
        ),
        (
            "series",
            (
                "مسلسل",
                "series",
            ),
        ),
        (
            "episode",
            (
                "حلقة",
                "episode",
            ),
        ),
        (
            "short",
            (
                "شورت",
                "short",
            ),
        ),
        (
            "story",
            (
                "ستوري",
                "story",
            ),
        ),
        (
            "poster",
            (
                "بوستر",
                "poster",
            ),
        ),
        (
            "thumbnail",
            (
                "صورة مصغرة",
                "thumbnail",
            ),
        ),
        (
            "animation",
            (
                "أنيميشن",
                "انيميشن",
                "animation",
            ),
        ),
        (
            "vfx",
            (
                "vfx",
                "مؤثرات بصرية",
            ),
        ),
        (
            "voice",
            (
                "تعليق صوتي",
                "voice",
            ),
        ),
        (
            "music",
            (
                "موسيقى",
                "music",
            ),
        ),
        (
            "subtitle",
            (
                "ترجمة نصية",
                "subtitle",
            ),
        ),
        (
            "dubbing",
            (
                "دبلجة",
                "dubbing",
            ),
        ),
        (
            "live",
            (
                "بث مباشر",
                "live",
            ),
        ),
        (
            "social_post",
            (
                "منشور",
                "بوست",
                "social post",
            ),
        ),
        (
            "channel",
            (
                "قناة",
                "channel",
            ),
        ),
        (
            "game_media",
            (
                "إعلام لعبة",
                "game media",
            ),
        ),
        (
            "video",
            (
                "فيديو",
                "video",
            ),
        ),
        (
            "image",
            (
                "صورة",
                "image",
            ),
        ),
        (
            "audio",
            (
                "ملف صوتي",
                "audio",
            ),
        ),
    ]

    for content_type, words in mappings:

        if any(
            word.lower()
            in lowered

            for word
            in words
        ):
            return content_type

    if (
        "ترجم"
        in command
        or
        "translate"
        in lowered
    ):
        return "translation"

    return None


def classify(
    command: str,
) -> tuple[
    Route,
    Optional[str],
]:

    command = (
        command.strip()
    )

    content_type = (
        detect_content_type(
            command
        )
    )

    if (
        contains_any(
            command,
            (
                "status",
                "health",
                "report",
                "حالة",
                "تقرير",
                "التقدم",
                "وش صار",
            ),
        )
        and
        not contains_any(
            command,
            (
                "لعبة",
                "game",
            ),
        )
    ):
        return (
            Route.STATUS,
            content_type,
        )

    if content_type:
        return (
            Route.CONTENT,
            content_type,
        )

    if contains_any(
        command,
        (
            "autonomous",
            "ذاتي",
            "تلقائي",
            "بدون تدخل",
            "استمر",
            "راقب",
        ),
    ):
        return (
            Route.AUTONOMOUS,
            None,
        )

    if contains_any(
        command,
        (
            "repair",
            "fix",
            "diagnose",
            "أصلح",
            "اصلح",
            "إصلاح",
            "تشخيص",
            "اربط",
            "ربط",
            "اعتماديات",
        ),
    ):
        return (
            Route.REPAIR,
            None,
        )

    if contains_any(
        command,
        (
            "لعبة",
            "game",
            "3d",
            "2d",
            "استراتيجية",
            "مغامرات",
            "سباق",
        ),
    ):
        return (
            Route.CREATE_GAME,
            None,
        )

    if contains_any(
        command,
        (
            "platform",
            "deploy",
            "service",
            "server",
            "publish",
            "test",
            "build",
            "منصة",
            "سيرفر",
            "خدمة",
            "نشر",
            "اختبار",
            "بناء",
            "حزم",
        ),
    ):
        return (
            Route.PLATFORM,
            None,
        )

    return (
        Route.GENERAL,
        None,
    )


# ============================================================
# GAME REQUEST
# ============================================================

def build_game_request(
    command: str,
) -> Dict[str, Any]:

    lowered = (
        command.lower()
    )

    if (
        "3d"
        in lowered
        or
        "ثلاث"
        in command
    ):
        dimension = "3D"
    else:
        dimension = "2D"

    if (
        "استراتيجية"
        in command
        or
        "strategy"
        in lowered
    ):
        genre = "STRATEGY"

    elif (
        "سباق"
        in command
        or
        "race"
        in lowered
    ):
        genre = "RACING"

    else:
        genre = "ADVENTURE"

    name = re.sub(
        r"\s+",
        "-",
        command[:80],
    ).strip(
        "-"
    )

    return {
        "success":
            True,

        "type":
            "CREATE_GAME",

        "name":
            name
            or
            "MAJD-GAME",

        "genre":
            genre,

        "dimension":
            dimension,

        "platform":
            [
                "WEB"
            ],

        "request":
            command,

        "command":
            command,

        "requested_at":
            now(),

        "source":
            AGENT_NAME,
    }


# ============================================================
# GAME PIPELINE
# ============================================================

def game_pipeline(
    command: str,
    job_id: str,
) -> Dict[str, Any]:

    try:
        mastermind = load_module(
            FILES["01"],
            "majd_01",
        )

    except Exception as error:
        return {
            "success":
                False,

            "status":
                "MASTERMIND_LOAD_FAILED",

            "error":
                str(error),
        }

    request = (
        build_game_request(
            command
        )
    )

    mastermind_result = (
        call_first(
            mastermind,
            (
                "process_game_request",
                "execute_game_request",
                "execute_request",
                "process_request",
                "execute",
                "run",
            ),
            command=
                command,
            request=
                request,
            job_id=
                job_id,
            owner=
                OWNER_ID,
            output_root=
                str(
                    OUTPUT_DIR
                ),
        )
    )

    if (
        mastermind_result.get(
            "success"
        )
        is not True
    ):
        return {
            "success":
                False,

            "status":
                "MASTERMIND_STAGE_FAILED",

            "mastermind":
                mastermind_result,
        }

    prepared = dict(
        request
    )

    for key in (
        "request",
        "prepared_request",
        "game_request",
        "result",
    ):
        value = (
            mastermind_result.get(
                key
            )
        )

        if isinstance(
            value,
            dict,
        ):
            prepared.update(
                value
            )
            break

    try:
        executor = load_module(
            FILES["03"],
            "majd_03",
        )

    except Exception as error:
        return {
            "success":
                False,

            "status":
                "EXECUTOR_LOAD_FAILED",

            "error":
                str(error),
        }

    executor_result = (
        call_first(
            executor,
            (
                "execute_game_request",
                "execute",
                "run",
            ),
            request=
                prepared,
            job_id=
                job_id,
            output_root=
                str(
                    OUTPUT_DIR
                ),
        )
    )

    if (
        executor_result.get(
            "success"
        )
        is not True
    ):
        return {
            "success":
                False,

            "status":
                "REAL_GAME_EXECUTION_FAILED",

            "executor":
                executor_result,
        }

    artifact = None

    for key in (
        "artifact",
        "artifact_path",
        "build_path",
        "game_dir",
        "output_path",
        "playable_artifact",
    ):

        value = (
            executor_result.get(
                key
            )
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
            path = (
                path.resolve()
            )

        if path.exists():
            artifact = path
            break

    if artifact is None:
        return {
            "success":
                False,

            "status":
                "REAL_ARTIFACT_NOT_FOUND",

            "executor":
                executor_result,
        }

    index_file = (
        artifact
        /
        "index.html"
    )

    if (
        not artifact.is_dir()
        or
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
                "REAL_ARTIFACT_INVALID",

            "artifact":
                str(
                    artifact
                ),
        }

    try:
        bridge = load_module(
            FILES["04"],
            "majd_04",
        )

    except Exception as error:
        return {
            "success":
                False,

            "status":
                "BRIDGE_LOAD_FAILED",

            "error":
                str(error),
        }

    bridge_result = (
        call_first(
            bridge,
            (
                "publish_game",
                "publish",
                "send_game",
                "send_to_majd",
                "execute",
            ),
            game_dir=
                artifact,
            artifact=
                artifact,
            game_name=
                prepared.get(
                    "name",
                    "MAJD-GAME",
                ),
            job_id=
                job_id,
            request=
                prepared,
            payload=
                prepared,
        )
    )

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
                "OFFICIAL_PLATFORM_PUBLISH_FAILED",

            "bridge":
                bridge_result,
        }

    published_directory = (
        bridge_result.get(
            "published_directory"
        )
    )

    if not published_directory:
        return {
            "success":
                False,

            "status":
                "PUBLISHED_DIRECTORY_MISSING",

            "bridge":
                bridge_result,
        }

    published_path = Path(
        str(
            published_directory
        )
    )

    if not published_path.is_absolute():
        published_path = (
            ROOT_DIR
            /
            published_path
        ).resolve()

    else:
        published_path = (
            published_path.resolve()
        )

    published_index = (
        published_path
        /
        "index.html"
    )

    if (
        not published_path.is_dir()
        or
        not published_index.exists()
        or
        published_index.stat().st_size
        <=
        0
    ):
        return {
            "success":
                False,

            "status":
                "FINAL_PUBLICATION_VALIDATION_FAILED",

            "bridge":
                bridge_result,
        }

    return {
        "success":
            True,

        "status":
            "GAME_BUILT_AND_PUBLISHED",

        "artifact":
            str(
                artifact
            ),

        "published_directory":
            str(
                published_path
            ),

        "game_path":
            bridge_result.get(
                "game_path"
            ),

        "public_url":
            bridge_result.get(
                "public_url"
            ),

        "bridge":
            bridge_result,
    }


# ============================================================
# RUNTIME 06
# ============================================================

def runtime_status(
    command: str = "status",
) -> Dict[str, Any]:

    try:
        runtime = load_module(
            FILES["06"],
            "majd_06",
        )

    except Exception as error:
        return {
            "success":
                False,

            "status":
                "RUNTIME_LOAD_FAILED",

            "error":
                str(error),
        }

    result = (
        call_first(
            runtime,
            (
                "autonomous_status",
                "inspect_platform",
                "capability_progress",
                "capability_map",
                "infrastructure_findings",
            ),
            command=
                command,
            owner=
                OWNER_ID,
        )
    )

    if (
        result.get(
            "status"
        )
        !=
        "INTERFACE_MISSING"
    ):
        return result

    for class_name in (
        "FullRuntime",
        "AutonomousRuntime",
        "OwnerBridge",
    ):

        cls = getattr(
            runtime,
            class_name,
            None,
        )

        if not inspect.isclass(
            cls
        ):
            continue

        try:
            instance = (
                call_supported(
                    cls,
                    owner=
                        OWNER_ID,
                )
            )

        except Exception:
            try:
                instance = cls()
            except Exception:
                continue

        return call_first(
            instance,
            (
                "status",
                "health",
                "inspect",
                "autonomous_status",
            ),
            command=
                command,
            owner=
                OWNER_ID,
        )

    return {
        "success":
            False,

        "status":
            "RUNTIME_STATUS_INTERFACE_MISSING",
    }


def runtime_execute(
    command: str,
    route: Route,
    job_id: str,
) -> Dict[str, Any]:

    try:
        runtime = load_module(
            FILES["06"],
            "majd_06",
        )

    except Exception as error:
        return {
            "success":
                False,

            "status":
                "RUNTIME_LOAD_FAILED",

            "error":
                str(error),
        }

    request = {
        "type":
            route.value,

        "command":
            command,

        "job_id":
            job_id,

        "owner":
            OWNER_ID,

        "source":
            AGENT_NAME,
    }

    kwargs = {
        "command":
            command,

        "request":
            request,

        "job_id":
            job_id,

        "owner":
            OWNER_ID,

        "mode":
            route.value,

        "work_mode":
            route.value,

        "autonomous":
            route
            ==
            Route.AUTONOMOUS,
    }

    result = (
        call_first(
            runtime,
            (
                "execute_owner_runtime",
                "execute_full_factory",
                "execute",
                "run",
            ),
            **kwargs,
        )
    )

    if (
        result.get(
            "status"
        )
        !=
        "INTERFACE_MISSING"
    ):
        return result

    for class_name in (
        "FullRuntime",
        "AutonomousRuntime",
        "OwnerBridge",
    ):

        cls = getattr(
            runtime,
            class_name,
            None,
        )

        if not inspect.isclass(
            cls
        ):
            continue

        try:
            instance = (
                call_supported(
                    cls,
                    owner=
                        OWNER_ID,
                )
            )

        except Exception:
            try:
                instance = cls()
            except Exception:
                continue

        return call_first(
            instance,
            (
                "execute",
                "run",
                "execute_owner_runtime",
                "execute_full_factory",
            ),
            **kwargs,
        )

    return {
        "success":
            False,

        "status":
            "RUNTIME_EXECUTION_INTERFACE_MISSING",
    }


# ============================================================
# MEDIA FACTORY 08
# ============================================================

def media_status() -> Dict[str, Any]:

    try:
        media = load_module(
            FILES["08"],
            "majd_08",
        )

    except Exception as error:
        return {
            "success":
                False,

            "status":
                "MEDIA_FACTORY_LOAD_FAILED",

            "error":
                str(error),
        }

    health = (
        call_first(
            media,
            (
                "factory_health",
                "health",
            ),
        )
    )

    capabilities = (
        call_first(
            media,
            (
                "factory_capabilities",
                "capability_report",
            ),
        )
    )

    success = (
        health.get(
            "success"
        )
        is True
        or
        str(
            health.get(
                "status",
                "",
            )
        ).upper()
        in {
            "READY",
            "ACTIVE",
            "HEALTHY",
        }
    )

    return {
        "success":
            success,

        "status":
            "MEDIA_FACTORY_STATUS",

        "health":
            health,

        "capabilities":
            capabilities,
    }


def media_execute(
    command: str,
    content_type: Optional[str],
    job_id: str,
) -> Dict[str, Any]:

    try:
        media = load_module(
            FILES["08"],
            "majd_08",
        )

    except Exception as error:
        return {
            "success":
                False,

            "status":
                "MEDIA_FACTORY_LOAD_FAILED",

            "error":
                str(error),
        }

    selected_type = (
        content_type
        or
        "video"
    )

    create_job = getattr(
        media,
        "create_media_job",
        None,
    )

    produce_media = getattr(
        media,
        "produce_media",
        None,
    )

    if (
        callable(
            create_job
        )
        and
        callable(
            produce_media
        )
    ):

        try:
            created = (
                call_supported(
                    create_job,
                    content_type=
                        selected_type,
                    title=
                        command[:180],
                    description=
                        command,
                    language=
                        "ar",
                    request={
                        "command":
                            command,

                        "owner":
                            OWNER_ID,

                        "agent_job_id":
                            job_id,
                    },
                )
            )

            created_result = (
                normalize(
                    created,
                    True,
                    "MEDIA_JOB_CREATED",
                )
            )

            media_job_id = (
                created_result.get(
                    "id"
                )
                or
                created_result.get(
                    "job_id"
                )
            )

            if (
                not media_job_id
                and
                isinstance(
                    created_result.get(
                        "data"
                    ),
                    dict,
                )
            ):
                media_job_id = (
                    created_result[
                        "data"
                    ].get(
                        "id"
                    )
                )

            if not media_job_id:
                return {
                    "success":
                        False,

                    "status":
                        "MEDIA_JOB_ID_MISSING",

                    "create_result":
                        created_result,
                }

            produced = (
                call_supported(
                    produce_media,
                    job_id=
                        str(
                            media_job_id
                        ),
                    job=
                        str(
                            media_job_id
                        ),
                )
            )

            production_result = (
                normalize(
                    produced,
                    False,
                    "MEDIA_PRODUCTION_RESULT",
                )
            )

            return {
                "success":
                    production_result.get(
                        "success"
                    )
                    is True,

                "status":
                    production_result.get(
                        "status",
                        "MEDIA_PRODUCTION_RESULT",
                    ),

                "media_job_id":
                    str(
                        media_job_id
                    ),

                "production":
                    production_result,
            }

        except Exception as error:
            return {
                "success":
                    False,

                "status":
                    "MEDIA_PIPELINE_FAILED",

                "error":
                    (
                        f"{type(error).__name__}: "
                        f"{error}"
                    ),

                "traceback":
                    traceback.format_exc(),
            }

    get_factory = getattr(
        media,
        "get_factory",
        None,
    )

    if callable(
        get_factory
    ):
        try:
            factory = (
                get_factory()
            )

            create_method = getattr(
                factory,
                "create_job",
                None,
            )

            produce_method = getattr(
                factory,
                "produce",
                None,
            )

            if (
                callable(
                    create_method
                )
                and
                callable(
                    produce_method
                )
            ):
                job = (
                    call_supported(
                        create_method,
                        content_type=
                            selected_type,
                        title=
                            command[:180],
                        description=
                            command,
                        language=
                            "ar",
                        request={
                            "command":
                                command,

                            "owner":
                                OWNER_ID,

                            "agent_job_id":
                                job_id,
                        },
                    )
                )

                result = (
                    call_supported(
                        produce_method,
                        job=
                            job,
                    )
                )

                return normalize(
                    result,
                    False,
                    "MEDIA_PRODUCTION_RESULT",
                )

        except Exception as error:
            return {
                "success":
                    False,

                "status":
                    "MEDIA_INSTANCE_PIPELINE_FAILED",

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
            "MEDIA_FACTORY_INTERFACE_MISSING",
    }


# ============================================================
# FULL STATUS
# ============================================================

def component_presence() -> Dict[str, Any]:

    return {
        key: {
            "exists":
                path.exists(),

            "path":
                str(path),

            "size":
                (
                    path.stat().st_size
                    if path.exists()
                    else 0
                ),
        }

        for key, path
        in FILES.items()
    }


def full_status() -> Dict[str, Any]:

    runtime = (
        runtime_status()
    )

    media = (
        media_status()
    )

    return {
        "success":
            (
                runtime.get(
                    "success"
                )
                is True
                or
                media.get(
                    "success"
                )
                is True
            ),

        "status":
            "MAJD_FULL_STATUS",

        "runtime":
            runtime,

        "media_factory":
            media,

        "components":
            component_presence(),

        "time":
            now(),
    }


# ============================================================
# MAIN COMMAND EXECUTION
# ============================================================

def execute_command(
    command: str,
    job_id: Optional[str] = None,
) -> Dict[str, Any]:

    started_at = (
        now()
    )

    actual_job_id = (
        build_job_id(
            job_id
        )
    )

    route, content_type = (
        classify(
            command
        )
    )

    try:

        if not command.strip():

            execution = {
                "success":
                    False,

                "status":
                    "EMPTY_COMMAND",
            }

        elif (
            route
            ==
            Route.STATUS
        ):

            execution = (
                full_status()
            )

        elif (
            route
            ==
            Route.CREATE_GAME
        ):

            execution = (
                game_pipeline(
                    command,
                    actual_job_id,
                )
            )

        elif (
            route
            ==
            Route.CONTENT
        ):

            execution = (
                media_execute(
                    command,
                    content_type,
                    actual_job_id,
                )
            )

        else:

            execution = (
                runtime_execute(
                    command,
                    route,
                    actual_job_id,
                )
            )

        result = {
            "success":
                execution.get(
                    "success"
                )
                is True,

            "status":
                execution.get(
                    "status",
                    "UNKNOWN_RESULT",
                ),

            "system":
                SYSTEM_NAME,

            "agent":
                AGENT_NAME,

            "version":
                VERSION,

            "owner":
                OWNER_ID,

            "job_id":
                actual_job_id,

            "route":
                route.value,

            "content_type":
                content_type,

            "command":
                command,

            "execution":
                execution,

            "started_at":
                started_at,

            "finished_at":
                now(),
        }

    except Exception as error:

        result = {
            "success":
                False,

            "status":
                "AGENT_SYSTEM_CRASH",

            "job_id":
                actual_job_id,

            "route":
                route.value,

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
                now(),
        }

    try:
        result[
            "agent_receipt"
        ] = save_receipt(
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
        job_id,
    )


def process_command(
    command: str,
    job_id: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    return execute_command(
        command,
        job_id,
    )


def execute(
    command: str,
    job_id: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    return execute_command(
        command,
        job_id,
    )


def run(
    command: str,
    job_id: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    return execute_command(
        command,
        job_id,
    )


# ============================================================
# FASTAPI
# ============================================================

app = (
    FastAPI(
        title=
            "MAJD AI AGENT - Sovereign Command Router",

        version=
            VERSION,
    )

    if FastAPI
    else None
)


if app:

    @app.get(
        "/",
        response_class=HTMLResponse,
    )
    async def ui():

        return HTMLResponse(
            """
<!doctype html>

<html
lang="ar"
dir="rtl"
>

<meta charset="utf-8">

<meta
name="viewport"
content="width=device-width,initial-scale=1"
>

<title>
MAJD AI Agent
</title>

<style>

body {
    background:#0b0f1c;
    color:#fff;
    font-family:Arial;
    margin:0;
    display:grid;
    place-items:center;
    min-height:100vh;
}

.box {
    width:min(760px,92vw);
    background:#151e2e;
    padding:24px;
    border-radius:18px;
}

textarea {
    width:100%;
    min-height:130px;
    box-sizing:border-box;
    background:#0b0f1c;
    color:#fff;
    padding:12px;
}

button {
    width:100%;
    padding:14px;
    margin-top:10px;
    background:#f0c84b;
    border:0;
    font-weight:bold;
}

pre {
    white-space:pre-wrap;
    word-break:break-word;
    background:#0b0f1c;
    padding:12px;
    max-height:55vh;
    overflow:auto;
}

</style>

<div class="box">

<h1>
MAJD AI Agent
</h1>

<textarea id="command">
اعرض حالة المنصة والتقدم الحالي
</textarea>

<button onclick="runAI()">
تنفيذ
</button>

<pre id="output">
جاهز
</pre>

</div>

<script>

async function runAI() {

    output.textContent =
        'جاري التنفيذ...';

    try {

        let response =
            await fetch(
                '/run',
                {
                    method:'POST',

                    headers:{
                        'Content-Type':
                            'application/json'
                    },

                    body:
                        JSON.stringify({
                            command:
                                command.value
                        })
                }
            );

        let data =
            await response.json();

        output.textContent =
            JSON.stringify(
                data,
                null,
                2
            );

    } catch(error) {

        output.textContent =
            'خطأ: '
            +
            error;
    }
}

</script>

</html>
"""
        )


    @app.get(
        "/health"
    )
    async def health():
        return full_status()


    async def execute_request(
        request: Request,
    ):

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

        result = (
            execute_command(
                command,
                (
                    str(
                        body.get(
                            "job_id"
                        )
                    )
                    if body.get(
                        "job_id"
                    )
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
    async def run_api(
        request: Request,
    ):
        return await execute_request(
            request
        )


    @app.post(
        "/api/run"
    )
    async def run_api_alt(
        request: Request,
    ):
        return await execute_request(
            request
        )


# ============================================================
# CLI
# ============================================================

def main() -> int:

    parser = (
        argparse.ArgumentParser()
    )

    parser.add_argument(
        "command",
        nargs="*",
    )

    parser.add_argument(
        "--job-id",
    )

    parser.add_argument(
        "--status",
        action="store_true",
    )

    parser.add_argument(
        "--host",
        default=
            os.getenv(
                "MAJD_AI_AGENT_HOST",
                "0.0.0.0",
            ),
    )

    parser.add_argument(
        "--port",
        type=int,
        default=
            int(
                os.getenv(
                    "PORT",
                    "8000",
                )
            ),
    )

    args = (
        parser.parse_args()
    )

    if args.status:

        result = (
            full_status()
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
            else 1
        )

    if args.command:

        command = (
            " ".join(
                args.command
            ).strip()
        )

        result = (
            execute_command(
                command,
                args.job_id,
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
            else 1
        )

    if (
        not app
        or
        not uvicorn
    ):

        print(
            json.dumps(
                {
                    "success":
                        False,

                    "status":
                        "FASTAPI_NOT_AVAILABLE",
                },
                ensure_ascii=False,
            )
        )

        return 1

    uvicorn.run(
        app,
        host=
            args.host,
        port=
            args.port,
    )

    return 0


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    raise SystemExit(
        main()
    )

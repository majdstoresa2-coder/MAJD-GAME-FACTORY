#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-FULL-EXECUTION-RUNTIME-06.py
============================================================

SOVEREIGN FULL EXECUTION RUNTIME

هذا الملف هو بوابة التنفيذ المركزية بين واجهة المالك
والعقل المدبر السيادي.

المسؤوليات:
- استقبال أمر المالك.
- تحميل مركز أوامر المالك 02.
- التحقق من هوية وسلطة المالك عبر 02.
- تحليل الأوامر العربية والإنجليزية.
- تمرير أوامر الحالة إلى 02.
- تمرير CREATE_GAME إلى العقل المدبر 01.
- تمرير الأوامر العامة/البرمجية إلى العقل المدبر 01.
- عدم إعادة تنفيذ 03 و04 داخل 06 لأن 01 يديرهما.
- التحقق من نتيجة العقل المدبر.
- التحقق من Artifact الحقيقي في أوامر إنشاء الألعاب.
- التحقق من أن النسخة المنشورة موجودة فعلياً.
- منع HTTP 200 أو accepted من أن يعتبر نجاح تنفيذ.
- حفظ Runtime ID ونتيجة كل مرحلة.
- إعادة النتيجة النهائية الحقيقية لواجهة المالك.

السلسلة:

OWNER UI
   ↓
06 FULL EXECUTION RUNTIME
   ↓
02 OWNER COMMAND CENTER
   ↓
COMMAND CLASSIFICATION
   ├── STATUS / SYSTEM_STATUS
   │       ↓
   │      02
   │       ↓
   │   REAL STATUS
   │
   └── CREATE_GAME / GENERAL OWNER OBJECTIVE
           ↓
          01 SOVEREIGN MASTERMIND
           ↓
      PLAN / DIAGNOSE / REPAIR
           ↓
          03
           ↓
      REAL BUILD / TEST
           ↓
      PLAYABLE ARTIFACT
           ↓
          04
           ↓
      PUBLISHED ARTIFACT
           ↓
          01
           ↓
      VERIFIED FINAL RESULT
           ↓
          06
           ↓
        OWNER UI

قاعدة أساسية:
06 لا يكرر مسؤوليات 01.
01 هو العقل المدبر.
06 هو Runtime / Gateway / Final Verification Layer.
"""

from __future__ import annotations

import argparse
import importlib.util
import inspect
import json
import sys
import traceback
import uuid

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Optional


# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(
    __file__
).resolve().parent


MASTERMIND_FILE = (
    ROOT_DIR
    /
    "MAJD-AI-MASTERMIND-01.py"
)


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


STATE_DIR = (
    ROOT_DIR
    /
    "majd_factory_state"
)


RUNTIME_DIR = (
    STATE_DIR
    /
    "runtime"
)


OUTPUT_DIR = (
    ROOT_DIR
    /
    "majd_game_output"
)


PUBLIC_DIR = (
    ROOT_DIR
    /
    "public"
)


ARTIFACTS_DIR = (
    PUBLIC_DIR
    /
    "artifacts"
)


for directory in (
    STATE_DIR,
    RUNTIME_DIR,
    OUTPUT_DIR,
    PUBLIC_DIR,
    ARTIFACTS_DIR,
):

    directory.mkdir(
        parents=True,
        exist_ok=True
    )


# ============================================================
# IDENTITY
# ============================================================

SYSTEM_NAME = "MAJD-GAME-FACTORY"

RUNTIME_NAME = "MAJD-FULL-EXECUTION-RUNTIME"

VERSION = "2.0.0"

DEFAULT_OWNER = "MAJD"

OFFICIAL_MAJD_PLATFORM = "https://majd.shop"


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

def save_json(
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

    temporary.replace(
        path
    )


# ============================================================
# MODULE LOADER
# ============================================================

def load_module(
    path: Path,
    module_name: str
) -> Any:

    if not path.exists():

        raise FileNotFoundError(
            f"Required file not found: {path.name}"
        )

    spec = (
        importlib.util
        .spec_from_file_location(
            module_name,
            str(path)
        )
    )

    if (
        spec is None
        or
        spec.loader is None
    ):

        raise RuntimeError(
            f"Unable to load module: {path.name}"
        )

    module = (
        importlib.util
        .module_from_spec(
            spec
        )
    )

    sys.modules[
        module_name
    ] = module

    spec.loader.exec_module(
        module
    )

    return module


# ============================================================
# FUNCTION DISCOVERY
# ============================================================

def find_callable(
    module: Any,
    names: tuple[str, ...]
) -> Optional[
    Callable[..., Any]
]:

    for name in names:

        value = getattr(
            module,
            name,
            None
        )

        if callable(
            value
        ):

            return value

    return None


# ============================================================
# SAFE FUNCTION CALL
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

    kwargs: Dict[
        str,
        Any
    ] = {}

    for key, value in values.items():

        if (
            accepts_kwargs
            or
            key in parameters
        ):

            kwargs[
                key
            ] = value

    return function(
        **kwargs
    )


# ============================================================
# REQUIRED FILE VERIFICATION
# ============================================================

def verify_required_files() -> Dict[str, Any]:

    required = {

        "01_mastermind":
            MASTERMIND_FILE,

        "02_owner_command_center":
            OWNER_COMMAND_CENTER_FILE,

        "03_real_game_executor":
            REAL_GAME_EXECUTOR_FILE,

        "04_official_platform_bridge":
            OFFICIAL_PLATFORM_BRIDGE_FILE
    }

    files: Dict[
        str,
        Any
    ] = {}

    missing = []

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
                )
        }

        if not exists:

            missing.append(
                path.name
            )

    return {

        "success":
            not missing,

        "files":
            files,

        "missing":
            missing
    }


# ============================================================
# OWNER COMMAND CENTER BRIDGE
# ============================================================

class OwnerCommandCenterRuntime:

    def __init__(
        self
    ):

        self.module = load_module(

            OWNER_COMMAND_CENTER_FILE,

            "majd_owner_command_center_02_runtime"
        )


    # ========================================================
    # PARSE
    # ========================================================

    def parse(
        self,
        command: str
    ) -> Dict[str, Any]:

        parser_class = getattr(

            self.module,

            "OwnerCommandParser",

            None
        )

        if parser_class is None:

            return {

                "type":
                    "GENERAL_OWNER_COMMAND",

                "raw":
                    command,

                "warning":
                    "OWNER_COMMAND_PARSER_NOT_FOUND"
            }

        try:

            parser = (
                parser_class()
            )

            result = (
                parser.parse(
                    command
                )
            )

            if not isinstance(
                result,
                dict
            ):

                return {

                    "type":
                        "GENERAL_OWNER_COMMAND",

                    "raw":
                        command,

                    "warning":
                        "INVALID_PARSE_RESULT"
                }

            result_type = str(
                result.get(
                    "type",
                    ""
                )
            ).upper()

            # -----------------------------------------------
            # UNKNOWN لا يعني رفض الأمر.
            # يتحول إلى هدف عام للعقل المدبر.
            # -----------------------------------------------

            if (
                not result_type
                or
                result_type == "UNKNOWN"
            ):

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
                    (
                        f"{type(error).__name__}: "
                        f"{error}"
                    )
            }


    # ========================================================
    # EXECUTE 02
    # ========================================================

    def execute(
        self,
        command: str,
        owner: str
    ) -> Dict[str, Any]:

        function = getattr(

            self.module,

            "execute_owner_command",

            None
        )

        if not callable(
            function
        ):

            return {

                "success":
                    False,

                "status":
                    "OWNER_COMMAND_INTERFACE_MISSING",

                "message":
                    (
                        "MAJD-OWNER-COMMAND-CENTER-02.py "
                        "does not expose execute_owner_command()."
                    )
            }

        try:

            result = call_supported(

                function,

                {

                    "command":
                        command,

                    "owner":
                        owner
                }
            )

        except Exception as error:

            return {

                "success":
                    False,

                "status":
                    "OWNER_COMMAND_EXECUTION_EXCEPTION",

                "error":
                    (
                        f"{type(error).__name__}: "
                        f"{error}"
                    ),

                "traceback":
                    traceback.format_exc()
            }

        if not isinstance(
            result,
            dict
        ):

            return {

                "success":
                    False,

                "status":
                    "INVALID_OWNER_COMMAND_RESULT",

                "result_type":
                    type(
                        result
                    ).__name__
            }

        return result


# ============================================================
# MASTERMIND BRIDGE
# ============================================================

class MastermindRuntime:

    """
    06 يسلم المهمة إلى 01.

    لا يشغل 03 أو 04 بنفسه.
    01 مسؤول عن السلسلة الداخلية كاملة.
    """

    FUNCTION_NAMES = (

        "execute_request",

        "process_request",

        "execute_game_request",

        "run",

        "run_request",

        "execute",
    )


    def __init__(
        self
    ):

        self.module = load_module(

            MASTERMIND_FILE,

            "majd_ai_mastermind_01_runtime"
        )


    # ========================================================
    # EXECUTE
    # ========================================================

    def execute(
        self,
        command: str,
        request: Dict[str, Any],
        runtime_id: str,
        owner: str
    ) -> Dict[str, Any]:

        function = find_callable(

            self.module,

            self.FUNCTION_NAMES
        )

        # ----------------------------------------------------
        # FALLBACK:
        # إذا لم توجد دالة عامة، نحاول class Mastermind
        # ----------------------------------------------------

        if function is None:

            mastermind_class = getattr(

                self.module,

                "Mastermind",

                None
            )

            if mastermind_class is None:

                return {

                    "success":
                        False,

                    "status":
                        "MASTERMIND_INTERFACE_NOT_FOUND",

                    "file":
                        MASTERMIND_FILE.name,

                    "message":
                        (
                            "لم يتم العثور على واجهة تشغيل "
                            "في العقل المدبر."
                        )
                }

            try:

                instance = call_supported(

                    mastermind_class,

                    {

                        "owner":
                            owner
                    }
                )

            except Exception as error:

                return {

                    "success":
                        False,

                    "status":
                        "MASTERMIND_INITIALIZATION_FAILED",

                    "error":
                        (
                            f"{type(error).__name__}: "
                            f"{error}"
                        ),

                    "traceback":
                        traceback.format_exc()
                }

            function = getattr(

                instance,

                "run",

                None
            )

            if not callable(
                function
            ):

                return {

                    "success":
                        False,

                    "status":
                        "MASTERMIND_RUN_INTERFACE_MISSING"
                }

        # ----------------------------------------------------
        # EXECUTE MASTERMIND
        # ----------------------------------------------------

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

                    "owner":
                        owner,

                    "output_root":
                        str(
                            OUTPUT_DIR
                        )
                }
            )

        except Exception as error:

            return {

                "success":
                    False,

                "status":
                    "MASTERMIND_EXECUTION_EXCEPTION",

                "error":
                    (
                        f"{type(error).__name__}: "
                        f"{error}"
                    ),

                "traceback":
                    traceback.format_exc()
            }

        if not isinstance(
            result,
            dict
        ):

            return {

                "success":
                    False,

                "status":
                    "INVALID_MASTERMIND_RESULT",

                "result_type":
                    type(
                        result
                    ).__name__
            }

        return result


# ============================================================
# PLAYABLE ARTIFACT FINAL VERIFIER
# ============================================================

def verify_playable_artifact(
    artifact_value: Any
) -> Dict[str, Any]:

    if not artifact_value:

        return {

            "success":
                False,

            "status":
                "PLAYABLE_ARTIFACT_MISSING"
        }

    artifact = Path(
        str(
            artifact_value
        )
    )

    if not artifact.is_absolute():

        artifact = (
            ROOT_DIR
            /
            artifact
        ).resolve()

    else:

        artifact = (
            artifact.resolve()
        )

    if not artifact.exists():

        return {

            "success":
                False,

            "status":
                "PLAYABLE_ARTIFACT_NOT_FOUND",

            "artifact":
                str(
                    artifact
                )
        }

    if not artifact.is_dir():

        return {

            "success":
                False,

            "status":
                "PLAYABLE_ARTIFACT_NOT_DIRECTORY",

            "artifact":
                str(
                    artifact
                )
        }

    index_file = (
        artifact
        /
        "index.html"
    )

    if not index_file.exists():

        return {

            "success":
                False,

            "status":
                "PLAYABLE_INDEX_NOT_FOUND",

            "artifact":
                str(
                    artifact
                )
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
                "PLAYABLE_INDEX_EMPTY",

            "artifact":
                str(
                    artifact
                )
        }

    files = [

        path

        for path
        in artifact.rglob(
            "*"
        )

        if path.is_file()
    ]

    javascript_files = [

        path

        for path
        in files

        if path.suffix.lower()
        in (
            ".js",
            ".mjs"
        )
    ]

    if not javascript_files:

        return {

            "success":
                False,

            "status":
                "PLAYABLE_JAVASCRIPT_NOT_FOUND",

            "artifact":
                str(
                    artifact
                )
        }

    return {

        "success":
            True,

        "status":
            "PLAYABLE_ARTIFACT_VERIFIED",

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
            )
    }


# ============================================================
# PUBLISHED ARTIFACT FINAL VERIFIER
# ============================================================

def verify_published_result(
    platform_result: Dict[str, Any]
) -> Dict[str, Any]:

    if not isinstance(
        platform_result,
        dict
    ):

        return {

            "success":
                False,

            "status":
                "PLATFORM_RESULT_INVALID"
        }

    if not platform_result.get(
        "success"
    ):

        return {

            "success":
                False,

            "status":
                platform_result.get(
                    "status",
                    "PLATFORM_NOT_SUCCESSFUL"
                ),

            "platform":
                platform_result
        }

    published_directory = (
        platform_result.get(
            "published_directory"
        )
    )

    if not published_directory:

        return {

            "success":
                False,

            "status":
                "PUBLISHED_DIRECTORY_MISSING",

            "platform":
                platform_result
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

    if not published_path.exists():

        return {

            "success":
                False,

            "status":
                "PUBLISHED_DIRECTORY_NOT_FOUND",

            "published_directory":
                str(
                    published_path
                )
        }

    index_file = (
        published_path
        /
        "index.html"
    )

    if not index_file.exists():

        return {

            "success":
                False,

            "status":
                "PUBLISHED_INDEX_NOT_FOUND",

            "published_directory":
                str(
                    published_path
                )
        }

    public_url = (
        platform_result.get(
            "public_url"
        )
    )

    game_path = (
        platform_result.get(
            "game_path"
        )
    )

    if not public_url:

        return {

            "success":
                False,

            "status":
                "PUBLIC_URL_MISSING",

            "published_directory":
                str(
                    published_path
                )
        }

    if not game_path:

        return {

            "success":
                False,

            "status":
                "GAME_PATH_MISSING",

            "published_directory":
                str(
                    published_path
                )
        }

    return {

        "success":
            True,

        "status":
            "PUBLISHED_RESULT_VERIFIED",

        "published_directory":
            str(
                published_path
            ),

        "index":
            str(
                index_file
            ),

        "game_path":
            game_path,

        "public_url":
            public_url
    }


# ============================================================
# FINAL MASTERMIND RESULT VERIFICATION
# ============================================================

def verify_mastermind_result(
    command_type: str,
    result: Dict[str, Any]
) -> Dict[str, Any]:

    if not isinstance(
        result,
        dict
    ):

        return {

            "success":
                False,

            "status":
                "INVALID_FINAL_RESULT"
        }

    if not result.get(
        "success"
    ):

        return {

            "success":
                False,

            "status":
                result.get(
                    "status",
                    "MASTERMIND_FAILED"
                ),

            "result":
                result
        }

    # --------------------------------------------------------
    # GENERAL COMMAND
    # --------------------------------------------------------

    if (
        command_type
        !=
        "CREATE_GAME"
    ):

        return {

            "success":
                True,

            "status":
                "MASTERMIND_RESULT_VERIFIED",

            "result":
                result
        }

    # --------------------------------------------------------
    # CREATE GAME REQUIRES HARD PROOF
    # --------------------------------------------------------

    artifact = (
        result.get(
            "artifact"
        )
    )

    artifact_verification = (
        verify_playable_artifact(
            artifact
        )
    )

    if not artifact_verification.get(
        "success"
    ):

        return {

            "success":
                False,

            "status":
                artifact_verification.get(
                    "status",
                    "ARTIFACT_FINAL_VERIFICATION_FAILED"
                ),

            "artifact_verification":
                artifact_verification,

            "mastermind_result":
                result
        }

    platform_result = (
        result.get(
            "platform"
        )
    )

    if not isinstance(
        platform_result,
        dict
    ):

        return {

            "success":
                False,

            "status":
                "PLATFORM_RESULT_MISSING",

            "artifact_verification":
                artifact_verification,

            "mastermind_result":
                result
        }

    publication_verification = (
        verify_published_result(
            platform_result
        )
    )

    if not publication_verification.get(
        "success"
    ):

        return {

            "success":
                False,

            "status":
                publication_verification.get(
                    "status",
                    "PUBLICATION_FINAL_VERIFICATION_FAILED"
                ),

            "artifact_verification":
                artifact_verification,

            "publication_verification":
                publication_verification,

            "mastermind_result":
                result
        }

    return {

        "success":
            True,

        "status":
            "FULL_EXECUTION_VERIFIED",

        "artifact":
            artifact_verification,

        "publication":
            publication_verification,

        "result":
            result
    }


# ============================================================
# FULL EXECUTION RUNTIME
# ============================================================

class MajdFullExecutionRuntime:

    def __init__(
        self
    ):

        self.runtime_id = str(
            uuid.uuid4()
        )


    # ========================================================
    # STATE PATH
    # ========================================================

    def state_path(
        self
    ) -> Path:

        return (
            RUNTIME_DIR
            /
            f"{self.runtime_id}.json"
        )


    # ========================================================
    # SAVE
    # ========================================================

    def save(
        self,
        state: Dict[str, Any]
    ) -> None:

        state[
            "updated_at"
        ] = utc_now()

        save_json(
            self.state_path(),
            state
        )


    # ========================================================
    # EXECUTE
    # ========================================================

    def execute(
        self,
        command: str,
        owner: str = DEFAULT_OWNER
    ) -> Dict[str, Any]:

        command = str(
            command
            or
            ""
        ).strip()

        state: Dict[
            str,
            Any
        ] = {

            "runtime_id":
                self.runtime_id,

            "system":
                SYSTEM_NAME,

            "runtime":
                RUNTIME_NAME,

            "version":
                VERSION,

            "owner":
                owner,

            "command":
                command,

            "official_platform":
                OFFICIAL_MAJD_PLATFORM,

            "started_at":
                utc_now(),

            "updated_at":
                utc_now(),

            "finished_at":
                None,

            "success":
                False,

            "status":
                "STARTING",

            "stages":
                {}
        }

        self.save(
            state
        )

        try:

            # =================================================
            # EMPTY COMMAND
            # =================================================

            if not command:

                state[
                    "status"
                ] = (
                    "EMPTY_OWNER_COMMAND"
                )

                state[
                    "error"
                ] = (
                    "Owner command cannot be empty."
                )

                state[
                    "finished_at"
                ] = utc_now()

                self.save(
                    state
                )

                return state


            # =================================================
            # VERIFY CORE FILES
            # =================================================

            state[
                "status"
            ] = (
                "VERIFYING_CORE"
            )

            self.save(
                state
            )

            files_result = (
                verify_required_files()
            )

            state[
                "stages"
            ][
                "core_files"
            ] = files_result

            if not files_result.get(
                "success"
            ):

                state[
                    "status"
                ] = (
                    "REQUIRED_FILES_MISSING"
                )

                state[
                    "error"
                ] = (
                    "REQUIRED_FILES_MISSING"
                )

                state[
                    "finished_at"
                ] = utc_now()

                self.save(
                    state
                )

                return state


            # =================================================
            # LOAD 02
            # =================================================

            state[
                "status"
            ] = (
                "OWNER_COMMAND_CENTER"
            )

            self.save(
                state
            )

            owner_runtime = (
                OwnerCommandCenterRuntime()
            )


            # =================================================
            # PARSE COMMAND
            # =================================================

            parsed_request = (
                owner_runtime.parse(
                    command
                )
            )

            command_type = str(
                parsed_request.get(
                    "type",
                    "GENERAL_OWNER_COMMAND"
                )
            ).upper()

            if (
                not command_type
                or
                command_type == "UNKNOWN"
            ):

                command_type = (
                    "GENERAL_OWNER_COMMAND"
                )

                parsed_request[
                    "type"
                ] = (
                    command_type
                )

            state[
                "stages"
            ][
                "command"
            ] = {

                "success":
                    True,

                "status":
                    "OWNER_COMMAND_PARSED",

                "type":
                    command_type,

                "request":
                    parsed_request
            }

            self.save(
                state
            )


            # =================================================
            # STATUS COMMANDS STAY IN 02
            # =================================================

            if command_type in (

                "STATUS",

                "SYSTEM_STATUS",

            ):

                state[
                    "status"
                ] = (
                    "OWNER_STATUS_EXECUTION"
                )

                self.save(
                    state
                )

                result = (
                    owner_runtime.execute(
                        command=command,
                        owner=owner
                    )
                )

                state[
                    "stages"
                ][
                    "owner_status"
                ] = result

                state[
                    "result"
                ] = result

                state[
                    "success"
                ] = bool(
                    result.get(
                        "success",
                        False
                    )
                )

                state[
                    "status"
                ] = str(
                    result.get(
                        "status"
                    )
                    or
                    (
                        "COMPLETED"
                        if state[
                            "success"
                        ]
                        else
                        "FAILED"
                    )
                )

                if not state[
                    "success"
                ]:

                    state[
                        "error"
                    ] = (
                        result.get(
                            "error"
                        )
                        or
                        result.get(
                            "message"
                        )
                        or
                        state[
                            "status"
                        ]
                    )

                state[
                    "finished_at"
                ] = utc_now()

                self.save(
                    state
                )

                return state


            # =================================================
            # EVERYTHING ELSE GOES TO 01
            # =================================================

            state[
                "status"
            ] = (
                "MASTERMIND_EXECUTION"
            )

            self.save(
                state
            )

            mastermind = (
                MastermindRuntime()
            )

            mastermind_result = (
                mastermind.execute(

                    command=
                        command,

                    request=
                        parsed_request,

                    runtime_id=
                        self.runtime_id,

                    owner=
                        owner
                )
            )

            state[
                "stages"
            ][
                "mastermind"
            ] = mastermind_result

            self.save(
                state
            )


            # =================================================
            # MASTER FAILURE
            # =================================================

            if not mastermind_result.get(
                "success"
            ):

                state[
                    "success"
                ] = False

                state[
                    "status"
                ] = str(
                    mastermind_result.get(
                        "status",
                        "MASTERMIND_FAILED"
                    )
                )

                state[
                    "error"
                ] = (
                    mastermind_result.get(
                        "error"
                    )
                    or
                    mastermind_result.get(
                        "message"
                    )
                    or
                    state[
                        "status"
                    ]
                )

                state[
                    "result"
                ] = (
                    mastermind_result
                )

                state[
                    "finished_at"
                ] = utc_now()

                self.save(
                    state
                )

                return state


            # =================================================
            # FINAL VERIFICATION
            # =================================================

            state[
                "status"
            ] = (
                "FINAL_VERIFICATION"
            )

            self.save(
                state
            )

            final_verification = (
                verify_mastermind_result(

                    command_type=
                        command_type,

                    result=
                        mastermind_result
                )
            )

            state[
                "stages"
            ][
                "final_verification"
            ] = final_verification

            self.save(
                state
            )


            # =================================================
            # FINAL FAILURE
            # =================================================

            if not final_verification.get(
                "success"
            ):

                state[
                    "success"
                ] = False

                state[
                    "status"
                ] = str(
                    final_verification.get(
                        "status",
                        "FINAL_VERIFICATION_FAILED"
                    )
                )

                state[
                    "error"
                ] = (
                    state[
                        "status"
                    ]
                )

                state[
                    "result"
                ] = (
                    mastermind_result
                )

                state[
                    "finished_at"
                ] = utc_now()

                self.save(
                    state
                )

                return state


            # =================================================
            # VERIFIED SUCCESS
            # =================================================

            state[
                "success"
            ] = True

            state[
                "status"
            ] = (
                "COMPLETED"
            )

            state[
                "result"
            ] = (
                mastermind_result
            )

            state[
                "verification"
            ] = (
                final_verification
            )


            if (
                command_type
                ==
                "CREATE_GAME"
            ):

                publication = (
                    final_verification.get(
                        "publication",
                        {}
                    )
                )

                artifact = (
                    final_verification.get(
                        "artifact",
                        {}
                    )
                )

                state[
                    "artifact"
                ] = (
                    artifact.get(
                        "artifact"
                    )
                )

                state[
                    "game_path"
                ] = (
                    publication.get(
                        "game_path"
                    )
                )

                state[
                    "public_url"
                ] = (
                    publication.get(
                        "public_url"
                    )
                )

                state[
                    "published"
                ] = True

                state[
                    "message"
                ] = (
                    "تم تنفيذ أمر المالك عبر العقل المدبر، "
                    "وبناء اللعبة والتحقق من Artifact "
                    "والتحقق من النسخة المنشورة فعلياً."
                )

            else:

                state[
                    "message"
                ] = (
                    "تم تنفيذ أمر المالك عبر العقل المدبر "
                    "وتم التحقق من النتيجة."
                )


            state[
                "finished_at"
            ] = utc_now()

            self.save(
                state
            )

            return state


        # =====================================================
        # UNEXPECTED ERROR
        # =====================================================

        except Exception as error:

            state[
                "success"
            ] = False

            state[
                "status"
            ] = (
                "RUNTIME_EXCEPTION"
            )

            state[
                "error"
            ] = (
                f"{type(error).__name__}: "
                f"{error}"
            )

            state[
                "traceback"
            ] = (
                traceback.format_exc()
            )

            state[
                "finished_at"
            ] = utc_now()

            self.save(
                state
            )

            return state


# ============================================================
# PUBLIC API
# ============================================================

def execute_full_factory(
    command: str,
    owner: str = DEFAULT_OWNER,
    **kwargs: Any
) -> Dict[str, Any]:

    runtime = (
        MajdFullExecutionRuntime()
    )

    return runtime.execute(

        command=
            command,

        owner=
            owner
    )


# ============================================================
# COMPATIBILITY API
# ============================================================

def execute_owner_runtime(
    command: str,
    owner: str = DEFAULT_OWNER,
    **kwargs: Any
) -> Dict[str, Any]:

    return execute_full_factory(

        command=
            command,

        owner=
            owner
    )


def execute(
    command: str,
    owner: str = DEFAULT_OWNER,
    **kwargs: Any
) -> Dict[str, Any]:

    return execute_full_factory(

        command=
            command,

        owner=
            owner
    )


def run(
    command: str,
    owner: str = DEFAULT_OWNER,
    **kwargs: Any
) -> Dict[str, Any]:

    return execute_full_factory(

        command=
            command,

        owner=
            owner
    )


# ============================================================
# OUTPUT
# ============================================================

def print_result(
    result: Dict[str, Any]
) -> None:

    print(

        json.dumps(

            result,

            ensure_ascii=False,

            indent=2,

            default=str
        )
    )


# ============================================================
# CLI
# ============================================================

def main() -> int:

    parser = argparse.ArgumentParser(

        description=(
            "MAJD SOVEREIGN FULL EXECUTION RUNTIME 06"
        )
    )


    parser.add_argument(

        "command",

        nargs="+",

        help="Owner command in Arabic or English"
    )


    parser.add_argument(

        "--owner",

        default=
            DEFAULT_OWNER,

        help=
            "Owner identity"
    )


    args = (
        parser.parse_args()
    )


    command = " ".join(
        args.command
    ).strip()


    print(
        "=============================================="
    )

    print(
        "MAJD GAME FACTORY"
    )

    print(
        "SOVEREIGN FULL EXECUTION RUNTIME 06"
    )

    print(
        "=============================================="
    )

    print(
        f"OWNER: {args.owner}"
    )

    print(
        f"COMMAND: {command}"
    )

    print(
        f"PLATFORM: {OFFICIAL_MAJD_PLATFORM}"
    )

    print(
        "=============================================="
    )


    result = execute_full_factory(

        command=
            command,

        owner=
            args.owner
    )


    print_result(
        result
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

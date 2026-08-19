#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-FULL-EXECUTION-RUNTIME-05.py
=================================

FULL EXECUTION RUNTIME

وظيفة هذا الملف:
- استقبال أمر المالك.
- تشغيل مركز أوامر المالك 02.
- تشغيل العقل المدبر 01 فعلياً.
- ربط منفذ الألعاب الحقيقي 03.
- ربط منصة مجد الرسمية عبر 04.
- منع النجاح الوهمي.
- التحقق من وجود مخرجات لعبة حقيقية.
- التحقق من وجود Playable Artifact فعلي.
- حفظ نتيجة التشغيل النهائية.
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

ROOT_DIR = Path(__file__).resolve().parent

MASTERMIND_FILE = (
    ROOT_DIR / "MAJD-AI-MASTERMIND-01.py"
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

STATE_DIR = (
    ROOT_DIR / "majd_factory_state"
)

RUNTIME_DIR = (
    STATE_DIR / "runtime"
)

OUTPUT_DIR = (
    ROOT_DIR / "majd_game_output"
)

RUNTIME_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CONSTANTS
# ============================================================

SYSTEM_NAME = "MAJD-GAME-FACTORY"

RUNTIME_NAME = "MAJD-FULL-EXECUTION-RUNTIME"

VERSION = "1.0.0"

DEFAULT_OWNER = "MAJD"

OFFICIAL_MAJD_PLATFORM = "https://majd.shop/"


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

    temp = path.with_suffix(
        path.suffix + ".tmp"
    )

    with temp.open(
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

    temp.replace(path)


# ============================================================
# MODULE LOADER
# ============================================================

def load_module(
    path: Path,
    module_name: str
):

    if not path.exists():

        raise FileNotFoundError(
            f"Required file not found: {path.name}"
        )

    spec = importlib.util.spec_from_file_location(
        module_name,
        str(path)
    )

    if (
        spec is None
        or
        spec.loader is None
    ):

        raise RuntimeError(
            f"Unable to load module: {path.name}"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    sys.modules[module_name] = module

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
) -> Optional[Callable[..., Any]]:

    for name in names:

        value = getattr(
            module,
            name,
            None
        )

        if callable(value):

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

    kwargs: Dict[str, Any] = {}

    accepts_kwargs = any(
        parameter.kind
        ==
        inspect.Parameter.VAR_KEYWORD
        for parameter
        in signature.parameters.values()
    )

    for key, value in values.items():

        if (
            accepts_kwargs
            or
            key in signature.parameters
        ):

            kwargs[key] = value

    return function(
        **kwargs
    )


# ============================================================
# FILE VERIFICATION
# ============================================================

def verify_required_files() -> Dict[str, Any]:

    files = {

        "mastermind":
            MASTERMIND_FILE,

        "owner_command_center":
            OWNER_COMMAND_CENTER_FILE,

        "real_game_executor":
            REAL_GAME_EXECUTOR_FILE,

        "official_platform_bridge":
            OFFICIAL_PLATFORM_BRIDGE_FILE
    }

    status: Dict[str, Any] = {}

    missing = []

    for name, path in files.items():

        exists = path.exists()

        status[name] = {

            "file":
                path.name,

            "exists":
                exists
        }

        if not exists:

            missing.append(
                path.name
            )

    return {

        "success":
            not missing,

        "files":
            status,

        "missing":
            missing
    }


# ============================================================
# MASTERMIND RUNTIME
# ============================================================

class MastermindRuntime:

    FUNCTION_NAMES = (

        "process_game_request",

        "execute_game_request",

        "execute_request",

        "process_request",

        "run_request",

        "run",

        "execute"
    )

    def __init__(self):

        self.module = load_module(
            MASTERMIND_FILE,
            "majd_ai_mastermind_01"
        )


    def execute(
        self,
        command: str,
        request: Dict[str, Any],
        job_id: str,
        owner: str
    ) -> Dict[str, Any]:

        function = find_callable(
            self.module,
            self.FUNCTION_NAMES
        )

        if function is None:

            return {

                "success": False,

                "status":
                    "MASTERMIND_INTERFACE_NOT_FOUND",

                "message":
                    (
                        "تم تحميل ملف العقل المدبر، "
                        "لكن لم يتم العثور على واجهة تشغيل عامة متوافقة."
                    ),

                "file":
                    MASTERMIND_FILE.name
            }

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
                    job_id,

                "owner":
                    owner,

                "output_root":
                    str(OUTPUT_DIR)
            }
        )

        if result is None:

            return {

                "success": True,

                "status":
                    "MASTERMIND_EXECUTED",

                "request":
                    request
            }

        if isinstance(
            result,
            dict
        ):

            result.setdefault(
                "success",
                True
            )

            return result

        return {

            "success": True,

            "status":
                "MASTERMIND_EXECUTED",

            "result":
                result
        }


# ============================================================
# OWNER COMMAND CENTER RUNTIME
# ============================================================

class OwnerCommandCenterRuntime:

    def __init__(self):

        self.module = load_module(
            OWNER_COMMAND_CENTER_FILE,
            "majd_owner_command_center_02"
        )


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

                "success": False,

                "status":
                    "OWNER_COMMAND_INTERFACE_MISSING",

                "message":
                    (
                        "MAJD-OWNER-COMMAND-CENTER-02.py "
                        "does not expose execute_owner_command()."
                    )
            }

        result = function(
            command=command,
            owner=owner
        )

        if not isinstance(
            result,
            dict
        ):

            return {

                "success": False,

                "status":
                    "INVALID_OWNER_COMMAND_RESULT",

                "message":
                    "Owner Command Center returned invalid result."
            }

        return result


# ============================================================
# REAL GAME EXECUTOR RUNTIME
# ============================================================

class RealGameExecutorRuntime:

    def __init__(self):

        self.module = load_module(
            REAL_GAME_EXECUTOR_FILE,
            "majd_real_game_executor_03_runtime"
        )


    def execute(
        self,
        request: Dict[str, Any],
        job_id: str
    ) -> Dict[str, Any]:

        function = getattr(
            self.module,
            "execute_game_request",
            None
        )

        if not callable(
            function
        ):

            return {

                "success": False,

                "status":
                    "REAL_EXECUTOR_INTERFACE_MISSING",

                "message":
                    (
                        "MAJD-REAL-GAME-EXECUTOR-03.py "
                        "does not expose execute_game_request()."
                    )
            }

        result = function(

            request=request,

            job_id=job_id,

            output_root=str(
                OUTPUT_DIR
            )
        )

        if not isinstance(
            result,
            dict
        ):

            return {

                "success": False,

                "status":
                    "INVALID_EXECUTOR_RESULT",

                "message":
                    "Real Game Executor returned invalid result."
            }

        return result


# ============================================================
# OFFICIAL PLATFORM BRIDGE RUNTIME
# ============================================================

class OfficialPlatformRuntime:

    FUNCTION_NAMES = (

        "publish_game",

        "send_game",

        "send_to_majd",

        "publish",

        "execute"
    )

    def __init__(self):

        self.module = load_module(
            OFFICIAL_PLATFORM_BRIDGE_FILE,
            "majd_official_platform_bridge_04"
        )


    def execute(
        self,
        artifact: str,
        request: Dict[str, Any],
        job_id: str
    ) -> Dict[str, Any]:

        function = find_callable(
            self.module,
            self.FUNCTION_NAMES
        )

        if function is None:

            return {

                "success": False,

                "status":
                    "PLATFORM_BRIDGE_INTERFACE_NOT_FOUND",

                "platform":
                    OFFICIAL_MAJD_PLATFORM,

                "message":
                    (
                        "تم تحميل جسر منصة مجد، "
                        "لكن لم يتم العثور على واجهة نشر عامة متوافقة."
                    )
            }

        result = call_supported(

            function,

            {
                "artifact":
                    artifact,

                "artifact_path":
                    artifact,

                "build_path":
                    artifact,

                "request":
                    request,

                "payload":
                    request,

                "job_id":
                    job_id,

                "platform_url":
                    OFFICIAL_MAJD_PLATFORM
            }
        )

        if result is None:

            return {

                "success": True,

                "status":
                    "PLATFORM_BRIDGE_EXECUTED",

                "platform":
                    OFFICIAL_MAJD_PLATFORM
            }

        if isinstance(
            result,
            dict
        ):

            result.setdefault(
                "platform",
                OFFICIAL_MAJD_PLATFORM
            )

            return result

        return {

            "success": True,

            "status":
                "PLATFORM_BRIDGE_EXECUTED",

            "platform":
                OFFICIAL_MAJD_PLATFORM,

            "result":
                result
        }


# ============================================================
# ARTIFACT VERIFICATION
# ============================================================

def verify_artifact(
    result: Dict[str, Any]
) -> Dict[str, Any]:

    artifact = (
        result.get("artifact")
        or
        result.get("build_path")
        or
        result.get("output_path")
    )

    if not artifact:

        return {

            "success": False,

            "status":
                "PLAYABLE_ARTIFACT_MISSING",

            "message":
                "Real executor returned success without an artifact."
        }

    artifact_path = Path(
        str(artifact)
    )

    if not artifact_path.is_absolute():

        artifact_path = (
            ROOT_DIR
            /
            artifact_path
        ).resolve()

    if not artifact_path.exists():

        return {

            "success": False,

            "status":
                "PLAYABLE_ARTIFACT_NOT_FOUND",

            "artifact":
                str(artifact_path),

            "message":
                "Declared playable artifact does not exist."
        }

    if artifact_path.is_file():

        size = artifact_path.stat().st_size

        if size <= 0:

            return {

                "success": False,

                "status":
                    "PLAYABLE_ARTIFACT_EMPTY",

                "artifact":
                    str(artifact_path)
            }

    elif artifact_path.is_dir():

        files = [

            path
            for path
            in artifact_path.rglob("*")
            if path.is_file()
        ]

        if not files:

            return {

                "success": False,

                "status":
                    "PLAYABLE_ARTIFACT_EMPTY",

                "artifact":
                    str(artifact_path)
            }

    return {

        "success": True,

        "status":
            "PLAYABLE_ARTIFACT_VERIFIED",

        "artifact":
            str(artifact_path)
    }


# ============================================================
# FULL EXECUTION RUNTIME
# ============================================================

class MajdFullExecutionRuntime:

    def __init__(self):

        self.runtime_id = str(
            uuid.uuid4()
        )


    def execute(
        self,
        command: str,
        owner: str = DEFAULT_OWNER
    ) -> Dict[str, Any]:

        started_at = utc_now()

        state: Dict[str, Any] = {

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
                started_at,

            "status":
                "STARTING",

            "stages":
                {}
        }

        state_file = (
            RUNTIME_DIR
            /
            f"{self.runtime_id}.json"
        )

        save_json(
            state_file,
            state
        )

        try:

            # =================================================
            # VERIFY 01 - 04
            # =================================================

            verification = (
                verify_required_files()
            )

            state["stages"]["files"] = (
                verification
            )

            if not verification["success"]:

                state["status"] = (
                    "FAILED"
                )

                state["error"] = (
                    "REQUIRED_FILES_MISSING"
                )

                save_json(
                    state_file,
                    state
                )

                return state

            # =================================================
            # LOAD OWNER COMMAND CENTER
            # =================================================

            owner_runtime = (
                OwnerCommandCenterRuntime()
            )

            owner_module = (
                owner_runtime.module
            )

            parser_class = getattr(
                owner_module,
                "OwnerCommandParser",
                None
            )

            if parser_class is None:

                raise RuntimeError(
                    "OwnerCommandParser missing from file 02."
                )

            parser = parser_class()

            parsed_request = parser.parse(
                command
            )

            state["stages"]["command"] = {

                "success":
                    True,

                "status":
                    "OWNER_COMMAND_RECEIVED",

                "request":
                    parsed_request
            }

            if (
                parsed_request.get("type")
                !=
                "CREATE_GAME"
            ):

                state["status"] = (
                    "FAILED"
                )

                state["error"] = (
                    "COMMAND_IS_NOT_CREATE_GAME"
                )

                save_json(
                    state_file,
                    state
                )

                return state

            # =================================================
            # 01 - MASTERMIND
            # =================================================

            state["status"] = (
                "MASTERMIND"
            )

            save_json(
                state_file,
                state
            )

            mastermind = (
                MastermindRuntime()
            )

            mastermind_result = (
                mastermind.execute(

                    command=command,

                    request=parsed_request,

                    job_id=self.runtime_id,

                    owner=owner
                )
            )

            state["stages"]["mastermind"] = (
                mastermind_result
            )

            if not mastermind_result.get(
                "success"
            ):

                state["status"] = (
                    "FAILED"
                )

                state["error"] = (
                    mastermind_result.get(
                        "status",
                        "MASTERMIND_FAILED"
                    )
                )

                save_json(
                    state_file,
                    state
                )

                return state

            prepared_request = (
                mastermind_result.get(
                    "request"
                )
                or
                mastermind_result.get(
                    "payload"
                )
                or
                parsed_request
            )

            if not isinstance(
                prepared_request,
                dict
            ):

                prepared_request = (
                    parsed_request
                )

            # =================================================
            # 03 - REAL GAME EXECUTOR
            # =================================================

            state["status"] = (
                "REAL_GAME_EXECUTION"
            )

            save_json(
                state_file,
                state
            )

            executor = (
                RealGameExecutorRuntime()
            )

            executor_result = (
                executor.execute(

                    request=prepared_request,

                    job_id=self.runtime_id
                )
            )

            state["stages"]["executor"] = (
                executor_result
            )

            if not executor_result.get(
                "success"
            ):

                state["status"] = (
                    "FAILED"
                )

                state["error"] = (
                    executor_result.get(
                        "status",
                        "REAL_GAME_EXECUTION_FAILED"
                    )
                )

                save_json(
                    state_file,
                    state
                )

                return state

            # =================================================
            # VERIFY PLAYABLE ARTIFACT
            # =================================================

            artifact_result = (
                verify_artifact(
                    executor_result
                )
            )

            state["stages"]["artifact"] = (
                artifact_result
            )

            if not artifact_result.get(
                "success"
            ):

                state["status"] = (
                    "FAILED"
                )

                state["error"] = (
                    artifact_result.get(
                        "status",
                        "ARTIFACT_VERIFICATION_FAILED"
                    )
                )

                save_json(
                    state_file,
                    state
                )

                return state

            artifact = (
                artifact_result[
                    "artifact"
                ]
            )

            # =================================================
            # 04 - OFFICIAL MAJD PLATFORM
            # =================================================

            state["status"] = (
                "PLATFORM_BRIDGE"
            )

            save_json(
                state_file,
                state
            )

            platform = (
                OfficialPlatformRuntime()
            )

            platform_result = (
                platform.execute(

                    artifact=artifact,

                    request=prepared_request,

                    job_id=self.runtime_id
                )
            )

            state["stages"]["platform"] = (
                platform_result
            )

            # عدم إعلان النشر إذا لم ينجح الجسر فعلياً.
            if not platform_result.get(
                "success"
            ):

                state["status"] = (
                    "READY"
                )

                state["success"] = True

                state["published"] = False

                state["artifact"] = (
                    artifact
                )

                state["message"] = (
                    "اللعبة جاهزة وقابلة للعب، "
                    "لكن جسر النشر الرسمي لم يؤكد النشر."
                )

            else:

                state["status"] = (
                    "COMPLETED"
                )

                state["success"] = True

                state["published"] = True

                state["artifact"] = (
                    artifact
                )

                state["message"] = (
                    "تم تنفيذ سلسلة المصنع والتحقق "
                    "من Playable Artifact وربط منصة مجد."
                )

            state["finished_at"] = (
                utc_now()
            )

            save_json(
                state_file,
                state
            )

            return state

        except Exception as error:

            state["success"] = False

            state["status"] = (
                "FAILED"
            )

            state["error"] = (
                f"{type(error).__name__}: {error}"
            )

            state["traceback"] = (
                traceback.format_exc()
            )

            state["finished_at"] = (
                utc_now()
            )

            save_json(
                state_file,
                state
            )

            return state


# ============================================================
# PUBLIC API
# ============================================================

def execute_full_factory(
    command: str,
    owner: str = DEFAULT_OWNER
) -> Dict[str, Any]:

    runtime = (
        MajdFullExecutionRuntime()
    )

    return runtime.execute(
        command=command,
        owner=owner
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
            "MAJD FULL EXECUTION RUNTIME"
        )
    )

    parser.add_argument(

        "command",

        nargs="+",

        help="Owner game creation command"
    )

    parser.add_argument(

        "--owner",

        default=DEFAULT_OWNER,

        help="Owner identity"
    )

    args = parser.parse_args()

    command = " ".join(
        args.command
    ).strip()

    print(
        "========================================"
    )

    print(
        "MAJD GAME FACTORY - FULL EXECUTION"
    )

    print(
        "========================================"
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
        "========================================"
    )

    result = execute_full_factory(
        command=command,
        owner=args.owner
    )

    print_result(
        result
    )

    return (
        0
        if result.get("success")
        else 1
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )

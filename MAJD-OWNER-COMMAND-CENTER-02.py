#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-OWNER-COMMAND-CENTER-02.py
================================

OWNER COMMAND CENTER

المسؤوليات:
- استقبال أوامر المالك.
- التحقق من سلطة المالك.
- تحليل أوامر إنشاء الألعاب.
- إنشاء Job حقيقي لكل أمر.
- تمرير الأمر إلى العقل المدبر.
- تمرير أمر اللعبة إلى منفذ الألعاب الحقيقي.
- متابعة حالات التنفيذ.
- منع رسائل النجاح الوهمية.
- حفظ سجل كامل للأوامر والنتائج.

المسار المستهدف:

OWNER
  ↓
COMMAND CENTER
  ↓
MASTERMIND
  ↓
REAL GAME EXECUTOR
  ↓
BUILD
  ↓
TEST
  ↓
AUTO REPAIR
  ↓
PLAYABLE ARTIFACT
  ↓
MAJD PLATFORM
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
import time
import traceback
import uuid

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional


# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent

MASTERMIND_FILE = (
    ROOT_DIR / "MAJD-AI-MASTERMIND-01.py"
)

GAME_EXECUTOR_FILE = (
    ROOT_DIR / "MAJD-REAL-GAME-EXECUTOR-03.py"
)

STATE_DIR = (
    ROOT_DIR / "majd_factory_state"
)

JOBS_DIR = (
    STATE_DIR / "jobs"
)

LOGS_DIR = (
    STATE_DIR / "logs"
)

OUTPUT_DIR = (
    ROOT_DIR / "majd_game_output"
)

OWNER_CONFIG_FILE = (
    STATE_DIR / "owner.json"
)


for directory in (
    STATE_DIR,
    JOBS_DIR,
    LOGS_DIR,
    OUTPUT_DIR,
):
    directory.mkdir(
        parents=True,
        exist_ok=True
    )


# ============================================================
# CONSTANTS
# ============================================================

SYSTEM_NAME = "MAJD-GAME-FACTORY"

COMMAND_CENTER_NAME = (
    "MAJD-OWNER-COMMAND-CENTER"
)

VERSION = "1.0.0"

OWNER_ROLE = "OWNER"

DEFAULT_OWNER_NAME = "MAJD"


# ============================================================
# JOB STATUS
# ============================================================

class JobStatus(str, Enum):

    RECEIVED = "RECEIVED"

    AUTHORIZED = "AUTHORIZED"

    PARSED = "PARSED"

    QUEUED = "QUEUED"

    EXECUTING = "EXECUTING"

    BUILDING = "BUILDING"

    TESTING = "TESTING"

    REPAIRING = "REPAIRING"

    READY = "READY"

    PUBLISHED = "PUBLISHED"

    FAILED = "FAILED"

    REJECTED = "REJECTED"


# ============================================================
# COMMAND TYPES
# ============================================================

class CommandType(str, Enum):

    CREATE_GAME = "CREATE_GAME"

    STATUS = "STATUS"

    SYSTEM_STATUS = "SYSTEM_STATUS"

    UNKNOWN = "UNKNOWN"


# ============================================================
# TIME
# ============================================================

def utc_now() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat()


# ============================================================
# SAFE JSON
# ============================================================

def save_json(
    path: Path,
    data: Dict[str, Any]
) -> None:

    temp_path = path.with_suffix(
        path.suffix + ".tmp"
    )

    with temp_path.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )

    temp_path.replace(path)


def load_json(
    path: Path,
    default: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:

    if not path.exists():

        return (
            default.copy()
            if default is not None
            else {}
        )

    try:

        with path.open(
            "r",
            encoding="utf-8"
        ) as file:

            value = json.load(file)

        if isinstance(value, dict):
            return value

    except Exception:
        pass

    return (
        default.copy()
        if default is not None
        else {}
    )


# ============================================================
# OWNER CONFIGURATION
# ============================================================

def ensure_owner_config() -> Dict[str, Any]:

    config = load_json(
        OWNER_CONFIG_FILE
    )

    if not config:

        config = {
            "owner_name": DEFAULT_OWNER_NAME,
            "role": OWNER_ROLE,
            "enabled": True,
            "created_at": utc_now()
        }

        save_json(
            OWNER_CONFIG_FILE,
            config
        )

    return config


# ============================================================
# OWNER AUTHORITY
# ============================================================

class OwnerAuthority:

    def __init__(self):

        self.config = (
            ensure_owner_config()
        )


    def authorize(
        self,
        actor: str
    ) -> bool:

        if not self.config.get(
            "enabled",
            True
        ):
            return False

        expected_owner = str(
            self.config.get(
                "owner_name",
                DEFAULT_OWNER_NAME
            )
        ).strip().lower()

        supplied_actor = str(
            actor
        ).strip().lower()

        return (
            supplied_actor
            ==
            expected_owner
        )


# ============================================================
# JOB MODEL
# ============================================================

@dataclass
class OwnerJob:

    job_id: str

    owner: str

    raw_command: str

    command_type: str

    status: str

    created_at: str

    updated_at: str

    payload: Dict[str, Any]

    result: Optional[
        Dict[str, Any]
    ] = None

    error: Optional[str] = None


# ============================================================
# JOB STORE
# ============================================================

class JobStore:

    def path(
        self,
        job_id: str
    ) -> Path:

        return (
            JOBS_DIR
            /
            f"{job_id}.json"
        )


    def save(
        self,
        job: OwnerJob
    ) -> None:

        job.updated_at = utc_now()

        save_json(
            self.path(job.job_id),
            asdict(job)
        )


    def load(
        self,
        job_id: str
    ) -> Optional[OwnerJob]:

        path = self.path(
            job_id
        )

        if not path.exists():
            return None

        data = load_json(
            path
        )

        if not data:
            return None

        return OwnerJob(
            **data
        )


# ============================================================
# COMMAND PARSER
# ============================================================

class OwnerCommandParser:

    CREATE_GAME_WORDS = (
        "أنشئ لعبة",
        "انشئ لعبة",
        "اصنع لعبة",
        "ابني لعبة",
        "ابن لعبة",
        "create game",
        "build game",
        "make game",
    )


    def parse(
        self,
        text: str
    ) -> Dict[str, Any]:

        command = (
            text.strip()
        )

        lowered = (
            command.lower()
        )


        # ----------------------------------------------------
        # JOB STATUS
        # ----------------------------------------------------

        status_match = re.search(
            r"(?:حالة|status)\s+"
            r"([a-zA-Z0-9\-_]+)",
            command,
            re.IGNORECASE
        )

        if status_match:

            return {
                "type":
                    CommandType.STATUS.value,

                "job_id":
                    status_match.group(1)
            }


        # ----------------------------------------------------
        # SYSTEM STATUS
        # ----------------------------------------------------

        if lowered in (
            "حالة النظام",
            "حالة المصنع",
            "system status",
            "factory status",
        ):

            return {
                "type":
                    CommandType.SYSTEM_STATUS.value
            }


        # ----------------------------------------------------
        # CREATE GAME
        # ----------------------------------------------------

        if any(
            word in lowered
            for word
            in self.CREATE_GAME_WORDS
        ):

            return self._parse_game(
                command
            )


        return {
            "type":
                CommandType.UNKNOWN.value,

            "raw":
                command
        }


    def _parse_game(
        self,
        command: str
    ) -> Dict[str, Any]:

        payload: Dict[str, Any] = {

            "type":
                CommandType.CREATE_GAME.value,

            "request":
                command,

            "name":
                None,

            "genre":
                None,

            "dimension":
                None,

            "platform":
                None,

            "description":
                command,

            "auto_test":
                True,

            "auto_repair":
                True,

            "produce_playable_build":
                True
        }


        # ----------------------------------------------------
        # GAME NAME
        # ----------------------------------------------------

        name_patterns = [

            r"(?:باسم|اسمها|اسم)\s+"
            r"[\"']?([^\"'\n،,]+)",

            r"(?:named|name)\s+"
            r"[\"']?([^\"'\n,]+)"
        ]


        for pattern in name_patterns:

            match = re.search(
                pattern,
                command,
                re.IGNORECASE
            )

            if match:

                name = (
                    match.group(1)
                    .strip()
                )

                name = re.split(
                    r"\s+(?:ثلاثية|ثنائي|3d|2d|للويب|للكمبيوتر|للهاتف)",
                    name,
                    maxsplit=1,
                    flags=re.IGNORECASE
                )[0].strip()

                payload["name"] = (
                    name[:120]
                )

                break


        if not payload["name"]:

            payload["name"] = (
                f"MAJD-GAME-{int(time.time())}"
            )


        # ----------------------------------------------------
        # DIMENSION
        # ----------------------------------------------------

        if re.search(
            r"\b3d\b|ثلاثي|ثلاثية",
            command,
            re.IGNORECASE
        ):

            payload["dimension"] = "3D"

        elif re.search(
            r"\b2d\b|ثنائي|ثنائية",
            command,
            re.IGNORECASE
        ):

            payload["dimension"] = "2D"


        # ----------------------------------------------------
        # GENRE
        # ----------------------------------------------------

        genres = {

            "استراتيجية":
                "STRATEGY",

            "استراتيجي":
                "STRATEGY",

            "مغامرات":
                "ADVENTURE",

            "مغامرة":
                "ADVENTURE",

            "اكشن":
                "ACTION",

            "أكشن":
                "ACTION",

            "قتال":
                "COMBAT",

            "سباق":
                "RACING",

            "رعب":
                "HORROR",

            "rpg":
                "RPG",

            "strategy":
                "STRATEGY",

            "adventure":
                "ADVENTURE",

            "action":
                "ACTION",

            "racing":
                "RACING"
        }


        for word, genre in genres.items():

            if word.lower() in command.lower():

                payload["genre"] = genre

                break


        # ----------------------------------------------------
        # TARGET PLATFORM
        # ----------------------------------------------------

        targets = []

        if re.search(
            r"ويب|web|متصفح",
            command,
            re.IGNORECASE
        ):
            targets.append("WEB")

        if re.search(
            r"كمبيوتر|pc|windows|لابتوب",
            command,
            re.IGNORECASE
        ):
            targets.append("PC")

        if re.search(
            r"جوال|هاتف|android",
            command,
            re.IGNORECASE
        ):
            targets.append("ANDROID")

        if re.search(
            r"ipad|آيباد|ايباد",
            command,
            re.IGNORECASE
        ):
            targets.append("IPAD")


        payload["platform"] = (
            targets
            if targets
            else ["WEB"]
        )


        return payload


# ============================================================
# DYNAMIC MODULE LOADER
# ============================================================

def load_python_module(
    path: Path,
    module_name: str
):

    if not path.exists():
        return None

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
        return None

    module = (
        importlib.util
        .module_from_spec(spec)
    )

    spec.loader.exec_module(
        module
    )

    return module


# ============================================================
# MASTERMIND BRIDGE
# ============================================================

class MastermindBridge:

    def __init__(self):

        self.available = (
            MASTERMIND_FILE.exists()
        )


    def status(
        self
    ) -> Dict[str, Any]:

        return {
            "available":
                self.available,

            "file":
                MASTERMIND_FILE.name
        }


    def execute(
        self,
        request: Dict[str, Any],
        job_id: str
    ) -> Dict[str, Any]:

        if not self.available:

            return {
                "success": False,

                "status":
                    "MASTERMIND_NOT_FOUND",

                "message":
                    (
                        "ملف العقل المدبر غير موجود: "
                        f"{MASTERMIND_FILE.name}"
                    ),

                "job_id":
                    job_id
            }


        try:

            module = load_python_module(
                MASTERMIND_FILE,
                "majd_ai_mastermind_01"
            )

        except Exception as error:

            return {
                "success": False,

                "status":
                    "MASTERMIND_LOAD_FAILED",

                "message":
                    str(error),

                "job_id":
                    job_id,

                "traceback":
                    traceback.format_exc()
            }


        if module is None:

            return {
                "success": False,

                "status":
                    "MASTERMIND_LOAD_FAILED",

                "message":
                    "تعذر تحميل العقل المدبر.",

                "job_id":
                    job_id
            }


        # ----------------------------------------------------
        # SUPPORTED MASTERMIND INTERFACES
        # ----------------------------------------------------

        possible_functions = (
            "execute_game_request",
            "execute_request",
            "execute_command",
            "process_request",
            "run",
        )


        for function_name in possible_functions:

            function = getattr(
                module,
                function_name,
                None
            )


            if not callable(
                function
            ):
                continue


            try:

                result = function(
                    request=request,
                    job_id=job_id
                )

            except TypeError:

                try:

                    result = function(
                        request
                    )

                except TypeError:

                    try:

                        result = function(
                            request.get(
                                "request",
                                ""
                            )
                        )

                    except Exception as error:

                        return {
                            "success": False,

                            "status":
                                "MASTERMIND_EXECUTION_FAILED",

                            "message":
                                str(error),

                            "job_id":
                                job_id,

                            "traceback":
                                traceback.format_exc()
                        }

                except Exception as error:

                    return {
                        "success": False,

                        "status":
                            "MASTERMIND_EXECUTION_FAILED",

                        "message":
                            str(error),

                        "job_id":
                            job_id,

                        "traceback":
                            traceback.format_exc()
                    }

            except Exception as error:

                return {
                    "success": False,

                    "status":
                        "MASTERMIND_EXECUTION_FAILED",

                    "message":
                        str(error),

                    "job_id":
                        job_id,

                    "traceback":
                        traceback.format_exc()
                }


            if result is None:

                return {
                    "success": True,

                    "status":
                        "MASTERMIND_EXECUTED",

                    "job_id":
                        job_id,

                    "request":
                        request
                }


            if isinstance(
                result,
                dict
            ):

                result.setdefault(
                    "job_id",
                    job_id
                )

                result.setdefault(
                    "success",
                    True
                )

                return result


            return {
                "success": True,

                "status":
                    "MASTERMIND_EXECUTED",

                "job_id":
                    job_id,

                "result":
                    result
            }


        return {
            "success": False,

            "status":
                "MASTERMIND_INTERFACE_NOT_FOUND",

            "message":
                (
                    "تم تحميل العقل المدبر، "
                    "لكن لم يتم العثور على واجهة تنفيذ معروفة."
                ),

            "job_id":
                job_id
        }


# ============================================================
# REAL GAME EXECUTOR BRIDGE
# ============================================================

class RealGameExecutorBridge:

    """
    هذا الجسر لا يعلن نجاح اللعبة من نفسه.

    النجاح لا يحدث إلا إذا كان ملف المنفذ الحقيقي موجودًا
    ونفّذ الطلب وأعاد نتيجة تؤكد وجود Artifact حقيقي.
    """

    def available(
        self
    ) -> bool:

        return (
            GAME_EXECUTOR_FILE.exists()
        )


    def execute(
        self,
        request: Dict[str, Any],
        job_id: str
    ) -> Dict[str, Any]:

        if not self.available():

            return {
                "success": False,

                "status":
                    "EXECUTOR_NOT_INSTALLED",

                "message":
                    (
                        "منفذ الألعاب الحقيقي غير مثبت بعد: "
                        f"{GAME_EXECUTOR_FILE.name}"
                    ),

                "job_id":
                    job_id
            }


        module = load_python_module(
            GAME_EXECUTOR_FILE,
            "majd_real_game_executor_03"
        )


        if module is None:

            return {
                "success": False,

                "status":
                    "EXECUTOR_LOAD_FAILED",

                "message":
                    "تعذر تحميل منفذ الألعاب الحقيقي.",

                "job_id":
                    job_id
            }


        execute_function = getattr(
            module,
            "execute_game_request",
            None
        )


        if not callable(
            execute_function
        ):

            return {
                "success": False,

                "status":
                    "EXECUTOR_INTERFACE_MISSING",

                "message":
                    (
                        "المنفذ موجود لكنه لا يحتوي "
                        "execute_game_request()."
                    ),

                "job_id":
                    job_id
            }


        result = execute_function(
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
                    "المنفذ أعاد نتيجة غير صالحة.",

                "job_id":
                    job_id
            }


        result.setdefault(
            "job_id",
            job_id
        )


        # ----------------------------------------------------
        # VERIFY REAL ARTIFACT
        # ----------------------------------------------------

        if result.get("success"):

            artifact = (
                result.get("artifact")
                or
                result.get("build_path")
            )


            if not artifact:

                result["success"] = False

                result["status"] = (
                    "ARTIFACT_MISSING"
                )

                result["message"] = (
                    "المنفذ أعلن النجاح بدون Artifact."
                )

                return result


            artifact_path = Path(
                artifact
            )


            if not artifact_path.is_absolute():

                artifact_path = (
                    ROOT_DIR
                    /
                    artifact_path
                ).resolve()


            if not artifact_path.exists():

                result["success"] = False

                result["status"] = (
                    "ARTIFACT_NOT_FOUND"
                )

                result["message"] = (
                    "مسار الـBuild المعلن غير موجود فعليًا."
                )

                return result


            result["artifact"] = str(
                artifact_path
            )


        return result


# ============================================================
# OWNER COMMAND CENTER
# ============================================================

class OwnerCommandCenter:

    def __init__(self):

        self.authority = (
            OwnerAuthority()
        )

        self.parser = (
            OwnerCommandParser()
        )

        self.jobs = (
            JobStore()
        )

        self.mastermind = (
            MastermindBridge()
        )

        self.game_executor = (
            RealGameExecutorBridge()
        )


    # ========================================================
    # CREATE JOB
    # ========================================================

    def _create_job(
        self,
        owner: str,
        raw_command: str,
        command_type: str,
        payload: Dict[str, Any]
    ) -> OwnerJob:

        now = utc_now()

        job = OwnerJob(

            job_id=str(
                uuid.uuid4()
            ),

            owner=owner,

            raw_command=raw_command,

            command_type=command_type,

            status=JobStatus.RECEIVED.value,

            created_at=now,

            updated_at=now,

            payload=payload
        )


        self.jobs.save(
            job
        )

        return job


    # ========================================================
    # SYSTEM STATUS
    # ========================================================

    def system_status(
        self
    ) -> Dict[str, Any]:

        return {

            "success": True,

            "system":
                SYSTEM_NAME,

            "command_center":
                COMMAND_CENTER_NAME,

            "version":
                VERSION,

            "owner_authority":
                True,

            "mastermind":
                self.mastermind.status(),

            "real_game_executor": {

                "available":
                    self.game_executor.available(),

                "expected_file":
                    GAME_EXECUTOR_FILE.name
            },

            "time":
                utc_now()
        }


    # ========================================================
    # JOB STATUS
    # ========================================================

    def job_status(
        self,
        job_id: str
    ) -> Dict[str, Any]:

        job = self.jobs.load(
            job_id
        )

        if job is None:

            return {

                "success": False,

                "status":
                    "JOB_NOT_FOUND",

                "job_id":
                    job_id
            }


        return {

            "success": True,

            "job":
                asdict(job)
        }


    # ========================================================
    # EXECUTE OWNER COMMAND
    # ========================================================

    def execute(
        self,
        owner: str,
        command_text: str
    ) -> Dict[str, Any]:

        parsed = self.parser.parse(
            command_text
        )


        # ----------------------------------------------------
        # STATUS COMMANDS
        # ----------------------------------------------------

        if (
            parsed.get("type")
            ==
            CommandType.SYSTEM_STATUS.value
        ):

            if not self.authority.authorize(
                owner
            ):

                return {
                    "success": False,
                    "status": "UNAUTHORIZED"
                }

            return self.system_status()


        if (
            parsed.get("type")
            ==
            CommandType.STATUS.value
        ):

            if not self.authority.authorize(
                owner
            ):

                return {
                    "success": False,
                    "status": "UNAUTHORIZED"
                }

            return self.job_status(
                parsed["job_id"]
            )


        # ----------------------------------------------------
        # CREATE JOB
        # ----------------------------------------------------

        job = self._create_job(

            owner=owner,

            raw_command=command_text,

            command_type=parsed.get(
                "type",
                CommandType.UNKNOWN.value
            ),

            payload=parsed
        )


        # ----------------------------------------------------
        # OWNER AUTHORIZATION
        # ----------------------------------------------------

        if not self.authority.authorize(
            owner
        ):

            job.status = (
                JobStatus.REJECTED.value
            )

            job.error = (
                "OWNER_AUTHORIZATION_FAILED"
            )

            self.jobs.save(
                job
            )

            return {

                "success": False,

                "job_id":
                    job.job_id,

                "status":
                    job.status,

                "message":
                    "تم رفض الأمر: سلطة المالك غير صحيحة."
            }


        job.status = (
            JobStatus.AUTHORIZED.value
        )

        self.jobs.save(
            job
        )


        # ----------------------------------------------------
        # UNKNOWN COMMAND
        # ----------------------------------------------------

        if (
            parsed.get("type")
            ==
            CommandType.UNKNOWN.value
        ):

            job.status = (
                JobStatus.REJECTED.value
            )

            job.error = (
                "UNKNOWN_COMMAND"
            )

            self.jobs.save(
                job
            )

            return {

                "success": False,

                "job_id":
                    job.job_id,

                "status":
                    job.status,

                "message":
                    "الأمر غير معروف لمركز القيادة."
            }


        job.status = (
            JobStatus.PARSED.value
        )

        self.jobs.save(
            job
        )


        # ----------------------------------------------------
        # CREATE REAL GAME
        # ----------------------------------------------------

        if (
            parsed.get("type")
            ==
            CommandType.CREATE_GAME.value
        ):

            return self._execute_game_job(
                job
            )


        job.status = (
            JobStatus.REJECTED.value
        )

        job.error = (
            "COMMAND_NOT_IMPLEMENTED"
        )

        self.jobs.save(
            job
        )


        return {

            "success": False,

            "job_id":
                job.job_id,

            "status":
                job.status,

            "message":
                "نوع الأمر معروف لكنه غير منفذ بعد."
        }


    # ========================================================
    # EXECUTE GAME JOB
    # ========================================================

    def _execute_game_job(
        self,
        job: OwnerJob
    ) -> Dict[str, Any]:

        job.status = (
            JobStatus.QUEUED.value
        )

        self.jobs.save(
            job
        )


        if not self.mastermind.available:

            job.status = (
                JobStatus.FAILED.value
            )

            job.error = (
                "MASTERMIND_NOT_FOUND"
            )

            self.jobs.save(
                job
            )

            return {

                "success": False,

                "job_id":
                    job.job_id,

                "status":
                    job.status,

                "message":
                    (
                        "ملف العقل المدبر غير موجود: "
                        f"{MASTERMIND_FILE.name}"
                    )
            }


        job.status = (
            JobStatus.EXECUTING.value
        )

        self.jobs.save(
            job
        )


        # ----------------------------------------------------
        # EXECUTE AI MASTERMIND
        # ----------------------------------------------------

        mastermind_result = (
            self.mastermind.execute(
                request=job.payload,
                job_id=job.job_id
            )
        )


        if not mastermind_result.get(
            "success"
        ):

            job.status = (
                JobStatus.FAILED.value
            )

            job.error = str(
                mastermind_result.get(
                    "status",
                    "MASTERMIND_EXECUTION_FAILED"
                )
            )

            job.result = {
                "mastermind":
                    mastermind_result
            }

            self.jobs.save(
                job
            )

            return {

                "success": False,

                "job_id":
                    job.job_id,

                "status":
                    job.status,

                "message":
                    "فشل تنفيذ العقل المدبر.",

                "mastermind":
                    mastermind_result
            }


        # ----------------------------------------------------
        # PASS MASTERMIND RESULT TO REAL EXECUTOR
        # ----------------------------------------------------

        job.payload[
            "mastermind_result"
        ] = mastermind_result

        self.jobs.save(
            job
        )


        # ----------------------------------------------------
        # EXECUTE REAL GAME EXECUTOR
        # ----------------------------------------------------

        try:

            result = (
                self.game_executor.execute(
                    request=job.payload,
                    job_id=job.job_id
                )
            )


        except Exception as error:

            job.status = (
                JobStatus.FAILED.value
            )

            job.error = (
                f"{type(error).__name__}: "
                f"{error}"
            )

            job.result = {

                "mastermind":
                    mastermind_result,

                "traceback":
                    traceback.format_exc()
            }

            self.jobs.save(
                job
            )


            return {

                "success": False,

                "job_id":
                    job.job_id,

                "status":
                    job.status,

                "message":
                    str(error)
            }


        job.result = {

            "mastermind":
                mastermind_result,

            "executor":
                result
        }


        if result.get(
            "success"
        ):

            job.status = (
                JobStatus.READY.value
            )

            job.error = None

        else:

            job.status = (
                JobStatus.FAILED.value
            )

            job.error = str(
                result.get(
                    "status",
                    "EXECUTION_FAILED"
                )
            )


        self.jobs.save(
            job
        )


        return {

            "success":
                bool(
                    result.get(
                        "success"
                    )
                ),

            "job_id":
                job.job_id,

            "status":
                job.status,

            "game":
                job.payload.get(
                    "name"
                ),

            "mastermind":
                mastermind_result,

            "result":
                result
        }


# ============================================================
# PUBLIC API
# ============================================================

def execute_owner_command(
    command: str,
    owner: str = DEFAULT_OWNER_NAME
) -> Dict[str, Any]:

    center = (
        OwnerCommandCenter()
    )

    return center.execute(
        owner=owner,
        command_text=command
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
            indent=2
        )
    )


# ============================================================
# INTERACTIVE MODE
# ============================================================

def interactive_mode(
    owner: str
) -> None:

    center = (
        OwnerCommandCenter()
    )


    print(
        "============================================"
    )

    print(
        " MAJD OWNER COMMAND CENTER"
    )

    print(
        "============================================"
    )

    print(
        f"OWNER: {owner}"
    )

    print(
        "اكتب أمر المالك."
    )

    print(
        "مثال: أنشئ لعبة استراتيجية 3D باسم مملكة مجد للويب والكمبيوتر"
    )

    print(
        "اكتب خروج للإنهاء."
    )


    while True:

        try:

            text = input(
                "\n👑 OWNER > "
            ).strip()

        except (
            EOFError,
            KeyboardInterrupt
        ):

            print()
            break


        if not text:
            continue


        if text.lower() in (
            "خروج",
            "exit",
            "quit"
        ):
            break


        result = center.execute(
            owner=owner,
            command_text=text
        )

        print_result(
            result
        )


# ============================================================
# CLI
# ============================================================

def main() -> int:

    parser = argparse.ArgumentParser(

        description=(
            "MAJD OWNER COMMAND CENTER"
        )
    )


    parser.add_argument(

        "command",

        nargs="*",

        help="Owner command"
    )


    parser.add_argument(

        "--owner",

        default=DEFAULT_OWNER_NAME,

        help="Owner identity"
    )


    parser.add_argument(

        "--status",

        dest="status_job",

        default=None,

        help="Show job status"
    )


    parser.add_argument(

        "--system-status",

        action="store_true",

        help="Show system status"
    )


    args = parser.parse_args()


    center = (
        OwnerCommandCenter()
    )


    if args.system_status:

        if not center.authority.authorize(
            args.owner
        ):

            print_result({
                "success": False,
                "status": "UNAUTHORIZED"
            })

            return 1


        print_result(
            center.system_status()
        )

        return 0


    if args.status_job:

        if not center.authority.authorize(
            args.owner
        ):

            print_result({
                "success": False,
                "status": "UNAUTHORIZED"
            })

            return 1


        print_result(
            center.job_status(
                args.status_job
            )
        )

        return 0


    if args.command:

        command_text = " ".join(
            args.command
        )


        result = center.execute(

            owner=args.owner,

            command_text=command_text
        )


        print_result(
            result
        )


        return (
            0
            if result.get("success")
            else 1
        )


    interactive_mode(
        args.owner
    )

    return 0


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )

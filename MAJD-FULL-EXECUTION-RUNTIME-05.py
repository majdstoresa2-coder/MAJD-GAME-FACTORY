#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-FULL-EXECUTION-RUNTIME-05.py
=================================

FULL EXECUTION RUNTIME
"""
from __future__ import annotations

import argparse
import importlib.util
import inspect
import json
import subprocess
import sys
import traceback
import uuid

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent

MASTERMIND_FILE = ROOT_DIR / "MAJD-AI-MASTERMIND-01.py"
OWNER_COMMAND_CENTER_FILE = ROOT_DIR / "MAJD-OWNER-COMMAND-CENTER-02.py"
REAL_GAME_EXECUTOR_FILE = ROOT_DIR / "MAJD-REAL-GAME-EXECUTOR-03.py"
OFFICIAL_PLATFORM_BRIDGE_FILE = ROOT_DIR / "MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py"

STATE_DIR = ROOT_DIR / "majd_factory_state"
RUNTIME_DIR = STATE_DIR / "runtime"
OUTPUT_DIR = ROOT_DIR / "majd_game_output"

RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CONSTANTS
# ============================================================

SYSTEM_NAME = "MAJD-GAME-FACTORY"
RUNTIME_NAME = "MAJD-FULL-EXECUTION-RUNTIME"
VERSION = "1.0.0"
DEFAULT_OWNER = "MAJD"
OFFICIAL_MAJD_PLATFORM = "https://majd.shop/"


# ============================================================
# TIME & JSON
# ============================================================

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def save_json(path: Path, data: Dict[str, Any]) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2, default=str)
    temp.replace(path)


# ============================================================
# MODULE LOADER (للـ 01 و 03 و 04)
# ============================================================

def load_module(path: Path, module_name: str):
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path.name}")
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def find_callable(module: Any, names: tuple[str, ...]) -> Optional[Any]:
    for name in names:
        value = getattr(module, name, None)
        if callable(value):
            return value
    return None

def call_supported(function, values: Dict[str, Any]) -> Any:
    import inspect
    sig = inspect.signature(function)
    kwargs = {}
    accepts_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
    for key, value in values.items():
        if accepts_kwargs or key in sig.parameters:
            kwargs[key] = value
    return function(**kwargs)


# ============================================================
# FILE VERIFICATION
# ============================================================

def verify_required_files() -> Dict[str, Any]:
    files = {
        "mastermind": MASTERMIND_FILE,
        "owner_command_center": OWNER_COMMAND_CENTER_FILE,
        "real_game_executor": REAL_GAME_EXECUTOR_FILE,
        "official_platform_bridge": OFFICIAL_PLATFORM_BRIDGE_FILE
    }
    missing = []
    status = {}
    for name, path in files.items():
        exists = path.exists()
        status[name] = {"file": path.name, "exists": exists}
        if not exists:
            missing.append(path.name)
    return {"success": not missing, "files": status, "missing": missing}


# ============================================================
# OWNER COMMAND EXECUTOR (تم التعديل ليعمل كـ subprocess)
# ============================================================

def execute_owner_command_02(command: str) -> Dict[str, Any]:
    """
    بما أن الملف 02 مصمم ليعمل كأداة سطر أوامر (argparse)،
    نقوم بتشغيله عبر subprocess لضمان توافقه مع تصميمه الأصلي دون تحميله كـ module.
    """
    try:
        result = subprocess.run(
            [sys.executable, str(OWNER_COMMAND_CENTER_FILE), command],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            return {"success": False, "stderr": result.stderr}

        # افترض أن الملف 02 يطبع JSON في بدايته أو يحاول العودة به.
        # إذا لم يطبع JSON، فشل النظام هنا.
        # للاحتياط، سنحاول استخراج أي مخرجات JSON من الطباعة.
        import re
        json_match = re.search(r'\{.*\}', result.stdout, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        
        return {"success": True, "message": "02 Executed"}

    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================
# MASTERMIND RUNTIME
# ============================================================

class MastermindRuntime:
    FUNCTION_NAMES = ("process_game_request", "execute_game_request", "execute_request")
    def __init__(self):
        self.module = load_module(MASTERMIND_FILE, "majd_ai_mastermind_01")
    def execute(self, command: str, request: Dict[str, Any], job_id: str, owner: str) -> Dict[str, Any]:
        func = find_callable(self.module, self.FUNCTION_NAMES)
        if func is None:
            return {"success": False, "status": "MASTERMIND_INTERFACE_NOT_FOUND"}
        result = call_supported(func, {"command": command, "request": request, "payload": request, "job_id": job_id, "owner": owner, "output_root": str(OUTPUT_DIR)})
        if result is None:
            return {"success": True, "status": "MASTERMIND_EXECUTED", "request": request}
        if isinstance(result, dict):
            result.setdefault("success", True)
            return result
        return {"success": True, "status": "MASTERMIND_EXECUTED", "result": result}


# ============================================================
# REAL GAME EXECUTOR RUNTIME
# ============================================================

class RealGameExecutorRuntime:
    def __init__(self):
        self.module = load_module(REAL_GAME_EXECUTOR_FILE, "majd_real_game_executor_03_runtime")
    def execute(self, request: Dict[str, Any], job_id: str) -> Dict[str, Any]:
        func = getattr(self.module, "execute_game_request", None)
        if not callable(func):
            return {"success": False, "status": "REAL_EXECUTOR_INTERFACE_MISSING"}
        result = func(request=request, job_id=job_id, output_root=str(OUTPUT_DIR))
        if not isinstance(result, dict):
            return {"success": False, "status": "INVALID_EXECUTOR_RESULT"}
        return result


# ============================================================
# ARTIFACT VERIFICATION
# ============================================================

def verify_artifact(result: Dict[str, Any]) -> Dict[str, Any]:
    artifact = result.get("artifact") or result.get("build_path")
    if not artifact:
        return {"success": False, "status": "PLAYABLE_ARTIFACT_MISSING"}
    artifact_path = Path(str(artifact))
    if not artifact_path.is_absolute():
        artifact_path = (ROOT_DIR / artifact_path).resolve()
    if not artifact_path.exists():
        return {"success": False, "status": "PLAYABLE_ARTIFACT_NOT_FOUND", "artifact": str(artifact_path)}
    return {"success": True, "status": "PLAYABLE_ARTIFACT_VERIFIED", "artifact": str(artifact_path)}


# ============================================================
# FULL EXECUTION RUNTIME
# ============================================================

class MajdFullExecutionRuntime:
    def __init__(self):
        self.runtime_id = str(uuid.uuid4())

    def execute(self, command: str, owner: str = DEFAULT_OWNER) -> Dict[str, Any]:
        started_at = utc_now()
        state = {
            "runtime_id": self.runtime_id, "system": SYSTEM_NAME, "runtime": RUNTIME_NAME, "version": VERSION,
            "owner": owner, "command": command, "official_platform": OFFICIAL_MAJD_PLATFORM,
            "started_at": started_at, "status": "STARTING", "stages": {}
        }
        state_file = RUNTIME_DIR / f"{self.runtime_id}.json"
        save_json(state_file, state)

        try:
            verification = verify_required_files()
            state["stages"]["files"] = verification
            if not verification["success"]:
                state["status"] = "FAILED"
                state["error"] = "REQUIRED_FILES_MISSING"
                save_json(state_file, state)
                return state

            # تشغيل 02 كأمر خارجي (حل المشكلة الحقيقية)
            command_result = execute_owner_command_02(command)
            state["stages"]["command"] = command_result
            if not command_result.get("success"):
                state["status"] = "FAILED"
                state["error"] = command_result.get("error") or command_result.get("stderr") or "OWNER_COMMAND_FAILED"
                save_json(state_file, state)
                return state

            parsed_request = command_result.get("request") or command_result.get("payload") or {}
            if "CREATE_GAME" not in str(parsed_request.get("type", "")):
                state["status"] = "FAILED"
                state["error"] = "COMMAND_IS_NOT_CREATE_GAME"
                save_json(state_file, state)
                return state

            # تشغيل 01
            state["status"] = "MASTERMIND"
            save_json(state_file, state)
            mastermind = MastermindRuntime()
            mastermind_result = mastermind.execute(command=command, request=parsed_request, job_id=self.runtime_id, owner=owner)
            state["stages"]["mastermind"] = mastermind_result
            if not mastermind_result.get("success"):
                state["status"] = "FAILED"
                state["error"] = mastermind_result.get("status", "MASTERMIND_FAILED")
                save_json(state_file, state)
                return state

            prepared_request = mastermind_result.get("request") or parsed_request

            # تشغيل 03
            state["status"] = "REAL_GAME_EXECUTION"
            save_json(state_file, state)
            executor = RealGameExecutorRuntime()
            executor_result = executor.execute(request=prepared_request, job_id=self.runtime_id)
            state["stages"]["executor"] = executor_result
            if not executor_result.get("success"):
                state["status"] = "FAILED"
                state["error"] = executor_result.get("status", "REAL_GAME_EXECUTION_FAILED")
                save_json(state_file, state)
                return state

            artifact_result = verify_artifact(executor_result)
            state["stages"]["artifact"] = artifact_result
            if not artifact_result.get("success"):
                state["status"] = "FAILED"
                state["error"] = artifact_result.get("status", "ARTIFACT_VERIFICATION_FAILED")
                save_json(state_file, state)
                return state

            artifact = artifact_result["artifact"]
            state["status"] = "COMPLETED"
            state["success"] = True
            state["artifact"] = artifact
            state["message"] = "تم تنفيذ سلسلة المصنع بالكامل."
            state["finished_at"] = utc_now()
            save_json(state_file, state)
            return state

        except Exception as error:
            state["success"] = False
            state["status"] = "FAILED"
            state["error"] = f"{type(error).__name__}: {error}"
            state["traceback"] = traceback.format_exc()
            state["finished_at"] = utc_now()
            save_json(state_file, state)
            return state


# ============================================================
# CLI
# ============================================================

def main() -> int:
    parser = argparse.ArgumentParser(description=("MAJD FULL EXECUTION RUNTIME"))
    parser.add_argument("command", nargs="+", help="Owner game creation command")
    args = parser.parse_args()
    command = " ".join(args.command).strip()

    print("=" * 40)
    print("MAJD GAME FACTORY - FULL EXECUTION")
    print("=" * 40)
    print(f"COMMAND: {command}")
    print("=" * 40)

    result = MajdFullExecutionRuntime().execute(command=command)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0 if result.get("success") else 1

if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-FULL-EXECUTION-RUNTIME-05.py
=================================
FULL EXECUTION RUNTIME (السلسلة الحقيقية: 05 -> 03 -> 04)
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
import traceback
import uuid
import re

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

ROOT_DIR = Path(__file__).resolve().parent
REAL_GAME_EXECUTOR_FILE = ROOT_DIR / "MAJD-REAL-GAME-EXECUTOR-03.py"
OFFICIAL_PLATFORM_BRIDGE_FILE = ROOT_DIR / "MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py"

STATE_DIR = ROOT_DIR / "majd_factory_state"
RUNTIME_DIR = STATE_DIR / "runtime"
OUTPUT_DIR = ROOT_DIR / "majd_game_output"

RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SYSTEM_NAME = "MAJD-GAME-FACTORY"
RUNTIME_NAME = "MAJD-FULL-EXECUTION-RUNTIME"
VERSION = "1.0.0"
DEFAULT_OWNER = "MAJD"

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def save_json(path: Path, data: Dict[str, Any]) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2, default=str)
    temp.replace(path)

def load_python_module(path: Path, module_name: str):
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path.name}")
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def safe_name(value: str) -> str:
    value = str(value or "MAJD-GAME").strip()
    value = re.sub(r"[^\w\u0600-\u06FF\- ]+", "", value, flags=re.UNICODE)
    value = re.sub(r"\s+", "-", value).strip("-_")
    if not value: value = "MAJD-GAME"
    return value[:80]

def execute_real_game_executor(command: str, job_id: str) -> Dict[str, Any]:
    try:
        module = load_python_module(REAL_GAME_EXECUTOR_FILE, "majd_real_game_executor_03")
    except Exception as e:
        return {"success": False, "error": f"LOAD_FAILED: {str(e)}", "traceback": traceback.format_exc()}

    function = getattr(module, "execute_game_request", None)
    if not callable(function):
        return {"success": False, "error": "EXECUTOR_INTERFACE_NOT_FOUND"}
    
    command_text = command.strip()
    game_name = safe_name(command_text[:80]) if command_text else f"MAJD-GAME-{int(time.time())}"
    
    request_payload = {
        "type": "CREATE_GAME",
        "name": game_name,
        "genre": "ADVENTURE",
        "dimension": "2D",
        "platform": ["WEB"],
        "request": command_text,
        "auto_test": True,
        "auto_repair": True,
        "produce_playable_build": True
    }

    try:
        result = function(
            request=request_payload,
            job_id=job_id,
            output_root=str(OUTPUT_DIR)
        )
        if not isinstance(result, dict):
            return {"success": False, "error": "INVALID_RESULT_TYPE", "result_raw": str(result)}
        return result
    except Exception as e:
        return {"success": False, "error": f"EXECUTION_FAILED: {str(e)}", "traceback": traceback.format_exc()}

def execute_official_bridge(game_artifact_path: Path, job_id: str, game_name: str) -> Dict[str, Any]:
    try:
        module = load_python_module(OFFICIAL_PLATFORM_BRIDGE_FILE, "majd_official_platform_bridge_04")
    except Exception as e:
        return {"success": False, "error": f"BRIDGE_LOAD_FAILED: {str(e)}"}

    try:
        ManifestBuilder = getattr(module, "ManifestBuilder")
        PackageBuilder = getattr(module, "PackageBuilder")
        MajdPlatformClient = getattr(module, "MajdPlatformClient")

        manifest_builder = ManifestBuilder()
        manifest = manifest_builder.build(
            game_dir=game_artifact_path,
            game_name=game_name,
            game_version="1.0.0",
            metadata={"job_id": job_id}
        )

        package_builder = PackageBuilder()
        package_path = package_builder.build(game_dir=game_artifact_path, manifest=manifest)

        client = MajdPlatformClient()
        receipt = client.publish(package_path=package_path, manifest=manifest)

        return {
            "success": True,
            "status": receipt.status,
            "manifest_path": str(manifest),
            "package_path": str(package_path),
            "receipt": receipt.__dict__
        }
    except Exception as e:
        return {"success": False, "error": f"BRIDGE_EXECUTION_FAILED: {str(e)}", "traceback": traceback.format_exc()}

class MajdFullExecutionRuntime:
    def __init__(self):
        self.runtime_id = str(uuid.uuid4())

    def execute(self, command: str, owner: str = DEFAULT_OWNER) -> Dict[str, Any]:
        started_at = utc_now()
        state = {
            "runtime_id": self.runtime_id,
            "system": SYSTEM_NAME,
            "runtime": RUNTIME_NAME,
            "version": VERSION,
            "owner": owner,
            "command": command,
            "started_at": started_at,
            "status": "STARTING",
            "stages": {}
        }
        state_file = RUNTIME_DIR / f"{self.runtime_id}.json"
        save_json(state_file, state)

        try:
            state["status"] = "REAL_GAME_EXECUTOR"
            save_json(state_file, state)

            executor_result = execute_real_game_executor(command, self.runtime_id)
            state["stages"]["executor"] = executor_result

            if not executor_result.get("success"):
                state["status"] = "FAILED"
                state["error"] = executor_result.get("error") or executor_result.get("status", "EXECUTOR_FAILED")
                save_json(state_file, state)
                return state

            artifact = executor_result.get("artifact") or executor_result.get("build_path")
            if not artifact:
                state["status"] = "FAILED"
                state["error"] = "ARTIFACT_NOT_FOUND_AFTER_EXECUTOR"
                save_json(state_file, state)
                return state

            artifact_path = Path(artifact)
            if not artifact_path.exists():
                state["status"] = "FAILED"
                state["error"] = f"ARTIFACT_PATH_DOES_NOT_EXIST: {artifact}"
                save_json(state_file, state)
                return state

            game_name = executor_result.get("game_name") or safe_name(command[:80]) or "MAJD-GAME"

            state["status"] = "PLATFORM_BRIDGE"
            save_json(state_file, state)

            bridge_result = execute_official_bridge(
                game_artifact_path=artifact_path,
                job_id=self.runtime_id,
                game_name=game_name
            )
            state["stages"]["bridge"] = bridge_result

            if not bridge_result.get("success"):
                state["status"] = "PARTIALLY_COMPLETED"
                state["success"] = True
                state["artifact"] = str(artifact_path)
                state["package"] = bridge_result.get("package_path")
                state["message"] = f"تم بناء اللعبة بنجاح، لكن منصة النشر الرسمية لم تستلمها: {bridge_result.get('error')}"
                state["finished_at"] = utc_now()
                save_json(state_file, state)
                return state

            state["status"] = "COMPLETED"
            state["success"] = True
            state["artifact"] = str(artifact_path)
            state["package"] = bridge_result.get("package_path")
            state["receipt"] = bridge_result.get("receipt")
            state["message"] = "تم تنفيذ منفذ الألعاب (03) وجسر المنصة (04) بنجاح!"
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

def main() -> int:
    parser = argparse.ArgumentParser(description="MAJD FULL EXECUTION RUNTIME")
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

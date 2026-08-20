#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAJD GAME FACTORY
MAJD-FULL-EXECUTION-RUNTIME-05.py
=================================
FULL EXECUTION RUNTIME - (متوافق مع الجسر الذاتي)
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import uuid
import traceback
import re

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent
REAL_GAME_EXECUTOR_FILE = ROOT_DIR / "MAJD-REAL-GAME-EXECUTOR-03.py"
OFFICIAL_PLATFORM_BRIDGE_FILE = ROOT_DIR / "MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py"

OUTPUT_DIR = ROOT_DIR / "majd_game_output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CONSTANTS & HELPERS
# ============================================================

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def load_python_module(path: Path, module_name: str):
    if not path.exists(): raise FileNotFoundError(f"Required file not found: {path.name}")
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    if spec is None or spec.loader is None: raise RuntimeError(f"Unable to load module: {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def safe_name(value: str) -> str:
    import re
    value = str(value or "MAJD-GAME").strip()
    value = re.sub(r"[^\w\u0600-\u06FF\- ]+", "", value, flags=re.UNICODE)
    value = re.sub(r"\s+", "-", value).strip("-_")
    return value[:80] or "MAJD-GAME"

# ============================================================
# 1. REAL GAME EXECUTOR (تشغيل 03.py)
# ============================================================

def execute_real_game_executor(command: str, job_id: str) -> Dict[str, Any]:
    try:
        module = load_python_module(REAL_GAME_EXECUTOR_FILE, "majd_real_game_executor_03")
        function = getattr(module, "execute_game_request", None)
        if not callable(function): return {"success": False, "error": "EXECUTOR_INTERFACE_NOT_FOUND"}
        
        return function(request={
            "type": "CREATE_GAME", "name": safe_name(command[:80]), "genre": "ADVENTURE", 
            "dimension": "2D", "platform": ["WEB"], "request": command
        }, job_id=job_id, output_root=str(OUTPUT_DIR))
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

# ============================================================
# 2. OFFICIAL PLATFORM BRIDGE (تشغيل 04.py - النسخة الذاتية)
# ============================================================

def execute_official_bridge(game_artifact_path: Path, job_id: str, game_name: str) -> Dict[str, Any]:
    try:
        module = load_python_module(OFFICIAL_PLATFORM_BRIDGE_FILE, "majd_official_platform_bridge_04")
        publish_func = getattr(module, "publish_game", None)
        if not callable(publish_func): return {"success": False, "error": "BRIDGE_INTERFACE_MISSING"}
        return publish_func(game_dir=game_artifact_path, game_name=game_name, job_id=job_id)
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

# ============================================================
# FULL EXECUTION RUNTIME (05)
# ============================================================

class MajdFullExecutionRuntime:
    def __init__(self):
        self.runtime_id = str(uuid.uuid4())

    def execute(self, command: str) -> Dict[str, Any]:
        state = {"runtime_id": self.runtime_id, "command": command, "stages": {}}
        try:
            state["stages"]["executor"] = execute_real_game_executor(command, self.runtime_id)
            if not state["stages"]["executor"].get("success"):
                state["success"] = False
                return state

            artifact_path = Path(state["stages"]["executor"].get("artifact") or "")
            game_name = state["stages"]["executor"].get("game", safe_name(command[:80]))

            if not artifact_path.exists():
                state["success"] = False
                return state

            bridge_result = execute_official_bridge(artifact_path, self.runtime_id, game_name)
            state["stages"]["bridge"] = bridge_result

            if not bridge_result.get("success"):
                state["success"] = False
            else:
                state["success"] = True
                state["game_path"] = bridge_result.get("game_path")
                state["game_id"] = bridge_result.get("game_id")

            return state
        except Exception as e:
            state["success"] = False
            state["error"] = f"EXCEPTION: {str(e)}"
            return state

# ============================================================
# MAIN (CLI)
# ============================================================

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="+")
    args = parser.parse_args()
    command = " ".join(args.command)

    result = MajdFullExecutionRuntime().execute(command)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("success") else 1

if __name__ == "__main__":
    raise SystemExit(main())

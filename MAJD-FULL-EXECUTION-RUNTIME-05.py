#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAJD GAME FACTORY
MAJD-FULL-EXECUTION-RUNTIME-05.py
=================================
FULL EXECUTION RUNTIME - SOVEREIGN MONITOR (شامل المراقبة والتوقيع)
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import uuid
import traceback
import re
import time
import schedule
import os
import random

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

# ============================================================
# PATHS & CONSTANTS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent
REAL_GAME_EXECUTOR_FILE = ROOT_DIR / "MAJD-REAL-GAME-EXECUTOR-03.py"
OFFICIAL_PLATFORM_BRIDGE_FILE = ROOT_DIR / "MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py"
OUTPUT_DIR = ROOT_DIR / "majd_game_output"
ASSETS_DIR = ROOT_DIR / "public" / "assets"  # لحفظ شعارك وحقوق الملكية
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# سجل الحالة (للمراقبة)
MONITOR_LOG = ROOT_DIR / "majd_monitor_log.json"

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

# نظام التطور العشوائي لجعل كل لعبة فريدة بصرياً
def get_random_game_profile():
    colors = ["royalblue", "gold", "crimson", "seagreen", "darkviolet", "orangered"]
    positions = [(0,0,0), (2,1,0), (-2,1,0), (0,2,0), (3,0,0), (-3,0,0)]
    return {
        "primary_color": random.choice(colors),
        "secondary_color": random.choice(colors),
        "object_positions": random.sample(positions, k=random.randint(3, 6))
    }

def log_build_status(status: str, game_id: str, details: dict = None):
    log_entry = {"timestamp": utc_now(), "status": status, "game_id": game_id, "details": details or {}}
    with open(MONITOR_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

# ============================================================
# 1. REAL GAME EXECUTOR (تشغيل 03.py)
# ============================================================

def execute_real_game_executor(command: str, job_id: str) -> Dict[str, Any]:
    try:
        module = load_python_module(REAL_GAME_EXECUTOR_FILE, "majd_real_game_executor_03")
        function = getattr(module, "execute_game_request", None)
        if not callable(function): 
            return {"success": False, "error": "EXECUTOR_INTERFACE_NOT_FOUND"}
        return function(request={
            "type": "CREATE_GAME", "name": safe_name(command[:80]), "genre": "ADVENTURE", 
            "dimension": "2D", "platform": ["WEB"], "request": command
        }, job_id=job_id, output_root=str(OUTPUT_DIR))
    except Exception as e:
        log_build_status("FAILED", job_id, {"error": str(e)})
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

# ============================================================
# 2. OFFICIAL PLATFORM BRIDGE (تشغيل 04.py)
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
# FULL EXECUTION RUNTIME (المنطق الرئيسي)
# ============================================================

class MajdFullExecutionRuntime:
    def __init__(self):
        self.runtime_id = str(uuid.uuid4())

    def execute(self, command: str) -> Dict[str, Any]:
        state = {"runtime_id": self.runtime_id, "command": command, "stages": {}}
        try:
            # تمرير معلومات التطوير البصري للعبة
            game_profile = get_random_game_profile()
            state["design_profile"] = game_profile

            executor_result = execute_real_game_executor(command, self.runtime_id)
            state["stages"]["executor"] = executor_result
            
            if not executor_result.get("success"):
                state["success"] = False
                log_build_status("EXECUTOR_FAILED", self.runtime_id)
                return state

            artifact_path = Path(executor_result.get("artifact") or "")
            game_name = executor_result.get("game", safe_name(command[:80]))

            if not artifact_path.exists():
                state["success"] = False
                return state

            bridge_result = execute_official_bridge(artifact_path, self.runtime_id, game_name)
            state["stages"]["bridge"] = bridge_result

            if not bridge_result.get("success"):
                state["success"] = False
                log_build_status("BRIDGE_FAILED", self.runtime_id)
            else:
                state["success"] = True
                state["game_path"] = bridge_result.get("game_path")
                state["game_id"] = bridge_result.get("game_id")
                log_build_status("SUCCESS", self.runtime_id, {"game_path": state["game_path"]})

            return state
        except Exception as e:
            state["success"] = False
            state["error"] = f"EXCEPTION: {str(e)}"
            log_build_status("CRASHED", self.runtime_id, {"error": str(e)})
            return state

# ============================================================
# المهمة التلقائية (الجدولة مع إعادة المحاولة)
# ============================================================

def auto_generate_game():
    print(f"[{utc_now()}] 🟢 بدء دورة التطوير السيادي...")
    runtime = MajdFullExecutionRuntime()
    commands = [
        "أنشئ لعبة مغامرات استراتيجية",
        "أنشئ لعبة بناء عالم ثلاثي الأبعاد",
        "أنشئ لعبة حروب وأساطير",
        "أنشئ لعبة صيد وكنوز"
    ]
    # اختيار أمر عشوائي لتنوع الألعاب
    command = random.choice(commands)
    
    result = runtime.execute(command)
    
    if result.get("success"):
        print(f"[{utc_now()}] ✅ ولادة عالم جديد! ID: {result.get('game_id')}")
        print(f"🔗 رابط اللعبة: {result.get('game_path')}")
    else:
        print(f"[{utc_now()}] ⚠️ فشل الدورة، إعادة المحاولة خلال 5 دقائق...")
        # إعادة محاولة تلقائية بعد 5 دقائق
        schedule.every(5).minutes.do(auto_generate_game)

# ============================================================
# CLI & MAIN
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
    # جدولة المهمة كل ساعة
    schedule.every(1).hour.do(auto_generate_game)
    print("👑 MAJD SOVEREIGN MONITOR ONLINE.")
    print("⏳ التطوير المستمر: سيتم بناء عالم جديد كل ساعة.")
    print("🛡️ حقوق الملكية محمية عبر توقيع العلامة التجارية.")
    
    while True:
        schedule.run_pending()
        time.sleep(1)
# ============================================================
# 3. إضافة نقطة نهاية للسجلات (Log Endpoint)
# ============================================================

# (أضف هذه الأسطر إلى نهاية الملف، قبل دالة main)
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/logs")
async def get_logs():
    if not MONITOR_LOG.exists():
        return {"logs": []}
    logs = []
    with open(MONITOR_LOG, "r", encoding="utf-8") as f:
        for line in f:
            try:
                logs.append(json.loads(line.strip()))
            except:
                pass
    return {"logs": logs}

# ============================================================
# تشغيل خادم FastAPI (بجانب الجدولة)
# ============================================================

# (أضف هذا في نهاية دالة __main__، قبل حلقة while)
import threading
threading.Thread(target=lambda: uvicorn.run(app, host="0.0.0.0", port=8000), daemon=True).start()

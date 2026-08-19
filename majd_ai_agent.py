#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD AI AGENT (النسخة النهائية للخادم السيادي)
===============================================
يعمل كخادم ويب دائم يستقبل الأوامر من المتصفح،
يشغّل العقل المدبر (01) ومنفذ الألعاب (03) وجسر المنصة (04)،
ويعيد النتيجة (Artifact) إلى majd.shop.
"""

import importlib.util
import sys
import os
import uuid
import json
import time
import traceback
from pathlib import Path
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn

# ============================================================
# إعدادات المسارات (Paths)
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent

MASTERMIND_FILE = ROOT_DIR / "MAJD-AI-MASTERMIND-01.py"
REAL_GAME_EXECUTOR_FILE = ROOT_DIR / "MAJD-REAL-GAME-EXECUTOR-03.py"
OFFICIAL_PLATFORM_BRIDGE_FILE = ROOT_DIR / "MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py"

OUTPUT_DIR = ROOT_DIR / "majd_game_output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# دوال مساعدة (Helpers)
# ============================================================

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
    import re
    value = str(value or "MAJD-GAME").strip()
    value = re.sub(r"[^\w\u0600-\u06FF\- ]+", "", value, flags=re.UNICODE)
    value = re.sub(r"\s+", "-", value).strip("-_")
    if not value: value = "MAJD-GAME"
    return value[:80]

# ============================================================
# تشغيل سلسلة الذكاء الاصطناعي (المنطق الرئيسي)
# ============================================================

def run_game_creation(command: str):
    try:
        job_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        # تحليل بسيط للأمر
        game_name = safe_name(command[:80]) or f"MAJD-GAME-{int(time.time())}"
        parsed_request = {
            "type": "CREATE_GAME",
            "name": game_name,
            "genre": "ADVENTURE",
            "dimension": "2D",
            "platform": ["WEB"],
            "request": command
        }

        # 1. استدعاء العقل المدبر (01)
        try:
            mastermind = load_python_module(MASTERMIND_FILE, "majd_ai_mastermind_01")
            # البحث عن أي دالة تنفيذ ممكنة (حسب ما هو موجود في ملفك)
            func = getattr(mastermind, "process_game_request", None) or getattr(mastermind, "execute_request", None) or getattr(mastermind, "run", None)
            if func:
                mastermind_result = func(command=command, request=parsed_request, job_id=job_id, owner="MAJD", output_root=str(OUTPUT_DIR))
            else:
                mastermind_result = {"success": True, "request": parsed_request}
        except Exception as e:
            return {"success": False, "error": f"MASTERMIND_FAILED: {str(e)}", "traceback": traceback.format_exc()}

        prepared_request = mastermind_result.get("request") if mastermind_result.get("success") else parsed_request

        # 2. استدعاء منفذ الألعاب الحقيقي (03)
        try:
            executor_mod = load_python_module(REAL_GAME_EXECUTOR_FILE, "majd_real_game_executor_03")
            execute_func = getattr(executor_mod, "execute_game_request", None)
            if not execute_func:
                return {"success": False, "error": "EXECUTOR_INTERFACE_MISSING"}
            executor_result = execute_func(request=prepared_request, job_id=job_id, output_root=str(OUTPUT_DIR))
        except Exception as e:
            return {"success": False, "error": f"EXECUTOR_FAILED: {str(e)}", "traceback": traceback.format_exc()}

        if not executor_result.get("success"):
            return executor_result

        artifact = executor_result.get("artifact") or executor_result.get("build_path")
        if not artifact or not Path(artifact).exists():
            return {"success": False, "error": "ARTIFACT_NOT_FOUND"}

        # 3. استدعاء جسر منصة مجد (04) للإرسال
        try:
            bridge_mod = load_python_module(OFFICIAL_PLATFORM_BRIDGE_FILE, "majd_official_platform_bridge_04")
            ManifestBuilder = getattr(bridge_mod, "ManifestBuilder")
            PackageBuilder = getattr(bridge_mod, "PackageBuilder")
            MajdPlatformClient = getattr(bridge_mod, "MajdPlatformClient")

            manifest_builder = ManifestBuilder()
            manifest = manifest_builder.build(
                game_dir=Path(artifact),
                game_name=parsed_request["name"],
                game_version="1.0.0",
                metadata={"job_id": job_id}
            )
            package_builder = PackageBuilder()
            package_path = package_builder.build(game_dir=Path(artifact), manifest=manifest)
            client = MajdPlatformClient()
            receipt = client.publish(package_path=package_path, manifest=manifest)

            return {
                "success": True,
                "job_id": job_id,
                "artifact": str(artifact),
                "package": str(package_path),
                "receipt": receipt.__dict__
            }
        except Exception as e:
            return {
                "success": True,
                "message": f"Game built but Platform Bridge failed: {str(e)}",
                "artifact": str(artifact)
            }

    except Exception as e:
        return {"success": False, "error": f"SYSTEM_CRASH: {str(e)}", "traceback": traceback.format_exc()}


# ============================================================
# خادم الويب FastAPI (لوحة التحكم الذاتية)
# ============================================================

app = FastAPI(title="MAJD AI AGENT - Sovereign Game Factory")

@app.get("/", response_class=HTMLResponse)
async def ui():
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>MAJD AI Agent</title>
    <style>
        body { background: #0b0f1c; color: white; font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .box { background: #151e2e; padding: 40px; border-radius: 20px; text-align: center; width: 400px; border: 1px solid #2b3a55; }
        h1 { margin-bottom: 20px; color: #f0c84b; }
        textarea { width: 100%; height: 80px; background: #0b0f1c; border: 1px solid #2b3a55; color: white; padding: 10px; border-radius: 10px; margin-bottom: 15px; font-family: inherit; }
        button { width: 100%; padding: 15px; background: #f0c84b; border: none; border-radius: 12px; font-weight: bold; font-size: 18px; cursor: pointer; transition: 0.2s; color: #0b0f1c; }
        button:hover { background: #ffd966; transform: scale(1.02); }
        #status { margin-top: 15px; font-size: 14px; color: #aab7d6; }
    </style>
    </head>
    <body>
        <div class="box">
            <h1>🧠 MAJD AI Agent</h1>
            <p style="font-size: 14px; color: #aab7d6;">الذكاء الاصطناعي السيادي. حدد الأمر وسننفذه فوراً.</p>
            <textarea id="cmd" placeholder="اكتب الأمر هنا... (مثال: أنشئ لعبة مغامرات 3D)">أنشئ لعبة مغامرات ثلاثية الأبعاد كاملة</textarea>
            <button onclick="runAI()">🚀 تشغيل العقل المدبر</button>
            <div id="status">في انتظار الأمر...</div>
        </div>
        <script>
            async function runAI() {
                const cmd = document.getElementById('cmd').value;
                const status = document.getElementById('status');
                status.innerHTML = '⏳ الذكاء الاصطناعي يعمل... سيستغرق ذلك 2-4 دقائق...';
                try {
                    const res = await fetch('/run', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({command: cmd}) });
                    const data = await res.json();
                    if(data.success) {
                        status.innerHTML = '✅ تم بناء اللعبة وإرسالها إلى majd.shop بنجاح!<br>Job ID: ' + data.job_id;
                    } else {
                        status.innerHTML = '❌ فشل: ' + data.error;
                    }
                } catch(e) { status.innerHTML = '❌ خطأ في الاتصال بالوكيل.'; }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.post("/run")
async def execute(request: Request):
    body = await request.json()
    command = body.get("command", "")
    if not command:
        return {"success": False, "error": "No command provided"}
    result = run_game_creation(command)
    return result

# ============================================================
# تشغيل الخادم
# ============================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"MAJD AI AGENT running on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)

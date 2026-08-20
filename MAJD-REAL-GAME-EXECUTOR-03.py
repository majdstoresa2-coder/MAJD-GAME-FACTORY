#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAJD GAME FACTORY
MAJD-REAL-GAME-EXECUTOR-03.py
================================
REAL GAME EXECUTOR (Sovereign React/3D Engine)
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import traceback
import uuid

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SYSTEM_NAME = "MAJD-GAME-FACTORY"
EXECUTOR_NAME = "MAJD-REAL-GAME-EXECUTOR"
VERSION = "1.0.0"

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    temp.replace(path)

def read_json(path: Path) -> Dict[str, Any]:
    if not path.exists(): return {}
    try:
        with path.open("r", encoding="utf-8") as file:
            value = json.load(file)
        if isinstance(value, dict): return value
    except Exception: pass
    return {}

def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        while True:
            chunk = file.read(1024 * 1024)
            if not chunk: break
            digest.update(chunk)
    return digest.hexdigest()

def safe_name(value: str) -> str:
    value = str(value or "MAJD-GAME").strip()
    value = re.sub(r"[^\w\u0600-\u06FF\- ]+", "", value, flags=re.UNICODE)
    value = re.sub(r"\s+", "-", value)
    value = value.strip("-_")
    if not value: value = "MAJD-GAME"
    return value[:80]

@dataclass
class BuildContext:
    job_id: str
    game_name: str
    safe_game_name: str
    request: Dict[str, Any]
    source_dir: Path
    build_dir: Path

class RealGameExecutor:
    def __init__(self, request: Dict[str, Any], job_id: str, output_root: str):
        self.request = dict(request or {})
        self.job_id = str(job_id or uuid.uuid4())
        self.output_root = Path(output_root).resolve()
        self.output_root.mkdir(parents=True, exist_ok=True)
        game_name = str(self.request.get("name") or f"MAJD-GAME-{int(time.time())}")
        cleaned_name = safe_name(game_name)
        workspace = self.output_root / self.job_id
        self.context = BuildContext(
            job_id=self.job_id,
            game_name=game_name,
            safe_game_name=cleaned_name,
            request=self.request,
            source_dir=workspace / "source",
            build_dir=workspace / "build"
        )
        self.context.source_dir.mkdir(parents=True, exist_ok=True)

    def create_react_project(self) -> None:
        ctx = self.context
        # 1. package.json
        package_json = {
            "name": ctx.safe_game_name,
            "private": True,
            "version": "1.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "three": "^0.160.0",
                "@react-three/fiber": "^8.0.0",
                "@react-three/drei": "^9.0.0"
            },
            "devDependencies": {
                "@vitejs/plugin-react": "^4.0.0",
                "vite": "^4.0.0"
            }
        }
        write_json(ctx.source_dir / "package.json", package_json)

        # 2. vite.config.js
        write_text(ctx.source_dir / "vite.config.js", """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
export default defineConfig({ plugins: [react()] })""")

        # 3. src files
        src_dir = ctx.source_dir / "src"
        src_dir.mkdir(parents=True, exist_ok=True)

        write_text(src_dir / "main.jsx", """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './style.css'
ReactDOM.createRoot(document.getElementById('root')).render(<App />)""")

        write_text(src_dir / "style.css", """* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #0f172a; overflow: hidden; font-family: Arial, sans-serif; }
#root { width: 100vw; height: 100vh; }""")

        # ========================================================
        # تعديل الشعار هنا: تم استبدال مسار الصورة بـ Base64
        # ========================================================
        app_jsx = """import React, { useState } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'

function World({ colors, positions }) {
  return (
    <group>
      {positions.map((pos, i) => (
        <mesh key={i} position={pos} rotation={[0, i * 0.5, 0]}>
          <boxGeometry args={[1.5, 1.5, 1.5]} />
          <meshStandardMaterial color={i % 2 === 0 ? colors.primary : colors.secondary} />
        </mesh>
      ))}
    </group>
  )
}

function App() {
  const [started, setStarted] = useState(false)
  const design = window.__DESIGN_PROFILE__ || { primary: 'royalblue', secondary: 'gold', positions: [[0,0,0], [2,1,0]] }

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative' }}>
      <div style={{
        position: 'absolute', top: '20px', left: '50%', transform: 'translateX(-50%)',
        zIndex: 10, display: 'flex', flexDirection: 'column', alignItems: 'center'
      }}>
        <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFhAJ/wlseKgAAAABJRU5ErkJggg==" alt="MAJD GAMES" style={{ width: '120px', marginBottom: '10px' }} />
        <h1 style={{ color: 'white', textShadow: '0 0 20px rgba(0,0,0,0.8)', letterSpacing: '2px' }}>MAJD WORLD</h1>
      </div>

      <Canvas>
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <World colors={design} positions={design.positions || [[0,0,0]]} />
        <OrbitControls enableZoom={true} />
      </Canvas>

      {!started && (
        <div style={{
          position: 'absolute', top: 0, left: 0, width: '100%', height: '100%',
          background: 'rgba(0,0,0,0.7)',
          display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 20
        }}>
          <div style={{
            background: 'linear-gradient(135deg, #1e293b, #0f172a)',
            padding: '40px', borderRadius: '20px',
            border: '1px solid rgba(255,215,0,0.3)', textAlign: 'center',
            boxShadow: '0 0 50px rgba(0,0,0,0.5)'
          }}>
            <h1 style={{ color: '#fbbf24', marginBottom: '20px' }}>MAJD GAMES</h1>
            <button onClick={() => setStarted(true)} style={{
              background: '#fbbf24', border: 'none', padding: '15px 40px',
              borderRadius: '30px', fontWeight: 'bold', fontSize: '18px',
              cursor: 'pointer', color: '#0f172a'
            }}>استكشف العالم</button>
          </div>
        </div>
      )}
    </div>
  )
}
export default App"""
        write_text(src_dir / "App.jsx", app_jsx)

    def build(self) -> None:
        ctx = self.context
        if ctx.build_dir.exists(): shutil.rmtree(ctx.build_dir)
        ctx.build_dir.mkdir(parents=True, exist_ok=True)
        # نسخ الملفات من source إلى build
        for item in ctx.source_dir.iterdir():
            dest = ctx.build_dir / item.name
            if item.is_dir(): shutil.copytree(item, dest)
            else: shutil.copy2(item, dest)

    def execute(self) -> Dict[str, Any]:
        try:
            self.create_react_project()
            self.build()
            return {
                "success": True,
                "status": "READY",
                "job_id": self.job_id,
                "game": self.context.game_name,
                "artifact": str(self.context.build_dir),
                "build_path": str(self.context.build_dir)
            }
        except Exception as e:
            return {"success": False, "status": "EXECUTOR_EXCEPTION", "error": str(e)}

def execute_game_request(request: Dict[str, Any], job_id: str, output_root: str) -> Dict[str, Any]:
    return RealGameExecutor(request=request, job_id=job_id, output_root=output_root).execute()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-REAL-GAME-EXECUTOR-03.py
============================================================

REAL GAME EXECUTOR
Sovereign React / Three.js Build Executor

المسؤوليات:
- استقبال طلب إنشاء اللعبة من العقل المدبر 01.
- إنشاء مشروع React/Vite فعلي.
- إنشاء index.html وملفات src.
- إنشاء واجهة لعبة 3D أولية قابلة للتشغيل.
- تثبيت Node dependencies فعلياً.
- تنفيذ npm run build فعلياً.
- التحقق من dist/index.html.
- التحقق من وجود ملفات JavaScript الناتجة.
- منع النجاح الوهمي.
- إعادة stdout / stderr الحقيقي عند الفشل.
- إعادة Artifact حقيقي فقط عند نجاح البناء.

مهم:
هذا الملف منفذ فقط.
العقل المدبر 01 هو المسؤول عن:
- التشخيص
- الإصلاح
- إعادة المحاولة
- تعديل الأكواد
- اتخاذ القرارات

السلسلة:

01 MASTERMIND
      ↓
03 REAL GAME EXECUTOR
      ↓
CREATE SOURCE
      ↓
INSTALL DEPENDENCIES
      ↓
VITE BUILD
      ↓
VERIFY DIST
      ↓
REAL PLAYABLE ARTIFACT
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import time
import traceback
import uuid

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ============================================================
# IDENTITY
# ============================================================

SYSTEM_NAME = "MAJD-GAME-FACTORY"

EXECUTOR_NAME = "MAJD-REAL-GAME-EXECUTOR"

VERSION = "2.0.0"

DEFAULT_TIMEOUT = 900


# ============================================================
# TIME
# ============================================================

def utc_now() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat()


# ============================================================
# HELPERS
# ============================================================

def write_json(
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


def write_text(
    path: Path,
    content: str
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    path.write_text(
        content,
        encoding="utf-8"
    )


def sha256_file(
    path: Path
) -> str:

    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as file:

        while True:

            chunk = file.read(
                1024 * 1024
            )

            if not chunk:
                break

            digest.update(
                chunk
            )

    return digest.hexdigest()


def safe_name(
    value: str
) -> str:

    value = str(
        value
        or
        "MAJD-GAME"
    ).strip()

    value = re.sub(
        r"[^\w\u0600-\u06FF\- ]+",
        "",
        value,
        flags=re.UNICODE
    )

    value = re.sub(
        r"\s+",
        "-",
        value
    )

    value = value.strip(
        "-_"
    )

    if not value:

        value = (
            "MAJD-GAME"
        )

    return value[:80]


# ============================================================
# COMMAND RESULT
# ============================================================

@dataclass
class CommandResult:

    command: List[str]

    cwd: str

    returncode: int

    stdout: str

    stderr: str

    success: bool

    duration_seconds: float


# ============================================================
# BUILD CONTEXT
# ============================================================

@dataclass
class BuildContext:

    job_id: str

    game_name: str

    safe_game_name: str

    request: Dict[str, Any]

    workspace_dir: Path

    source_dir: Path

    dist_dir: Path

    state_file: Path


# ============================================================
# PROCESS RUNNER
# ============================================================

class ProcessRunner:

    def run(
        self,
        command: List[str],
        cwd: Path,
        timeout: int = DEFAULT_TIMEOUT
    ) -> CommandResult:

        started = time.time()

        try:

            completed = subprocess.run(

                command,

                cwd=str(
                    cwd
                ),

                capture_output=True,

                text=True,

                timeout=timeout,

                env=os.environ.copy()
            )

            return CommandResult(

                command=
                    command,

                cwd=
                    str(
                        cwd
                    ),

                returncode=
                    completed.returncode,

                stdout=
                    completed.stdout
                    or
                    "",

                stderr=
                    completed.stderr
                    or
                    "",

                success=
                    (
                        completed.returncode
                        ==
                        0
                    ),

                duration_seconds=
                    time.time()
                    -
                    started
            )

        except subprocess.TimeoutExpired as error:

            return CommandResult(

                command=
                    command,

                cwd=
                    str(
                        cwd
                    ),

                returncode=
                    124,

                stdout=
                    (
                        error.stdout
                        if isinstance(
                            error.stdout,
                            str
                        )
                        else ""
                    ),

                stderr=
                    "Command timed out.",

                success=
                    False,

                duration_seconds=
                    time.time()
                    -
                    started
            )

        except Exception as error:

            return CommandResult(

                command=
                    command,

                cwd=
                    str(
                        cwd
                    ),

                returncode=
                    1,

                stdout=
                    "",

                stderr=
                    (
                        f"{type(error).__name__}: "
                        f"{error}"
                    ),

                success=
                    False,

                duration_seconds=
                    time.time()
                    -
                    started
            )


# ============================================================
# REAL GAME EXECUTOR
# ============================================================

class RealGameExecutor:

    def __init__(
        self,
        request: Dict[str, Any],
        job_id: str,
        output_root: str
    ):

        self.request = dict(
            request
            or
            {}
        )

        self.job_id = str(
            job_id
            or
            uuid.uuid4()
        )

        self.output_root = Path(
            output_root
        ).resolve()

        self.output_root.mkdir(
            parents=True,
            exist_ok=True
        )

        game_name = str(
            self.request.get(
                "name"
            )
            or
            f"MAJD-GAME-{int(time.time())}"
        )

        cleaned_name = safe_name(
            game_name
        )

        workspace = (
            self.output_root
            /
            self.job_id
        )

        source_dir = (
            workspace
            /
            "source"
        )

        dist_dir = (
            source_dir
            /
            "dist"
        )

        state_file = (
            workspace
            /
            "executor-state.json"
        )

        self.context = BuildContext(

            job_id=
                self.job_id,

            game_name=
                game_name,

            safe_game_name=
                cleaned_name,

            request=
                self.request,

            workspace_dir=
                workspace,

            source_dir=
                source_dir,

            dist_dir=
                dist_dir,

            state_file=
                state_file
        )

        self.runner = (
            ProcessRunner()
        )


    # ========================================================
    # STATE
    # ========================================================

    def save_state(
        self,
        status: str,
        extra: Optional[
            Dict[str, Any]
        ] = None
    ) -> None:

        state = {

            "system":
                SYSTEM_NAME,

            "executor":
                EXECUTOR_NAME,

            "version":
                VERSION,

            "job_id":
                self.job_id,

            "game":
                self.context.game_name,

            "status":
                status,

            "time":
                utc_now(),

            "request":
                self.request
        }

        if extra:

            state.update(
                extra
            )

        write_json(
            self.context.state_file,
            state
        )


    # ========================================================
    # CLEAN WORKSPACE
    # ========================================================

    def prepare_workspace(
        self
    ) -> None:

        ctx = self.context

        if ctx.source_dir.exists():

            shutil.rmtree(
                ctx.source_dir
            )

        ctx.source_dir.mkdir(
            parents=True,
            exist_ok=True
        )


    # ========================================================
    # PACKAGE JSON
    # ========================================================

    def create_package_json(
        self
    ) -> None:

        ctx = self.context

        package_json = {

            "name":
                ctx.safe_game_name.lower(),

            "private":
                True,

            "version":
                "1.0.0",

            "type":
                "module",

            "scripts": {

                "dev":
                    "vite",

                "build":
                    "vite build",

                "preview":
                    "vite preview"
            },

            "dependencies": {

                "react":
                    "^18.3.1",

                "react-dom":
                    "^18.3.1",

                "three":
                    "^0.170.0",

                "@react-three/fiber":
                    "^8.17.10",

                "@react-three/drei":
                    "^9.117.3"
            },

            "devDependencies": {

                "@vitejs/plugin-react":
                    "^4.3.4",

                "vite":
                    "^5.4.11"
            }
        }

        write_json(
            ctx.source_dir
            /
            "package.json",
            package_json
        )


    # ========================================================
    # INDEX HTML
    # ========================================================

    def create_index_html(
        self
    ) -> None:

        title = (
            self.context.game_name
        )

        content = f"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="theme-color" content="#050b14" />
  <title>{title}</title>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>
"""

        write_text(
            self.context.source_dir
            /
            "index.html",
            content
        )


    # ========================================================
    # VITE CONFIG
    # ========================================================

    def create_vite_config(
        self
    ) -> None:

        content = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: './',
  build: {
    outDir: 'dist',
    emptyOutDir: true
  }
})
"""

        write_text(
            self.context.source_dir
            /
            "vite.config.js",
            content
        )


    # ========================================================
    # MAIN JSX
    # ========================================================

    def create_main_jsx(
        self
    ) -> None:

        src_dir = (
            self.context.source_dir
            /
            "src"
        )

        src_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        content = """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './style.css'

ReactDOM.createRoot(
  document.getElementById('root')
).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
"""

        write_text(
            src_dir
            /
            "main.jsx",
            content
        )


    # ========================================================
    # STYLE
    # ========================================================

    def create_style(
        self
    ) -> None:

        content = """
* {
  box-sizing: border-box;
}

html,
body,
#root {
  width: 100%;
  height: 100%;
  margin: 0;
}

body {
  overflow: hidden;
  background: #050b14;
  font-family: Arial, sans-serif;
}

button {
  font-family: inherit;
}
"""

        write_text(
            self.context.source_dir
            /
            "src"
            /
            "style.css",
            content
        )


    # ========================================================
    # APP JSX
    # ========================================================

    def create_app_jsx(
        self
    ) -> None:

        request_json = json.dumps(
            self.request,
            ensure_ascii=False
        )

        game_name_json = json.dumps(
            self.context.game_name,
            ensure_ascii=False
        )

        content = f"""import React, {{ useMemo, useState }} from 'react'
import {{ Canvas }} from '@react-three/fiber'
import {{ OrbitControls, Stars }} from '@react-three/drei'

const GAME_NAME = {game_name_json}
const GAME_REQUEST = {request_json}

function Ground() {{
  return (
    <mesh
      rotation={{[-Math.PI / 2, 0, 0]}}
      position={{[0, -1, 0]}}
      receiveShadow
    >
      <planeGeometry args={{[60, 60]}} />
      <meshStandardMaterial color="#12263a" />
    </mesh>
  )
}}

function Castle() {{
  return (
    <group position={{[0, 0, 0]}}>
      <mesh castShadow>
        <boxGeometry args={{[4, 3, 4]}} />
        <meshStandardMaterial color="#9a7b4f" />
      </mesh>

      {{[
        [-2.2, 0.4, -2.2],
        [2.2, 0.4, -2.2],
        [-2.2, 0.4, 2.2],
        [2.2, 0.4, 2.2]
      ].map((position, index) => (
        <mesh
          key={{index}}
          position={{position}}
          castShadow
        >
          <cylinderGeometry args={{[0.8, 0.8, 4, 16]}} />
          <meshStandardMaterial
            color={{index % 2 === 0 ? '#b89352' : '#d3b56d'}}
          />
        </mesh>
      ))}}
    </group>
  )
}}

function World() {{

  const objects = useMemo(
    () => Array.from({{ length: 24 }}, (_, index) => {{
      const angle = (index / 24) * Math.PI * 2
      const radius = 8 + (index % 4)

      return {{
        x: Math.cos(angle) * radius,
        z: Math.sin(angle) * radius,
        scale: 0.5 + (index % 3) * 0.2
      }}
    }}),
    []
  )

  return (
    <>
      <ambientLight intensity={{0.8}} />

      <directionalLight
        position={{[10, 15, 8]}}
        intensity={{2}}
        castShadow
      />

      <Stars
        radius={{80}}
        depth={{40}}
        count={{1200}}
        factor={{3}}
      />

      <Ground />

      <Castle />

      {{objects.map((item, index) => (
        <mesh
          key={{index}}
          position={{[item.x, 0, item.z]}}
          scale={{item.scale}}
          castShadow
        >
          <coneGeometry args={{[1, 3, 8]}} />
          <meshStandardMaterial
            color={{index % 2 === 0 ? '#31572c' : '#4f772d'}}
          />
        </mesh>
      ))}}

      <OrbitControls
        enablePan
        enableZoom
        enableRotate
        maxDistance={{35}}
        minDistance={{6}}
      />
    </>
  )
}}

function App() {{

  const [started, setStarted] = useState(false)

  return (
    <div
      style={{{{
        width: '100%',
        height: '100%',
        position: 'relative',
        background: '#050b14'
      }}}}
    >

      <Canvas
        shadows
        camera={{{{
          position: [12, 10, 16],
          fov: 55
        }}}}
      >
        <World />
      </Canvas>

      <div
        style={{{{
          position: 'absolute',
          top: 20,
          right: 20,
          zIndex: 10,
          color: '#f7d67a',
          background: 'rgba(5,11,20,0.72)',
          border: '1px solid rgba(247,214,122,0.3)',
          borderRadius: 14,
          padding: '14px 18px',
          backdropFilter: 'blur(8px)'
        }}}}
      >
        <strong>MAJD GAMES</strong>

        <div
          style={{{{
            color: '#fff',
            marginTop: 6
          }}}}
        >
          {{GAME_NAME}}
        </div>
      </div>

      {{!started && (
        <div
          style={{{{
            position: 'absolute',
            inset: 0,
            zIndex: 20,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background:
              'radial-gradient(circle, rgba(16,35,54,.72), rgba(0,0,0,.92))'
          }}}}
        >

          <div
            style={{{{
              width: 'min(92vw, 520px)',
              padding: 36,
              borderRadius: 24,
              border:
                '1px solid rgba(247,214,122,.35)',
              background:
                'linear-gradient(145deg,#0e1b2a,#07111c)',
              color: '#fff',
              textAlign: 'center',
              boxShadow:
                '0 30px 80px rgba(0,0,0,.55)'
            }}}}
          >

            <div
              style={{{{
                fontSize: 44,
                marginBottom: 10
              }}}}
            >
              👑
            </div>

            <h1
              style={{{{
                margin: 0,
                color: '#f7d67a'
              }}}}
            >
              {{GAME_NAME}}
            </h1>

            <p
              style={{{{
                opacity: .75,
                lineHeight: 1.8
              }}}}
            >
              لعبة تم إنشاؤها وتشغيل بنائها
              بواسطة MAJD AI GAME FACTORY
            </p>

            <button
              onClick={{() => setStarted(true)}}
              style={{{{
                marginTop: 12,
                border: 0,
                borderRadius: 40,
                padding: '15px 34px',
                background:
                  'linear-gradient(90deg,#b88925,#f0cb68)',
                color: '#101010',
                fontWeight: 800,
                cursor: 'pointer',
                fontSize: 17
              }}}}
            >
              دخول اللعبة
            </button>

          </div>

        </div>
      )}}

      <script
        type="application/json"
        data-majd-request="true"
        dangerouslySetInnerHTML={{{{
          __html: JSON.stringify(GAME_REQUEST)
        }}}}
      />

    </div>
  )
}}

export default App
"""

        write_text(
            self.context.source_dir
            /
            "src"
            /
            "App.jsx",
            content
        )


    # ========================================================
    # CREATE PROJECT
    # ========================================================

    def create_project(
        self
    ) -> None:

        self.prepare_workspace()

        self.create_package_json()

        self.create_index_html()

        self.create_vite_config()

        self.create_main_jsx()

        self.create_style()

        self.create_app_jsx()


    # ========================================================
    # NODE CHECK
    # ========================================================

    def verify_node_tools(
        self
    ) -> Dict[str, Any]:

        node = shutil.which(
            "node"
        )

        npm = shutil.which(
            "npm"
        )

        return {

            "success":
                bool(
                    node
                    and
                    npm
                ),

            "node":
                node,

            "npm":
                npm
        }


    # ========================================================
    # INSTALL
    # ========================================================

    def install_dependencies(
        self
    ) -> CommandResult:

        npm = shutil.which(
            "npm"
        )

        if not npm:

            return CommandResult(

                command=
                    ["npm", "install"],

                cwd=
                    str(
                        self.context.source_dir
                    ),

                returncode=
                    127,

                stdout=
                    "",

                stderr=
                    "npm not found",

                success=
                    False,

                duration_seconds=
                    0.0
            )

        return self.runner.run(

            [
                npm,
                "install",
                "--no-audit",
                "--no-fund"
            ],

            cwd=
                self.context.source_dir,

            timeout=
                900
        )


    # ========================================================
    # BUILD
    # ========================================================

    def run_build(
        self
    ) -> CommandResult:

        npm = shutil.which(
            "npm"
        )

        if not npm:

            return CommandResult(

                command=
                    ["npm", "run", "build"],

                cwd=
                    str(
                        self.context.source_dir
                    ),

                returncode=
                    127,

                stdout=
                    "",

                stderr=
                    "npm not found",

                success=
                    False,

                duration_seconds=
                    0.0
            )

        return self.runner.run(

            [
                npm,
                "run",
                "build"
            ],

            cwd=
                self.context.source_dir,

            timeout=
                900
        )


    # ========================================================
    # VERIFY DIST
    # ========================================================

    def verify_dist(
        self
    ) -> Dict[str, Any]:

        ctx = self.context

        if not ctx.dist_dir.exists():

            return {

                "success":
                    False,

                "status":
                    "DIST_NOT_FOUND",

                "dist":
                    str(
                        ctx.dist_dir
                    )
            }

        index_file = (
            ctx.dist_dir
            /
            "index.html"
        )

        if not index_file.exists():

            return {

                "success":
                    False,

                "status":
                    "INDEX_HTML_NOT_FOUND",

                "dist":
                    str(
                        ctx.dist_dir
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
                    "INDEX_HTML_EMPTY"
            }

        files = [

            file

            for file
            in ctx.dist_dir.rglob(
                "*"
            )

            if file.is_file()
        ]

        if len(
            files
        ) < 2:

            return {

                "success":
                    False,

                "status":
                    "DIST_TOO_SMALL",

                "files":
                    [
                        str(
                            file
                        )
                        for file
                        in files
                    ]
            }

        javascript_files = [

            file

            for file
            in files

            if file.suffix.lower()
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
                    "BUILT_JAVASCRIPT_NOT_FOUND"
            }

        manifest = []

        for file in files:

            manifest.append({

                "path":
                    str(
                        file.relative_to(
                            ctx.dist_dir
                        )
                    ),

                "size":
                    file.stat().st_size,

                "sha256":
                    sha256_file(
                        file
                    )
            })

        return {

            "success":
                True,

            "status":
                "PLAYABLE_ARTIFACT_VERIFIED",

            "artifact":
                str(
                    ctx.dist_dir
                ),

            "index":
                str(
                    index_file
                ),

            "files":
                manifest
        }


    # ========================================================
    # EXECUTE
    # ========================================================

    def execute(
        self
    ) -> Dict[str, Any]:

        started_at = (
            utc_now()
        )

        self.save_state(
            "STARTING"
        )

        try:

            # ------------------------------------------------
            # CREATE PROJECT
            # ------------------------------------------------

            self.save_state(
                "CREATING_PROJECT"
            )

            self.create_project()


            # ------------------------------------------------
            # VERIFY NODE
            # ------------------------------------------------

            tool_status = (
                self.verify_node_tools()
            )

            if not tool_status.get(
                "success"
            ):

                result = {

                    "success":
                        False,

                    "status":
                        "NODE_RUNTIME_MISSING",

                    "job_id":
                        self.job_id,

                    "tools":
                        tool_status
                }

                self.save_state(
                    "FAILED",
                    result
                )

                return result


            # ------------------------------------------------
            # INSTALL DEPENDENCIES
            # ------------------------------------------------

            self.save_state(
                "INSTALLING_DEPENDENCIES"
            )

            install_result = (
                self.install_dependencies()
            )

            if not install_result.success:

                result = {

                    "success":
                        False,

                    "status":
                        "NPM_INSTALL_FAILED",

                    "job_id":
                        self.job_id,

                    "command":
                        asdict(
                            install_result
                        )
                }

                self.save_state(
                    "FAILED",
                    result
                )

                return result


            # ------------------------------------------------
            # BUILD
            # ------------------------------------------------

            self.save_state(
                "BUILDING"
            )

            build_result = (
                self.run_build()
            )

            if not build_result.success:

                result = {

                    "success":
                        False,

                    "status":
                        "VITE_BUILD_FAILED",

                    "job_id":
                        self.job_id,

                    "command":
                        asdict(
                            build_result
                        )
                }

                self.save_state(
                    "FAILED",
                    result
                )

                return result


            # ------------------------------------------------
            # VERIFY ARTIFACT
            # ------------------------------------------------

            self.save_state(
                "VERIFYING_ARTIFACT"
            )

            verification = (
                self.verify_dist()
            )

            if not verification.get(
                "success"
            ):

                result = {

                    "success":
                        False,

                    "status":
                        verification.get(
                            "status",
                            "ARTIFACT_VERIFICATION_FAILED"
                        ),

                    "job_id":
                        self.job_id,

                    "verification":
                        verification
                }

                self.save_state(
                    "FAILED",
                    result
                )

                return result


            # ------------------------------------------------
            # REAL SUCCESS
            # ------------------------------------------------

            result = {

                "success":
                    True,

                "status":
                    "READY",

                "system":
                    SYSTEM_NAME,

                "executor":
                    EXECUTOR_NAME,

                "version":
                    VERSION,

                "job_id":
                    self.job_id,

                "game":
                    self.context.game_name,

                "artifact":
                    verification[
                        "artifact"
                    ],

                "build_path":
                    verification[
                        "artifact"
                    ],

                "index":
                    verification[
                        "index"
                    ],

                "verification":
                    verification,

                "install":
                    {

                        "success":
                            install_result.success,

                        "duration_seconds":
                            install_result.duration_seconds
                    },

                "build":
                    {

                        "success":
                            build_result.success,

                        "duration_seconds":
                            build_result.duration_seconds,

                        "stdout":
                            build_result.stdout[-4000:],

                        "stderr":
                            build_result.stderr[-4000:]
                    },

                "started_at":
                    started_at,

                "finished_at":
                    utc_now()
            }

            self.save_state(
                "READY",
                result
            )

            return result

        except Exception as error:

            result = {

                "success":
                    False,

                "status":
                    "EXECUTOR_EXCEPTION",

                "job_id":
                    self.job_id,

                "error":
                    (
                        f"{type(error).__name__}: "
                        f"{error}"
                    ),

                "traceback":
                    traceback.format_exc(),

                "finished_at":
                    utc_now()
            }

            self.save_state(
                "FAILED",
                result
            )

            return result


# ============================================================
# PUBLIC API
# ============================================================

def execute_game_request(
    request: Dict[str, Any],
    job_id: str,
    output_root: str,
    **kwargs: Any
) -> Dict[str, Any]:

    executor = RealGameExecutor(

        request=
            request,

        job_id=
            job_id,

        output_root=
            output_root
    )

    return executor.execute()


# ============================================================
# CLI TEST
# ============================================================

def main() -> int:

    import argparse

    parser = argparse.ArgumentParser(

        description=(
            "MAJD REAL GAME EXECUTOR 03"
        )
    )

    parser.add_argument(

        "name",

        nargs="?",

        default="MAJD TEST GAME"
    )

    parser.add_argument(

        "--output",

        default=str(
            Path(__file__)
            .resolve()
            .parent
            /
            "majd_game_output"
        )
    )

    args = parser.parse_args()

    request = {

        "type":
            "CREATE_GAME",

        "name":
            args.name,

        "genre":
            "STRATEGY",

        "dimension":
            "3D",

        "platform": [
            "WEB",
            "PC"
        ],

        "auto_test":
            True,

        "auto_repair":
            True,

        "produce_playable_build":
            True
    }

    result = execute_game_request(

        request=
            request,

        job_id=
            str(
                uuid.uuid4()
            ),

        output_root=
            args.output
    )

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
            default=str
        )
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

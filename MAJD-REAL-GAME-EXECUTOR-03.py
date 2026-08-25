#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-REAL-GAME-EXECUTOR-03.py
============================================================

REAL GAME EXECUTOR
Sovereign React / Three.js Gameplay Build Executor

المسؤوليات:
- استقبال طلب إنشاء اللعبة من العقل المدبر 01.
- إنشاء مشروع React/Vite فعلي.
- إنشاء index.html وملفات src.
- إنشاء Gameplay ثلاثي الأبعاد فعلي.
- لاعب قابل للحركة.
- تحكم PC ولوحة مفاتيح.
- تحكم جوال باللمس.
- قفز.
- كاميرا تتبع.
- إيقاف / متابعة.
- إعادة تمركز اللاعب.
- تثبيت Node dependencies فعلياً.
- تنفيذ npm run build فعلياً.
- التحقق من dist/index.html.
- التحقق من ملفات JavaScript الناتجة.
- منع النجاح الوهمي.
- إعادة Artifact حقيقي فقط عند نجاح البناء.

السلسلة:

01 MASTERMIND
      ↓
03 REAL GAME EXECUTOR
      ↓
CREATE REAL GAME SOURCE
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
VERSION = "3.0.0"

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
    ).strip(
        "-_"
    )

    return (
        value
        or
        "MAJD-GAME"
    )[:80]


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
                command=command,
                cwd=str(
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
                    completed.returncode
                    ==
                    0,
                duration_seconds=
                    time.time()
                    -
                    started
            )

        except subprocess.TimeoutExpired as error:

            return CommandResult(
                command=command,
                cwd=str(
                    cwd
                ),
                returncode=124,
                stdout=(
                    error.stdout
                    if isinstance(
                        error.stdout,
                        str
                    )
                    else ""
                ),
                stderr="Command timed out.",
                success=False,
                duration_seconds=
                    time.time()
                    -
                    started
            )

        except Exception as error:

            return CommandResult(
                command=command,
                cwd=str(
                    cwd
                ),
                returncode=1,
                stdout="",
                stderr=(
                    f"{type(error).__name__}: "
                    f"{error}"
                ),
                success=False,
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
    # WORKSPACE
    # ========================================================

    def prepare_workspace(
        self
    ) -> None:

        if self.context.source_dir.exists():

            shutil.rmtree(
                self.context.source_dir
            )

        self.context.source_dir.mkdir(
            parents=True,
            exist_ok=True
        )


    # ========================================================
    # PACKAGE
    # ========================================================

    def create_package_json(
        self
    ) -> None:

        package_json = {

            "name":
                self.context
                .safe_game_name
                .lower(),

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
            self.context.source_dir
            /
            "package.json",
            package_json
        )


    # ========================================================
    # HTML
    # ========================================================

    def create_index_html(
        self
    ) -> None:

        title = (
            self.context.game_name
            .replace(
                "&",
                "&amp;"
            )
            .replace(
                "<",
                "&lt;"
            )
            .replace(
                ">",
                "&gt;"
            )
        )

        content = f"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8" />
  <meta
    name="viewport"
    content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no"
  />
  <meta
    name="theme-color"
    content="#050b14"
  />
  <title>{title}</title>
</head>
<body>
  <div id="root"></div>
  <script
    type="module"
    src="/src/main.jsx"
  ></script>
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
    # VITE
    # ========================================================

    def create_vite_config(
        self
    ) -> None:

        content = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [
    react()
  ],

  base: './',

  build: {
    outDir: 'dist',
    emptyOutDir: true,
    sourcemap: false
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
    # MAIN
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

ReactDOM
  .createRoot(
    document.getElementById('root')
  )
  .render(
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
    # CSS
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

html,
body {
  overscroll-behavior: none;
  touch-action: none;
}

body {
  overflow: hidden;
  background: #050b14;
  font-family: Arial, sans-serif;
  user-select: none;
}

button {
  font-family: inherit;
  -webkit-tap-highlight-color: transparent;
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
    # REAL GAMEPLAY APP
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

        template = r"""
import React, {
  useEffect,
  useMemo,
  useRef,
  useState
} from 'react'

import {
  Canvas,
  useFrame,
  useThree
} from '@react-three/fiber'

import {
  Stars
} from '@react-three/drei'

import * as THREE from 'three'


const GAME_NAME =
  __GAME_NAME__

const GAME_REQUEST =
  __GAME_REQUEST__


function Ground() {

  return (
    <mesh
      rotation={[
        -Math.PI / 2,
        0,
        0
      ]}
      position={[
        0,
        -1,
        0
      ]}
      receiveShadow
    >

      <planeGeometry
        args={[
          80,
          80
        ]}
      />

      <meshStandardMaterial
        color="#12263a"
      />

    </mesh>
  )
}


function Castle() {

  return (

    <group
      position={[
        0,
        0,
        -10
      ]}
    >

      <mesh
        castShadow
      >

        <boxGeometry
          args={[
            6,
            4,
            5
          ]}
        />

        <meshStandardMaterial
          color="#9a7b4f"
        />

      </mesh>

      {[
        [-3.3, .5, -2.8],
        [3.3, .5, -2.8],
        [-3.3, .5, 2.8],
        [3.3, .5, 2.8]

      ].map(
        (
          position,
          index
        ) => (

          <mesh
            key={index}
            position={position}
            castShadow
          >

            <cylinderGeometry
              args={[
                1,
                1,
                5,
                16
              ]}
            />

            <meshStandardMaterial
              color={
                index % 2 === 0
                  ?
                  '#b89352'
                  :
                  '#d3b56d'
              }
            />

          </mesh>
        )
      )}

    </group>
  )
}


function WorldDecor() {

  const objects = useMemo(
    () =>
      Array.from(
        {
          length: 36
        },
        (
          _,
          index
        ) => {

          const angle =
            (
              index
              /
              36
            )
            *
            Math.PI
            *
            2

          const radius =
            11
            +
            (
              index
              %
              6
            )
            *
            2.5

          return {

            x:
              Math.cos(
                angle
              )
              *
              radius,

            z:
              Math.sin(
                angle
              )
              *
              radius,

            scale:
              .65
              +
              (
                index
                %
                4
              )
              *
              .15
          }
        }
      ),

    []
  )


  return (

    <>

      <ambientLight
        intensity={.9}
      />

      <directionalLight
        position={[
          10,
          18,
          10
        ]}
        intensity={2.4}
        castShadow
      />

      <Stars
        radius={100}
        depth={50}
        count={1400}
        factor={3}
      />

      <Ground />

      <Castle />

      {objects.map(
        (
          item,
          index
        ) => (

          <mesh
            key={index}
            position={[
              item.x,
              0,
              item.z
            ]}
            scale={item.scale}
            castShadow
          >

            <coneGeometry
              args={[
                1,
                3.2,
                8
              ]}
            />

            <meshStandardMaterial
              color={
                index % 2 === 0
                  ?
                  '#31572c'
                  :
                  '#4f772d'
              }
            />

          </mesh>
        )
      )}

    </>
  )
}


function FollowCamera({
  playerRef
}) {

  const {
    camera
  } = useThree()

  const desired =
    useRef(
      new THREE.Vector3()
    )

  const target =
    useRef(
      new THREE.Vector3()
    )


  useFrame(
    () => {

      const player =
        playerRef.current

      if (!player) {
        return
      }


      target.current.set(
        player.position.x,
        player.position.y + 1.2,
        player.position.z
      )


      desired.current.set(
        player.position.x + 7,
        player.position.y + 6,
        player.position.z + 9
      )


      camera.position.lerp(
        desired.current,
        .08
      )

      camera.lookAt(
        target.current
      )
    }
  )


  return null
}


function Player({
  active,
  input,
  resetSignal,
  onPositionChange
}) {

  const ref =
    useRef()

  const verticalVelocity =
    useRef(0)

  const grounded =
    useRef(true)

  const lastReset =
    useRef(
      resetSignal
    )


  useEffect(
    () => {

      if (
        lastReset.current
        !==
        resetSignal
        &&
        ref.current
      ) {

        ref.current.position.set(
          0,
          0,
          6
        )

        verticalVelocity.current =
          0

        grounded.current =
          true

        lastReset.current =
          resetSignal
      }

    },
    [
      resetSignal
    ]
  )


  useFrame(
    (
      _,
      delta
    ) => {

      if (
        !ref.current
        ||
        !active
      ) {

        return
      }


      const speed =
        7.2


      const dx =
        (
          input.right
            ?
            1
            :
            0
        )
        -
        (
          input.left
            ?
            1
            :
            0
        )


      const dz =
        (
          input.down
            ?
            1
            :
            0
        )
        -
        (
          input.up
            ?
            1
            :
            0
        )


      if (
        dx
        ||
        dz
      ) {

        const length =
          Math.hypot(
            dx,
            dz
          )
          ||
          1


        ref.current.position.x +=
          (
            dx
            /
            length
          )
          *
          speed
          *
          delta


        ref.current.position.z +=
          (
            dz
            /
            length
          )
          *
          speed
          *
          delta


        ref.current.rotation.y =
          Math.atan2(
            dx,
            dz
          )
      }


      if (
        input.jump
        &&
        grounded.current
      ) {

        verticalVelocity.current =
          6.8

        grounded.current =
          false
      }


      verticalVelocity.current -=
        16
        *
        delta


      ref.current.position.y +=
        verticalVelocity.current
        *
        delta


      if (
        ref.current.position.y
        <=
        0
      ) {

        ref.current.position.y =
          0

        verticalVelocity.current =
          0

        grounded.current =
          true
      }


      ref.current.position.x =
        THREE.MathUtils.clamp(
          ref.current.position.x,
          -32,
          32
        )


      ref.current.position.z =
        THREE.MathUtils.clamp(
          ref.current.position.z,
          -32,
          32
        )


      if (
        onPositionChange
      ) {

        onPositionChange({

          x:
            ref.current.position.x,

          y:
            ref.current.position.y,

          z:
            ref.current.position.z

        })
      }
    }
  )


  return (

    <>

      <group
        ref={ref}
        position={[
          0,
          0,
          6
        ]}
      >

        <mesh
          castShadow
          position={[
            0,
            .85,
            0
          ]}
        >

          <capsuleGeometry
            args={[
              .55,
              1.1,
              8,
              16
            ]}
          />

          <meshStandardMaterial
            color="#f0c84b"
          />

        </mesh>


        <mesh
          castShadow
          position={[
            0,
            1.8,
            0
          ]}
        >

          <sphereGeometry
            args={[
              .42,
              20,
              20
            ]}
          />

          <meshStandardMaterial
            color="#f4d6a0"
          />

        </mesh>

      </group>


      <FollowCamera
        playerRef={ref}
      />

    </>
  )
}


function GameScene({
  active,
  input,
  resetSignal,
  onPositionChange
}) {

  return (

    <>

      <WorldDecor />

      <Player
        active={active}
        input={input}
        resetSignal={resetSignal}
        onPositionChange={
          onPositionChange
        }
      />

    </>
  )
}


function TouchButton({
  label,
  onDown,
  onUp,
  style
}) {

  return (

    <button
      type="button"

      onPointerDown={
        event => {

          event.preventDefault()

          onDown()
        }
      }

      onPointerUp={
        event => {

          event.preventDefault()

          onUp()
        }
      }

      onPointerCancel={
        onUp
      }

      onPointerLeave={
        onUp
      }

      style={{
        width: 58,
        height: 58,
        borderRadius: 18,
        border:
          '1px solid rgba(255,255,255,.22)',
        background:
          'rgba(7,17,28,.78)',
        color:
          '#fff',
        fontWeight:
          900,
        fontSize:
          24,
        touchAction:
          'none',
        ...style
      }}
    >

      {label}

    </button>
  )
}


function App() {

  const [
    started,
    setStarted
  ] = useState(
    false
  )


  const [
    paused,
    setPaused
  ] = useState(
    false
  )


  const [
    resetSignal,
    setResetSignal
  ] = useState(
    0
  )


  const [
    position,
    setPosition
  ] = useState({
    x: 0,
    y: 0,
    z: 6
  })


  const [
    input,
    setInput
  ] = useState({

    up:
      false,

    down:
      false,

    left:
      false,

    right:
      false,

    jump:
      false
  })


  const active =
    started
    &&
    !paused


  const setControl = (
    key,
    value
  ) => {

    setInput(
      current => ({

        ...current,

        [key]:
          value

      })
    )
  }


  useEffect(
    () => {

      const down =
        event => {

          const key =
            event.key
            .toLowerCase()


          if (
            key === 'w'
            ||
            key === 'arrowup'
          ) {

            setControl(
              'up',
              true
            )
          }


          if (
            key === 's'
            ||
            key === 'arrowdown'
          ) {

            setControl(
              'down',
              true
            )
          }


          if (
            key === 'a'
            ||
            key === 'arrowleft'
          ) {

            setControl(
              'left',
              true
            )
          }


          if (
            key === 'd'
            ||
            key === 'arrowright'
          ) {

            setControl(
              'right',
              true
            )
          }


          if (
            key === ' '
          ) {

            event.preventDefault()

            setControl(
              'jump',
              true
            )
          }


          if (
            key === 'escape'
            &&
            started
          ) {

            setPaused(
              value =>
                !value
            )
          }
        }


      const up =
        event => {

          const key =
            event.key
            .toLowerCase()


          if (
            key === 'w'
            ||
            key === 'arrowup'
          ) {

            setControl(
              'up',
              false
            )
          }


          if (
            key === 's'
            ||
            key === 'arrowdown'
          ) {

            setControl(
              'down',
              false
            )
          }


          if (
            key === 'a'
            ||
            key === 'arrowleft'
          ) {

            setControl(
              'left',
              false
            )
          }


          if (
            key === 'd'
            ||
            key === 'arrowright'
          ) {

            setControl(
              'right',
              false
            )
          }


          if (
            key === ' '
          ) {

            setControl(
              'jump',
              false
            )
          }
        }


      window.addEventListener(
        'keydown',
        down,
        {
          passive:
            false
        }
      )


      window.addEventListener(
        'keyup',
        up
      )


      return () => {

        window.removeEventListener(
          'keydown',
          down
        )

        window.removeEventListener(
          'keyup',
          up
        )
      }

    },
    [
      started
    ]
  )


  const startGame =
    () => {

      setPaused(
        false
      )

      setStarted(
        true
      )

      setResetSignal(
        value =>
          value + 1
      )
    }


  return (

    <div
      style={{
        width:
          '100%',
        height:
          '100%',
        position:
          'relative',
        background:
          '#050b14'
      }}
    >

      <Canvas
        shadows
        camera={{
          position:
            [
              7,
              6,
              15
            ],

          fov:
            55
        }}
      >

        <GameScene
          active={
            active
          }

          input={
            input
          }

          resetSignal={
            resetSignal
          }

          onPositionChange={
            setPosition
          }
        />

      </Canvas>


      <div
        style={{
          position:
            'absolute',
          top:
            14,
          right:
            14,
          zIndex:
            15,
          color:
            '#f7d67a',
          background:
            'rgba(5,11,20,.78)',
          border:
            '1px solid rgba(247,214,122,.28)',
          borderRadius:
            14,
          padding:
            '10px 14px',
          pointerEvents:
            'none'
        }}
      >

        <strong>
          MAJD GAMES
        </strong>

        <div
          style={{
            color:
              '#fff',

            marginTop:
              4
          }}
        >

          {GAME_NAME}

        </div>


        {started && (

          <div
            style={{
              color:
                '#9fd8ff',
              marginTop:
                5,
              fontSize:
                12
            }}
          >

            X {position.x.toFixed(1)}
            {' · '}
            Z {position.z.toFixed(1)}

          </div>
        )}

      </div>


      {started && (

        <>

          <div
            style={{
              position:
                'absolute',
              left:
                18,
              bottom:
                22,
              zIndex:
                30,
              display:
                'grid',
              gridTemplateColumns:
                '58px 58px 58px',
              gap:
                7,
              direction:
                'ltr'
            }}
          >

            <span />

            <TouchButton
              label="▲"
              onDown={
                () =>
                  setControl(
                    'up',
                    true
                  )
              }
              onUp={
                () =>
                  setControl(
                    'up',
                    false
                  )
              }
            />

            <span />


            <TouchButton
              label="◀"
              onDown={
                () =>
                  setControl(
                    'left',
                    true
                  )
              }
              onUp={
                () =>
                  setControl(
                    'left',
                    false
                  )
              }
            />


            <TouchButton
              label="▼"
              onDown={
                () =>
                  setControl(
                    'down',
                    true
                  )
              }
              onUp={
                () =>
                  setControl(
                    'down',
                    false
                  )
              }
            />


            <TouchButton
              label="▶"
              onDown={
                () =>
                  setControl(
                    'right',
                    true
                  )
              }
              onUp={
                () =>
                  setControl(
                    'right',
                    false
                  )
              }
            />

          </div>


          <div
            style={{
              position:
                'absolute',
              right:
                18,
              bottom:
                24,
              zIndex:
                30,
              display:
                'flex',
              flexDirection:
                'column',
              gap:
                10
            }}
          >

            <TouchButton
              label="⤒"

              onDown={
                () =>
                  setControl(
                    'jump',
                    true
                  )
              }

              onUp={
                () =>
                  setControl(
                    'jump',
                    false
                  )
              }

              style={{
                background:
                  'rgba(184,137,37,.88)'
              }}
            />


            <button
              type="button"

              onClick={
                () =>
                  setResetSignal(
                    value =>
                      value + 1
                  )
              }

              style={{
                minWidth:
                  76,
                padding:
                  '12px 14px',
                borderRadius:
                  14,
                border:
                  '1px solid rgba(255,255,255,.2)',
                background:
                  'rgba(7,17,28,.82)',
                color:
                  '#fff',
                fontWeight:
                  800
              }}
            >

              إعادة

            </button>

          </div>


          <button
            type="button"

            onClick={
              () =>
                setPaused(
                  value =>
                    !value
                )
            }

            style={{
              position:
                'absolute',
              top:
                16,
              left:
                16,
              zIndex:
                32,
              border:
                0,
              borderRadius:
                14,
              padding:
                '11px 15px',
              background:
                paused
                  ?
                  '#f0c84b'
                  :
                  'rgba(7,17,28,.82)',
              color:
                paused
                  ?
                  '#111'
                  :
                  '#fff',
              fontWeight:
                900
            }}
          >

            {
              paused
                ?
                'متابعة'
                :
                'إيقاف'
            }

          </button>

        </>
      )}


      {!started && (

        <div
          style={{
            position:
              'absolute',
            inset:
              0,
            zIndex:
              40,
            display:
              'flex',
            alignItems:
              'center',
            justifyContent:
              'center',
            background:
              'radial-gradient(circle,rgba(16,35,54,.76),rgba(0,0,0,.94))'
          }}
        >

          <div
            style={{
              width:
                'min(92vw,520px)',
              padding:
                36,
              borderRadius:
                24,
              border:
                '1px solid rgba(247,214,122,.35)',
              background:
                'linear-gradient(145deg,#0e1b2a,#07111c)',
              color:
                '#fff',
              textAlign:
                'center',
              boxShadow:
                '0 30px 80px rgba(0,0,0,.55)'
            }}
          >

            <div
              style={{
                fontSize:
                  44,
                marginBottom:
                  10
              }}
            >
              👑
            </div>


            <h1
              style={{
                margin:
                  0,
                color:
                  '#f7d67a'
              }}
            >
              {GAME_NAME}
            </h1>


            <p
              style={{
                opacity:
                  .78,
                lineHeight:
                  1.8
              }}
            >

              لعبة ثلاثية الأبعاد قابلة للتحكم.

              <br />

              استخدم WASD أو الأسهم على الكمبيوتر.

              <br />

              واستخدم أزرار اللمس على الجوال.

            </p>


            <button
              type="button"

              onClick={
                startGame
              }

              style={{
                marginTop:
                  12,
                border:
                  0,
                borderRadius:
                  40,
                padding:
                  '15px 34px',
                background:
                  'linear-gradient(90deg,#b88925,#f0cb68)',
                color:
                  '#101010',
                fontWeight:
                  900,
                cursor:
                  'pointer',
                fontSize:
                  17
              }}
            >

              دخول اللعبة

            </button>

          </div>

        </div>
      )}


      {paused && (

        <div
          style={{
            position:
              'absolute',
            inset:
              0,
            zIndex:
              35,
            display:
              'flex',
            alignItems:
              'center',
            justifyContent:
              'center',
            pointerEvents:
              'none',
            color:
              '#fff',
            fontSize:
              28,
            fontWeight:
              900,
            background:
              'rgba(0,0,0,.34)'
          }}
        >

          متوقف مؤقتاً

        </div>
      )}


      <script
        type="application/json"
        data-majd-request="true"
        dangerouslySetInnerHTML={{
          __html:
            JSON.stringify(
              GAME_REQUEST
            )
        }}
      />

    </div>
  )
}


export default App
"""

        content = (
            template
            .replace(
                "__GAME_NAME__",
                game_name_json
            )
            .replace(
                "__GAME_REQUEST__",
                request_json
            )
        )

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
    # NODE
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

                command=[
                    "npm",
                    "install"
                ],

                cwd=str(
                    self.context.source_dir
                ),

                returncode=127,

                stdout="",

                stderr=
                    "npm not found",

                success=False,

                duration_seconds=0.0
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

                command=[
                    "npm",
                    "run",
                    "build"
                ],

                cwd=str(
                    self.context.source_dir
                ),

                returncode=127,

                stdout="",

                stderr=
                    "npm not found",

                success=False,

                duration_seconds=0.0
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
    # VERIFY
    # ========================================================

    def verify_dist(
        self
    ) -> Dict[str, Any]:

        ctx = (
            self.context
        )


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


        index_text = (
            index_file
            .read_text(
                encoding="utf-8",
                errors="replace"
            )
        )


        if (
            '<div id="root"></div>'
            not in
            index_text
        ):

            return {

                "success":
                    False,

                "status":
                    "REACT_ROOT_NOT_FOUND"
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

            "javascript_count":
                len(
                    javascript_files
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

            self.save_state(
                "CREATING_PROJECT"
            )


            self.create_project()


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

                "gameplay": {

                    "real_player":
                        True,

                    "keyboard_controls":
                        True,

                    "touch_controls":
                        True,

                    "jump":
                        True,

                    "pause":
                        True,

                    "reset":
                        True,

                    "follow_camera":
                        True
                },

                "install": {

                    "success":
                        install_result.success,

                    "duration_seconds":
                        install_result.duration_seconds
                },

                "build": {

                    "success":
                        build_result.success,

                    "duration_seconds":
                        build_result.duration_seconds,

                    "stdout":
                        build_result.stdout[
                            -4000:
                        ],

                    "stderr":
                        build_result.stderr[
                            -4000:
                        ]
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
# CLI
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

        default=
            "MAJD TEST GAME"
    )


    parser.add_argument(

        "--output",

        default=str(

            Path(
                __file__
            )
            .resolve()
            .parent

            /

            "majd_game_output"
        )
    )


    args = (
        parser.parse_args()
    )


    request = {

        "type":
            "CREATE_GAME",

        "name":
            args.name,

        "genre":
            "ADVENTURE",

        "dimension":
            "3D",

        "platform": [

            "WEB",

            "PC",

            "MOBILE"
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

        else

        1
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )

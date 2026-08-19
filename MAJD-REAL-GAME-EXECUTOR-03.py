#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-REAL-GAME-EXECUTOR-03.py
================================

REAL GAME EXECUTOR
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


# ============================================================
# SYSTEM
# ============================================================

SYSTEM_NAME = "MAJD-GAME-FACTORY"
EXECUTOR_NAME = "MAJD-REAL-GAME-EXECUTOR"
VERSION = "1.0.0"

MAX_REPAIR_ATTEMPTS = 3

SUPPORTED_TARGETS = {
    "WEB",
    "PC",
    "ANDROID",
    "IPAD",
}

REQUIRED_BUILD_FILES = (
    "index.html",
    "game.js",
    "style.css",
    "game.json",
)


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

def write_json(
    path: Path,
    data: Dict[str, Any]
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

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
            indent=2
        )

    temp.replace(path)


def read_json(
    path: Path
) -> Dict[str, Any]:

    if not path.exists():
        return {}

    try:

        with path.open(
            "r",
            encoding="utf-8"
        ) as file:

            value = json.load(file)

        if isinstance(
            value,
            dict
        ):
            return value

    except Exception:
        pass

    return {}


# ============================================================
# TEXT
# ============================================================

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


# ============================================================
# HASH
# ============================================================

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


# ============================================================
# SAFE NAME
# ============================================================

def safe_name(
    value: str
) -> str:

    value = str(
        value or "MAJD-GAME"
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
        value = "MAJD-GAME"

    return value[:80]


# ============================================================
# RESULT MODEL
# ============================================================

@dataclass
class CheckResult:

    name: str
    passed: bool
    message: str


@dataclass
class BuildContext:

    job_id: str
    game_name: str
    safe_game_name: str

    genre: str
    dimension: str

    targets: List[str]

    request: Dict[str, Any]

    workspace: Path
    source_dir: Path
    build_dir: Path
    logs_dir: Path

    created_at: str


# ============================================================
# EXECUTOR
# ============================================================

class RealGameExecutor:

    def __init__(
        self,
        request: Dict[str, Any],
        job_id: str,
        output_root: str
    ):

        self.request = dict(
            request or {}
        )

        self.job_id = str(
            job_id or uuid.uuid4()
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

        self.context = BuildContext(

            job_id=self.job_id,

            game_name=game_name,

            safe_game_name=cleaned_name,

            genre=str(
                self.request.get(
                    "genre"
                )
                or
                "ADVENTURE"
            ),

            dimension=str(
                self.request.get(
                    "dimension"
                )
                or
                "2D"
            ),

            targets=self._normalize_targets(
                self.request.get(
                    "platform"
                )
            ),

            request=self.request,

            workspace=workspace,

            source_dir=(
                workspace
                /
                "source"
            ),

            build_dir=(
                workspace
                /
                "build"
            ),

            logs_dir=(
                workspace
                /
                "logs"
            ),

            created_at=utc_now()
        )

        self.checks: List[
            CheckResult
        ] = []

        self.repair_attempts = 0


    # ========================================================
    # TARGETS
    # ========================================================

    def _normalize_targets(
        self,
        value: Any
    ) -> List[str]:

        if isinstance(
            value,
            str
        ):

            values = [
                value
            ]

        elif isinstance(
            value,
            list
        ):

            values = value

        else:

            values = [
                "WEB"
            ]


        normalized = []

        for target in values:

            item = str(
                target
            ).upper().strip()

            if (
                item
                in
                SUPPORTED_TARGETS
                and
                item
                not in normalized
            ):

                normalized.append(
                    item
                )


        if not normalized:

            normalized = [
                "WEB"
            ]


        return normalized


    # ========================================================
    # WORKSPACE
    # ========================================================

    def prepare_workspace(
        self
    ) -> None:

        ctx = self.context

        ctx.workspace.mkdir(
            parents=True,
            exist_ok=True
        )

        ctx.source_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        ctx.build_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        ctx.logs_dir.mkdir(
            parents=True,
            exist_ok=True
        )


        write_json(

            ctx.workspace
            /
            "request.json",

            ctx.request
        )


        write_json(

            ctx.workspace
            /
            "build-context.json",

            {
                **asdict(ctx),

                "workspace":
                    str(ctx.workspace),

                "source_dir":
                    str(ctx.source_dir),

                "build_dir":
                    str(ctx.build_dir),

                "logs_dir":
                    str(ctx.logs_dir),
            }
        )


    # ========================================================
    # GAME CONFIG
    # ========================================================

    def create_game_config(
        self
    ) -> Dict[str, Any]:

        ctx = self.context

        config = {

            "id":
                ctx.job_id,

            "name":
                ctx.game_name,

            "genre":
                ctx.genre,

            "dimension":
                ctx.dimension,

            "targets":
                ctx.targets,

            "engine":
                "MAJD-WEB-RUNTIME",

            "version":
                "1.0.0",

            "created_at":
                ctx.created_at,

            "status":
                "BUILDING",

            "controls": {

                "move_left": [
                    "ArrowLeft",
                    "a",
                    "A"
                ],

                "move_right": [
                    "ArrowRight",
                    "d",
                    "D"
                ],

                "move_up": [
                    "ArrowUp",
                    "w",
                    "W"
                ],

                "move_down": [
                    "ArrowDown",
                    "s",
                    "S"
                ]
            }
        }


        write_json(

            ctx.source_dir
            /
            "game.json",

            config
        )


        return config


    # ========================================================
    # HTML
    # ========================================================

    def create_index_html(
        self
    ) -> None:

        name = (
            self.context.game_name
        )

        html = f"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"
    >
    <meta
        name="theme-color"
        content="#05070c"
    >
    <title>{name}</title>
    <link
        rel="stylesheet"
        href="./style.css"
    >
</head>

<body>

<div id="game-shell">

    <header id="top-bar">

        <div>
            <strong id="game-title">
                {name}
            </strong>
        </div>

        <div id="game-status">
            جاهز
        </div>

    </header>

    <main id="game-container">

        <canvas
            id="game-canvas"
            width="1280"
            height="720"
            aria-label="{name}"
        ></canvas>

        <section
            id="start-screen"
            class="overlay"
        >

            <div class="panel">

                <h1>
                    {name}
                </h1>

                <p>
                    لعبة تم بناؤها بواسطة
                    MAJD GAME FACTORY
                </p>

                <button
                    id="start-button"
                    type="button"
                >
                    ابدأ اللعب
                </button>

            </div>

        </section>

        <section
            id="win-screen"
            class="overlay hidden"
        >

            <div class="panel">

                <h2>
                    تم إنهاء المرحلة
                </h2>

                <button
                    id="restart-button"
                    type="button"
                >
                    العب مرة أخرى
                </button>

            </div>

        </section>

    </main>

    <div
        id="mobile-controls"
        aria-label="أزرار التحكم"
    >

        <button
            data-action="left"
            type="button"
        >
            ◀
        </button>

        <button
            data-action="up"
            type="button"
        >
            ▲
        </button>

        <button
            data-action="down"
            type="button"
        >
            ▼
        </button>

        <button
            data-action="right"
            type="button"
        >
            ▶
        </button>

    </div>

</div>

<script src="./game.js"></script>

</body>
</html>
"""

        write_text(

            self.context.source_dir
            /
            "index.html",

            html
        )


    # ========================================================
    # CSS
    # ========================================================

    def create_style_css(
        self
    ) -> None:

        css = """
* {
    box-sizing: border-box;
}

html,
body {
    width: 100%;
    min-height: 100%;
    margin: 0;
    background:
        radial-gradient(
            circle at top,
            #17213b 0%,
            #080b13 45%,
            #030407 100%
        );
    color: #ffffff;
    font-family:
        Arial,
        Tahoma,
        sans-serif;
}

body {
    overflow-x: hidden;
}

button {
    font: inherit;
}

#game-shell {
    width: min(100%, 1500px);
    margin: 0 auto;
    min-height: 100vh;
    padding: 12px;
}

#top-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    min-height: 54px;
    padding: 10px 16px;
    background: rgba(0, 0, 0, 0.45);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 14px;
    margin-bottom: 12px;
}

#game-container {
    position: relative;
    width: 100%;
    aspect-ratio: 16 / 9;
    overflow: hidden;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.15);
    background: #07101d;
    box-shadow: 0 20px 70px rgba(0,0,0,0.5);
}

#game-canvas {
    display: block;
    width: 100%;
    height: 100%;
    touch-action: none;
}

.overlay {
    position: absolute;
    inset: 0;
    display: grid;
    place-items: center;
    padding: 20px;
    background: rgba(0,0,0,0.50);
    backdrop-filter: blur(5px);
}

.hidden {
    display: none !important;
}

.panel {
    width: min(92%, 520px);
    padding: 28px;
    border-radius: 18px;
    text-align: center;
    background: rgba(8,13,25,0.92);
    border: 1px solid rgba(255,255,255,0.15);
}

.panel h1,
.panel h2 {
    margin-top: 0;
}

.panel button {
    border: 0;
    border-radius: 12px;
    padding: 13px 24px;
    cursor: pointer;
    font-weight: 700;
}

#mobile-controls {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    width: min(100%, 520px);
    margin: 14px auto 0;
}

#mobile-controls button {
    min-height: 58px;
    border: 1px solid rgba(255,255,255,0.16);
    border-radius: 14px;
    background: rgba(255,255,255,0.10);
    color: white;
    font-size: 22px;
    touch-action: manipulation;
}

@media (min-width: 900px) {
    #mobile-controls {
        width: 420px;
    }
}
"""

        write_text(

            self.context.source_dir
            /
            "style.css",

            css.strip()
        )


    # ========================================================
    # GAME JAVASCRIPT
    # ========================================================

    def create_game_js(
        self
    ) -> None:

        game_name_json = json.dumps(
            self.context.game_name,
            ensure_ascii=False
        )

        genre_json = json.dumps(
            self.context.genre,
            ensure_ascii=False
        )

        dimension_json = json.dumps(
            self.context.dimension,
            ensure_ascii=False
        )


        javascript = f"""
"use strict";

(() => {{

const GAME = Object.freeze({{
    name: {game_name_json},
    genre: {genre_json},
    dimension: {dimension_json}
}});

const canvas =
    document.getElementById("game-canvas");

const ctx =
    canvas.getContext("2d");

const startScreen =
    document.getElementById("start-screen");

const winScreen =
    document.getElementById("win-screen");

const startButton =
    document.getElementById("start-button");

const restartButton =
    document.getElementById("restart-button");

const statusElement =
    document.getElementById("game-status");


if (!canvas || !ctx) {{
    throw new Error(
        "MAJD GAME RUNTIME: Canvas unavailable"
    );
}}


const world = {{

    width: 2400,

    height: 1350,

    goal: {{
        x: 2180,
        y: 1080,
        width: 90,
        height: 120
    }},

    obstacles: [
        {{
            x: 520,
            y: 1020,
            width: 150,
            height: 150
        }},
        {{
            x: 930,
            y: 900,
            width: 170,
            height: 270
        }},
        {{
            x: 1420,
            y: 980,
            width: 220,
            height: 190
        }},
        {{
            x: 1830,
            y: 850,
            width: 180,
            height: 320
        }}
    ]
}};


const player = {{

    x: 120,

    y: 1080,

    width: 54,

    height: 54,

    speed: 430
}};


const keys = new Set();

let running = false;

let lastTime = 0;

let cameraX = 0;

let cameraY = 0;


function resetGame() {{

    player.x = 120;

    player.y = 1080;

    cameraX = 0;

    cameraY = 0;

    winScreen.classList.add(
        "hidden"
    );

    statusElement.textContent =
        "قيد اللعب";
}}


function startGame() {{

    resetGame();

    startScreen.classList.add(
        "hidden"
    );

    running = true;

    lastTime =
        performance.now();

    requestAnimationFrame(
        loop
    );
}}


function stopWithWin() {{

    running = false;

    statusElement.textContent =
        "تم إنهاء المرحلة";

    winScreen.classList.remove(
        "hidden"
    );
}}


function intersects(
    a,
    b
) {{

    return (
        a.x < b.x + b.width &&
        a.x + a.width > b.x &&
        a.y < b.y + b.height &&
        a.y + a.height > b.y
    );
}}


function tryMove(
    dx,
    dy
) {{

    const candidate = {{

        x:
            Math.max(
                0,
                Math.min(
                    world.width - player.width,
                    player.x + dx
                )
            ),

        y:
            Math.max(
                0,
                Math.min(
                    world.height - player.height,
                    player.y + dy
                )
            ),

        width:
            player.width,

        height:
            player.height
    }};


    for (
        const obstacle
        of world.obstacles
    ) {{

        if (
            intersects(
                candidate,
                obstacle
            )
        ) {{

            return;
        }}
    }}


    player.x =
        candidate.x;

    player.y =
        candidate.y;


    if (
        intersects(
            player,
            world.goal
        )
    ) {{

        stopWithWin();
    }}
}}


function update(
    dt
) {{

    let dx = 0;

    let dy = 0;


    if (
        keys.has("ArrowLeft")
        ||
        keys.has("a")
        ||
        keys.has("A")
    ) {{

        dx -=
            player.speed
            *
            dt;
    }}


    if (
        keys.has("ArrowRight")
        ||
        keys.has("d")
        ||
        keys.has("D")
    ) {{

        dx +=
            player.speed
            *
            dt;
    }}


    if (
        keys.has("ArrowUp")
        ||
        keys.has("w")
        ||
        keys.has("W")
    ) {{

        dy -=
            player.speed
            *
            dt;
    }}


    if (
        keys.has("ArrowDown")
        ||
        keys.has("s")
        ||
        keys.has("S")
    ) {{

        dy +=
            player.speed
            *
            dt;
    }}


    if (
        dx !== 0
        &&
        dy !== 0
    ) {{

        const factor =
            1 / Math.sqrt(2);

        dx *= factor;

        dy *= factor;
    }}


    tryMove(
        dx,
        0
    );

    tryMove(
        0,
        dy
    );


    cameraX =
        Math.max(
            0,
            Math.min(
                world.width
                -
                canvas.width,

                player.x
                -
                canvas.width
                /
                2
            )
        );


    cameraY =
        Math.max(
            0,
            Math.min(
                world.height
                -
                canvas.height,

                player.y
                -
                canvas.height
                /
                2
            )
        );
}}


function drawBackground() {{

    const gradient =
        ctx.createLinearGradient(
            0,
            0,
            0,
            canvas.height
        );

    gradient.addColorStop(
        0,
        "#152a48"
    );

    gradient.addColorStop(
        1,
        "#07101d"
    );

    ctx.fillStyle =
        gradient;

    ctx.fillRect(
        0,
        0,
        canvas.width,
        canvas.height
    );


    ctx.fillStyle =
        "rgba(255,255,255,0.08)";


    for (
        let x = -cameraX % 90;
        x < canvas.width;
        x += 90
    ) {{

        ctx.fillRect(
            x,
            0,
            1,
            canvas.height
        );
    }}


    for (
        let y = -cameraY % 90;
        y < canvas.height;
        y += 90
    ) {{

        ctx.fillRect(
            0,
            y,
            canvas.width,
            1
        );
    }}
}}


function drawWorld() {{

    ctx.save();

    ctx.translate(
        -cameraX,
        -cameraY
    );


    ctx.fillStyle =
        "#253b2b";

    ctx.fillRect(
        0,
        1170,
        world.width,
        180
    );


    ctx.fillStyle =
        "#704c2c";


    for (
        const obstacle
        of world.obstacles
    ) {{

        ctx.fillRect(
            obstacle.x,
            obstacle.y,
            obstacle.width,
            obstacle.height
        );

        ctx.strokeStyle =
            "rgba(255,255,255,0.22)";

        ctx.lineWidth =
            4;

        ctx.strokeRect(
            obstacle.x,
            obstacle.y,
            obstacle.width,
            obstacle.height
        );
    }}


    ctx.fillStyle =
        "#f0c84b";

    ctx.fillRect(
        world.goal.x,
        world.goal.y,
        world.goal.width,
        world.goal.height
    );


    ctx.fillStyle =
        "#ffffff";

    ctx.font =
        "28px Arial";

    ctx.fillText(
        "الهدف",
        world.goal.x - 2,
        world.goal.y - 18
    );


    ctx.fillStyle =
        "#55a7ff";

    ctx.fillRect(
        player.x,
        player.y,
        player.width,
        player.height
    );


    ctx.strokeStyle =
        "#ffffff";

    ctx.lineWidth =
        3;

    ctx.strokeRect(
        player.x,
        player.y,
        player.width,
        player.height
    );


    ctx.restore();
}}


function drawHud() {{

    ctx.fillStyle =
        "rgba(0,0,0,0.48)";

    ctx.fillRect(
        18,
        18,
        400,
        100
    );


    ctx.fillStyle =
        "#ffffff";

    ctx.font =
        "26px Arial";

    ctx.fillText(
        GAME.name,
        38,
        55
    );


    ctx.font =
        "19px Arial";

    ctx.fillText(
        "X: " + Math.round(player.x) + "  Y: " + Math.round(player.y),
        38,
        91
    );
}}


function render() {{

    drawBackground();

    drawWorld();

    drawHud();
}}


function loop(
    now
) {{

    if (!running) {{
        render();
        return;
    }}


    const dt =
        Math.min(
            0.033,
            Math.max(
                0,
                (
                    now
                    -
                    lastTime
                )
                /
                1000
            )
        );


    lastTime =
        now;


    update(
        dt
    );

    render();


    if (running) {{

        requestAnimationFrame(
            loop
        );
    }}
}}


window.addEventListener(
    "keydown",
    event => {{

        keys.add(
            event.key
        );


        if (
            [
                "ArrowLeft",
                "ArrowRight",
                "ArrowUp",
                "ArrowDown"
            ].includes(
                event.key
            )
        ) {{

            event.preventDefault();
        }}
    }}
);


window.addEventListener(
    "keyup",
    event => {{

        keys.delete(
            event.key
        );
    }}
);


document
    .querySelectorAll(
        "#mobile-controls button"
    )
    .forEach(
        button => {{

            const action =
                button.dataset.action;


            const keyMap = {{

                left:
                    "ArrowLeft",

                right:
                    "ArrowRight",

                up:
                    "ArrowUp",

                down:
                    "ArrowDown"
            };


            const key =
                keyMap[action];


            const press =
                event => {{

                    event.preventDefault();

                    keys.add(
                        key
                    );
                }};


            const release =
                event => {{

                    event.preventDefault();

                    keys.delete(
                        key
                    );
                }};


            button.addEventListener(
                "pointerdown",
                press
            );

            button.addEventListener(
                "pointerup",
                release
            );

            button.addEventListener(
                "pointercancel",
                release
            );

            button.addEventListener(
                "pointerleave",
                release
            );
        }}
    );


startButton.addEventListener(
    "click",
    startGame
);


restartButton.addEventListener(
    "click",
    startGame
);


render();

}})();
"""

        write_text(

            self.context.source_dir
            /
            "game.js",

            javascript.strip()
        )


    # ========================================================
    # README
    # ========================================================

    def create_readme(
        self
    ) -> None:

        ctx = self.context

        content = f"""# {ctx.game_name}

Generated by MAJD GAME FACTORY.

Job ID: {ctx.job_id}

Genre: {ctx.genre}

Dimension request: {ctx.dimension}

Targets: {", ".join(ctx.targets)}

## Run

Serve the build directory using any static HTTP server.

Example:

python -m http.server 8080 --directory build

Then open localhost:8080 in a browser.
"""

        write_text(

            ctx.source_dir
            /
            "README.md",

            content
        )


    # ========================================================
    # GENERATE SOURCE
    # ========================================================

    def generate_source(
        self
    ) -> None:

        self.create_game_config()

        self.create_index_html()

        self.create_style_css()

        self.create_game_js()

        self.create_readme()


    # ========================================================
    # BUILD
    # ========================================================

    def build(
        self
    ) -> None:

        ctx = self.context


        if ctx.build_dir.exists():

            shutil.rmtree(
                ctx.build_dir
            )


        ctx.build_dir.mkdir(
            parents=True,
            exist_ok=True
        )


        for item in (
            ctx.source_dir.iterdir()
        ):

            destination = (
                ctx.build_dir
                /
                item.name
            )


            if item.is_dir():

                shutil.copytree(
                    item,
                    destination
                )

            else:

                shutil.copy2(
                    item,
                    destination
                )


        game_config_path = (
            ctx.build_dir
            /
            "game.json"
        )


        config = read_json(
            game_config_path
        )


        config["status"] = (
            "BUILT"
        )

        config["built_at"] = (
            utc_now()
        )


        write_json(
            game_config_path,
            config
        )


    # ========================================================
    # CHECK
    # ========================================================

    def add_check(
        self,
        name: str,
        passed: bool,
        message: str
    ) -> None:

        self.checks.append(

            CheckResult(

                name=name,

                passed=passed,

                message=message
            )
        )


    # ========================================================
    # REQUIRED FILE TEST
    # ========================================================

    def test_required_files(
        self
    ) -> bool:

        passed = True


        for filename in (
            REQUIRED_BUILD_FILES
        ):

            path = (
                self.context.build_dir
                /
                filename
            )


            exists = (
                path.exists()
                and
                path.is_file()
                and
                path.stat().st_size > 0
            )


            self.add_check(

                name=(
                    f"required:{filename}"
                ),

                passed=exists,

                message=(
                    "OK"
                    if exists
                    else
                    "MISSING_OR_EMPTY"
                )
            )


            if not exists:
                passed = False


        return passed


    # ========================================================
    # HTML TEST
    # ========================================================

    def test_html(
        self
    ) -> bool:

        path = (
            self.context.build_dir
            /
            "index.html"
        )


        if not path.exists():

            self.add_check(
                "html",
                False,
                "index.html missing"
            )

            return False


        content = path.read_text(
            encoding="utf-8"
        )


        required = (

            '<canvas',

            'id="game-canvas"',

            'game.js',

            'style.css',
        )


        missing = [

            token

            for token
            in required

            if token
            not in content
        ]


        passed = (
            not missing
        )


        self.add_check(

            "html",

            passed,

            (
                "OK"
                if passed
                else
                "Missing: "
                +
                ", ".join(
                    missing
                )
            )
        )


        return passed


    # ========================================================
    # JAVASCRIPT TEST
    # ========================================================

    def test_javascript(
        self
    ) -> bool:

        path = (
            self.context.build_dir
            /
            "game.js"
        )


        if not path.exists():

            self.add_check(
                "javascript",
                False,
                "game.js missing"
            )

            return False


        content = path.read_text(
            encoding="utf-8"
        )


        required = (

            '"use strict"',

            "requestAnimationFrame",

            "function update",

            "function render",

            "startGame",

            "mobile-controls",
        )


        missing = [

            token

            for token
            in required

            if token
            not in content
        ]


        if missing:

            self.add_check(

                "javascript",

                False,

                "Missing runtime tokens: "
                +
                ", ".join(
                    missing
                )
            )

            return False


        node = shutil.which(
            "node"
        )


        if node:

            process = subprocess.run(

                [
                    node,
                    "--check",
                    str(path)
                ],

                capture_output=True,

                text=True,

                timeout=30
            )


            passed = (
                process.returncode
                ==
                0
            )


            self.add_check(

                "javascript-syntax",

                passed,

                (
                    "Node syntax check OK"
                    if passed
                    else
                    (
                        process.stderr.strip()
                        or
                        "Node syntax check failed"
                    )
                )
            )


            return passed


        self.add_check(

            "javascript-structure",

            True,

            "Node unavailable; structural JS validation passed"
        )


        return True


    # ========================================================
    # CONFIG TEST
    # ========================================================

    def test_game_config(
        self
    ) -> bool:

        path = (
            self.context.build_dir
            /
            "game.json"
        )


        config = read_json(
            path
        )


        required = (

            "id",

            "name",

            "genre",

            "dimension",

            "targets",

            "engine",

            "status",
        )


        missing = [

            key

            for key
            in required

            if key
            not in config
        ]


        passed = (
            not missing
        )


        self.add_check(

            "game-config",

            passed,

            (
                "OK"
                if passed
                else
                "Missing keys: "
                +
                ", ".join(
                    missing
                )
            )
        )


        return passed


    # ========================================================
    # ARTIFACT TEST
    # ========================================================

    def test_artifact(
        self
    ) -> bool:

        build_dir = (
            self.context.build_dir
        )


        if (
            not build_dir.exists()
            or
            not build_dir.is_dir()
        ):

            self.add_check(

                "artifact",

                False,

                "Build directory missing"
            )

            return False


        files = [

            path

            for path
            in build_dir.rglob("*")

            if path.is_file()
        ]


        passed = (
            len(files) >= 4
        )


        self.add_check(

            "artifact",

            passed,

            (
                f"{len(files)} build files"
                if passed
                else
                "Artifact incomplete"
            )
        )


        return passed


    # ========================================================
    # RUN TESTS
    # ========================================================

    def run_tests(
        self
    ) -> bool:

        self.checks = []


        results = [

            self.test_required_files(),

            self.test_html(),

            self.test_javascript(),

            self.test_game_config(),

            self.test_artifact(),
        ]


        passed = all(
            results
        )


        write_json(

            self.context.logs_dir
            /
            "test-results.json",

            {
                "passed":
                    passed,

                "checked_at":
                    utc_now(),

                "checks": [
                    asdict(check)
                    for check
                    in self.checks
                ]
            }
        )


        return passed


    # ========================================================
    # AUTO REPAIR
    # ========================================================

    def repair(
        self
    ) -> None:

        self.repair_attempts += 1


        build_dir = (
            self.context.build_dir
        )


        index_path = (
            build_dir
            /
            "index.html"
        )


        style_path = (
            build_dir
            /
            "style.css"
        )


        js_path = (
            build_dir
            /
            "game.js"
        )


        config_path = (
            build_dir
            /
            "game.json"
        )


        if (
            not index_path.exists()
            or
            index_path.stat().st_size == 0
        ):

            self.create_index_html()

            shutil.copy2(

                self.context.source_dir
                /
                "index.html",

                index_path
            )


        if (
            not style_path.exists()
            or
            style_path.stat().st_size == 0
        ):

            self.create_style_css()

            shutil.copy2(

                self.context.source_dir
                /
                "style.css",

                style_path
            )


        if (
            not js_path.exists()
            or
            js_path.stat().st_size == 0
        ):

            self.create_game_js()

            shutil.copy2(

                self.context.source_dir
                /
                "game.js",

                js_path
            )


        if (
            not config_path.exists()
            or
            not read_json(
                config_path
            )
        ):

            self.create_game_config()

            shutil.copy2(

                self.context.source_dir
                /
                "game.json",

                config_path
            )


        write_json(

            self.context.logs_dir
            /
            f"repair-{self.repair_attempts}.json",

            {
                "attempt":
                    self.repair_attempts,

                "time":
                    utc_now()
            }
        )


    # ========================================================
    # MANIFEST
    # ========================================================

    def create_manifest(
        self
    ) -> Path:

        ctx = self.context

        files = []


        for path in sorted(
            ctx.build_dir.rglob("*")
        ):

            if not path.is_file():
                continue


            files.append({

                "path":
                    str(
                        path.relative_to(
                            ctx.build_dir
                        )
                    ),

                "size":
                    path.stat().st_size,

                "sha256":
                    sha256_file(
                        path
                    )
            })


        manifest = {

            "system":
                SYSTEM_NAME,

            "executor":
                EXECUTOR_NAME,

            "executor_version":
                VERSION,

            "job_id":
                ctx.job_id,

            "game_name":
                ctx.game_name,

            "genre":
                ctx.genre,

            "dimension":
                ctx.dimension,

            "targets":
                ctx.targets,

            "artifact":
                str(
                    ctx.build_dir
                ),

            "created_at":
                ctx.created_at,

            "completed_at":
                utc_now(),

            "repair_attempts":
                self.repair_attempts,

            "files":
                files,

            "checks": [
                asdict(check)
                for check
                in self.checks
            ]
        }


        manifest_path = (
            ctx.workspace
            /
            "artifact-manifest.json"
        )


        write_json(
            manifest_path,
            manifest
        )


        return manifest_path


    # ========================================================
    # FINALIZE CONFIG
    # ========================================================

    def finalize_config(
        self
    ) -> None:

        path = (
            self.context.build_dir
            /
            "game.json"
        )


        config = read_json(
            path
        )


        config["status"] = (
            "READY"
        )

        config["verified"] = (
            True
        )

        config["verified_at"] = (
            utc_now()
        )


        write_json(
            path,
            config
        )


    # ========================================================
    # EXECUTE
    # ========================================================

    def execute(
        self
    ) -> Dict[str, Any]:

        started = time.time()


        try:

            # ------------------------------------------------
            # PREPARE
            # ------------------------------------------------

            self.prepare_workspace()


            # ------------------------------------------------
            # GENERATE
            # ------------------------------------------------

            self.generate_source()


            # ------------------------------------------------
            # BUILD
            # ------------------------------------------------

            self.build()


            # ------------------------------------------------
            # TEST + REPAIR LOOP
            # ------------------------------------------------

            passed = (
                self.run_tests()
            )


            while (
                not passed
                and
                self.repair_attempts
                <
                MAX_REPAIR_ATTEMPTS
            ):

                self.repair()

                passed = (
                    self.run_tests()
                )


            # ------------------------------------------------
            # FAILURE
            # ------------------------------------------------

            if not passed:

                return {

                    "success":
                        False,

                    "status":
                        "BUILD_TEST_FAILED",

                    "job_id":
                        self.job_id,

                    "game":
                        self.context.game_name,

                    "artifact":
                        None,

                    "workspace":
                        str(
                            self.context.workspace
                        ),

                    "repair_attempts":
                        self.repair_attempts,

                    "checks": [
                        asdict(check)
                        for check
                        in self.checks
                    ],

                    "duration_seconds":
                        round(
                            time.time()
                            -
                            started,
                            3
                        )
                }


            # ------------------------------------------------
            # FINALIZE
            # ------------------------------------------------

            self.finalize_config()


            # Test one more time after finalization.

            if not self.run_tests():

                return {

                    "success":
                        False,

                    "status":
                        "FINAL_VERIFICATION_FAILED",

                    "job_id":
                        self.job_id,

                    "artifact":
                        None,

                    "workspace":
                        str(
                            self.context.workspace
                        ),

                    "checks": [
                        asdict(check)
                        for check
                        in self.checks
                    ]
                }


            manifest = (
                self.create_manifest()
            )


            # ------------------------------------------------
            # FINAL ARTIFACT GUARANTEE
            # ------------------------------------------------

            artifact = (
                self.context.build_dir
            )


            if (
                not artifact.exists()
                or
                not (
                    artifact
                    /
                    "index.html"
                ).exists()
            ):

                return {

                    "success":
                        False,

                    "status":
                        "ARTIFACT_VERIFICATION_FAILED",

                    "job_id":
                        self.job_id,

                    "artifact":
                        None
                }


            return {

                "success":
                    True,

                "status":
                    "READY",

                "job_id":
                    self.job_id,

                "game":
                    self.context.game_name,

                "genre":
                    self.context.genre,

                "dimension":
                    self.context.dimension,

                "targets":
                    self.context.targets,

                "artifact":
                    str(
                        artifact
                    ),

                "build_path":
                    str(
                        artifact
                    ),

                "entry_file":
                    str(
                        artifact
                        /
                        "index.html"
                    ),

                "manifest":
                    str(
                        manifest
                    ),

                "repair_attempts":
                    self.repair_attempts,

                "checks": [
                    asdict(check)
                    for check
                    in self.checks
                ],

                "duration_seconds":
                    round(
                        time.time()
                        -
                        started,
                        3
                    )
            }


        except Exception as error:

            error_log = {

                "time":
                    utc_now(),

                "job_id":
                    self.job_id,

                "type":
                    type(error).__name__,

                "message":
                    str(error),

                "traceback":
                    traceback.format_exc()
            }


            try:

                self.context.logs_dir.mkdir(
                    parents=True,
                    exist_ok=True
                )

                write_json(

                    self.context.logs_dir
                    /
                    "fatal-error.json",

                    error_log
                )

            except Exception:
                pass


            return {

                "success":
                    False,

                "status":
                    "EXECUTOR_EXCEPTION",

                "job_id":
                    self.job_id,

                "error":
                    str(error),

                "workspace":
                    str(
                        self.context.workspace
                    )
            }


# ============================================================
# PUBLIC INTERFACE REQUIRED BY FILE 02
# ============================================================

def execute_game_request(
    request: Dict[str, Any],
    job_id: str,
    output_root: str
) -> Dict[str, Any]:

    executor = RealGameExecutor(

        request=request,

        job_id=job_id,

        output_root=output_root
    )


    return executor.execute()


# ============================================================
# DIRECT TEST
# ============================================================

def direct_test() -> int:

    request = {

        "type":
            "CREATE_GAME",

        "name":
            "MAJD Test Game",

        "genre":
            "ADVENTURE",

        "dimension":
            "2D",

        "platform": [
            "WEB",
            "PC",
            "ANDROID",
            "IPAD"
        ],

        "description":
            "MAJD GAME FACTORY direct executor test",

        "auto_test":
            True,

        "auto_repair":
            True,

        "produce_playable_build":
            True
    }


    result = execute_game_request(

        request=request,

        job_id=(
            "DIRECT-TEST-"
            +
            uuid.uuid4().hex[:12]
        ),

        output_root=str(
            Path(__file__)
            .resolve()
            .parent
            /
            "majd_game_output"
        )
    )


    print(

        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
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
# ENTRY
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        direct_test()
    )

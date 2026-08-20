#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAJD GAME FACTORY
MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py
===================================
OFFICIAL MAJD PLATFORM BRIDGE
"""
from __future__ import annotations

import hashlib
import json
import mimetypes
import shutil
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

ROOT_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = ROOT_DIR / "public"
ARTIFACTS_DIR = PUBLIC_DIR / "artifacts"
PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def publish_game(game_dir: Path, game_name: str, job_id: str) -> Dict[str, Any]:
    game_id = str(uuid.uuid4())
    artifact_path = ARTIFACTS_DIR / game_id
    artifact_path.mkdir(parents=True, exist_ok=True)

    # نسخ ملفات اللعبة إلى artifacts
    for item in game_dir.iterdir():
        dest = artifact_path / item.name
        if item.is_dir(): shutil.copytree(item, dest)
        else: shutil.copy2(item, dest)

    return {
        "success": True,
        "status": "PUBLISHED_LOCALLY",
        "game_id": game_id,
        "game_path": f"/artifacts/{game_id}/index.html"
    }

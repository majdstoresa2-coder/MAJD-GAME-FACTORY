#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAJD GAME FACTORY
MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py
===================================
OFFICIAL MAJD PLATFORM BRIDGE (نسخة الخادم الذاتي - بدون إعدادات مسبقة)
"""
from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import shutil
import uuid
import zipfile

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ============================================================
# PATHS & CONSTANTS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = ROOT_DIR / "public"
ARTIFACTS_DIR = PUBLIC_DIR / "artifacts"
BRIDGE_DIR = ROOT_DIR / "majd-platform-bridge"

# التأكد من وجود المجلدات
PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
BRIDGE_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# TIME & HELPERS
# ============================================================

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def safe_name(value: str) -> str:
    value = value.strip()
    allowed = [c for c in value if c.isalnum() or c in ("-", "_", ".")]
    return "".join(allowed).strip("-") or "majd-game"

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        while True:
            chunk = file.read(1024 * 1024)
            if not chunk: break
            digest.update(chunk)
    return digest.hexdigest()

# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class GameFile:
    path: str; size: int; sha256: str; content_type: str

@dataclass
class GameManifest:
    game_id: str; game_name: str; game_version: str
    created_at: str; entry_file: Optional[str]; files: List[Dict[str, Any]]

# ============================================================
# MANIFEST BUILDER
# ============================================================

class ManifestBuilder:
    def build(self, game_dir: Path, game_name: str, game_version: str) -> GameManifest:
        files = []
        entry_file = None
        for p in game_dir.rglob("*"):
            if p.is_file():
                rel = str(p.relative_to(game_dir))
                if rel in ["index.html", "game.html", "main.html"]: entry_file = rel
                files.append({
                    "path": rel, "size": p.stat().st_size, 
                    "sha256": sha256_file(p), 
                    "content_type": mimetypes.guess_type(str(p))[0] or "application/octet-stream"
                })
        return GameManifest(
            game_id=str(uuid.uuid4()), game_name=game_name, game_version=game_version,
            created_at=utc_now(), entry_file=entry_file, files=files
        )

# ============================================================
# PUBLIC HOST BUILDER (بدون الحاجة لأي API خارجي)
# ============================================================

def host_game_locally(game_dir: Path, manifest: GameManifest) -> str:
    # إنشاء مجلد اللعبة في المسار العام للخادم
    artifact_path = ARTIFACTS_DIR / manifest.game_id
    artifact_path.mkdir(parents=True, exist_ok=True)

    # نسخ ملفات اللعبة
    for item in game_dir.iterdir():
        dest = artifact_path / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)

    # إنشاء مسار اللعبة (سيتم فتحه عبر متصفح الخادم نفسه)
    # `action.up.railway.app/artifacts/{game_id}/index.html`
    return f"/artifacts/{manifest.game_id}/{manifest.entry_file or 'index.html'}"

# ============================================================
# PUBLIC INTERFACE (للاستخدام من 05.py)
# ============================================================

def publish_game(game_dir: Path, game_name: str, job_id: str) -> Dict[str, Any]:
    builder = ManifestBuilder()
    manifest = builder.build(game_dir=game_dir, game_name=game_name, game_version="1.0.0")

    # استضافة اللعبة محلياً بدلاً من إرسالها لمنصة خارجية
    local_path = host_game_locally(game_dir, manifest)

    # إرجاع النتيجة المباشرة التي سيفهمها 05.py
    return {
        "success": True,
        "status": "PUBLISHED_LOCALLY",
        "game_id": manifest.game_id,
        "game_path": local_path,  # سيستخدم هذا 05.py لعرض الرابط
        "manifest": asdict(manifest)
    }

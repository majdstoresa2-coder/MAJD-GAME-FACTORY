#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-AI-CONTENT-MEDIA-FACTORY-08.py
====================================
MAJD SOVEREIGN AI CONTENT + MEDIA FACTORY

Single-file sovereign content/media production runtime for:
- Movies
- Series
- Episodes
- Video
- Shorts
- Stories
- Images
- Posters
- Thumbnails
- Animation
- VFX
- Audio
- Voice
- Music
- Subtitles
- Dubbing
- Live Streaming
- Channels
- Social Content
- Events
- Games Media
- Publishing
- Scheduling
- Quality Assurance
- Automatic Repair
- Asset Management
- Analytics
- AI Orchestration Integration

Design rule:
This file NEVER reports an external capability as operational unless a
real adapter/engine is configured and its health check succeeds.

Built-in capabilities that can run locally:
- Local project/job/asset storage
- JSON manifests and audit events
- SQLite analytics/index database
- Hashing and validation
- Scheduling metadata
- QA checks
- Safe retry/repair orchestration
- FFmpeg/FFprobe media inspection/transcoding when installed

External capabilities are represented by adapters and remain unavailable
until configured with a real executable/endpoint.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import logging
import mimetypes
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


# ============================================================
# IDENTITY / VERSION
# ============================================================

FACTORY_ID = "MAJD-AI-CONTENT-MEDIA-FACTORY-08"
FACTORY_NAME = "MAJD Sovereign AI Content + Media Factory"
VERSION = "1.0.0"
SCHEMA_VERSION = "1"

ROOT_DIR = Path(__file__).resolve().parent
FACTORY_ROOT = ROOT_DIR / "majd-content-media-factory"
PROJECTS_DIR = FACTORY_ROOT / "projects"
JOBS_DIR = FACTORY_ROOT / "jobs"
ASSETS_DIR = FACTORY_ROOT / "assets"
MANIFESTS_DIR = FACTORY_ROOT / "manifests"
PUBLISH_DIR = FACTORY_ROOT / "published"
LIVE_DIR = FACTORY_ROOT / "live"
LOG_DIR = FACTORY_ROOT / "logs"
TMP_DIR = FACTORY_ROOT / "tmp"
DB_FILE = FACTORY_ROOT / "factory.sqlite3"
CAPABILITY_FILE = FACTORY_ROOT / "capability-report.json"

LOGGER = logging.getLogger("majd.content.media.factory")


# ============================================================
# UTILITIES
# ============================================================

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs() -> None:
    for path in (
        FACTORY_ROOT,
        PROJECTS_DIR,
        JOBS_DIR,
        ASSETS_DIR,
        MANIFESTS_DIR,
        PUBLISH_DIR,
        LIVE_DIR,
        LOG_DIR,
        TMP_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)


def configure_logging(verbose: bool = False) -> None:
    ensure_dirs()
    level = logging.DEBUG if verbose else logging.INFO
    LOGGER.setLevel(level)
    LOGGER.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    stream = logging.StreamHandler(sys.stdout)
    stream.setLevel(level)
    stream.setFormatter(formatter)
    LOGGER.addHandler(stream)

    file_handler = logging.FileHandler(
        LOG_DIR / "factory.log", encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    LOGGER.addHandler(file_handler)


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=path.name + ".",
        suffix=".tmp",
        dir=str(path.parent),
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(
        path,
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False),
    )


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def safe_slug(value: str, fallback: str = "item") -> str:
    raw = (value or "").strip().lower()
    allowed = []
    previous_dash = False
    for char in raw:
        if char.isalnum() or char in ("_", "-"):
            allowed.append(char)
            previous_dash = False
        elif char.isspace() and not previous_dash:
            allowed.append("-")
            previous_dash = True
    slug = "".join(allowed).strip("-_")
    return slug or fallback


def unique_id(prefix: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"{prefix}-{stamp}-{uuid.uuid4().hex[:10]}"


def executable_exists(name: str) -> bool:
    return shutil.which(name) is not None


def run_process(
    args: Sequence[str],
    *,
    cwd: Optional[Path] = None,
    timeout: int = 120,
    env: Optional[Mapping[str, str]] = None,
) -> Tuple[int, str, str]:
    try:
        completed = subprocess.run(
            list(args),
            cwd=str(cwd) if cwd else None,
            timeout=timeout,
            env=dict(os.environ, **dict(env or {})),
            text=True,
            capture_output=True,
            check=False,
        )
        return completed.returncode, completed.stdout, completed.stderr
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        return 124, str(stdout), f"{stderr}\nPROCESS_TIMEOUT".strip()
    except Exception as exc:
        return 1, "", f"{type(exc).__name__}: {exc}"


# ============================================================
# ENUMS / DATA MODELS
# ============================================================

class CapabilityState(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    DEGRADED = "DEGRADED"
    CONFIGURED = "CONFIGURED"
    DISABLED = "DISABLED"


class JobState(str, Enum):
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    BLOCKED = "BLOCKED"


class AssetType(str, Enum):
    MOVIE = "movie"
    SERIES = "series"
    EPISODE = "episode"
    VIDEO = "video"
    SHORT = "short"
    STORY = "story"
    IMAGE = "image"
    POSTER = "poster"
    THUMBNAIL = "thumbnail"
    ANIMATION = "animation"
    VFX = "vfx"
    AUDIO = "audio"
    VOICE = "voice"
    MUSIC = "music"
    SUBTITLE = "subtitle"
    DUB = "dub"
    LIVE_STREAM = "live_stream"
    CHANNEL = "channel"
    SOCIAL_POST = "social_post"
    EVENT = "event"
    GAME_MEDIA = "game_media"
    GENERIC = "generic"


@dataclass
class Capability:
    key: str
    label: str
    state: CapabilityState
    real: bool
    engine: Optional[str] = None
    reason: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AssetRecord:
    asset_id: str
    asset_type: str
    title: str
    path: str
    created_at: str
    sha256: Optional[str] = None
    mime_type: Optional[str] = None
    size_bytes: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    published: bool = False
    live: bool = False


@dataclass
class JobRecord:
    job_id: str
    operation: str
    state: str
    created_at: str
    updated_at: str
    request: Dict[str, Any] = field(default_factory=dict)
    result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    attempts: int = 0
    max_attempts: int = 1


@dataclass
class QAResult:
    ok: bool
    checks: List[Dict[str, Any]]
    score: float
    errors: List[str]
    warnings: List[str]


@dataclass
class PublishResult:
    success: bool
    published: bool
    live: bool
    target: Optional[str]
    message: str
    artifact: Optional[str] = None


# ============================================================
# SQLITE STORE
# ============================================================

class FactoryDatabase:
    def __init__(self, path: Path = DB_FILE) -> None:
        self.path = path
        self._lock = threading.RLock()
        ensure_dirs()
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.path), timeout=30)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self._lock, self.connect() as db:
            db.executescript(
                """
                PRAGMA journal_mode=WAL;
                PRAGMA foreign_keys=ON;

                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    operation TEXT NOT NULL,
                    state TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    request_json TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    error TEXT,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    max_attempts INTEGER NOT NULL DEFAULT 1
                );

                CREATE TABLE IF NOT EXISTS assets (
                    asset_id TEXT PRIMARY KEY,
                    asset_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    path TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    sha256 TEXT,
                    mime_type TEXT,
                    size_bytes INTEGER,
                    metadata_json TEXT NOT NULL,
                    published INTEGER NOT NULL DEFAULT 0,
                    live INTEGER NOT NULL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS schedules (
                    schedule_id TEXT PRIMARY KEY,
                    operation TEXT NOT NULL,
                    run_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    state TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric TEXT NOT NULL,
                    value REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    labels_json TEXT NOT NULL
                );
                """
            )
            db.commit()

    def save_job(self, job: JobRecord) -> None:
        with self._lock, self.connect() as db:
            db.execute(
                """
                INSERT INTO jobs (
                    job_id, operation, state, created_at, updated_at,
                    request_json, result_json, error, attempts, max_attempts
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(job_id) DO UPDATE SET
                    operation=excluded.operation,
                    state=excluded.state,
                    updated_at=excluded.updated_at,
                    request_json=excluded.request_json,
                    result_json=excluded.result_json,
                    error=excluded.error,
                    attempts=excluded.attempts,
                    max_attempts=excluded.max_attempts
                """,
                (
                    job.job_id,
                    job.operation,
                    job.state,
                    job.created_at,
                    job.updated_at,
                    json.dumps(job.request, ensure_ascii=False),
                    json.dumps(job.result, ensure_ascii=False),
                    job.error,
                    job.attempts,
                    job.max_attempts,
                ),
            )
            db.commit()

    def get_job(self, job_id: str) -> Optional[JobRecord]:
        with self._lock, self.connect() as db:
            row = db.execute(
                "SELECT * FROM jobs WHERE job_id = ?",
                (job_id,),
            ).fetchone()
        if not row:
            return None
        return JobRecord(
            job_id=row["job_id"],
            operation=row["operation"],
            state=row["state"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            request=json.loads(row["request_json"]),
            result=json.loads(row["result_json"]),
            error=row["error"],
            attempts=int(row["attempts"]),
            max_attempts=int(row["max_attempts"]),
        )

    def save_asset(self, asset: AssetRecord) -> None:
        with self._lock, self.connect() as db:
            db.execute(
                """
                INSERT INTO assets (
                    asset_id, asset_type, title, path, created_at,
                    sha256, mime_type, size_bytes, metadata_json,
                    published, live
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(asset_id) DO UPDATE SET
                    asset_type=excluded.asset_type,
                    title=excluded.title,
                    path=excluded.path,
                    sha256=excluded.sha256,
                    mime_type=excluded.mime_type,
                    size_bytes=excluded.size_bytes,
                    metadata_json=excluded.metadata_json,
                    published=excluded.published,
                    live=excluded.live
                """,
                (
                    asset.asset_id,
                    asset.asset_type,
                    asset.title,
                    asset.path,
                    asset.created_at,
                    asset.sha256,
                    asset.mime_type,
                    asset.size_bytes,
                    json.dumps(asset.metadata, ensure_ascii=False),
                    1 if asset.published else 0,
                    1 if asset.live else 0,
                ),
            )
            db.commit()

    def get_asset(self, asset_id: str) -> Optional[AssetRecord]:
        with self._lock, self.connect() as db:
            row = db.execute(
                "SELECT * FROM assets WHERE asset_id = ?",
                (asset_id,),
            ).fetchone()
        if not row:
            return None
        return AssetRecord(
            asset_id=row["asset_id"],
            asset_type=row["asset_type"],
            title=row["title"],
            path=row["path"],
            created_at=row["created_at"],
            sha256=row["sha256"],
            mime_type=row["mime_type"],
            size_bytes=row["size_bytes"],
            metadata=json.loads(row["metadata_json"]),
            published=bool(row["published"]),
            live=bool(row["live"]),
        )

    def list_assets(self, limit: int = 100) -> List[AssetRecord]:
        with self._lock, self.connect() as db:
            rows = db.execute(
                "SELECT * FROM assets ORDER BY created_at DESC LIMIT ?",
                (int(limit),),
            ).fetchall()
        return [
            AssetRecord(
                asset_id=row["asset_id"],
                asset_type=row["asset_type"],
                title=row["title"],
                path=row["path"],
                created_at=row["created_at"],
                sha256=row["sha256"],
                mime_type=row["mime_type"],
                size_bytes=row["size_bytes"],
                metadata=json.loads(row["metadata_json"]),
                published=bool(row["published"]),
                live=bool(row["live"]),
            )
            for row in rows
        ]

    def emit(self, event_type: str, payload: Dict[str, Any]) -> None:
        with self._lock, self.connect() as db:
            db.execute(
                "INSERT INTO events(event_type, created_at, payload_json) VALUES (?, ?, ?)",
                (
                    event_type,
                    utc_now(),
                    json.dumps(payload, ensure_ascii=False),
                ),
            )
            db.commit()

    def metric(
        self,
        metric: str,
        value: float,
        labels: Optional[Dict[str, Any]] = None,
    ) -> None:
        with self._lock, self.connect() as db:
            db.execute(
                "INSERT INTO analytics(metric, value, created_at, labels_json) VALUES (?, ?, ?, ?)",
                (
                    metric,
                    float(value),
                    utc_now(),
                    json.dumps(labels or {}, ensure_ascii=False),
                ),
            )
            db.commit()

    def create_schedule(
        self,
        operation: str,
        run_at: str,
        payload: Dict[str, Any],
    ) -> str:
        schedule_id = unique_id("schedule")
        now = utc_now()
        with self._lock, self.connect() as db:
            db.execute(
                """
                INSERT INTO schedules(
                    schedule_id, operation, run_at, payload_json,
                    state, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    schedule_id,
                    operation,
                    run_at,
                    json.dumps(payload, ensure_ascii=False),
                    "SCHEDULED",
                    now,
                    now,
                ),
            )
            db.commit()
        return schedule_id


# ============================================================
# ADAPTER CONTRACTS
# ============================================================

class AdapterError(RuntimeError):
    pass


class BaseAdapter:
    key = "base"
    label = "Base Adapter"

    def configured(self) -> bool:
        return False

    def health(self) -> Capability:
        return Capability(
            key=self.key,
            label=self.label,
            state=CapabilityState.UNAVAILABLE,
            real=False,
            reason="adapter_not_configured",
        )

    def execute(self, operation: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise AdapterError(f"{self.key} does not implement {operation}")


class CommandAdapter(BaseAdapter):
    """
    Generic real command adapter.

    Configuration:
      MAJD_<PREFIX>_COMMAND=/absolute/path/to/executable

    The adapter sends the operation/payload as JSON on stdin.
    The executable must return JSON on stdout and exit 0.
    """

    def __init__(
        self,
        key: str,
        label: str,
        env_var: str,
        timeout: int = 300,
    ) -> None:
        self.key = key
        self.label = label
        self.env_var = env_var
        self.timeout = timeout

    def command(self) -> Optional[str]:
        value = os.getenv(self.env_var, "").strip()
        if not value:
            return None
        return value

    def configured(self) -> bool:
        command = self.command()
        return bool(command and Path(command).exists() and os.access(command, os.X_OK))

    def health(self) -> Capability:
        command = self.command()
        if not command:
            return Capability(
                key=self.key,
                label=self.label,
                state=CapabilityState.UNAVAILABLE,
                real=False,
                engine=None,
                reason=f"{self.env_var}_not_set",
            )
        if not Path(command).exists():
            return Capability(
                key=self.key,
                label=self.label,
                state=CapabilityState.UNAVAILABLE,
                real=False,
                engine=command,
                reason="configured_executable_not_found",
            )
        if not os.access(command, os.X_OK):
            return Capability(
                key=self.key,
                label=self.label,
                state=CapabilityState.UNAVAILABLE,
                real=False,
                engine=command,
                reason="configured_file_not_executable",
            )
        return Capability(
            key=self.key,
            label=self.label,
            state=CapabilityState.AVAILABLE,
            real=True,
            engine=command,
            reason=None,
        )

    def execute(self, operation: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        command = self.command()
        if not self.configured() or not command:
            raise AdapterError(f"{self.key} adapter is not operational")

        request = json.dumps(
            {"operation": operation, "payload": payload},
            ensure_ascii=False,
        )
        try:
            completed = subprocess.run(
                [command],
                input=request,
                text=True,
                capture_output=True,
                timeout=self.timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise AdapterError(f"{self.key} timed out") from exc

        if completed.returncode != 0:
            raise AdapterError(
                f"{self.key} exited {completed.returncode}: {completed.stderr.strip()}"
            )

        try:
            response = json.loads(completed.stdout or "{}")
        except json.JSONDecodeError as exc:
            raise AdapterError(
                f"{self.key} returned non-JSON output"
            ) from exc

        if not isinstance(response, dict):
            raise AdapterError(f"{self.key} returned invalid response type")
        return response


class FFmpegAdapter(BaseAdapter):
    key = "ffmpeg"
    label = "FFmpeg Media Engine"

    def ffmpeg_available(self) -> bool:
        return executable_exists("ffmpeg")

    def ffprobe_available(self) -> bool:
        return executable_exists("ffprobe")

    def configured(self) -> bool:
        return self.ffmpeg_available()

    def health(self) -> Capability:
        ffmpeg = shutil.which("ffmpeg")
        ffprobe = shutil.which("ffprobe")
        if not ffmpeg:
            return Capability(
                key=self.key,
                label=self.label,
                state=CapabilityState.UNAVAILABLE,
                real=False,
                reason="ffmpeg_not_installed",
                details={"ffprobe": bool(ffprobe)},
            )

        code, stdout, stderr = run_process(
            [ffmpeg, "-version"],
            timeout=15,
        )
        if code != 0:
            return Capability(
                key=self.key,
                label=self.label,
                state=CapabilityState.DEGRADED,
                real=False,
                engine=ffmpeg,
                reason=(stderr or stdout or "ffmpeg_health_failed").strip()[:300],
                details={"ffprobe": bool(ffprobe)},
            )

        first_line = (stdout.splitlines() or ["ffmpeg"])[0]
        return Capability(
            key=self.key,
            label=self.label,
            state=CapabilityState.AVAILABLE,
            real=True,
            engine=ffmpeg,
            details={
                "version": first_line,
                "ffprobe": bool(ffprobe),
            },
        )

    def probe(self, input_path: Path) -> Dict[str, Any]:
        if not self.ffprobe_available():
            raise AdapterError("ffprobe is not installed")
        code, stdout, stderr = run_process(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_format",
                "-show_streams",
                "-of",
                "json",
                str(input_path),
            ],
            timeout=120,
        )
        if code != 0:
            raise AdapterError(stderr.strip() or "ffprobe_failed")
        return json.loads(stdout or "{}")

    def transcode(
        self,
        input_path: Path,
        output_path: Path,
        *,
        video_codec: str = "libx264",
        audio_codec: str = "aac",
        overwrite: bool = False,
    ) -> Dict[str, Any]:
        if not self.ffmpeg_available():
            raise AdapterError("ffmpeg is not installed")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        args = ["ffmpeg"]
        args.append("-y" if overwrite else "-n")
        args.extend(
            [
                "-i",
                str(input_path),
                "-c:v",
                video_codec,
                "-c:a",
                audio_codec,
                "-movflags",
                "+faststart",
                str(output_path),
            ]
        )
        code, stdout, stderr = run_process(args, timeout=1800)
        if code != 0:
            raise AdapterError(stderr[-1500:] or stdout[-1500:] or "ffmpeg_failed")
        return {
            "success": output_path.exists(),
            "output": str(output_path),
            "sha256": sha256_file(output_path) if output_path.exists() else None,
        }

    def extract_thumbnail(
        self,
        input_path: Path,
        output_path: Path,
        *,
        at_seconds: float = 1.0,
    ) -> Dict[str, Any]:
        if not self.ffmpeg_available():
            raise AdapterError("ffmpeg is not installed")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        code, stdout, stderr = run_process(
            [
                "ffmpeg",
                "-y",
                "-ss",
                str(max(0.0, float(at_seconds))),
                "-i",
                str(input_path),
                "-frames:v",
                "1",
                "-q:v",
                "2",
                str(output_path),
            ],
            timeout=300,
        )
        if code != 0:
            raise AdapterError(stderr[-1200:] or stdout[-1200:] or "thumbnail_failed")
        return {
            "success": output_path.exists(),
            "output": str(output_path),
        }

    def execute(self, operation: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if operation == "probe":
            return self.probe(Path(payload["input_path"]))
        if operation == "transcode":
            return self.transcode(
                Path(payload["input_path"]),
                Path(payload["output_path"]),
                video_codec=str(payload.get("video_codec", "libx264")),
                audio_codec=str(payload.get("audio_codec", "aac")),
                overwrite=bool(payload.get("overwrite", False)),
            )
        if operation == "thumbnail":
            return self.extract_thumbnail(
                Path(payload["input_path"]),
                Path(payload["output_path"]),
                at_seconds=float(payload.get("at_seconds", 1.0)),
            )
        raise AdapterError(f"Unsupported ffmpeg operation: {operation}")


# ============================================================
# ADAPTER REGISTRY
# ============================================================

class AdapterRegistry:
    def __init__(self) -> None:
        self.adapters: Dict[str, BaseAdapter] = {}
        self.register(FFmpegAdapter())

        self.register(
            CommandAdapter(
                "ai_orchestrator",
                "MAJD AI Orchestration Engine",
                "MAJD_AI_ORCHESTRATOR_COMMAND",
                timeout=900,
            )
        )
        self.register(
            CommandAdapter(
                "image_engine",
                "Image Generation Engine",
                "MAJD_IMAGE_ENGINE_COMMAND",
                timeout=900,
            )
        )
        self.register(
            CommandAdapter(
                "video_engine",
                "Video Generation Engine",
                "MAJD_VIDEO_ENGINE_COMMAND",
                timeout=1800,
            )
        )
        self.register(
            CommandAdapter(
                "animation_engine",
                "Animation Engine",
                "MAJD_ANIMATION_ENGINE_COMMAND",
                timeout=1800,
            )
        )
        self.register(
            CommandAdapter(
                "vfx_engine",
                "VFX Engine",
                "MAJD_VFX_ENGINE_COMMAND",
                timeout=1800,
            )
        )
        self.register(
            CommandAdapter(
                "voice_engine",
                "Voice / TTS Engine",
                "MAJD_VOICE_ENGINE_COMMAND",
                timeout=900,
            )
        )
        self.register(
            CommandAdapter(
                "music_engine",
                "Music Generation Engine",
                "MAJD_MUSIC_ENGINE_COMMAND",
                timeout=1200,
            )
        )
        self.register(
            CommandAdapter(
                "subtitle_engine",
                "Speech Recognition / Subtitle Engine",
                "MAJD_SUBTITLE_ENGINE_COMMAND",
                timeout=1200,
            )
        )
        self.register(
            CommandAdapter(
                "translation_engine",
                "Translation Engine",
                "MAJD_TRANSLATION_ENGINE_COMMAND",
                timeout=900,
            )
        )
        self.register(
            CommandAdapter(
                "dubbing_engine",
                "Dubbing Engine",
                "MAJD_DUBBING_ENGINE_COMMAND",
                timeout=1800,
            )
        )
        self.register(
            CommandAdapter(
                "live_engine",
                "Live Streaming Engine",
                "MAJD_LIVE_ENGINE_COMMAND",
                timeout=600,
            )
        )
        self.register(
            CommandAdapter(
                "publisher",
                "Publishing Engine",
                "MAJD_PUBLISHER_COMMAND",
                timeout=600,
            )
        )
        self.register(
            CommandAdapter(
                "social_engine",
                "Social Content Engine",
                "MAJD_SOCIAL_ENGINE_COMMAND",
                timeout=600,
            )
        )
        self.register(
            CommandAdapter(
                "game_media_engine",
                "Game Media Engine",
                "MAJD_GAME_MEDIA_ENGINE_COMMAND",
                timeout=900,
            )
        )
        self.register(
            CommandAdapter(
                "storage_engine",
                "External Storage Engine",
                "MAJD_STORAGE_ENGINE_COMMAND",
                timeout=600,
            )
        )

    def register(self, adapter: BaseAdapter) -> None:
        self.adapters[adapter.key] = adapter

    def get(self, key: str) -> BaseAdapter:
        if key not in self.adapters:
            raise KeyError(f"Unknown adapter: {key}")
        return self.adapters[key]

    def health_report(self) -> Dict[str, Capability]:
        return {key: adapter.health() for key, adapter in self.adapters.items()}


# ============================================================
# ASSET MANAGEMENT
# ============================================================

class AssetManager:
    def __init__(self, db: FactoryDatabase) -> None:
        self.db = db

    def register(
        self,
        path: Path,
        asset_type: AssetType | str,
        title: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AssetRecord:
        path = path.resolve()
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(str(path))

        mime, _ = mimetypes.guess_type(str(path))
        record = AssetRecord(
            asset_id=unique_id("asset"),
            asset_type=asset_type.value if isinstance(asset_type, AssetType) else str(asset_type),
            title=title,
            path=str(path),
            created_at=utc_now(),
            sha256=sha256_file(path),
            mime_type=mime,
            size_bytes=path.stat().st_size,
            metadata=metadata or {},
        )
        self.db.save_asset(record)
        self.db.emit("asset.registered", asdict(record))
        return record

    def create_text_asset(
        self,
        asset_type: AssetType | str,
        title: str,
        content: str,
        *,
        suffix: str = ".txt",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AssetRecord:
        asset_id = unique_id("asset")
        folder = ASSETS_DIR / safe_slug(
            asset_type.value if isinstance(asset_type, AssetType) else str(asset_type)
        )
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"{asset_id}{suffix}"
        atomic_write_text(path, content)

        record = AssetRecord(
            asset_id=asset_id,
            asset_type=asset_type.value if isinstance(asset_type, AssetType) else str(asset_type),
            title=title,
            path=str(path.resolve()),
            created_at=utc_now(),
            sha256=sha256_file(path),
            mime_type=mimetypes.guess_type(str(path))[0],
            size_bytes=path.stat().st_size,
            metadata=metadata or {},
        )
        self.db.save_asset(record)
        self.db.emit("asset.created", asdict(record))
        return record

    def update_flags(
        self,
        asset: AssetRecord,
        *,
        published: Optional[bool] = None,
        live: Optional[bool] = None,
    ) -> AssetRecord:
        if published is not None:
            asset.published = bool(published)
        if live is not None:
            asset.live = bool(live)
        self.db.save_asset(asset)
        return asset


# ============================================================
# QUALITY ASSURANCE
# ============================================================

class QualityAssurance:
    def __init__(
        self,
        db: FactoryDatabase,
        registry: AdapterRegistry,
    ) -> None:
        self.db = db
        self.registry = registry

    def validate_asset(self, asset: AssetRecord) -> QAResult:
        checks: List[Dict[str, Any]] = []
        errors: List[str] = []
        warnings: List[str] = []

        path = Path(asset.path)

        exists = path.exists() and path.is_file()
        checks.append({"check": "file_exists", "ok": exists})
        if not exists:
            errors.append("asset_file_missing")

        if exists:
            size = path.stat().st_size
            non_empty = size > 0
            checks.append(
                {"check": "file_non_empty", "ok": non_empty, "size_bytes": size}
            )
            if not non_empty:
                errors.append("asset_file_empty")

            current_hash = sha256_file(path)
            hash_ok = not asset.sha256 or current_hash == asset.sha256
            checks.append(
                {
                    "check": "sha256_integrity",
                    "ok": hash_ok,
                    "current_sha256": current_hash,
                }
            )
            if not hash_ok:
                errors.append("asset_hash_mismatch")

            suffix = path.suffix.lower()
            media_like = suffix in {
                ".mp4", ".mov", ".mkv", ".webm", ".mp3", ".wav",
                ".m4a", ".aac", ".flac", ".ogg"
            }

            if media_like:
                ffmpeg = self.registry.get("ffmpeg")
                health = ffmpeg.health()
                checks.append(
                    {
                        "check": "ffprobe_capability",
                        "ok": health.real and bool(health.details.get("ffprobe")),
                        "state": health.state.value,
                    }
                )
                if isinstance(ffmpeg, FFmpegAdapter) and ffmpeg.ffprobe_available():
                    try:
                        probe = ffmpeg.probe(path)
                        streams = probe.get("streams", [])
                        has_streams = isinstance(streams, list) and len(streams) > 0
                        checks.append(
                            {
                                "check": "media_streams_detected",
                                "ok": has_streams,
                                "stream_count": len(streams) if isinstance(streams, list) else 0,
                            }
                        )
                        if not has_streams:
                            errors.append("media_has_no_streams")
                    except Exception as exc:
                        checks.append(
                            {
                                "check": "media_probe",
                                "ok": False,
                                "error": str(exc),
                            }
                        )
                        errors.append("media_probe_failed")
                else:
                    warnings.append("ffprobe_not_available_media_not_deep_validated")

        passed = sum(1 for item in checks if item.get("ok"))
        score = (passed / len(checks) * 100.0) if checks else 0.0
        ok = not errors and score >= 60.0

        result = QAResult(
            ok=ok,
            checks=checks,
            score=round(score, 2),
            errors=errors,
            warnings=warnings,
        )
        self.db.emit(
            "qa.asset",
            {"asset_id": asset.asset_id, "result": asdict(result)},
        )
        self.db.metric(
            "qa.score",
            result.score,
            {"asset_type": asset.asset_type},
        )
        return result


# ============================================================
# AUTOMATIC REPAIR
# ============================================================

class AutomaticRepair:
    def __init__(
        self,
        db: FactoryDatabase,
        registry: AdapterRegistry,
        assets: AssetManager,
    ) -> None:
        self.db = db
        self.registry = registry
        self.assets = assets

    def repair_asset(
        self,
        asset: AssetRecord,
        qa: QAResult,
    ) -> Dict[str, Any]:
        """
        Conservative repair only.
        It never fabricates a successful repair.
        """
        path = Path(asset.path)
        actions: List[Dict[str, Any]] = []

        if not path.exists():
            return {
                "success": False,
                "repaired": False,
                "reason": "missing_source_cannot_be_repaired",
                "actions": actions,
            }

        if "asset_hash_mismatch" in qa.errors:
            old = asset.sha256
            asset.sha256 = sha256_file(path)
            asset.size_bytes = path.stat().st_size
            self.db.save_asset(asset)
            actions.append(
                {
                    "action": "refresh_integrity_metadata",
                    "old_sha256": old,
                    "new_sha256": asset.sha256,
                }
            )

        media_errors = {
            "media_probe_failed",
            "media_has_no_streams",
        }
        if media_errors.intersection(qa.errors):
            ffmpeg = self.registry.get("ffmpeg")
            if isinstance(ffmpeg, FFmpegAdapter) and ffmpeg.ffmpeg_available():
                repaired = TMP_DIR / f"{asset.asset_id}-repair.mp4"
                try:
                    ffmpeg.transcode(path, repaired, overwrite=True)
                    if repaired.exists() and repaired.stat().st_size > 0:
                        backup = path.with_suffix(path.suffix + ".broken")
                        if not backup.exists():
                            shutil.copy2(path, backup)
                        shutil.move(str(repaired), str(path))
                        asset.sha256 = sha256_file(path)
                        asset.size_bytes = path.stat().st_size
                        asset.mime_type = mimetypes.guess_type(str(path))[0]
                        self.db.save_asset(asset)
                        actions.append(
                            {
                                "action": "ffmpeg_transcode_repair",
                                "backup": str(backup),
                            }
                        )
                except Exception as exc:
                    actions.append(
                        {
                            "action": "ffmpeg_transcode_repair",
                            "success": False,
                            "error": str(exc),
                        }
                    )

        success = any(
            action.get("success", True) is not False for action in actions
        )
        result = {
            "success": success,
            "repaired": success,
            "asset_id": asset.asset_id,
            "actions": actions,
        }
        self.db.emit("repair.asset", result)
        return result


# ============================================================
# PUBLISHING
# ============================================================

class Publisher:
    def __init__(
        self,
        db: FactoryDatabase,
        registry: AdapterRegistry,
        assets: AssetManager,
        qa: QualityAssurance,
    ) -> None:
        self.db = db
        self.registry = registry
        self.assets = assets
        self.qa = qa

    def publish_local(
        self,
        asset: AssetRecord,
        *,
        target_name: Optional[str] = None,
    ) -> PublishResult:
        qa_result = self.qa.validate_asset(asset)
        if not qa_result.ok:
            return PublishResult(
                success=False,
                published=False,
                live=False,
                target=None,
                message="QA_FAILED",
            )

        source = Path(asset.path)
        if not source.exists():
            return PublishResult(
                success=False,
                published=False,
                live=False,
                target=None,
                message="SOURCE_MISSING",
            )

        folder = PUBLISH_DIR / safe_slug(asset.asset_type)
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / (
            target_name
            or f"{safe_slug(asset.title, asset.asset_id)}-{asset.asset_id}{source.suffix}"
        )
        shutil.copy2(source, target)

        if not target.exists() or target.stat().st_size <= 0:
            return PublishResult(
                success=False,
                published=False,
                live=False,
                target=str(target),
                message="COPY_FAILED",
            )

        asset.published = True
        asset.live = False
        self.db.save_asset(asset)
        self.db.emit(
            "publish.local",
            {
                "asset_id": asset.asset_id,
                "target": str(target),
                "published": True,
                "live": False,
            },
        )
        return PublishResult(
            success=True,
            published=True,
            live=False,
            target=str(target),
            message="PUBLISHED_TO_LOCAL_FACTORY_STORAGE",
            artifact=str(target),
        )

    def publish_external(
        self,
        asset: AssetRecord,
        destination: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> PublishResult:
        qa_result = self.qa.validate_asset(asset)
        if not qa_result.ok:
            return PublishResult(
                success=False,
                published=False,
                live=False,
                target=destination,
                message="QA_FAILED",
            )

        adapter = self.registry.get("publisher")
        health = adapter.health()
        if not health.real:
            return PublishResult(
                success=False,
                published=False,
                live=False,
                target=destination,
                message=f"PUBLISHER_UNAVAILABLE:{health.reason}",
            )

        response = adapter.execute(
            "publish",
            {
                "asset": asdict(asset),
                "destination": destination,
                "options": options or {},
            },
        )

        confirmed = bool(
            response.get("success")
            and response.get("published")
        )
        live = bool(response.get("live")) if confirmed else False

        if confirmed:
            asset.published = True
            asset.live = live
            self.db.save_asset(asset)

        result = PublishResult(
            success=confirmed,
            published=confirmed,
            live=live,
            target=destination,
            message=str(response.get("message", "publisher_response")),
            artifact=response.get("artifact"),
        )
        self.db.emit(
            "publish.external",
            {"asset_id": asset.asset_id, "result": asdict(result)},
        )
        return result


# ============================================================
# LIVE STREAMING
# ============================================================

class LiveStreamingManager:
    def __init__(
        self,
        db: FactoryDatabase,
        registry: AdapterRegistry,
    ) -> None:
        self.db = db
        self.registry = registry

    def start(
        self,
        title: str,
        source: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        adapter = self.registry.get("live_engine")
        health = adapter.health()

        if not health.real:
            result = {
                "success": False,
                "live": False,
                "status": "LIVE_ENGINE_UNAVAILABLE",
                "reason": health.reason,
            }
            self.db.emit("live.start.blocked", result)
            return result

        response = adapter.execute(
            "start",
            {
                "title": title,
                "source": source,
                "options": options or {},
            },
        )

        confirmed = bool(response.get("success") and response.get("live"))
        result = {
            "success": confirmed,
            "live": confirmed,
            "status": "LIVE" if confirmed else "LIVE_NOT_CONFIRMED",
            "response": response,
        }
        self.db.emit("live.start", result)
        return result

    def stop(self, stream_id: str) -> Dict[str, Any]:
        adapter = self.registry.get("live_engine")
        health = adapter.health()
        if not health.real:
            return {
                "success": False,
                "live": False,
                "status": "LIVE_ENGINE_UNAVAILABLE",
                "reason": health.reason,
            }
        response = adapter.execute("stop", {"stream_id": stream_id})
        stopped = bool(response.get("success"))
        result = {
            "success": stopped,
            "live": False if stopped else bool(response.get("live")),
            "response": response,
        }
        self.db.emit("live.stop", result)
        return result


# ============================================================
# CONTENT GENERATION ROUTER
# ============================================================

class ContentGenerator:
    ENGINE_BY_TYPE = {
        AssetType.IMAGE.value: "image_engine",
        AssetType.POSTER.value: "image_engine",
        AssetType.THUMBNAIL.value: "image_engine",
        AssetType.VIDEO.value: "video_engine",
        AssetType.SHORT.value: "video_engine",
        AssetType.MOVIE.value: "video_engine",
        AssetType.EPISODE.value: "video_engine",
        AssetType.ANIMATION.value: "animation_engine",
        AssetType.VFX.value: "vfx_engine",
        AssetType.VOICE.value: "voice_engine",
        AssetType.AUDIO.value: "voice_engine",
        AssetType.MUSIC.value: "music_engine",
        AssetType.SUBTITLE.value: "subtitle_engine",
        AssetType.DUB.value: "dubbing_engine",
        AssetType.SOCIAL_POST.value: "social_engine",
        AssetType.STORY.value: "social_engine",
        AssetType.GAME_MEDIA.value: "game_media_engine",
    }

    def __init__(
        self,
        db: FactoryDatabase,
        registry: AdapterRegistry,
        assets: AssetManager,
    ) -> None:
        self.db = db
        self.registry = registry
        self.assets = assets

    def generate(
        self,
        asset_type: str,
        title: str,
        prompt: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        asset_type = str(asset_type).strip().lower()
        engine_key = self.ENGINE_BY_TYPE.get(asset_type)

        if not engine_key:
            return {
                "success": False,
                "generated": False,
                "reason": f"no_generation_engine_mapping_for:{asset_type}",
            }

        adapter = self.registry.get(engine_key)
        health = adapter.health()
        if not health.real:
            return {
                "success": False,
                "generated": False,
                "engine": engine_key,
                "reason": health.reason or "engine_unavailable",
            }

        response = adapter.execute(
            "generate",
            {
                "asset_type": asset_type,
                "title": title,
                "prompt": prompt,
                "options": options or {},
            },
        )

        output_path = response.get("output_path") or response.get("path")
        if not response.get("success") or not output_path:
            return {
                "success": False,
                "generated": False,
                "engine": engine_key,
                "response": response,
            }

        path = Path(str(output_path)).expanduser()
        if not path.is_absolute():
            path = ROOT_DIR / path

        if not path.exists() or not path.is_file() or path.stat().st_size <= 0:
            return {
                "success": False,
                "generated": False,
                "engine": engine_key,
                "reason": "engine_reported_output_but_file_not_found",
                "response": response,
            }

        asset = self.assets.register(
            path,
            asset_type,
            title,
            metadata={
                "prompt": prompt,
                "engine": engine_key,
                "engine_response": response,
            },
        )

        return {
            "success": True,
            "generated": True,
            "engine": engine_key,
            "asset": asdict(asset),
        }


# ============================================================
# MOVIES / SERIES / EPISODES / CHANNELS / EVENTS
# ============================================================

class StructuredContentManager:
    def __init__(
        self,
        db: FactoryDatabase,
        assets: AssetManager,
    ) -> None:
        self.db = db
        self.assets = assets

    def create_manifest(
        self,
        kind: str,
        title: str,
        data: Dict[str, Any],
    ) -> AssetRecord:
        payload = {
            "schema_version": SCHEMA_VERSION,
            "kind": kind,
            "title": title,
            "created_at": utc_now(),
            "data": data,
        }
        return self.assets.create_text_asset(
            kind,
            title,
            json.dumps(payload, ensure_ascii=False, indent=2),
            suffix=".json",
            metadata={"structured_manifest": True, "kind": kind},
        )

    def create_series(
        self,
        title: str,
        description: str,
        seasons: Optional[List[Dict[str, Any]]] = None,
    ) -> AssetRecord:
        return self.create_manifest(
            AssetType.SERIES.value,
            title,
            {
                "description": description,
                "seasons": seasons or [],
                "status": "DRAFT",
            },
        )

    def create_episode(
        self,
        title: str,
        series_id: str,
        season: int,
        episode: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AssetRecord:
        return self.create_manifest(
            AssetType.EPISODE.value,
            title,
            {
                "series_id": series_id,
                "season": int(season),
                "episode": int(episode),
                "metadata": metadata or {},
                "status": "DRAFT",
            },
        )

    def create_channel(
        self,
        title: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AssetRecord:
        return self.create_manifest(
            AssetType.CHANNEL.value,
            title,
            {
                "description": description,
                "metadata": metadata or {},
                "status": "CONFIGURED_NOT_LIVE",
            },
        )

    def create_event(
        self,
        title: str,
        starts_at: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AssetRecord:
        return self.create_manifest(
            AssetType.EVENT.value,
            title,
            {
                "starts_at": starts_at,
                "metadata": metadata or {},
                "status": "SCHEDULED",
            },
        )


# ============================================================
# SUBTITLES / TRANSLATION / DUBBING
# ============================================================

class LanguagePipeline:
    def __init__(
        self,
        db: FactoryDatabase,
        registry: AdapterRegistry,
        assets: AssetManager,
    ) -> None:
        self.db = db
        self.registry = registry
        self.assets = assets

    def subtitles(
        self,
        media_path: Path,
        language: str = "ar",
    ) -> Dict[str, Any]:
        adapter = self.registry.get("subtitle_engine")
        health = adapter.health()
        if not health.real:
            return {
                "success": False,
                "generated": False,
                "reason": health.reason,
            }

        response = adapter.execute(
            "transcribe",
            {
                "media_path": str(media_path),
                "language": language,
            },
        )
        return self._register_external_text_output(
            response,
            AssetType.SUBTITLE,
            f"Subtitles {media_path.name}",
        )

    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> Dict[str, Any]:
        adapter = self.registry.get("translation_engine")
        health = adapter.health()
        if not health.real:
            return {
                "success": False,
                "translated": False,
                "reason": health.reason,
            }
        response = adapter.execute(
            "translate",
            {
                "text": text,
                "source_language": source_language,
                "target_language": target_language,
            },
        )
        translated = response.get("text") or response.get("translation")
        return {
            "success": bool(response.get("success") and isinstance(translated, str)),
            "translated": bool(response.get("success") and isinstance(translated, str)),
            "text": translated,
            "response": response,
        }

    def dub(
        self,
        media_path: Path,
        target_language: str,
        voice: Optional[str] = None,
    ) -> Dict[str, Any]:
        adapter = self.registry.get("dubbing_engine")
        health = adapter.health()
        if not health.real:
            return {
                "success": False,
                "generated": False,
                "reason": health.reason,
            }

        response = adapter.execute(
            "dub",
            {
                "media_path": str(media_path),
                "target_language": target_language,
                "voice": voice,
            },
        )
        return self._register_external_file_output(
            response,
            AssetType.DUB,
            f"Dub {media_path.name} ({target_language})",
        )

    def _register_external_text_output(
        self,
        response: Dict[str, Any],
        asset_type: AssetType,
        title: str,
    ) -> Dict[str, Any]:
        if not response.get("success"):
            return {
                "success": False,
                "generated": False,
                "response": response,
            }

        output_path = response.get("output_path") or response.get("path")
        if output_path:
            return self._register_external_file_output(
                response,
                asset_type,
                title,
            )

        text = response.get("text")
        if not isinstance(text, str) or not text.strip():
            return {
                "success": False,
                "generated": False,
                "reason": "engine_returned_no_text",
                "response": response,
            }

        suffix = ".srt" if asset_type == AssetType.SUBTITLE else ".txt"
        asset = self.assets.create_text_asset(
            asset_type,
            title,
            text,
            suffix=suffix,
            metadata={"engine_response": response},
        )
        return {
            "success": True,
            "generated": True,
            "asset": asdict(asset),
        }

    def _register_external_file_output(
        self,
        response: Dict[str, Any],
        asset_type: AssetType,
        title: str,
    ) -> Dict[str, Any]:
        output_path = response.get("output_path") or response.get("path")
        if not response.get("success") or not output_path:
            return {
                "success": False,
                "generated": False,
                "response": response,
            }

        path = Path(str(output_path)).expanduser()
        if not path.is_absolute():
            path = ROOT_DIR / path

        if not path.exists() or path.stat().st_size <= 0:
            return {
                "success": False,
                "generated": False,
                "reason": "engine_output_missing",
                "response": response,
            }

        asset = self.assets.register(
            path,
            asset_type,
            title,
            metadata={"engine_response": response},
        )
        return {
            "success": True,
            "generated": True,
            "asset": asdict(asset),
        }


# ============================================================
# ANALYTICS
# ============================================================

class AnalyticsManager:
    def __init__(self, db: FactoryDatabase) -> None:
        self.db = db

    def track(
        self,
        metric: str,
        value: float = 1.0,
        labels: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.db.metric(metric, value, labels)

    def summary(self) -> Dict[str, Any]:
        with self.db.connect() as db:
            jobs = db.execute(
                "SELECT state, COUNT(*) AS c FROM jobs GROUP BY state"
            ).fetchall()
            assets = db.execute(
                "SELECT asset_type, COUNT(*) AS c FROM assets GROUP BY asset_type"
            ).fetchall()
            events = db.execute(
                "SELECT COUNT(*) AS c FROM events"
            ).fetchone()
            schedules = db.execute(
                "SELECT state, COUNT(*) AS c FROM schedules GROUP BY state"
            ).fetchall()

        return {
            "jobs": {row["state"]: row["c"] for row in jobs},
            "assets": {row["asset_type"]: row["c"] for row in assets},
            "events": int(events["c"]) if events else 0,
            "schedules": {row["state"]: row["c"] for row in schedules},
            "generated_at": utc_now(),
        }


# ============================================================
# SCHEDULING
# ============================================================

class Scheduler:
    def __init__(self, db: FactoryDatabase) -> None:
        self.db = db

    def schedule(
        self,
        operation: str,
        run_at: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        try:
            parsed = datetime.fromisoformat(run_at.replace("Z", "+00:00"))
        except ValueError as exc:
            return {
                "success": False,
                "scheduled": False,
                "reason": f"invalid_iso_datetime:{exc}",
            }

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        schedule_id = self.db.create_schedule(
            operation,
            parsed.astimezone(timezone.utc).isoformat(),
            payload,
        )
        result = {
            "success": True,
            "scheduled": True,
            "schedule_id": schedule_id,
            "operation": operation,
            "run_at": parsed.astimezone(timezone.utc).isoformat(),
        }
        self.db.emit("schedule.created", result)
        return result


# ============================================================
# CAPABILITY REPORT
# ============================================================

class CapabilityReporter:
    def __init__(
        self,
        db: FactoryDatabase,
        registry: AdapterRegistry,
    ) -> None:
        self.db = db
        self.registry = registry

    def build(self) -> Dict[str, Any]:
        external = self.registry.health_report()

        built_in = {
            "local_storage": Capability(
                key="local_storage",
                label="Local Asset / Manifest Storage",
                state=CapabilityState.AVAILABLE,
                real=True,
                engine="python-filesystem",
            ),
            "sqlite": Capability(
                key="sqlite",
                label="SQLite Job / Asset / Analytics Store",
                state=CapabilityState.AVAILABLE,
                real=True,
                engine=sqlite3.sqlite_version,
            ),
            "qa": Capability(
                key="qa",
                label="Quality Assurance",
                state=CapabilityState.AVAILABLE,
                real=True,
                engine="majd-internal",
            ),
            "repair": Capability(
                key="repair",
                label="Automatic Repair Orchestration",
                state=CapabilityState.AVAILABLE,
                real=True,
                engine="majd-internal",
                details={
                    "note": "media repair requires FFmpeg for transcode operations"
                },
            ),
            "scheduling": Capability(
                key="scheduling",
                label="Scheduling Metadata",
                state=CapabilityState.AVAILABLE,
                real=True,
                engine="majd-internal",
                details={
                    "note": "persistent schedule records only; external clock/worker must trigger due jobs"
                },
            ),
            "analytics": Capability(
                key="analytics",
                label="Internal Analytics",
                state=CapabilityState.AVAILABLE,
                real=True,
                engine="sqlite",
            ),
        }

        capabilities = {**built_in, **external}
        report = {
            "factory": {
                "id": FACTORY_ID,
                "name": FACTORY_NAME,
                "version": VERSION,
                "generated_at": utc_now(),
            },
            "capabilities": {
                key: {
                    **asdict(value),
                    "state": value.state.value,
                }
                for key, value in capabilities.items()
            },
            "summary": {
                "total": len(capabilities),
                "real_available": sum(
                    1
                    for value in capabilities.values()
                    if value.real and value.state == CapabilityState.AVAILABLE
                ),
                "unavailable": sum(
                    1
                    for value in capabilities.values()
                    if value.state == CapabilityState.UNAVAILABLE
                ),
                "degraded": sum(
                    1
                    for value in capabilities.values()
                    if value.state == CapabilityState.DEGRADED
                ),
            },
        }
        atomic_write_json(CAPABILITY_FILE, report)
        self.db.emit("capability.report", report["summary"])
        return report


# ============================================================
# AI ORCHESTRATION
# ============================================================

class AIOrchestratorBridge:
    def __init__(
        self,
        db: FactoryDatabase,
        registry: AdapterRegistry,
    ) -> None:
        self.db = db
        self.registry = registry

    def available(self) -> bool:
        return self.registry.get("ai_orchestrator").health().real

    def plan(
        self,
        objective: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        adapter = self.registry.get("ai_orchestrator")
        health = adapter.health()
        if not health.real:
            result = {
                "success": False,
                "planned": False,
                "reason": health.reason,
            }
            self.db.emit("ai.plan.blocked", result)
            return result

        response = adapter.execute(
            "plan",
            {
                "objective": objective,
                "context": context or {},
                "factory": {
                    "id": FACTORY_ID,
                    "version": VERSION,
                },
            },
        )
        confirmed = bool(response.get("success"))
        result = {
            "success": confirmed,
            "planned": confirmed,
            "response": response,
        }
        self.db.emit("ai.plan", result)
        return result

    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        adapter = self.registry.get("ai_orchestrator")
        health = adapter.health()
        if not health.real:
            return {
                "success": False,
                "executed": False,
                "reason": health.reason,
            }

        response = adapter.execute(
            "execute_plan",
            {"plan": plan},
        )
        confirmed = bool(response.get("success"))
        result = {
            "success": confirmed,
            "executed": confirmed,
            "response": response,
        }
        self.db.emit("ai.execute_plan", result)
        return result


# ============================================================
# JOB ENGINE
# ============================================================

class JobEngine:
    def __init__(self, db: FactoryDatabase) -> None:
        self.db = db

    def create(
        self,
        operation: str,
        request: Dict[str, Any],
        max_attempts: int = 1,
    ) -> JobRecord:
        now = utc_now()
        job = JobRecord(
            job_id=unique_id("job"),
            operation=operation,
            state=JobState.CREATED.value,
            created_at=now,
            updated_at=now,
            request=request,
            result={},
            attempts=0,
            max_attempts=max(1, int(max_attempts)),
        )
        self.db.save_job(job)
        self.db.emit("job.created", asdict(job))
        return job

    def run(
        self,
        job: JobRecord,
        function: Callable[[], Dict[str, Any]],
    ) -> JobRecord:
        while job.attempts < job.max_attempts:
            job.attempts += 1
            job.state = JobState.RUNNING.value
            job.updated_at = utc_now()
            job.error = None
            self.db.save_job(job)

            try:
                result = function()
                if not isinstance(result, dict):
                    raise TypeError("job function must return dict")

                job.result = result
                if result.get("success") is False:
                    raise RuntimeError(
                        str(result.get("reason") or result.get("message") or "operation_failed")
                    )

                job.state = JobState.SUCCEEDED.value
                job.updated_at = utc_now()
                self.db.save_job(job)
                self.db.emit("job.succeeded", asdict(job))
                return job
            except Exception as exc:
                job.error = f"{type(exc).__name__}: {exc}"
                job.updated_at = utc_now()
                LOGGER.error(
                    "Job %s attempt %s/%s failed: %s",
                    job.job_id,
                    job.attempts,
                    job.max_attempts,
                    job.error,
                )
                if job.attempts >= job.max_attempts:
                    job.state = JobState.FAILED.value
                    job.result = {
                        "success": False,
                        "error": job.error,
                    }
                    self.db.save_job(job)
                    self.db.emit("job.failed", asdict(job))
                    return job
                time.sleep(min(2 ** (job.attempts - 1), 5))

        return job


# ============================================================
# MAIN FACTORY FACADE
# ============================================================

class MajdAIContentMediaFactory:
    def __init__(self) -> None:
        ensure_dirs()
        self.db = FactoryDatabase()
        self.registry = AdapterRegistry()
        self.assets = AssetManager(self.db)
        self.qa = QualityAssurance(self.db, self.registry)
        self.repair = AutomaticRepair(
            self.db,
            self.registry,
            self.assets,
        )
        self.publisher = Publisher(
            self.db,
            self.registry,
            self.assets,
            self.qa,
        )
        self.live = LiveStreamingManager(
            self.db,
            self.registry,
        )
        self.generator = ContentGenerator(
            self.db,
            self.registry,
            self.assets,
        )
        self.structured = StructuredContentManager(
            self.db,
            self.assets,
        )
        self.language = LanguagePipeline(
            self.db,
            self.registry,
            self.assets,
        )
        self.analytics = AnalyticsManager(self.db)
        self.scheduler = Scheduler(self.db)
        self.capabilities = CapabilityReporter(
            self.db,
            self.registry,
        )
        self.ai = AIOrchestratorBridge(
            self.db,
            self.registry,
        )
        self.jobs = JobEngine(self.db)

    def health(self) -> Dict[str, Any]:
        report = self.capabilities.build()
        return {
            "success": True,
            "factory": FACTORY_ID,
            "version": VERSION,
            "status": "READY",
            "generated_at": utc_now(),
            "capability_summary": report["summary"],
            "paths": {
                "root": str(FACTORY_ROOT),
                "database": str(DB_FILE),
                "capability_report": str(CAPABILITY_FILE),
            },
        }

    def generate(
        self,
        asset_type: str,
        title: str,
        prompt: str,
        options: Optional[Dict[str, Any]] = None,
        *,
        max_attempts: int = 1,
    ) -> Dict[str, Any]:
        job = self.jobs.create(
            "generate",
            {
                "asset_type": asset_type,
                "title": title,
                "prompt": prompt,
                "options": options or {},
            },
            max_attempts=max_attempts,
        )
        completed = self.jobs.run(
            job,
            lambda: self.generator.generate(
                asset_type,
                title,
                prompt,
                options,
            ),
        )
        return asdict(completed)

    def qa_asset(self, asset_id: str) -> Dict[str, Any]:
        asset = self.db.get_asset(asset_id)
        if not asset:
            return {
                "success": False,
                "reason": "asset_not_found",
                "asset_id": asset_id,
            }
        result = self.qa.validate_asset(asset)
        return {
            "success": result.ok,
            "asset_id": asset_id,
            "qa": asdict(result),
        }

    def repair_asset(self, asset_id: str) -> Dict[str, Any]:
        asset = self.db.get_asset(asset_id)
        if not asset:
            return {
                "success": False,
                "reason": "asset_not_found",
                "asset_id": asset_id,
            }
        qa_result = self.qa.validate_asset(asset)
        repair_result = self.repair.repair_asset(asset, qa_result)
        post_qa = self.qa.validate_asset(asset)
        return {
            "success": repair_result.get("success", False) and post_qa.ok,
            "asset_id": asset_id,
            "repair": repair_result,
            "post_qa": asdict(post_qa),
        }

    def publish_asset(
        self,
        asset_id: str,
        *,
        destination: Optional[str] = None,
    ) -> Dict[str, Any]:
        asset = self.db.get_asset(asset_id)
        if not asset:
            return {
                "success": False,
                "published": False,
                "live": False,
                "reason": "asset_not_found",
            }

        if destination:
            result = self.publisher.publish_external(
                asset,
                destination,
            )
        else:
            result = self.publisher.publish_local(asset)

        return asdict(result)

    def create_social_post(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not text.strip():
            return {
                "success": False,
                "reason": "empty_text",
            }

        asset = self.assets.create_text_asset(
            AssetType.SOCIAL_POST,
            title=(text.strip()[:60] or "Social Post"),
            content=text.strip(),
            suffix=".txt",
            metadata={
                "status": "DRAFT",
                **(metadata or {}),
            },
        )
        return {
            "success": True,
            "created": True,
            "published": False,
            "live": False,
            "asset": asdict(asset),
        }

    def create_story(
        self,
        title: str,
        content: str,
    ) -> Dict[str, Any]:
        asset = self.assets.create_text_asset(
            AssetType.STORY,
            title=title,
            content=content,
            suffix=".txt",
            metadata={"status": "DRAFT"},
        )
        return {
            "success": True,
            "created": True,
            "published": False,
            "live": False,
            "asset": asdict(asset),
        }

    def register_existing_asset(
        self,
        path: str,
        asset_type: str,
        title: str,
    ) -> Dict[str, Any]:
        asset = self.assets.register(
            Path(path),
            asset_type,
            title,
        )
        return {
            "success": True,
            "asset": asdict(asset),
        }

    def transcode(
        self,
        asset_id: str,
        output_suffix: str = ".mp4",
    ) -> Dict[str, Any]:
        asset = self.db.get_asset(asset_id)
        if not asset:
            return {
                "success": False,
                "reason": "asset_not_found",
            }

        ffmpeg = self.registry.get("ffmpeg")
        if not isinstance(ffmpeg, FFmpegAdapter) or not ffmpeg.ffmpeg_available():
            return {
                "success": False,
                "reason": "ffmpeg_unavailable",
            }

        source = Path(asset.path)
        target = ASSETS_DIR / "transcoded" / (
            f"{asset.asset_id}-transcoded{output_suffix}"
        )

        result = ffmpeg.transcode(
            source,
            target,
            overwrite=True,
        )
        if not result.get("success"):
            return result

        new_asset = self.assets.register(
            target,
            AssetType.VIDEO,
            f"{asset.title} (transcoded)",
            metadata={"source_asset_id": asset.asset_id},
        )
        return {
            "success": True,
            "asset": asdict(new_asset),
            "ffmpeg": result,
        }


# ============================================================
# SELF TEST
# ============================================================

def run_self_test() -> Dict[str, Any]:
    """
    Real local smoke test.

    It verifies:
    - directory creation
    - SQLite read/write
    - JSON write
    - asset creation
    - hashing
    - QA
    - local publishing
    - capability report generation

    It does NOT mark external engines as available unless their real
    health checks succeed.
    """
    factory = MajdAIContentMediaFactory()
    checks: List[Dict[str, Any]] = []

    try:
        checks.append(
            {
                "name": "factory_root_exists",
                "ok": FACTORY_ROOT.exists(),
            }
        )

        probe_asset = factory.assets.create_text_asset(
            AssetType.GENERIC,
            "MAJD Factory Self Test",
            "MAJD FACTORY SELF TEST\n" + utc_now(),
            suffix=".txt",
            metadata={"self_test": True},
        )
        checks.append(
            {
                "name": "asset_created",
                "ok": Path(probe_asset.path).exists()
                and Path(probe_asset.path).stat().st_size > 0,
            }
        )

        loaded = factory.db.get_asset(probe_asset.asset_id)
        checks.append(
            {
                "name": "asset_database_roundtrip",
                "ok": loaded is not None
                and loaded.asset_id == probe_asset.asset_id,
            }
        )

        qa = factory.qa.validate_asset(probe_asset)
        checks.append(
            {
                "name": "qa_passed",
                "ok": qa.ok,
                "score": qa.score,
            }
        )

        publish = factory.publisher.publish_local(
            probe_asset,
            target_name=f"{probe_asset.asset_id}.txt",
        )
        checks.append(
            {
                "name": "local_publish",
                "ok": publish.success
                and publish.published
                and not publish.live,
            }
        )

        report = factory.capabilities.build()
        checks.append(
            {
                "name": "capability_report",
                "ok": CAPABILITY_FILE.exists()
                and report.get("summary", {}).get("total", 0) > 0,
            }
        )

        factory.analytics.track(
            "self_test",
            1.0,
            {"version": VERSION},
        )
        checks.append(
            {
                "name": "analytics_write",
                "ok": True,
            }
        )
    except Exception as exc:
        checks.append(
            {
                "name": "unexpected_exception",
                "ok": False,
                "error": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc(),
            }
        )

    success = all(bool(item.get("ok")) for item in checks)
    result = {
        "success": success,
        "factory": FACTORY_ID,
        "version": VERSION,
        "checked_at": utc_now(),
        "checks": checks,
    }
    atomic_write_json(
        FACTORY_ROOT / "self-test-report.json",
        result,
    )
    return result


# ============================================================
# CLI
# ============================================================

def print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="MAJD-AI-CONTENT-MEDIA-FACTORY-08.py",
        description=FACTORY_NAME,
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )

    sub = parser.add_subparsers(dest="command")

    sub.add_parser(
        "health",
        help="Show factory health.",
    )
    sub.add_parser(
        "capabilities",
        help="Generate the real capability report.",
    )
    sub.add_parser(
        "self-test",
        help="Run the local real smoke test.",
    )
    sub.add_parser(
        "analytics",
        help="Show local analytics summary.",
    )
    sub.add_parser(
        "assets",
        help="List registered assets.",
    )

    p_register = sub.add_parser(
        "register",
        help="Register an existing real file as an asset.",
    )
    p_register.add_argument("path")
    p_register.add_argument("asset_type")
    p_register.add_argument("title")

    p_generate = sub.add_parser(
        "generate",
        help="Generate content using a configured real engine.",
    )
    p_generate.add_argument("asset_type")
    p_generate.add_argument("title")
    p_generate.add_argument("prompt")
    p_generate.add_argument(
        "--attempts",
        type=int,
        default=1,
    )

    p_qa = sub.add_parser(
        "qa",
        help="Run QA for an asset.",
    )
    p_qa.add_argument("asset_id")

    p_repair = sub.add_parser(
        "repair",
        help="Attempt conservative automatic repair.",
    )
    p_repair.add_argument("asset_id")

    p_publish = sub.add_parser(
        "publish",
        help="Publish an asset. Without destination, publishes only to local factory storage.",
    )
    p_publish.add_argument("asset_id")
    p_publish.add_argument(
        "--destination",
        default=None,
    )

    p_social = sub.add_parser(
        "social-post",
        help="Create a draft social post asset.",
    )
    p_social.add_argument("text")

    p_story = sub.add_parser(
        "story",
        help="Create a draft story asset.",
    )
    p_story.add_argument("title")
    p_story.add_argument("content")

    p_series = sub.add_parser(
        "series",
        help="Create a series manifest.",
    )
    p_series.add_argument("title")
    p_series.add_argument("description")

    p_episode = sub.add_parser(
        "episode",
        help="Create an episode manifest.",
    )
    p_episode.add_argument("title")
    p_episode.add_argument("series_id")
    p_episode.add_argument("season", type=int)
    p_episode.add_argument("episode", type=int)

    p_channel = sub.add_parser(
        "channel",
        help="Create a channel manifest; this does not make it LIVE.",
    )
    p_channel.add_argument("title")
    p_channel.add_argument("description")

    p_event = sub.add_parser(
        "event",
        help="Create an event manifest.",
    )
    p_event.add_argument("title")
    p_event.add_argument("starts_at")

    p_schedule = sub.add_parser(
        "schedule",
        help="Create a persistent schedule record.",
    )
    p_schedule.add_argument("operation")
    p_schedule.add_argument("run_at")
    p_schedule.add_argument(
        "payload_json",
        help="JSON object payload.",
    )

    p_live = sub.add_parser(
        "live-start",
        help="Start a real live stream only through a configured live engine.",
    )
    p_live.add_argument("title")
    p_live.add_argument("source")

    p_live_stop = sub.add_parser(
        "live-stop",
        help="Stop a real live stream through the configured live engine.",
    )
    p_live_stop.add_argument("stream_id")

    p_ai_plan = sub.add_parser(
        "ai-plan",
        help="Ask the configured MAJD AI orchestrator for a real plan.",
    )
    p_ai_plan.add_argument("objective")

    p_transcode = sub.add_parser(
        "transcode",
        help="Transcode a registered asset with FFmpeg.",
    )
    p_transcode.add_argument("asset_id")

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.verbose)

    factory = MajdAIContentMediaFactory()

    command = args.command or "health"

    try:
        if command == "health":
            result = factory.health()

        elif command == "capabilities":
            result = factory.capabilities.build()

        elif command == "self-test":
            result = run_self_test()

        elif command == "analytics":
            result = {
                "success": True,
                "analytics": factory.analytics.summary(),
            }

        elif command == "assets":
            result = {
                "success": True,
                "assets": [
                    asdict(asset)
                    for asset in factory.db.list_assets()
                ],
            }

        elif command == "register":
            result = factory.register_existing_asset(
                args.path,
                args.asset_type,
                args.title,
            )

        elif command == "generate":
            result = factory.generate(
                args.asset_type,
                args.title,
                args.prompt,
                max_attempts=args.attempts,
            )

        elif command == "qa":
            result = factory.qa_asset(args.asset_id)

        elif command == "repair":
            result = factory.repair_asset(args.asset_id)

        elif command == "publish":
            result = factory.publish_asset(
                args.asset_id,
                destination=args.destination,
            )

        elif command == "social-post":
            result = factory.create_social_post(args.text)

        elif command == "story":
            result = factory.create_story(
                args.title,
                args.content,
            )

        elif command == "series":
            asset = factory.structured.create_series(
                args.title,
                args.description,
            )
            result = {
                "success": True,
                "asset": asdict(asset),
            }

        elif command == "episode":
            asset = factory.structured.create_episode(
                args.title,
                args.series_id,
                args.season,
                args.episode,
            )
            result = {
                "success": True,
                "asset": asdict(asset),
            }

        elif command == "channel":
            asset = factory.structured.create_channel(
                args.title,
                args.description,
            )
            result = {
                "success": True,
                "live": False,
                "asset": asdict(asset),
            }

        elif command == "event":
            asset = factory.structured.create_event(
                args.title,
                args.starts_at,
            )
            result = {
                "success": True,
                "asset": asdict(asset),
            }

        elif command == "schedule":
            payload = json.loads(args.payload_json)
            if not isinstance(payload, dict):
                raise ValueError("payload_json must be a JSON object")
            result = factory.scheduler.schedule(
                args.operation,
                args.run_at,
                payload,
            )

        elif command == "live-start":
            result = factory.live.start(
                args.title,
                args.source,
            )

        elif command == "live-stop":
            result = factory.live.stop(args.stream_id)

        elif command == "ai-plan":
            result = factory.ai.plan(args.objective)

        elif command == "transcode":
            result = factory.transcode(args.asset_id)

        else:
            parser.error(f"Unknown command: {command}")
            return 2

        print_json(result)
        return 0 if result.get("success", False) else 1

    except KeyboardInterrupt:
        print_json(
            {
                "success": False,
                "error": "interrupted",
            }
        )
        return 130
    except Exception as exc:
        LOGGER.exception("Factory command failed")
        print_json(
            {
                "success": False,
                "error": f"{type(exc).__name__}: {exc}",
            }
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

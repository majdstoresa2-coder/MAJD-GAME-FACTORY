#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-AI-CONTENT-MEDIA-FACTORY-08.py
====================================
MAJD SOVEREIGN AI CONTENT + MEDIA FACTORY

Unified sovereign production system for:
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

IMPORTANT:
This module never reports generated/published/live content unless
a real execution adapter has actually completed the operation.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import uuid

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


# ============================================================
# IDENTITY
# ============================================================

SYSTEM_ID = "MAJD-AI-CONTENT-MEDIA-FACTORY-08"
SYSTEM_NAME = "MAJD Sovereign AI Content & Media Factory"
PLATFORM_NAME = "MAJD"
VERSION = "1.0.0"

ROOT_DIR = Path(__file__).resolve().parent

FACTORY_ROOT = ROOT_DIR / "majd-content-media-factory"
PROJECTS_DIR = FACTORY_ROOT / "projects"
ASSETS_DIR = FACTORY_ROOT / "assets"
MOVIES_DIR = FACTORY_ROOT / "movies"
SERIES_DIR = FACTORY_ROOT / "series"
EPISODES_DIR = FACTORY_ROOT / "episodes"
VIDEOS_DIR = FACTORY_ROOT / "videos"
SHORTS_DIR = FACTORY_ROOT / "shorts"
STORIES_DIR = FACTORY_ROOT / "stories"
IMAGES_DIR = FACTORY_ROOT / "images"
POSTERS_DIR = FACTORY_ROOT / "posters"
THUMBNAILS_DIR = FACTORY_ROOT / "thumbnails"
AUDIO_DIR = FACTORY_ROOT / "audio"
VOICE_DIR = FACTORY_ROOT / "voice"
MUSIC_DIR = FACTORY_ROOT / "music"
VFX_DIR = FACTORY_ROOT / "vfx"
SUBTITLES_DIR = FACTORY_ROOT / "subtitles"
DUBBING_DIR = FACTORY_ROOT / "dubbing"
LIVE_DIR = FACTORY_ROOT / "live"
CHANNELS_DIR = FACTORY_ROOT / "channels"
SOCIAL_DIR = FACTORY_ROOT / "social"
EVENTS_DIR = FACTORY_ROOT / "events"
PUBLISH_DIR = FACTORY_ROOT / "published"
TEMP_DIR = FACTORY_ROOT / "tmp"
LOGS_DIR = FACTORY_ROOT / "logs"
STATE_DIR = FACTORY_ROOT / "state"

REGISTRY_FILE = STATE_DIR / "registry.json"
JOBS_FILE = STATE_DIR / "jobs.json"
CAPABILITIES_FILE = STATE_DIR / "capabilities.json"
PUBLISHING_FILE = STATE_DIR / "publishing.json"


# ============================================================
# ENUMS
# ============================================================

class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    PLANNING = "PLANNING"
    GENERATING = "GENERATING"
    PROCESSING = "PROCESSING"
    TESTING = "TESTING"
    REPAIRING = "REPAIRING"
    READY = "READY"
    PUBLISHING = "PUBLISHING"
    PUBLISHED = "PUBLISHED"
    LIVE = "LIVE"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


class ContentType(str, Enum):
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
    DUBBING = "dubbing"
    LIVE = "live"
    CHANNEL = "channel"
    SOCIAL_POST = "social_post"
    EVENT = "event"
    GAME_MEDIA = "game_media"


# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class FactoryResult:
    success: bool
    status: str
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    generated_at: str = ""


@dataclass
class MediaJob:
    id: str
    content_type: str
    title: str
    description: str
    language: str
    status: str
    created_at: str
    updated_at: str
    owner: str = "SUPREME_OWNER"
    platform: str = PLATFORM_NAME
    request: Dict[str, Any] = field(default_factory=dict)
    plan: Dict[str, Any] = field(default_factory=dict)
    assets: List[Dict[str, Any]] = field(default_factory=list)
    outputs: List[Dict[str, Any]] = field(default_factory=list)
    tests: List[Dict[str, Any]] = field(default_factory=list)
    publication: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


@dataclass
class Adapter:
    name: str
    capability: str
    handler: Callable[[Dict[str, Any]], Dict[str, Any]]
    real: bool = True
    enabled: bool = True


# ============================================================
# UTILITIES
# ============================================================

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs() -> None:
    directories = [
        FACTORY_ROOT,
        PROJECTS_DIR,
        ASSETS_DIR,
        MOVIES_DIR,
        SERIES_DIR,
        EPISODES_DIR,
        VIDEOS_DIR,
        SHORTS_DIR,
        STORIES_DIR,
        IMAGES_DIR,
        POSTERS_DIR,
        THUMBNAILS_DIR,
        AUDIO_DIR,
        VOICE_DIR,
        MUSIC_DIR,
        VFX_DIR,
        SUBTITLES_DIR,
        DUBBING_DIR,
        LIVE_DIR,
        CHANNELS_DIR,
        SOCIAL_DIR,
        EVENTS_DIR,
        PUBLISH_DIR,
        TEMP_DIR,
        LOGS_DIR,
        STATE_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary = path.with_suffix(path.suffix + ".tmp")

    temporary.write_text(
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    temporary.replace(path)


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()


def safe_name(value: str) -> str:
    cleaned = "".join(
        character
        if character.isalnum() or character in "-_"
        else "-"
        for character in value.strip()
    )

    cleaned = cleaned.strip("-")

    return cleaned[:100] or "majd-content"


def command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def run_command(
    command: List[str],
    timeout: int = 3600,
) -> FactoryResult:

    try:
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            check=False,
        )

        return FactoryResult(
            success=process.returncode == 0,
            status="COMMAND_COMPLETED"
            if process.returncode == 0
            else "COMMAND_FAILED",
            data={
                "command": command,
                "returncode": process.returncode,
                "stdout": process.stdout[-10000:],
                "stderr": process.stderr[-10000:],
            },
            generated_at=utc_now(),
        )

    except Exception as exc:
        return FactoryResult(
            success=False,
            status="COMMAND_EXCEPTION",
            errors=[str(exc)],
            generated_at=utc_now(),
        )


# ============================================================
# MAIN FACTORY
# ============================================================

class MajdAIContentMediaFactory:

    def __init__(self) -> None:
        ensure_dirs()

        self.adapters: Dict[str, Adapter] = {}

        self.registry = read_json(
            REGISTRY_FILE,
            {
                "system": SYSTEM_ID,
                "version": VERSION,
                "created_at": utc_now(),
                "content": {},
            },
        )

        self.jobs = read_json(
            JOBS_FILE,
            {
                "system": SYSTEM_ID,
                "jobs": {},
            },
        )

        self._register_builtin_capabilities()
        self._persist_capabilities()

    # ========================================================
    # ADAPTER SYSTEM
    # ========================================================

    def register_adapter(
        self,
        capability: str,
        name: str,
        handler: Callable[[Dict[str, Any]], Dict[str, Any]],
        real: bool = True,
    ) -> None:

        self.adapters[capability] = Adapter(
            name=name,
            capability=capability,
            handler=handler,
            real=real,
            enabled=True,
        )

        self._persist_capabilities()

    def unregister_adapter(self, capability: str) -> None:
        self.adapters.pop(capability, None)
        self._persist_capabilities()

    def has_real_adapter(self, capability: str) -> bool:
        adapter = self.adapters.get(capability)

        return bool(
            adapter
            and adapter.enabled
            and adapter.real
        )

    def execute_adapter(
        self,
        capability: str,
        payload: Dict[str, Any],
    ) -> FactoryResult:

        adapter = self.adapters.get(capability)

        if not adapter or not adapter.enabled:
            return FactoryResult(
                success=False,
                status="CAPABILITY_NOT_CONNECTED",
                message=(
                    f"No real execution adapter connected "
                    f"for capability: {capability}"
                ),
                data={
                    "capability": capability,
                    "real_execution": False,
                },
                generated_at=utc_now(),
            )

        try:
            result = adapter.handler(payload)

            if not isinstance(result, dict):
                raise TypeError(
                    "Adapter must return a dictionary."
                )

            success = bool(result.get("success"))

            return FactoryResult(
                success=success,
                status=result.get(
                    "status",
                    "ADAPTER_SUCCESS"
                    if success
                    else "ADAPTER_FAILED",
                ),
                message=result.get("message", ""),
                data={
                    **result,
                    "adapter": adapter.name,
                    "capability": capability,
                    "real_execution": adapter.real,
                },
                errors=result.get("errors", []),
                warnings=result.get("warnings", []),
                generated_at=utc_now(),
            )

        except Exception as exc:
            return FactoryResult(
                success=False,
                status="ADAPTER_EXCEPTION",
                errors=[str(exc)],
                data={
                    "adapter": adapter.name,
                    "capability": capability,
                },
                generated_at=utc_now(),
            )

    # ========================================================
    # CAPABILITIES
    # ========================================================

    def _register_builtin_capabilities(self) -> None:

        self.capability_catalog = {
            "ai_planning": {
                "description": "AI production planning",
                "required": True,
            },
            "script_generation": {
                "description": "Scripts, stories and dialogue",
                "required": True,
            },
            "image_generation": {
                "description": "Image generation",
                "required": False,
            },
            "video_generation": {
                "description": "Video generation",
                "required": False,
            },
            "animation_generation": {
                "description": "Animation generation",
                "required": False,
            },
            "vfx_generation": {
                "description": "Visual effects",
                "required": False,
            },
            "voice_generation": {
                "description": "Voice generation",
                "required": False,
            },
            "music_generation": {
                "description": "Music generation",
                "required": False,
            },
            "audio_processing": {
                "description": "Audio processing",
                "required": False,
            },
            "subtitle_generation": {
                "description": "Subtitle generation",
                "required": False,
            },
            "translation": {
                "description": "Translation",
                "required": False,
            },
            "dubbing": {
                "description": "Dubbing",
                "required": False,
            },
            "video_editing": {
                "description": "Video editing",
                "required": False,
            },
            "media_transcoding": {
                "description": "Media transcoding",
                "required": False,
            },
            "thumbnail_generation": {
                "description": "Thumbnail generation",
                "required": False,
            },
            "poster_generation": {
                "description": "Poster generation",
                "required": False,
            },
            "live_streaming": {
                "description": "Real live streaming",
                "required": False,
            },
            "media_storage": {
                "description": "Media storage",
                "required": False,
            },
            "cdn_delivery": {
                "description": "Media delivery",
                "required": False,
            },
            "social_publish": {
                "description": "Social publishing",
                "required": False,
            },
            "cinema_publish": {
                "description": "Movies and series publishing",
                "required": False,
            },
            "analytics": {
                "description": "Real analytics",
                "required": False,
            },
        }

    def _persist_capabilities(self) -> None:

        data = {
            "system": SYSTEM_ID,
            "version": VERSION,
            "updated_at": utc_now(),
            "capabilities": {},
        }

        for name, definition in getattr(
            self,
            "capability_catalog",
            {},
        ).items():

            adapter = self.adapters.get(name)

            data["capabilities"][name] = {
                **definition,
                "connected": adapter is not None,
                "real": bool(adapter.real)
                if adapter
                else False,
                "adapter": adapter.name
                if adapter
                else None,
            }

        write_json(
            CAPABILITIES_FILE,
            data,
        )

    def capability_report(self) -> Dict[str, Any]:

        self._persist_capabilities()

        return read_json(
            CAPABILITIES_FILE,
            {},
        )

    # ========================================================
    # JOBS
    # ========================================================

    def create_job(
        self,
        content_type: str,
        title: str,
        description: str = "",
        language: str = "ar",
        request: Optional[Dict[str, Any]] = None,
    ) -> MediaJob:

        try:
            content_type = ContentType(content_type).value
        except ValueError:
            raise ValueError(
                f"Unsupported content type: {content_type}"
            )

        job_id = (
            f"{content_type}-"
            f"{uuid.uuid4().hex[:16]}"
        )

        now = utc_now()

        job = MediaJob(
            id=job_id,
            content_type=content_type,
            title=title.strip() or "MAJD Content",
            description=description.strip(),
            language=language,
            status=JobStatus.QUEUED.value,
            created_at=now,
            updated_at=now,
            request=request or {},
        )

        self._save_job(job)

        return job

    def _save_job(self, job: MediaJob) -> None:

        job.updated_at = utc_now()

        self.jobs.setdefault(
            "jobs",
            {},
        )[job.id] = asdict(job)

        write_json(
            JOBS_FILE,
            self.jobs,
        )

        project_dir = (
            PROJECTS_DIR
            / safe_name(job.id)
        )

        write_json(
            project_dir / "job.json",
            asdict(job),
        )

    def get_job(
        self,
        job_id: str,
    ) -> Optional[MediaJob]:

        data = (
            self.jobs
            .get("jobs", {})
            .get(job_id)
        )

        if not data:
            return None

        return MediaJob(**data)

    def list_jobs(self) -> List[Dict[str, Any]]:
        return list(
            self.jobs
            .get("jobs", {})
            .values()
        )

    # ========================================================
    # AI PLANNING
    # ========================================================

    def plan_content(
        self,
        job: MediaJob,
    ) -> FactoryResult:

        job.status = JobStatus.PLANNING.value
        self._save_job(job)

        payload = {
            "platform": PLATFORM_NAME,
            "system": SYSTEM_ID,
            "job": asdict(job),
            "instruction": (
                "Create a complete professional production plan "
                "for this MAJD content request. "
                "Return structured JSON only."
            ),
        }

        result = self.execute_adapter(
            "ai_planning",
            payload,
        )

        if result.success:
            job.plan = result.data.get(
                "plan",
                result.data,
            )
            self._save_job(job)

        return result

    # ========================================================
    # SCRIPT / STORY / DIALOGUE
    # ========================================================

    def generate_script(
        self,
        job: MediaJob,
    ) -> FactoryResult:

        payload = {
            "job": asdict(job),
            "plan": job.plan,
            "language": job.language,
            "requirements": {
                "story": True,
                "scenes": True,
                "dialogue": True,
                "characters": True,
                "shots": True,
                "continuity": True,
            },
        }

        return self.execute_adapter(
            "script_generation",
            payload,
        )

    # ========================================================
    # IMAGES
    # ========================================================

    def generate_image(
        self,
        prompt: str,
        job: Optional[MediaJob] = None,
        purpose: str = "image",
    ) -> FactoryResult:

        return self.execute_adapter(
            "image_generation",
            {
                "prompt": prompt,
                "purpose": purpose,
                "job": asdict(job)
                if job
                else None,
            },
        )

    def generate_poster(
        self,
        job: MediaJob,
    ) -> FactoryResult:

        return self.execute_adapter(
            "poster_generation",
            {
                "job": asdict(job),
                "title": job.title,
                "description": job.description,
            },
        )

    def generate_thumbnail(
        self,
        job: MediaJob,
    ) -> FactoryResult:

        return self.execute_adapter(
            "thumbnail_generation",
            {
                "job": asdict(job),
                "title": job.title,
            },
        )

    # ========================================================
    # VIDEO / MOVIES / SERIES
    # ========================================================

    def generate_video(
        self,
        job: MediaJob,
        scene: Dict[str, Any],
    ) -> FactoryResult:

        return self.execute_adapter(
            "video_generation",
            {
                "job": asdict(job),
                "scene": scene,
            },
        )

    def generate_animation(
        self,
        job: MediaJob,
        scene: Dict[str, Any],
    ) -> FactoryResult:

        return self.execute_adapter(
            "animation_generation",
            {
                "job": asdict(job),
                "scene": scene,
            },
        )

    def generate_vfx(
        self,
        job: MediaJob,
        asset: Dict[str, Any],
    ) -> FactoryResult:

        return self.execute_adapter(
            "vfx_generation",
            {
                "job": asdict(job),
                "asset": asset,
            },
        )

    # ========================================================
    # AUDIO / VOICE / MUSIC
    # ========================================================

    def generate_voice(
        self,
        text: str,
        language: str = "ar",
        voice: Optional[str] = None,
    ) -> FactoryResult:

        return self.execute_adapter(
            "voice_generation",
            {
                "text": text,
                "language": language,
                "voice": voice,
            },
        )

    def generate_music(
        self,
        prompt: str,
        duration: Optional[int] = None,
    ) -> FactoryResult:

        return self.execute_adapter(
            "music_generation",
            {
                "prompt": prompt,
                "duration": duration,
            },
        )

    def process_audio(
        self,
        source: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> FactoryResult:

        return self.execute_adapter(
            "audio_processing",
            {
                "source": source,
                "options": options or {},
            },
        )

    # ========================================================
    # SUBTITLES / TRANSLATION / DUBBING
    # ========================================================

    def generate_subtitles(
        self,
        job: MediaJob,
        source: str,
        language: str,
    ) -> FactoryResult:

        return self.execute_adapter(
            "subtitle_generation",
            {
                "job": asdict(job),
                "source": source,
                "language": language,
            },
        )

    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> FactoryResult:

        return self.execute_adapter(
            "translation",
            {
                "text": text,
                "source_language": source_language,
                "target_language": target_language,
            },
        )

    def dub(
        self,
        job: MediaJob,
        source: str,
        target_language: str,
    ) -> FactoryResult:

        return self.execute_adapter(
            "dubbing",
            {
                "job": asdict(job),
                "source": source,
                "target_language": target_language,
            },
        )

    # ========================================================
    # FFMPEG REAL LOCAL PROCESSING
    # ========================================================

    def ffmpeg_available

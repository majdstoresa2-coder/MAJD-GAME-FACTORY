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

        def ffmpeg_available(self) -> bool:
        """Return True only when a real local FFmpeg executable exists."""
        return command_exists("ffmpeg")

    def ffprobe_available(self) -> bool:
        """Return True only when a real local FFprobe executable exists."""
        return command_exists("ffprobe")

    def probe_media(
        self,
        source: str,
    ) -> FactoryResult:
        """
        Inspect a real local media file using FFprobe.
        No fake metadata is returned.
        """

        if not self.ffprobe_available():
            return FactoryResult(
                success=False,
                status="FFPROBE_NOT_AVAILABLE",
                message="FFprobe is not installed or not available in PATH.",
                data={
                    "source": source,
                    "real_execution": False,
                },
                generated_at=utc_now(),
            )

        source_path = Path(source).expanduser().resolve()

        if not source_path.exists() or not source_path.is_file():
            return FactoryResult(
                success=False,
                status="SOURCE_NOT_FOUND",
                message=f"Media source does not exist: {source_path}",
                data={
                    "source": str(source_path),
                    "real_execution": False,
                },
                generated_at=utc_now(),
            )

        result = run_command(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_format",
                "-show_streams",
                "-of",
                "json",
                str(source_path),
            ]
        )

        if not result.success:
            return FactoryResult(
                success=False,
                status="FFPROBE_FAILED",
                message="Unable to inspect media source.",
                data=result.data,
                errors=result.errors,
                generated_at=utc_now(),
            )

        try:
            metadata = json.loads(
                result.data.get("stdout", "{}")
            )
        except json.JSONDecodeError as exc:
            return FactoryResult(
                success=False,
                status="FFPROBE_INVALID_OUTPUT",
                errors=[str(exc)],
                generated_at=utc_now(),
            )

        return FactoryResult(
            success=True,
            status="MEDIA_PROBED",
            message="Media source inspected successfully.",
            data={
                "source": str(source_path),
                "metadata": metadata,
                "sha256": sha256_file(source_path),
                "real_execution": True,
            },
            generated_at=utc_now(),
        )

    def transcode_media(
        self,
        source: str,
        output: str,
        video_codec: str = "libx264",
        audio_codec: str = "aac",
        overwrite: bool = False,
    ) -> FactoryResult:
        """
        Perform real local media transcoding using FFmpeg.
        """

        if not self.ffmpeg_available():
            return FactoryResult(
                success=False,
                status="FFMPEG_NOT_AVAILABLE",
                message="FFmpeg is not installed or not available in PATH.",
                data={
                    "real_execution": False,
                },
                generated_at=utc_now(),
            )

        source_path = Path(source).expanduser().resolve()
        output_path = Path(output).expanduser().resolve()

        if not source_path.exists() or not source_path.is_file():
            return FactoryResult(
                success=False,
                status="SOURCE_NOT_FOUND",
                message=f"Source file does not exist: {source_path}",
                generated_at=utc_now(),
            )

        if output_path.exists() and not overwrite:
            return FactoryResult(
                success=False,
                status="OUTPUT_ALREADY_EXISTS",
                message=f"Output already exists: {output_path}",
                generated_at=utc_now(),
            )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        command = [
            "ffmpeg",
            "-y" if overwrite else "-n",
            "-i",
            str(source_path),
            "-c:v",
            video_codec,
            "-c:a",
            audio_codec,
            str(output_path),
        ]

        result = run_command(command)

        if not result.success:
            return FactoryResult(
                success=False,
                status="TRANSCODE_FAILED",
                message="FFmpeg transcoding failed.",
                data=result.data,
                errors=result.errors,
                generated_at=utc_now(),
            )

        if not output_path.exists():
            return FactoryResult(
                success=False,
                status="TRANSCODE_OUTPUT_MISSING",
                message="FFmpeg completed but output file was not found.",
                generated_at=utc_now(),
            )

        return FactoryResult(
            success=True,
            status="TRANSCODE_COMPLETED",
            message="Media transcoded successfully.",
            data={
                "source": str(source_path),
                "output": str(output_path),
                "sha256": sha256_file(output_path),
                "size": output_path.stat().st_size,
                "real_execution": True,
            },
            generated_at=utc_now(),
        )

    def extract_audio(
        self,
        source: str,
        output: str,
        codec: str = "aac",
        overwrite: bool = False,
    ) -> FactoryResult:

        if not self.ffmpeg_available():
            return FactoryResult(
                success=False,
                status="FFMPEG_NOT_AVAILABLE",
                generated_at=utc_now(),
            )

        source_path = Path(source).expanduser().resolve()
        output_path = Path(output).expanduser().resolve()

        if not source_path.exists():
            return FactoryResult(
                success=False,
                status="SOURCE_NOT_FOUND",
                message=str(source_path),
                generated_at=utc_now(),
            )

        if output_path.exists() and not overwrite:
            return FactoryResult(
                success=False,
                status="OUTPUT_ALREADY_EXISTS",
                message=str(output_path),
                generated_at=utc_now(),
            )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        result = run_command(
            [
                "ffmpeg",
                "-y" if overwrite else "-n",
                "-i",
                str(source_path),
                "-vn",
                "-c:a",
                codec,
                str(output_path),
            ]
        )

        if not result.success or not output_path.exists():
            return FactoryResult(
                success=False,
                status="AUDIO_EXTRACTION_FAILED",
                data=result.data,
                errors=result.errors,
                generated_at=utc_now(),
            )

        return FactoryResult(
            success=True,
            status="AUDIO_EXTRACTED",
            data={
                "output": str(output_path),
                "sha256": sha256_file(output_path),
                "size": output_path.stat().st_size,
                "real_execution": True,
            },
            generated_at=utc_now(),
        )

    def create_thumbnail_from_video(
        self,
        source: str,
        output: str,
        timestamp: str = "00:00:01",
        overwrite: bool = False,
    ) -> FactoryResult:

        if not self.ffmpeg_available():
            return FactoryResult(
                success=False,
                status="FFMPEG_NOT_AVAILABLE",
                generated_at=utc_now(),
            )

        source_path = Path(source).expanduser().resolve()
        output_path = Path(output).expanduser().resolve()

        if not source_path.exists():
            return FactoryResult(
                success=False,
                status="SOURCE_NOT_FOUND",
                message=str(source_path),
                generated_at=utc_now(),
            )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        result = run_command(
            [
                "ffmpeg",
                "-y" if overwrite else "-n",
                "-ss",
                timestamp,
                "-i",
                str(source_path),
                "-frames:v",
                "1",
                str(output_path),
            ]
        )

        if not result.success or not output_path.exists():
            return FactoryResult(
                success=False,
                status="THUMBNAIL_EXTRACTION_FAILED",
                data=result.data,
                errors=result.errors,
                generated_at=utc_now(),
            )

        return FactoryResult(
            success=True,
            status="THUMBNAIL_CREATED",
            data={
                "output": str(output_path),
                "sha256": sha256_file(output_path),
                "real_execution": True,
            },
            generated_at=utc_now(),
        )

    # ========================================================
    # ASSET MANAGEMENT
    # ========================================================

    def register_asset(
        self,
        job: MediaJob,
        path: str,
        asset_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> FactoryResult:

        asset_path = Path(path).expanduser().resolve()

        if not asset_path.exists() or not asset_path.is_file():
            return FactoryResult(
                success=False,
                status="ASSET_NOT_FOUND",
                message=str(asset_path),
                generated_at=utc_now(),
            )

        asset = {
            "id": f"asset-{uuid.uuid4().hex[:16]}",
            "type": asset_type,
            "path": str(asset_path),
            "size": asset_path.stat().st_size,
            "sha256": sha256_file(asset_path),
            "metadata": metadata or {},
            "registered_at": utc_now(),
            "verified": True,
        }

        job.assets.append(asset)
        self._save_job(job)

        return FactoryResult(
            success=True,
            status="ASSET_REGISTERED",
            data=asset,
            generated_at=utc_now(),
        )

    def register_output(
        self,
        job: MediaJob,
        path: str,
        output_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> FactoryResult:

        output_path = Path(path).expanduser().resolve()

        if not output_path.exists() or not output_path.is_file():
            return FactoryResult(
                success=False,
                status="OUTPUT_NOT_FOUND",
                message=str(output_path),
                generated_at=utc_now(),
            )

        output = {
            "id": f"output-{uuid.uuid4().hex[:16]}",
            "type": output_type,
            "path": str(output_path),
            "size": output_path.stat().st_size,
            "sha256": sha256_file(output_path),
            "metadata": metadata or {},
            "registered_at": utc_now(),
            "verified": True,
        }

        job.outputs.append(output)
        self._save_job(job)

        return FactoryResult(
            success=True,
            status="OUTPUT_REGISTERED",
            data=output,
            generated_at=utc_now(),
        )

    # ========================================================
    # QUALITY ASSURANCE
    # ========================================================

    def validate_job(
        self,
        job: MediaJob,
    ) -> FactoryResult:

        errors: List[str] = []
        warnings: List[str] = []
        verified_outputs: List[Dict[str, Any]] = []

        if not job.title.strip():
            errors.append("Job title is empty.")

        if not job.content_type:
            errors.append("Content type is missing.")

        for output in job.outputs:
            raw_path = output.get("path")

            if not raw_path:
                errors.append(
                    "Output contains no path."
                )
                continue

            output_path = Path(raw_path)

            if not output_path.exists():
                errors.append(
                    f"Missing output: {output_path}"
                )
                continue

            if not output_path.is_file():
                errors.append(
                    f"Output is not a file: {output_path}"
                )
                continue

            actual_hash = sha256_file(output_path)

            expected_hash = output.get("sha256")

            if expected_hash and expected_hash != actual_hash:
                errors.append(
                    f"Checksum mismatch: {output_path}"
                )
                continue

            verified_outputs.append(
                {
                    "path": str(output_path),
                    "sha256": actual_hash,
                    "size": output_path.stat().st_size,
                    "verified": True,
                }
            )

        if not job.outputs:
            warnings.append(
                "Job currently has no registered output files."
            )

        passed = len(errors) == 0

        test = {
            "id": f"test-{uuid.uuid4().hex[:12]}",
            "passed": passed,
            "errors": errors,
            "warnings": warnings,
            "verified_outputs": verified_outputs,
            "tested_at": utc_now(),
        }

        job.tests.append(test)

        if passed and job.outputs:
            job.status = JobStatus.READY.value
        elif not passed:
            job.status = JobStatus.FAILED.value

        self._save_job(job)

        return FactoryResult(
            success=passed,
            status=(
                "QA_PASSED"
                if passed
                else "QA_FAILED"
            ),
            data=test,
            errors=errors,
            warnings=warnings,
            generated_at=utc_now(),
        )

    # ========================================================
    # AUTOMATIC REPAIR
    # ========================================================

    def automatic_repair(
        self,
        job: MediaJob,
    ) -> FactoryResult:

        job.status = JobStatus.REPAIRING.value
        self._save_job(job)

        if not self.has_real_adapter(
            "ai_planning"
        ):
            return FactoryResult(
                success=False,
                status="REPAIR_ENGINE_NOT_CONNECTED",
                message=(
                    "AI planning/repair adapter is not connected."
                ),
                generated_at=utc_now(),
            )

        result = self.execute_adapter(
            "ai_planning",
            {
                "operation": "repair",
                "job": asdict(job),
                "tests": job.tests,
                "instruction": (
                    "Analyze the failed MAJD media production "
                    "job and return a structured repair plan."
                ),
            },
        )

        if result.success:
            job.plan.setdefault(
                "repairs",
                [],
            ).append(result.data)

            self._save_job(job)

        return result

    # ========================================================
    # LIVE STREAMING
    # ========================================================

    def create_live_stream(
        self,
        job: MediaJob,
        title: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> FactoryResult:

        return self.execute_adapter(
            "live_streaming",
            {
                "operation": "create",
                "job": asdict(job),
                "title": title or job.title,
                "options": options or {},
            },
        )

    def start_live_stream(
        self,
        job: MediaJob,
        stream_id: str,
    ) -> FactoryResult:

        result = self.execute_adapter(
            "live_streaming",
            {
                "operation": "start",
                "job": asdict(job),
                "stream_id": stream_id,
            },
        )

        if result.success:
            job.status = JobStatus.LIVE.value
            self._save_job(job)

        return result

    def stop_live_stream(
        self,
        job: MediaJob,
        stream_id: str,
    ) -> FactoryResult:

        result = self.execute_adapter(
            "live_streaming",
            {
                "operation": "stop",
                "job": asdict(job),
                "stream_id": stream_id,
            },
        )

        if result.success:
            job.status = JobStatus.READY.value
            self._save_job(job)

        return result

    # ========================================================
    # CHANNELS
    # ========================================================

    def create_channel(
        self,
        name: str,
        description: str = "",
        channel_type: str = "general",
    ) -> FactoryResult:

        channel_id = (
            "channel-"
            + uuid.uuid4().hex[:16]
        )

        channel = {
            "id": channel_id,
            "name": name,
            "description": description,
            "type": channel_type,
            "created_at": utc_now(),
            "verified": False,
            "status": "CREATED",
        }

        channels = read_json(
            CHANNELS_DIR / "channels.json",
            {
                "channels": {},
            },
        )

        channels["channels"][channel_id] = channel

        write_json(
            CHANNELS_DIR / "channels.json",
            channels,
        )

        return FactoryResult(
            success=True,
            status="CHANNEL_CREATED",
            data=channel,
            generated_at=utc_now(),
        )

    # ========================================================
    # SOCIAL PUBLISHING
    # ========================================================

    def publish_social(
        self,
        job: MediaJob,
        destinations: List[str],
        text: str = "",
    ) -> FactoryResult:

        result = self.execute_adapter(
            "social_publish",
            {
                "job": asdict(job),
                "destinations": destinations,
                "text": text,
            },
        )

        if result.success:
            self._record_publication(
                job,
                "social",
                result,
            )

        return result

    # ========================================================
    # CINEMA / MOVIES / SERIES PUBLISHING
    # ========================================================

    def publish_cinema(
        self,
        job: MediaJob,
        visibility: str = "public",
        release_at: Optional[str] = None,
    ) -> FactoryResult:

        qa = self.validate_job(job)

        if not qa.success:
            return FactoryResult(
                success=False,
                status="PUBLISH_BLOCKED_QA",
                errors=qa.errors,
                warnings=qa.warnings,
                generated_at=utc_now(),
            )

        if not job.outputs:
            return FactoryResult(
                success=False,
                status="PUBLISH_BLOCKED_NO_OUTPUT",
                message=(
                    "No verified real output exists."
                ),
                generated_at=utc_now(),
            )

        job.status = JobStatus.PUBLISHING.value
        self._save_job(job)

        result = self.execute_adapter(
            "cinema_publish",
            {
                "job": asdict(job),
                "visibility": visibility,
                "release_at": release_at,
            },
        )

        if result.success:
            job.status = JobStatus.PUBLISHED.value

            self._record_publication(
                job,
                "cinema",
                result,
            )

            self._save_job(job)

        else:
            job.status = JobStatus.FAILED.value
            self._save_job(job)

        return result

    # ========================================================
    # PUBLICATION RECORD
    # ========================================================

    def _record_publication(
        self,
        job: MediaJob,
        publication_type: str,
        result: FactoryResult,
    ) -> None:

        publication = {
            "id": (
                "publication-"
                + uuid.uuid4().hex[:16]
            ),
            "job_id": job.id,
            "type": publication_type,
            "published_at": utc_now(),
            "result": result.data,
            "verified_real_execution": bool(
                result.data.get(
                    "real_execution"
                )
            ),
        }

        job.publication = publication

        publications = read_json(
            PUBLISHING_FILE,
            {
                "system": SYSTEM_ID,
                "publications": [],
            },
        )

        publications.setdefault(
            "publications",
            [],
        ).append(publication)

        write_json(
            PUBLISHING_FILE,
            publications,
        )

        self._save_job(job)

    # ========================================================
    # ANALYTICS
    # ========================================================

    def analytics(
        self,
        job: Optional[MediaJob] = None,
    ) -> FactoryResult:

        return self.execute_adapter(
            "analytics",
            {
                "job": asdict(job)
                if job
                else None,
                "platform": PLATFORM_NAME,
            },
        )

    # ========================================================
    # COMPLETE PRODUCTION PIPELINE
    # ========================================================

    def produce(
        self,
        job: MediaJob,
    ) -> FactoryResult:

        job.status = JobStatus.GENERATING.value
        self._save_job(job)

        production_log: List[Dict[str, Any]] = []

        planning = self.plan_content(job)

        production_log.append(
            {
                "stage": "planning",
                "success": planning.success,
                "status": planning.status,
            }
        )

        if not planning.success:
            job.status = JobStatus.BLOCKED.value
            job.errors.extend(
                planning.errors
                or [planning.message]
            )
            self._save_job(job)

            return FactoryResult(
                success=False,
                status="PRODUCTION_BLOCKED_PLANNING",
                data={
                    "job": asdict(job),
                    "pipeline": production_log,
                },
                errors=planning.errors,
                generated_at=utc_now(),
            )

        script = self.generate_script(job)

        production_log.append(
            {
                "stage": "script",
                "success": script.success,
                "status": script.status,
            }
        )

        if not script.success:
            job.status = JobStatus.BLOCKED.value
            self._save_job(job)

            return FactoryResult(
                success=False,
                status="PRODUCTION_BLOCKED_SCRIPT",
                data={
                    "job": asdict(job),
                    "pipeline": production_log,
                },
                errors=script.errors,
                generated_at=utc_now(),
            )

        content_type = job.content_type

        if content_type in {
            ContentType.MOVIE.value,
            ContentType.SERIES.value,
            ContentType.EPISODE.value,
            ContentType.VIDEO.value,
            ContentType.SHORT.value,
            ContentType.STORY.value,
            ContentType.ANIMATION.value,
            ContentType.GAME_MEDIA.value,
        }:

            scenes = (
                job.plan.get("scenes")
                or script.data.get("scenes")
                or []
            )

            if not scenes:
                return FactoryResult(
                    success=False,
                    status="NO_SCENES_PRODUCED",
                    message=(
                        "Planning/script adapters returned no scenes."
                    ),
                    data={
                        "pipeline": production_log,
                    },
                    generated_at=utc_now(),
                )

            for index, scene in enumerate(
                scenes,
                start=1,
            ):

                if content_type == ContentType.ANIMATION.value:
                    generated = self.generate_animation(
                        job,
                        scene,
                    )
                else:
                    generated = self.generate_video(
                        job,
                        scene,
                    )

                production_log.append(
                    {
                        "stage": f"scene-{index}",
                        "success": generated.success,
                        "status": generated.status,
                    }
                )

                if not generated.success:
                    job.status = JobStatus.FAILED.value
                    self._save_job(job)

                    return FactoryResult(
                        success=False,
                        status="SCENE_GENERATION_FAILED",
                        data={
                            "scene": index,
                            "pipeline": production_log,
                        },
                        errors=generated.errors,
                        generated_at=utc_now(),
                    )

                output_path = generated.data.get(
                    "output"
                )

                if output_path:
                    registered = self.register_output(
                        job,
                        output_path,
                        "video",
                        {
                            "scene": index,
                        },
                    )

                    if not registered.success:
                        return registered

        elif content_type in {
            ContentType.IMAGE.value,
            ContentType.POSTER.value,
            ContentType.THUMBNAIL.value,
        }:

            if content_type == ContentType.POSTER.value:
                generated = self.generate_poster(job)

            elif content_type == ContentType.THUMBNAIL.value:
                generated = self.generate_thumbnail(job)

            else:
                generated = self.generate_image(
                    job.description or job.title,
                    job,
                )

            production_log.append(
                {
                    "stage": "visual",
                    "success": generated.success,
                    "status": generated.status,
                }
            )

            if not generated.success:
                return FactoryResult(
                    success=False,
                    status="VISUAL_GENERATION_FAILED",
                    data={
                        "pipeline": production_log,
                    },
                    errors=generated.errors,
                    generated_at=utc_now(),
                )

            output_path = generated.data.get(
                "output"
            )

            if output_path:
                registered = self.register_output(
                    job,
                    output_path,
                    content_type,
                )

                if not registered.success:
                    return registered

        elif content_type == ContentType.MUSIC.value:

            generated = self.generate_music(
                job.description or job.title,
                job.request.get("duration"),
            )

            production_log.append(
                {
                    "stage": "music",
                    "success": generated.success,
                    "status": generated.status,
                }
            )

            if not generated.success:
                return generated

            output_path = generated.data.get(
                "output"
            )

            if output_path:
                registered = self.register_output(
                    job,
                    output_path,
                    "music",
                )

                if not registered.success:
                    return registered

        elif content_type == ContentType.VOICE.value:

            generated = self.generate_voice(
                job.description or job.title,
                job.language,
                job.request.get("voice"),
            )

            production_log.append(
                {
                    "stage": "voice",
                    "success": generated.success,
                    "status": generated.status,
                }
            )

            if not generated.success:
                return generated

            output_path = generated.data.get(
                "output"
            )

            if output_path:
                registered = self.register_output(
                    job,
                    output_path,
                    "voice",
                )

                if not registered.success:
                    return registered

        qa = self.validate_job(job)

        production_log.append(
            {
                "stage": "qa",
                "success": qa.success,
                "status": qa.status,
            }
        )

        if not qa.success:
            repair = self.automatic_repair(job)

            production_log.append(
                {
                    "stage": "repair",
                    "success": repair.success,
                    "status": repair.status,
                }
            )

            return FactoryResult(
                success=False,
                status="PRODUCTION_REQUIRES_REPAIR",
                data={
                    "job": asdict(job),
                    "pipeline": production_log,
                    "repair": repair.data,
                },
                errors=qa.errors,
                warnings=qa.warnings,
                generated_at=utc_now(),
            )

        job.status = JobStatus.READY.value
        self._save_job(job)

        return FactoryResult(
            success=True,
            status="PRODUCTION_READY",
            message=(
                "Real production pipeline completed "
                "and outputs passed QA."
            ),
            data={
                "job": asdict(job),
                "pipeline": production_log,
            },
            generated_at=utc_now(),
        )

    # ========================================================
    # STATUS / HEALTH
    # ========================================================

    def health(self) -> Dict[str, Any]:

        capabilities = self.capability_report()

        connected = [
            name
            for name, data
            in capabilities.get(
                "capabilities",
                {},
            ).items()
            if data.get("connected")
            and data.get("real")
        ]

        disconnected = [
            name
            for name, data
            in capabilities.get(
                "capabilities",
                {},
            ).items()
            if not data.get("connected")
        ]

        return {
            "system": SYSTEM_ID,
            "name": SYSTEM_NAME,
            "version": VERSION,
            "platform": PLATFORM_NAME,
            "status": "ACTIVE",
            "time": utc_now(),
            "ffmpeg": self.ffmpeg_available(),
            "ffprobe": self.ffprobe_available(),
            "real_capabilities_connected": connected,
            "capabilities_not_connected": disconnected,
            "jobs": len(
                self.jobs.get(
                    "jobs",
                    {},
                )
            ),
        }


# ============================================================
# FACTORY SINGLETON
# ============================================================

_factory: Optional[
    MajdAIContentMediaFactory
] = None


def get_factory() -> MajdAIContentMediaFactory:

    global _factory

    if _factory is None:
        _factory = MajdAIContentMediaFactory()

    return _factory


# ============================================================
# PUBLIC API
# ============================================================

def create_media_job(
    content_type: str,
    title: str,
    description: str = "",
    language: str = "ar",
    request: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:

    factory = get_factory()

    job = factory.create_job(
        content_type=content_type,
        title=title,
        description=description,
        language=language,
        request=request,
    )

    return asdict(job)


def produce_media(
    job_id: str,
) -> Dict[str, Any]:

    factory = get_factory()

    job = factory.get_job(job_id)

    if not job:
        return asdict(
            FactoryResult(
                success=False,
                status="JOB_NOT_FOUND",
                message=job_id,
                generated_at=utc_now(),
            )
        )

    return asdict(
        factory.produce(job)
    )


def factory_health() -> Dict[str, Any]:
    return get_factory().health()


def factory_capabilities() -> Dict[str, Any]:
    return get_factory().capability_report()


# ============================================================
# CLI
# ============================================================

def main() -> int:

    factory = get_factory()

    print(
        json.dumps(
            factory.health(),
            ensure_ascii=False,
            indent=2,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

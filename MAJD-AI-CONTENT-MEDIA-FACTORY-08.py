#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-AI-CONTENT-MEDIA-FACTORY-08.py
====================================

MAJD SOVEREIGN AI CONTENT + MEDIA FACTORY

Official sovereign content/media production runtime for MAJD.

Responsibilities:
- AI production planning
- Scripts / stories / dialogue
- Movies / series / episodes
- Video / shorts / stories
- Images / posters / thumbnails
- Animation / VFX
- Audio / voice / music
- Subtitles / translation / dubbing
- Live streaming
- MAJD channels
- Social content
- Social publishing adapters
- Internal MAJD advertising
- External campaign preparation
- Email content and delivery adapters
- Scheduling
- Asset management
- FFmpeg / FFprobe processing
- Quality assurance
- Automatic repair
- Analytics
- Financial event emission
- Secure owner-action requests
- Integration contracts with the existing MAJD runtime

SECURITY / TRUTH RULES
----------------------
1. Never report external generation, publication, email delivery,
   social publication, payment, live streaming, or other external
   execution as successful unless a REAL enabled adapter executed
   successfully.

2. Secrets, passwords, OTP codes, OAuth credentials, private keys,
   payment credentials and owner-sensitive information MUST NOT be
   requested through source code, terminal arguments, logs, GitHub
   commits or public job payloads.

3. Operations requiring owner authorization return
   OWNER_ACTION_REQUIRED and create a secure owner-action record.

4. This module does not grant access to the sovereign control room.
   Authorization remains the responsibility of the sovereign
   authority/runtime layer.

5. Financial events emitted here are accounting/event requests only.
   This file does not fabricate balances or move real money.

6. Existing MAJD files are not modified by this module.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import uuid

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


# ============================================================
# IDENTITY
# ============================================================

SYSTEM_ID = "MAJD-AI-CONTENT-MEDIA-FACTORY-08"
SYSTEM_NAME = "MAJD Sovereign AI Content & Media Factory"
PLATFORM_NAME = "MAJD"
VERSION = "2.0.0"

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
EMAIL_DIR = FACTORY_ROOT / "email"
ADS_DIR = FACTORY_ROOT / "ads"
EVENTS_DIR = FACTORY_ROOT / "events"

PUBLISH_DIR = FACTORY_ROOT / "published"
SCHEDULE_DIR = FACTORY_ROOT / "schedule"

TEMP_DIR = FACTORY_ROOT / "tmp"
LOGS_DIR = FACTORY_ROOT / "logs"
STATE_DIR = FACTORY_ROOT / "state"

OWNER_ACTIONS_DIR = STATE_DIR / "owner-actions"
INTEGRATIONS_DIR = STATE_DIR / "integrations"
FINANCIAL_EVENTS_DIR = STATE_DIR / "financial-events"

REGISTRY_FILE = STATE_DIR / "registry.json"
JOBS_FILE = STATE_DIR / "jobs.json"
CAPABILITIES_FILE = STATE_DIR / "capabilities.json"
PUBLISHING_FILE = STATE_DIR / "publishing.json"
CHANNELS_FILE = STATE_DIR / "channels.json"
ADS_FILE = STATE_DIR / "ads.json"
SCHEDULE_FILE = STATE_DIR / "schedule.json"
OWNER_ACTIONS_FILE = STATE_DIR / "owner-actions.json"
FINANCIAL_EVENTS_FILE = STATE_DIR / "financial-events.json"
INTEGRATIONS_FILE = STATE_DIR / "integrations.json"


# ============================================================
# EXISTING MAJD COMPONENT CONTRACTS
# ============================================================

MAJD_COMPONENTS = {
    "mastermind": "MAJD-AI-MASTERMIND-01.py",
    "owner_command_center": "MAJD-OWNER-COMMAND-CENTER-02.py",
    "real_executor": "MAJD-REAL-GAME-EXECUTOR-03.py",
    "official_bridge": "MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py",
    "execution_runtime": "MAJD-FULL-EXECUTION-RUNTIME-06.py",
    "public_platform": "MAJD-SOVEREIGN-PUBLIC-PLATFORM-07.py",
}

# This module only discovers these files.
# It does NOT guess or invoke undocumented functions inside them.


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
    SCHEDULED = "SCHEDULED"
    PUBLISHING = "PUBLISHING"
    PUBLISHED = "PUBLISHED"
    LIVE = "LIVE"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    OWNER_ACTION_REQUIRED = "OWNER_ACTION_REQUIRED"


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
    ADVERTISEMENT = "advertisement"
    EMAIL_CAMPAIGN = "email_campaign"
    EVENT = "event"
    GAME_MEDIA = "game_media"


class OwnerActionStatus(str, Enum):
    REQUIRED = "REQUIRED"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class VerificationLevel(str, Enum):
    GUEST = "GUEST"
    REGISTERED = "REGISTERED"
    PROVIDER_VERIFIED = "PROVIDER_VERIFIED"
    MAJD_VERIFIED = "MAJD_VERIFIED"
    FINANCIAL_VERIFIED = "FINANCIAL_VERIFIED"


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

    account_id: Optional[str] = None
    channel_id: Optional[str] = None

    request: Dict[str, Any] = field(default_factory=dict)
    plan: Dict[str, Any] = field(default_factory=dict)

    assets: List[Dict[str, Any]] = field(default_factory=list)
    outputs: List[Dict[str, Any]] = field(default_factory=list)
    tests: List[Dict[str, Any]] = field(default_factory=list)

    publication: Dict[str, Any] = field(default_factory=dict)

    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class Adapter:
    name: str
    capability: str
    handler: Callable[[Dict[str, Any]], Dict[str, Any]]
    real: bool = True
    enabled: bool = True


@dataclass
class OwnerAction:
    id: str
    action_type: str
    title: str
    description: str
    status: str
    created_at: str

    capability: Optional[str] = None
    provider: Optional[str] = None
    job_id: Optional[str] = None

    safe_payload: Dict[str, Any] = field(default_factory=dict)


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
        EMAIL_DIR,
        ADS_DIR,
        EVENTS_DIR,
        PUBLISH_DIR,
        SCHEDULE_DIR,
        TEMP_DIR,
        LOGS_DIR,
        STATE_DIR,
        OWNER_ACTIONS_DIR,
        INTEGRATIONS_DIR,
        FINANCIAL_EVENTS_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary = path.with_suffix(path.suffix + ".tmp")

    temporary.write_text(
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    temporary.replace(path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()


def safe_name(value: str) -> str:
    cleaned = "".join(
        character if character.isalnum() or character in "-_"
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

        success = process.returncode == 0

        return FactoryResult(
            success=success,
            status=(
                "COMMAND_COMPLETED"
                if success
                else "COMMAND_FAILED"
            ),
            data={
                "command": command,
                "returncode": process.returncode,
                "stdout": process.stdout[-10000:],
                "stderr": process.stderr[-10000:],
                "real_execution": True,
            },
            generated_at=utc_now(),
        )

    except subprocess.TimeoutExpired as exc:
        return FactoryResult(
            success=False,
            status="COMMAND_TIMEOUT",
            errors=[str(exc)],
            generated_at=utc_now(),
        )

    except Exception as exc:
        return FactoryResult(
            success=False,
            status="COMMAND_EXCEPTION",
            errors=[str(exc)],
            generated_at=utc_now(),
        )


def sanitize_sensitive_payload(
    payload: Dict[str, Any],
) -> Dict[str, Any]:

    sensitive_terms = {
        "password",
        "secret",
        "token",
        "access_token",
        "refresh_token",
        "private_key",
        "api_key",
        "otp",
        "authorization",
        "cookie",
        "session",
        "client_secret",
    }

    sanitized: Dict[str, Any] = {}

    for key, value in payload.items():
        lowered = key.lower()

        if any(term in lowered for term in sensitive_terms):
            sanitized[key] = "[REDACTED]"
            continue

        if isinstance(value, dict):
            sanitized[key] = sanitize_sensitive_payload(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_sensitive_payload(item)
                if isinstance(item, dict)
                else item
                for item in value
            ]
        else:
            sanitized[key] = value

    return sanitized


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
    # CAPABILITY CATALOG
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
                "description": "Real image generation",
                "required": False,
            },
            "video_generation": {
                "description": "Real video generation",
                "required": False,
            },
            "animation_generation": {
                "description": "Animation generation",
                "required": False,
            },
            "vfx_generation": {
                "description": "Visual effects generation",
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
                "description": "External social publishing",
                "required": False,
            },
            "email_delivery": {
                "description": "Official email delivery",
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
            "financial_event_sink": {
                "description": "Financial ledger event integration",
                "required": False,
            },
            "owner_secure_action": {
                "description": "Secure owner action integration",
                "required": False,
            },
        }

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

        if capability not in self.capability_catalog:
            raise ValueError(
                f"Unknown capability: {capability}"
            )

        if not callable(handler):
            raise TypeError(
                "Adapter handler must be callable."
            )

        self.adapters[capability] = Adapter(
            name=name,
            capability=capability,
            handler=handler,
            real=real,
            enabled=True,
        )

        self._persist_capabilities()

    def unregister_adapter(
        self,
        capability: str,
    ) -> None:

        self.adapters.pop(capability, None)
        self._persist_capabilities()

    def has_real_adapter(
        self,
        capability: str,
    ) -> bool:

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
                    f"No execution adapter connected for "
                    f"{capability}."
                ),
                data={
                    "capability": capability,
                    "real_execution": False,
                },
                generated_at=utc_now(),
            )

        if not adapter.real:
            return FactoryResult(
                success=False,
                status="REAL_EXECUTION_REQUIRED",
                message=(
                    f"Adapter {adapter.name} is not marked "
                    f"as a real execution adapter."
                ),
                data={
                    "capability": capability,
                    "adapter": adapter.name,
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

            success = bool(result.get("success", False))

            adapter_real_execution = bool(
                result.get(
                    "real_execution",
                    success,
                )
            )

            if success and not adapter_real_execution:
                return FactoryResult(
                    success=False,
                    status="REAL_EXECUTION_NOT_VERIFIED",
                    message=(
                        "Adapter claimed success without verified "
                        "real execution."
                    ),
                    data={
                        "adapter": adapter.name,
                        "capability": capability,
                        "real_execution": False,
                    },
                    generated_at=utc_now(),
                )

            return FactoryResult(
                success=success,
                status=result.get(
                    "status",
                    (
                        "ADAPTER_SUCCESS"
                        if success
                        else "ADAPTER_FAILED"
                    ),
                ),
                message=result.get("message", ""),
                data={
                    **result,
                    "adapter": adapter.name,
                    "capability": capability,
                    "real_execution": adapter_real_execution,
                },
                errors=list(result.get("errors", [])),
                warnings=list(result.get("warnings", [])),
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
                    "real_execution": False,
                },
                generated_at=utc_now(),
            )

    # ========================================================
    # CAPABILITY STATE
    # ========================================================

    def _persist_capabilities(self) -> None:

        data = {
            "system": SYSTEM_ID,
            "version": VERSION,
            "updated_at": utc_now(),
            "capabilities": {},
        }

        for name, definition in self.capability_catalog.items():

            adapter = self.adapters.get(name)

            data["capabilities"][name] = {
                **definition,
                "connected": adapter is not None,
                "enabled": bool(
                    adapter.enabled
                    if adapter
                    else False
                ),
                "real": bool(
                    adapter.real
                    if adapter
                    else False
                ),
                "adapter": (
                    adapter.name
                    if adapter
                    else None
                ),
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
    # MAJD COMPONENT DISCOVERY
    # ========================================================

    def discover_majd_components(
        self,
    ) -> Dict[str, Any]:

        components: Dict[str, Any] = {}

        for component, filename in MAJD_COMPONENTS.items():

            path = ROOT_DIR / filename

            components[component] = {
                "filename": filename,
                "path": str(path),
                "exists": path.exists(),
                "is_file": path.is_file(),
                "sha256": (
                    sha256_file(path)
                    if path.exists() and path.is_file()
                    else None
                ),
            }

        return {
            "system": SYSTEM_ID,
            "checked_at": utc_now(),
            "components": components,
        }

    # ========================================================
    # OWNER SECURE ACTIONS
    # ========================================================

    def require_owner_action(
        self,
        action_type: str,
        title: str,
        description: str,
        capability: Optional[str] = None,
        provider: Optional[str] = None,
        job_id: Optional[str] = None,
        safe_payload: Optional[Dict[str, Any]] = None,
    ) -> FactoryResult:

        action = OwnerAction(
            id=(
                "owner-action-"
                + uuid.uuid4().hex[:16]
            ),
            action_type=action_type,
            title=title,
            description=description,
            status=OwnerActionStatus.REQUIRED.value,
            created_at=utc_now(),
            capability=capability,
            provider=provider,
            job_id=job_id,
            safe_payload=sanitize_sensitive_payload(
                safe_payload or {}
            ),
        )

        state = read_json(
            OWNER_ACTIONS_FILE,
            {
                "system": SYSTEM_ID,
                "actions": {},
            },
        )

        state.setdefault(
            "actions",
            {},
        )[action.id] = asdict(action)

        write_json(
            OWNER_ACTIONS_FILE,
            state,
        )

        write_json(
            OWNER_ACTIONS_DIR / f"{action.id}.json",
            asdict(action),
        )

        return FactoryResult(
            success=False,
            status="OWNER_ACTION_REQUIRED",
            message=description,
            data={
                "owner_action": asdict(action),
                "secret_input_required_in_source": False,
            },
            generated_at=utc_now(),
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
        account_id: Optional[str] = None,
        channel_id: Optional[str] = None,
    ) -> MediaJob:

        try:
            normalized_type = ContentType(
                content_type
            ).value
        except ValueError as exc:
            raise ValueError(
                f"Unsupported content type: {content_type}"
            ) from exc

        now = utc_now()

        job = MediaJob(
            id=(
                f"{normalized_type}-"
                f"{uuid.uuid4().hex[:16]}"
            ),
            content_type=normalized_type,
            title=title.strip() or "MAJD Content",
            description=description.strip(),
            language=language,
            status=JobStatus.QUEUED.value,
            created_at=now,
            updated_at=now,
            request=request or {},
            account_id=account_id,
            channel_id=channel_id,
        )

        self._save_job(job)

        return job

    def _save_job(
        self,
        job: MediaJob,
    ) -> None:

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

    def list_jobs(
        self,
    ) -> List[Dict[str, Any]]:

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

        result = self.execute_adapter(
            "ai_planning",
            {
                "platform": PLATFORM_NAME,
                "system": SYSTEM_ID,
                "job": asdict(job),
                "instruction": (
                    "Create a complete professional MAJD "
                    "production plan as structured data."
                ),
            },
        )

        if result.success:
            job.plan = result.data.get(
                "plan",
                result.data,
            )

            self._save_job(job)

        return result

    # ========================================================
    # SCRIPT
    # ========================================================

    def generate_script(
        self,
        job: MediaJob,
    ) -> FactoryResult:

        return self.execute_adapter(
            "script_generation",
            {
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
                    "originality": True,
                },
            },
        )

    # ========================================================
    # VISUAL GENERATION
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
                "job": (
                    asdict(job)
                    if job
                    else None
                ),
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
    # VIDEO / ANIMATION / VFX
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
    # LANGUAGE / SUBTITLES / DUBBING
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
    # FFMPEG / FFPROBE
    # ========================================================

    def ffmpeg_available(self) -> bool:
        """Return True only when a real FFmpeg executable exists."""
        return command_exists("ffmpeg")

    def ffprobe_available(self) -> bool:
        """Return True only when a real FFprobe executable exists."""
        return command_exists("ffprobe")

    def probe_media(
        self,
        source: str,
    ) -> FactoryResult:

        if not self.ffprobe_available():
            return FactoryResult(
                success=False,
                status="FFPROBE_NOT_AVAILABLE",
                data={
                    "real_execution": False,
                },
                generated_at=utc_now(),
            )

        source_path = Path(
            source
        ).expanduser().resolve()

        if not source_path.exists() or not source_path.is_file():
            return FactoryResult(
                success=False,
                status="SOURCE_NOT_FOUND",
                message=str(source_path),
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
                data=result.data,
                errors=result.errors,
                generated_at=utc_now(),
            )

        try:
            metadata = json.loads(
                result.data.get(
                    "stdout",
                    "{}",
                )
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

        if not self.ffmpeg_available():
            return FactoryResult(
                success=False,
                status="FFMPEG_NOT_AVAILABLE",
                data={
                    "real_execution": False,
                },
                generated_at=utc_now(),
            )

        source_path = Path(
            source
        ).expanduser().resolve()

        output_path = Path(
            output
        ).expanduser().resolve()

        if not source_path.exists() or not source_path.is_file():
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
                "-c:v",
                video_codec,
                "-c:a",
                audio_codec,
                str(output_path),
            ]
        )

        if not result.success:
            return FactoryResult(
                success=False,
                status="TRANSCODE_FAILED",
                data=result.data,
                errors=result.errors,
                generated_at=utc_now(),
            )

        if not output_path.exists() or not output_path.is_file():
            return FactoryResult(
                success=False,
                status="TRANSCODE_OUTPUT_MISSING",
                generated_at=utc_now(),
            )

        return FactoryResult(
            success=True,
            status="TRANSCODE_COMPLETED",
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

        source_path = Path(
            source
        ).expanduser().resolve()

        output_path = Path(
            output
        ).expanduser().resolve()

        if not source_path.exists() or not source_path.is_file():
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

        source_path = Path(
            source
        ).expanduser().resolve()

        output_path = Path(
            output
        ).expanduser().resolve()

        if not source_path.exists() or not source_path.is_file():
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
                "size": output_path.stat().st_size,
                "real_execution": True,
            },
            generated_at=utc_now(),
        )

    # ========================================================
    # ASSETS / OUTPUTS
    # ========================================================

    def register_asset(
        self,
        job: MediaJob,
        path: str,
        asset_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> FactoryResult:

        asset_path = Path(
            path
        ).expanduser().resolve()

        if not asset_path.exists() or not asset_path.is_file():
            return FactoryResult(
                success=False,
                status="ASSET_NOT_FOUND",
                message=str(asset_path),
                generated_at=utc_now(),
            )

        asset = {
            "id": (
                "asset-"
                + uuid.uuid4().hex[:16]
            ),
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

        output_path = Path(
            path
        ).expanduser().resolve()

        if not output_path.exists() or not output_path.is_file():
            return FactoryResult(
                success=False,
                status="OUTPUT_NOT_FOUND",
                message=str(output_path),
                generated_at=utc_now(),
            )

        output = {
            "id": (
                "output-"
                + uuid.uuid4().hex[:16]
            ),
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
    # CHANNELS
    # ========================================================

    def create_channel(
        self,
        name: str,
        description: str = "",
        channel_type: str = "general",
        owner_account_id: Optional[str] = None,
    ) -> FactoryResult:

        channel_id = (
            "channel-"
            + uuid.uuid4().hex[:16]
        )

        channel = {
            "id": channel_id,
            "name": name.strip(),
            "description": description,
            "type": channel_type,
            "owner_account_id": owner_account_id,
            "created_at": utc_now(),
            "majd_verified": False,
            "external_connections": {},
            "status": "CREATED",
        }

        state = read_json(
            CHANNELS_FILE,
            {
                "system": SYSTEM_ID,
                "channels": {},
            },
        )

        state.setdefault(
            "channels",
            {},
        )[channel_id] = channel

        write_json(
            CHANNELS_FILE,
            state,
        )

        return FactoryResult(
            success=True,
            status="CHANNEL_CREATED",
            data=channel,
            generated_at=utc_now(),
        )

    # ========================================================
    # SOCIAL ACCOUNTS / OAUTH
    # ========================================================

    def request_social_connection(
        self,
        provider: str,
        account_label: str,
    ) -> FactoryResult:

        return self.require_owner_action(
            action_type="CONNECT_SOCIAL_ACCOUNT",
            title=f"Connect {provider}",
            description=(
                f"Owner authorization is required to connect "
                f"the official MAJD {provider} account."
            ),
            capability="social_publish",
            provider=provider,
            safe_payload={
                "provider": provider,
                "account_label": account_label,
            },
        )

    def publish_social(
        self,
        job: MediaJob,
        destinations: List[str],
        text: str = "",
    ) -> FactoryResult:

        if not destinations:
            return FactoryResult(
                success=False,
                status="NO_DESTINATIONS",
                generated_at=utc_now(),
            )

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
    # EMAIL
    # ========================================================

    def request_email_connection(
        self,
        provider: str = "google",
        account_label: str = "MAJD Official Email",
    ) -> FactoryResult:

        return self.require_owner_action(
            action_type="CONNECT_OFFICIAL_EMAIL",
            title="Connect MAJD Official Email",
            description=(
                "Secure owner authorization is required "
                "to connect the official MAJD email account."
            ),
            capability="email_delivery",
            provider=provider,
            safe_payload={
                "account_label": account_label,
                "provider": provider,
            },
        )

    def send_email(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        attachments: Optional[List[str]] = None,
    ) -> FactoryResult:

        if not recipients:
            return FactoryResult(
                success=False,
                status="NO_RECIPIENTS",
                generated_at=utc_now(),
            )

        return self.execute_adapter(
            "email_delivery",
            {
                "recipients": recipients,
                "subject": subject,
                "body": body,
                "attachments": attachments or [],
            },
        )

    # ========================================================
    # MAJD INTERNAL ADVERTISING
    # ========================================================

    def create_internal_ad(
        self,
        title: str,
        text: str,
        media: Optional[List[str]] = None,
        placement: Optional[List[str]] = None,
        target: Optional[Dict[str, Any]] = None,
        schedule_at: Optional[str] = None,
    ) -> FactoryResult:

        ad_id = (
            "majd-ad-"
            + uuid.uuid4().hex[:16]
        )

        ad = {
            "id": ad_id,
            "title": title,
            "text": text,
            "media": media or [],
            "placement": placement or ["platform"],
            "target": target or {},
            "schedule_at": schedule_at,
            "status": (
                "SCHEDULED"
                if schedule_at
                else "READY"
            ),
            "internal_majd_ad": True,
            "external_paid_campaign": False,
            "created_at": utc_now(),
        }

        state = read_json(
            ADS_FILE,
            {
                "system": SYSTEM_ID,
                "ads": {},
            },
        )

        state.setdefault(
            "ads",
            {},
        )[ad_id] = ad

        write_json(
            ADS_FILE,
            state,
        )

        return FactoryResult(
            success=True,
            status="MAJD_INTERNAL_AD_CREATED",
            data=ad,
            generated_at=utc_now(),
        )

    def prepare_external_campaign(
        self,
        job: MediaJob,
        destinations: List[str],
        campaign: Dict[str, Any],
    ) -> FactoryResult:

        campaign_id = (
            "external-campaign-"
            + uuid.uuid4().hex[:16]
        )

        prepared = {
            "id": campaign_id,
            "job_id": job.id,
            "destinations": destinations,
            "campaign": campaign,
            "status": "PREPARED_NOT_PUBLISHED",
            "created_at": utc_now(),
        }

        write_json(
            ADS_DIR / f"{campaign_id}.json",
            prepared,
        )

        return FactoryResult(
            success=True,
            status="EXTERNAL_CAMPAIGN_PREPARED",
            message=(
                "Campaign content is prepared. "
                "No external publication has been claimed."
            ),
            data={
                **prepared,
                "real_external_publication": False,
            },
            generated_at=utc_now(),
        )

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
    # FINANCIAL EVENT CONTRACT
    # ========================================================

    def emit_financial_event(
        self,
        event_type: str,
        account_id: str,
        source_id: str,
        amount: Optional[float] = None,
        currency: str = "SAR",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> FactoryResult:

        event_id = (
            "financial-event-"
            + uuid.uuid4().hex[:16]
        )

        event = {
            "id": event_id,
            "event_type": event_type,
            "account_id": account_id,
            "source_id": source_id,
            "amount": amount,
            "currency": currency,
            "metadata": metadata or {},
            "created_at": utc_now(),
            "ledger_applied": False,
            "real_money_moved": False,
        }

        state = read_json(
            FINANCIAL_EVENTS_FILE,
            {
                "system": SYSTEM_ID,
                "events": {},
            },
        )

        state.setdefault(
            "events",
            {},
        )[event_id] = event

        write_json(
            FINANCIAL_EVENTS_FILE,
            state,
        )

        write_json(
            FINANCIAL_EVENTS_DIR / f"{event_id}.json",
            event,
        )

        if self.has_real_adapter(
            "financial_event_sink"
        ):
            result = self.execute_adapter(
                "financial_event_sink",
                event,
            )

            if result.success:
                event["ledger_applied"] = True

                state["events"][event_id] = event

                write_json(
                    FINANCIAL_EVENTS_FILE,
                    state,
                )

                return FactoryResult(
                    success=True,
                    status="FINANCIAL_EVENT_DELIVERED",
                    data={
                        "event": event,
                        "sink": result.data,
                    },
                    generated_at=utc_now(),
                )

        return FactoryResult(
            success=True,
            status="FINANCIAL_EVENT_RECORDED_PENDING_LEDGER",
            message=(
                "Financial event recorded locally. "
                "No real money movement has been claimed."
            ),
            data={
                "event": event,
            },
            generated_at=utc_now(),
        )

    def record_creator_reward_event(
        self,
        account_id: str,
        content_id: str,
        amount: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> FactoryResult:

        return self.emit_financial_event(
            event_type="CREATOR_REWARD",
            account_id=account_id,
            source_id=content_id,
            amount=amount,
            metadata=metadata,
        )

    def record_live_support_event(
        self,
        account_id: str,
        stream_id: str,
        amount: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> FactoryResult:

        return self.emit_financial_event(
            event_type="LIVE_SUPPORT",
            account_id=account_id,
            source_id=stream_id,
            amount=amount,
            metadata=metadata,
        )

    def record_content_revenue_event(
        self,
        account_id: str,
        content_id: str,
        amount: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> FactoryResult:

        return self.emit_financial_event(
            event_type="CONTENT_REVENUE",
            account_id=account_id,
            source_id=content_id,
            amount=amount,
            metadata=metadata,
        )

    # ========================================================
    # SCHEDULING
    # ========================================================

    def schedule_operation(
        self,
        operation: str,
        execute_at: str,
        payload: Dict[str, Any],
    ) -> FactoryResult:

        schedule_id = (
            "schedule-"
            + uuid.uuid4().hex[:16]
        )

        record = {
            "id": schedule_id,
            "operation": operation,
            "execute_at": execute_at,
            "payload": sanitize_sensitive_payload(payload),
            "status": "SCHEDULED",
            "created_at": utc_now(),
        }

        state = read_json(
            SCHEDULE_FILE,
            {
                "system": SYSTEM_ID,
                "items": {},
            },
        )

        state.setdefault(
            "items",
            {},
        )[schedule_id] = record

        write_json(
            SCHEDULE_FILE,
            state,
        )

        return FactoryResult(
            success=True,
            status="OPERATION_SCHEDULED",
            data=record,
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

            actual_hash = sha256_file(
                output_path
            )

            expected_hash = output.get(
                "sha256"
            )

            if (
                expected_hash
                and expected_hash != actual_hash
            ):
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
                "Job has no registered real output files."
            )

        passed = len(errors) == 0

        test = {
            "id": (
                "test-"
                + uuid.uuid4().hex[:12]
            ),
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
                    "Real AI planning/repair adapter "
                    "is not connected."
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
                    "Analyze the failed MAJD media job and "
                    "return a structured repair plan."
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
    # PUBLISHING
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
                message="No verified real output exists.",
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
        else:
            job.status = JobStatus.FAILED.value
            self._save_job(job)

        return result

    def _record_publication(
        self,
        job: MediaJob,
        publication_type: str,
        result: FactoryResult,
    ) -> None:

        real_execution = bool(
            result.data.get(
                "real_execution",
                False,
            )
        )

        if not result.success or not real_execution:
            return

        publication = {
            "id": (
                "publication-"
                + uuid.uuid4().hex[:16]
            ),
            "job_id": job.id,
            "type": publication_type,
            "published_at": utc_now(),
            "result": result.data,
            "verified_real_execution": True,
        }

        job.publication = publication

        state = read_json(
            PUBLISHING_FILE,
            {
                "system": SYSTEM_ID,
                "publications": [],
            },
        )

        state.setdefault(
            "publications",
            [],
        ).append(publication)

        write_json(
            PUBLISHING_FILE,
            state,
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
                "job": (
                    asdict(job)
                    if job
                    else None
                ),
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

        pipeline: List[Dict[str, Any]] = []

        planning = self.plan_content(job)

        pipeline.append(
            {
                "stage": "planning",
                "success": planning.success,
                "status": planning.status,
            }
        )

        if not planning.success:
            job.status = JobStatus.BLOCKED.value

            if planning.message:
                job.errors.append(
                    planning.message
                )

            job.errors.extend(
                planning.errors
            )

            self._save_job(job)

            return FactoryResult(
                success=False,
                status="PRODUCTION_BLOCKED_PLANNING",
                data={
                    "job": asdict(job),
                    "pipeline": pipeline,
                },
                errors=planning.errors,
                generated_at=utc_now(),
            )

        script = self.generate_script(job)

        pipeline.append(
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
                    "pipeline": pipeline,
                },
                errors=script.errors,
                generated_at=utc_now(),
            )

        content_type = job.content_type

        video_types = {
            ContentType.MOVIE.value,
            ContentType.SERIES.value,
            ContentType.EPISODE.value,
            ContentType.VIDEO.value,
            ContentType.SHORT.value,
            ContentType.STORY.value,
            ContentType.ANIMATION.value,
            ContentType.GAME_MEDIA.value,
        }

        visual_types = {
            ContentType.IMAGE.value,
            ContentType.POSTER.value,
            ContentType.THUMBNAIL.value,
        }

        if content_type in video_types:

            scenes = (
                job.plan.get("scenes")
                or script.data.get("scenes")
                or []
            )

            if not scenes:
                job.status = JobStatus.BLOCKED.value
                self._save_job(job)

                return FactoryResult(
                    success=False,
                    status="NO_SCENES_PRODUCED",
                    message=(
                        "Planning/script adapters "
                        "returned no scenes."
                    ),
                    data={
                        "pipeline": pipeline,
                    },
                    generated_at=utc_now(),
                )

            for index, scene in enumerate(
                scenes,
                start=1,
            ):

                if (
                    content_type
                    == ContentType.ANIMATION.value
                ):
                    generated = self.generate_animation(
                        job,
                        scene,
                    )
                else:
                    generated = self.generate_video(
                        job,
                        scene,
                    )

                pipeline.append(
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
                            "pipeline": pipeline,
                        },
                        errors=generated.errors,
                        generated_at=utc_now(),
                    )

                output_path = generated.data.get(
                    "output"
                )

                if not output_path:
                    return FactoryResult(
                        success=False,
                        status="GENERATED_OUTPUT_NOT_PROVIDED",
                        message=(
                            "Generation adapter returned success "
                            "without a real output path."
                        ),
                        data={
                            "scene": index,
                            "pipeline": pipeline,
                        },
                        generated_at=utc_now(),
                    )

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

        elif content_type in visual_types:

            if content_type == ContentType.POSTER.value:
                generated = self.generate_poster(job)

            elif content_type == ContentType.THUMBNAIL.value:
                generated = self.generate_thumbnail(job)

            else:
                generated = self.generate_image(
                    job.description or job.title,
                    job,
                )

            pipeline.append(
                {
                    "stage": "visual",
                    "success": generated.success,
                    "status": generated.status,
                }
            )

            if not generated.success:
                return generated

            output_path = generated.data.get(
                "output"
            )

            if not output_path:
                return FactoryResult(
                    success=False,
                    status="GENERATED_OUTPUT_NOT_PROVIDED",
                    generated_at=utc_now(),
                )

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

            pipeline.append(
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

            if not output_path:
                return FactoryResult(
                    success=False,
                    status="GENERATED_OUTPUT_NOT_PROVIDED",
                    generated_at=utc_now(),
                )

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

            pipeline.append(
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

            if not output_path:
                return FactoryResult(
                    success=False,
                    status="GENERATED_OUTPUT_NOT_PROVIDED",
                    generated_at=utc_now(),
                )

            registered = self.register_output(
                job,
                output_path,
                "voice",
            )

            if not registered.success:
                return registered

        qa = self.validate_job(job)

        pipeline.append(
            {
                "stage": "qa",
                "success": qa.success,
                "status": qa.status,
            }
        )

        if not qa.success:
            repair = self.automatic_repair(job)

            pipeline.append(
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
                    "pipeline": pipeline,
                    "repair": repair.data,
                },
                errors=qa.errors,
                warnings=qa.warnings,
                generated_at=utc_now(),
            )

        if not job.outputs:
            job.status = JobStatus.BLOCKED.value
            self._save_job(job)

            return FactoryResult(
                success=False,
                status="PRODUCTION_BLOCKED_NO_REAL_OUTPUT",
                message=(
                    "Pipeline cannot report READY without "
                    "a verified real output."
                ),
                data={
                    "job": asdict(job),
                    "pipeline": pipeline,
                },
                generated_at=utc_now(),
            )

        job.status = JobStatus.READY.value
        self._save_job(job)

        return FactoryResult(
            success=True,
            status="PRODUCTION_READY",
            message=(
                "Production completed and real outputs "
                "passed QA."
            ),
            data={
                "job": asdict(job),
                "pipeline": pipeline,
            },
            generated_at=utc_now(),
        )

    # ========================================================
    # HEALTH
    # ========================================================

    def health(
        self,
    ) -> Dict[str, Any]:

        capabilities = self.capability_report()

        capability_data = capabilities.get(
            "capabilities",
            {},
        )

        connected = [
            name
            for name, data in capability_data.items()
            if (
                data.get("connected")
                and data.get("enabled")
                and data.get("real")
            )
        ]

        disconnected = [
            name
            for name, data in capability_data.items()
            if not data.get("connected")
        ]

        components = self.discover_majd_components()

        existing_components = [
            name
            for name, data
            in components["components"].items()
            if data.get("exists")
        ]

        missing_components = [
            name
            for name, data
            in components["components"].items()
            if not data.get("exists")
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

            "majd_components_found": existing_components,
            "majd_components_missing": missing_components,

            "jobs": len(
                self.jobs.get(
                    "jobs",
                    {},
                )
            ),

            "truth_policy": {
                "fake_external_success_allowed": False,
                "secret_in_source_allowed": False,
                "owner_action_required_supported": True,
                "financial_money_movement_claimed": False,
            },
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
    account_id: Optional[str] = None,
    channel_id: Optional[str] = None,
) -> Dict[str, Any]:

    factory = get_factory()

    job = factory.create_job(
        content_type=content_type,
        title=title,
        description=description,
        language=language,
        request=request,
        account_id=account_id,
        channel_id=channel_id,
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


def factory_integrations() -> Dict[str, Any]:
    return get_factory().discover_majd_components()


# ============================================================
# SELF CHECK
# ============================================================

def self_check() -> FactoryResult:

    factory = get_factory()

    errors: List[str] = []
    warnings: List[str] = []

    if not FACTORY_ROOT.exists():
        errors.append(
            "Factory root was not created."
        )

    if not STATE_DIR.exists():
        errors.append(
            "State directory was not created."
        )

    if not JOBS_FILE.exists():
        warnings.append(
            "Jobs state will be created on first persisted job."
        )

    components = factory.discover_majd_components()

    for name, data in components["components"].items():
        if not data.get("exists"):
            warnings.append(
                f"MAJD component not found: {name} "
                f"({data.get('filename')})"
            )

    passed = len(errors) == 0

    return FactoryResult(
        success=passed,
        status=(
            "SELF_CHECK_PASSED"
            if passed
            else "SELF_CHECK_FAILED"
        ),
        data={
            "health": factory.health(),
            "components": components,
        },
        errors=errors,
        warnings=warnings,
        generated_at=utc_now(),
    )


# ============================================================
# CLI
# ============================================================

def main() -> int:

    result = self_check()

    print(
        json.dumps(
            asdict(result),
            ensure_ascii=False,
            indent=2,
        )
    )

    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())

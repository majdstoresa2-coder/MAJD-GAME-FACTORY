#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py
============================================================

OFFICIAL MAJD PLATFORM BRIDGE
VERSION 2.1.0

المسؤوليات:
- استقبال Playable Artifact الحقيقي من المنفذ 03.
- التحقق من أن الـ Artifact موجود فعلياً.
- التحقق من وجود index.html.
- فحص جميع ملفات اللعبة.
- بناء Manifest حقيقي.
- بناء Package موثق بدون نجاح وهمي.
- نشر اللعبة داخل public/artifacts.
- إنشاء Game ID ثابت لكل عملية.
- التحقق من النسخة المنشورة بعد النسخ.
- التحقق من SHA256 لجميع الملفات.
- إنشاء metadata للنشر.
- توفير public_url حقيقي.
- دعم API الحديث publish_game().
- دعم واجهة التوافق القديمة:
    ManifestBuilder
    PackageBuilder
    MajdPlatformClient
- منع النجاح الوهمي.
- عدم إعلان PUBLISHED إلا بعد التحقق الحقيقي.

السلسلة:

01 MASTERMIND
      ↓
03 REAL GAME EXECUTOR
      ↓
PLAYABLE ARTIFACT
      ↓
04 OFFICIAL PLATFORM BRIDGE
      ↓
VERIFY SOURCE
      ↓
MANIFEST
      ↓
PACKAGE
      ↓
COPY TO PUBLIC
      ↓
VERIFY PUBLISHED COPY
      ↓
PUBLIC URL
      ↓
https://majd.shop/artifacts/<game-id>/index.html
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import uuid

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ============================================================
# IDENTITY
# ============================================================

SYSTEM_NAME = "MAJD-GAME-FACTORY"
BRIDGE_NAME = "MAJD-OFFICIAL-PLATFORM-BRIDGE"
VERSION = "2.1.0"
SCHEMA_VERSION = "1"

OFFICIAL_PLATFORM_URL = os.getenv(
    "MAJD_OFFICIAL_PLATFORM_URL",
    "https://majd.shop",
).rstrip("/")


# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent

PUBLIC_DIR = ROOT_DIR / "public"
ARTIFACTS_DIR = PUBLIC_DIR / "artifacts"

STATE_DIR = ROOT_DIR / "majd_factory_state"
PUBLISH_DIR = STATE_DIR / "published"
MANIFEST_DIR = STATE_DIR / "manifests"
PACKAGE_DIR = STATE_DIR / "packages"
RECEIPT_DIR = STATE_DIR / "receipts"
TMP_DIR = STATE_DIR / "tmp"


def ensure_directories() -> None:
    for directory in (
        PUBLIC_DIR,
        ARTIFACTS_DIR,
        STATE_DIR,
        PUBLISH_DIR,
        MANIFEST_DIR,
        PACKAGE_DIR,
        RECEIPT_DIR,
        TMP_DIR,
    ):
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )


ensure_directories()


# ============================================================
# TIME
# ============================================================

def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


# ============================================================
# SAFE VALUES
# ============================================================

def safe_text(
    value: Any,
    default: str = "",
) -> str:
    if value is None:
        return default

    text = str(value).strip()

    return text or default


def safe_identifier(
    value: Any,
    fallback: Optional[str] = None,
    max_length: int = 120,
) -> str:
    raw = safe_text(
        value,
        fallback or str(uuid.uuid4()),
    )

    result: List[str] = []

    for char in raw:
        if (
            char.isalnum()
            or char in ("-", "_", ".")
        ):
            result.append(char)
        else:
            result.append("-")

    cleaned = "".join(
        result
    )

    while "--" in cleaned:
        cleaned = cleaned.replace(
            "--",
            "-",
        )

    cleaned = cleaned.strip(
        "-_."
    )

    if not cleaned:
        cleaned = fallback or str(
            uuid.uuid4()
        )

    return cleaned[:max_length]


# ============================================================
# JSON
# ============================================================

def atomic_write_json(
    path: Path,
    data: Any,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fd, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".",
        suffix=".tmp",
        dir=str(path.parent),
    )

    try:
        with os.fdopen(
            fd,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
                default=str,
            )

            file.flush()
            os.fsync(
                file.fileno()
            )

        os.replace(
            temporary_name,
            path,
        )

    finally:
        if os.path.exists(
            temporary_name
        ):
            os.unlink(
                temporary_name
            )


def load_json(
    path: Path,
    default: Any = None,
) -> Any:
    if not path.exists():
        return default

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(
            file
        )


# ============================================================
# HASH
# ============================================================

def sha256_file(
    path: Path,
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
# PATH NORMALIZATION
# ============================================================

def normalize_artifact_path(
    value: Any,
) -> Path:
    path = Path(
        str(value)
    ).expanduser()

    if not path.is_absolute():
        path = (
            ROOT_DIR
            /
            path
        )

    return path.resolve()


# ============================================================
# ARTIFACT FILE COLLECTION
# ============================================================

def collect_files(
    directory: Path,
) -> Dict[str, Path]:
    files: Dict[
        str,
        Path
    ] = {}

    for path in directory.rglob(
        "*"
    ):
        if not path.is_file():
            continue

        relative = str(
            path.relative_to(
                directory
            )
        )

        files[
            relative
        ] = path

    return files


# ============================================================
# SOURCE VERIFICATION
# ============================================================

def verify_source_artifact(
    artifact: Path,
) -> Dict[str, Any]:
    artifact = artifact.resolve()

    if not artifact.exists():
        return {
            "success": False,
            "status": "SOURCE_ARTIFACT_NOT_FOUND",
            "artifact": str(
                artifact
            ),
        }

    if not artifact.is_dir():
        return {
            "success": False,
            "status": "SOURCE_ARTIFACT_NOT_DIRECTORY",
            "artifact": str(
                artifact
            ),
        }

    index_file = (
        artifact
        /
        "index.html"
    )

    if not index_file.exists():
        return {
            "success": False,
            "status": "SOURCE_INDEX_NOT_FOUND",
            "artifact": str(
                artifact
            ),
        }

    if not index_file.is_file():
        return {
            "success": False,
            "status": "SOURCE_INDEX_NOT_FILE",
            "artifact": str(
                artifact
            ),
        }

    if (
        index_file.stat().st_size
        <=
        0
    ):
        return {
            "success": False,
            "status": "SOURCE_INDEX_EMPTY",
            "artifact": str(
                artifact
            ),
        }

    files = collect_files(
        artifact
    )

    if not files:
        return {
            "success": False,
            "status": "SOURCE_ARTIFACT_EMPTY",
            "artifact": str(
                artifact
            ),
        }

    manifest: List[
        Dict[str, Any]
    ] = []

    total_bytes = 0

    for relative_path, file_path in sorted(
        files.items()
    ):
        size = (
            file_path.stat().st_size
        )

        total_bytes += size

        manifest.append(
            {
                "path": relative_path,
                "size": size,
                "sha256": sha256_file(
                    file_path
                ),
            }
        )

    return {
        "success": True,
        "status": "SOURCE_ARTIFACT_VERIFIED",
        "artifact": str(
            artifact
        ),
        "index": str(
            index_file
        ),
        "file_count": len(
            files
        ),
        "size_bytes": total_bytes,
        "manifest": manifest,
    }


# ============================================================
# COPY ARTIFACT
# ============================================================

def copy_artifact(
    source: Path,
    destination: Path,
) -> None:
    source = source.resolve()
    destination = destination.resolve()

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if destination.exists():
        shutil.rmtree(
            destination
        )

    shutil.copytree(
        source,
        destination,
    )


# ============================================================
# PUBLISHED VERIFICATION
# ============================================================

def verify_published_artifact(
    source: Path,
    destination: Path,
) -> Dict[str, Any]:
    source = source.resolve()
    destination = destination.resolve()

    if not destination.exists():
        return {
            "success": False,
            "status": "PUBLISHED_ARTIFACT_NOT_FOUND",
            "destination": str(
                destination
            ),
        }

    if not destination.is_dir():
        return {
            "success": False,
            "status": "PUBLISHED_ARTIFACT_NOT_DIRECTORY",
            "destination": str(
                destination
            ),
        }

    index_file = (
        destination
        /
        "index.html"
    )

    if not index_file.exists():
        return {
            "success": False,
            "status": "PUBLISHED_INDEX_NOT_FOUND",
            "destination": str(
                destination
            ),
        }

    if (
        index_file.stat().st_size
        <=
        0
    ):
        return {
            "success": False,
            "status": "PUBLISHED_INDEX_EMPTY",
            "destination": str(
                destination
            ),
        }

    source_files = collect_files(
        source
    )

    destination_files = collect_files(
        destination
    )

    source_names = set(
        source_files.keys()
    )

    destination_names = set(
        destination_files.keys()
    )

    if (
        source_names
        !=
        destination_names
    ):
        return {
            "success": False,
            "status": "PUBLISHED_FILE_SET_MISMATCH",
            "missing": sorted(
                source_names
                -
                destination_names
            ),
            "unexpected": sorted(
                destination_names
                -
                source_names
            ),
            "source_count": len(
                source_names
            ),
            "published_count": len(
                destination_names
            ),
        }

    mismatches: List[
        Dict[str, Any]
    ] = []

    manifest: List[
        Dict[str, Any]
    ] = []

    total_bytes = 0

    for relative_path in sorted(
        source_files.keys()
    ):
        source_file = (
            source_files[
                relative_path
            ]
        )

        destination_file = (
            destination_files[
                relative_path
            ]
        )

        source_hash = sha256_file(
            source_file
        )

        destination_hash = sha256_file(
            destination_file
        )

        destination_size = (
            destination_file
            .stat()
            .st_size
        )

        total_bytes += (
            destination_size
        )

        manifest.append(
            {
                "path":
                    relative_path,
                "size":
                    destination_size,
                "sha256":
                    destination_hash,
            }
        )

        if (
            source_hash
            !=
            destination_hash
        ):
            mismatches.append(
                {
                    "path":
                        relative_path,
                    "source_sha256":
                        source_hash,
                    "published_sha256":
                        destination_hash,
                }
            )

    if mismatches:
        return {
            "success": False,
            "status": "PUBLISHED_HASH_MISMATCH",
            "mismatches": mismatches,
        }

    return {
        "success": True,
        "status": "PUBLISHED_ARTIFACT_VERIFIED",
        "index": str(
            index_file
        ),
        "file_count": len(
            manifest
        ),
        "size_bytes": total_bytes,
        "manifest": manifest,
    }


# ============================================================
# GAME ID
# ============================================================

def build_game_id(
    job_id: str,
) -> str:
    return safe_identifier(
        job_id,
        fallback=str(
            uuid.uuid4()
        ),
    )


# ============================================================
# PUBLICATION METADATA
# ============================================================

def create_publication_metadata(
    game_id: str,
    game_name: str,
    job_id: str,
    artifact: Path,
    published_dir: Path,
    verification: Dict[str, Any],
    request: Optional[
        Dict[str, Any]
    ] = None,
) -> Dict[str, Any]:
    relative_game_path = (
        f"/artifacts/"
        f"{game_id}/"
        f"index.html"
    )

    public_url = (
        OFFICIAL_PLATFORM_URL
        +
        relative_game_path
    )

    return {
        "schema_version":
            SCHEMA_VERSION,
        "system":
            SYSTEM_NAME,
        "bridge":
            BRIDGE_NAME,
        "version":
            VERSION,
        "game_id":
            game_id,
        "game_name":
            game_name,
        "job_id":
            job_id,
        "source_artifact":
            str(
                artifact
            ),
        "published_directory":
            str(
                published_dir
            ),
        "game_path":
            relative_game_path,
        "public_url":
            public_url,
        "published_at":
            utc_now(),
        "verification":
            verification,
        "request":
            request
            or {},
    }


# ============================================================
# MANIFEST BUILDER
# ============================================================

class ManifestBuilder:
    """
    Compatibility API expected by existing MAJD agent.

    It performs real artifact verification before returning
    a manifest.
    """

    def build(
        self,
        game_dir: Path,
        game_name: str,
        game_version: str = "1.0.0",
        metadata: Optional[
            Dict[str, Any]
        ] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        source = normalize_artifact_path(
            game_dir
        )

        verification = (
            verify_source_artifact(
                source
            )
        )

        if not verification.get(
            "success"
        ):
            raise RuntimeError(
                verification.get(
                    "status",
                    "SOURCE_VERIFICATION_FAILED",
                )
            )

        actual_metadata = dict(
            metadata
            or {}
        )

        job_id = safe_text(
            actual_metadata.get(
                "job_id"
            ),
            str(
                uuid.uuid4()
            ),
        )

        manifest = {
            "schema_version":
                SCHEMA_VERSION,
            "system":
                SYSTEM_NAME,
            "bridge":
                BRIDGE_NAME,
            "bridge_version":
                VERSION,
            "game_name":
                safe_text(
                    game_name,
                    "MAJD-GAME",
                ),
            "game_version":
                safe_text(
                    game_version,
                    "1.0.0",
                ),
            "job_id":
                job_id,
            "game_dir":
                str(
                    source
                ),
            "created_at":
                utc_now(),
            "metadata":
                actual_metadata,
            "source_verification":
                verification,
            "files":
                verification.get(
                    "manifest",
                    [],
                ),
        }

        manifest_file = (
            MANIFEST_DIR
            /
            f"{build_game_id(job_id)}.json"
        )

        atomic_write_json(
            manifest_file,
            manifest,
        )

        manifest[
            "manifest_file"
        ] = str(
            manifest_file
        )

        return manifest


# ============================================================
# PACKAGE BUILDER
# ============================================================

class PackageBuilder:
    """
    Compatibility API expected by existing MAJD agent.

    No fake archive is created.

    The playable artifact directory itself is treated as the
    verified publishable package after checking that it matches
    the manifest generated by ManifestBuilder.
    """

    def build(
        self,
        game_dir: Path,
        manifest: Dict[str, Any],
        **kwargs: Any,
    ) -> Path:
        source = normalize_artifact_path(
            game_dir
        )

        verification = (
            verify_source_artifact(
                source
            )
        )

        if not verification.get(
            "success"
        ):
            raise RuntimeError(
                verification.get(
                    "status",
                    "PACKAGE_SOURCE_INVALID",
                )
            )

        if not isinstance(
            manifest,
            dict,
        ):
            raise TypeError(
                "MANIFEST_MUST_BE_DICT"
            )

        manifest_dir = safe_text(
            manifest.get(
                "game_dir"
            )
        )

        if manifest_dir:
            expected = normalize_artifact_path(
                manifest_dir
            )

            if expected != source:
                raise RuntimeError(
                    "PACKAGE_MANIFEST_SOURCE_MISMATCH"
                )

        expected_files = {
            item.get(
                "path"
            ):
            item.get(
                "sha256"
            )
            for item in manifest.get(
                "files",
                []
            )
            if isinstance(
                item,
                dict,
            )
            and item.get(
                "path"
            )
        }

        actual_files = {
            item.get(
                "path"
            ):
            item.get(
                "sha256"
            )
            for item in verification.get(
                "manifest",
                []
            )
            if isinstance(
                item,
                dict,
            )
            and item.get(
                "path"
            )
        }

        if (
            expected_files
            and
            expected_files
            !=
            actual_files
        ):
            raise RuntimeError(
                "PACKAGE_MANIFEST_HASH_MISMATCH"
            )

        job_id = safe_text(
            manifest.get(
                "job_id"
            ),
            str(
                uuid.uuid4()
            ),
        )

        package_record = {
            "schema_version":
                SCHEMA_VERSION,
            "system":
                SYSTEM_NAME,
            "bridge":
                BRIDGE_NAME,
            "version":
                VERSION,
            "job_id":
                job_id,
            "package_path":
                str(
                    source
                ),
            "package_type":
                "PLAYABLE_DIRECTORY",
            "verification":
                verification,
            "created_at":
                utc_now(),
        }

        package_file = (
            PACKAGE_DIR
            /
            f"{build_game_id(job_id)}.json"
        )

        atomic_write_json(
            package_file,
            package_record,
        )

        return source


# ============================================================
# RECEIPT
# ============================================================

@dataclass
class PublicationReceipt:
    success: bool
    status: str
    system: str
    bridge: str
    version: str

    game_id: Optional[str] = None
    game_name: Optional[str] = None
    job_id: Optional[str] = None

    artifact: Optional[str] = None
    package_path: Optional[str] = None

    published_directory: Optional[str] = None
    game_path: Optional[str] = None
    public_url: Optional[str] = None
    metadata: Optional[str] = None

    error: Optional[str] = None

    started_at: Optional[str] = None
    finished_at: Optional[str] = None

    details: Dict[
        str,
        Any
    ] = None

    def __post_init__(
        self
    ) -> None:
        if self.details is None:
            self.details = {}

    def to_dict(
        self
    ) -> Dict[str, Any]:
        return asdict(
            self
        )


# ============================================================
# MAIN REAL PUBLISH FUNCTION
# ============================================================

def publish_game(
    game_dir: Optional[
        Path
    ] = None,
    game_name: str = "MAJD-GAME",
    job_id: str = "",
    artifact: Optional[
        Any
    ] = None,
    artifact_path: Optional[
        Any
    ] = None,
    build_path: Optional[
        Any
    ] = None,
    request: Optional[
        Dict[str, Any]
    ] = None,
    payload: Optional[
        Dict[str, Any]
    ] = None,
    manifest: Optional[
        Dict[str, Any]
    ] = None,
    package_path: Optional[
        Any
    ] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    started_at = utc_now()

    source_value = (
        game_dir
        or artifact
        or artifact_path
        or build_path
        or package_path
    )

    if source_value is None:
        return {
            "success": False,
            "status": "ARTIFACT_ARGUMENT_MISSING",
            "bridge": BRIDGE_NAME,
            "version": VERSION,
            "finished_at": utc_now(),
        }

    try:
        source = normalize_artifact_path(
            source_value
        )

        source_verification = (
            verify_source_artifact(
                source
            )
        )

        if not source_verification.get(
            "success"
        ):
            return {
                "success": False,
                "status":
                    source_verification.get(
                        "status",
                        "SOURCE_VERIFICATION_FAILED",
                    ),
                "bridge":
                    BRIDGE_NAME,
                "version":
                    VERSION,
                "source_verification":
                    source_verification,
                "finished_at":
                    utc_now(),
            }

        actual_request = (
            request
            or payload
            or {}
        )

        if manifest and isinstance(
            manifest,
            dict,
        ):
            if (
                not job_id
                and manifest.get(
                    "job_id"
                )
            ):
                job_id = safe_text(
                    manifest.get(
                        "job_id"
                    )
                )

            if (
                (
                    not game_name
                    or game_name
                    ==
                    "MAJD-GAME"
                )
                and manifest.get(
                    "game_name"
                )
            ):
                game_name = safe_text(
                    manifest.get(
                        "game_name"
                    ),
                    game_name,
                )

        if (
            (
                not game_name
                or game_name
                ==
                "MAJD-GAME"
            )
            and isinstance(
                actual_request,
                dict,
            )
        ):
            game_name = safe_text(
                actual_request.get(
                    "name"
                ),
                game_name,
            )

        if not job_id:
            if isinstance(
                actual_request,
                dict,
            ):
                job_id = safe_text(
                    actual_request.get(
                        "job_id"
                    )
                )

        if not job_id:
            job_id = str(
                uuid.uuid4()
            )

        game_id = build_game_id(
            job_id
        )

        published_dir = (
            ARTIFACTS_DIR
            /
            game_id
        )

        copy_artifact(
            source,
            published_dir,
        )

        published_verification = (
            verify_published_artifact(
                source,
                published_dir,
            )
        )

        if not published_verification.get(
            "success"
        ):
            if published_dir.exists():
                shutil.rmtree(
                    published_dir,
                    ignore_errors=True,
                )

            return {
                "success": False,
                "status":
                    published_verification.get(
                        "status",
                        "PUBLISH_VERIFICATION_FAILED",
                    ),
                "bridge":
                    BRIDGE_NAME,
                "version":
                    VERSION,
                "game_id":
                    game_id,
                "published_directory":
                    str(
                        published_dir
                    ),
                "verification":
                    published_verification,
                "finished_at":
                    utc_now(),
            }

        metadata = (
            create_publication_metadata(
                game_id=
                    game_id,
                game_name=
                    game_name,
                job_id=
                    str(
                        job_id
                    ),
                artifact=
                    source,
                published_dir=
                    published_dir,
                verification=
                    published_verification,
                request=
                    actual_request,
            )
        )

        if manifest:
            metadata[
                "manifest"
            ] = manifest

        metadata_file = (
            PUBLISH_DIR
            /
            f"{game_id}.json"
        )

        atomic_write_json(
            metadata_file,
            metadata,
        )

        final_result = {
            "success":
                True,
            "status":
                "PUBLISHED",
            "system":
                SYSTEM_NAME,
            "bridge":
                BRIDGE_NAME,
            "version":
                VERSION,
            "game_id":
                game_id,
            "game_name":
                game_name,
            "job_id":
                str(
                    job_id
                ),
            "artifact":
                str(
                    source
                ),
            "published_directory":
                str(
                    published_dir
                ),
            "game_path":
                metadata[
                    "game_path"
                ],
            "public_url":
                metadata[
                    "public_url"
                ],
            "metadata":
                str(
                    metadata_file
                ),
            "source_verification":
                source_verification,
            "published_verification":
                published_verification,
            "started_at":
                started_at,
            "finished_at":
                utc_now(),
        }

        receipt_file = (
            RECEIPT_DIR
            /
            f"{game_id}.json"
        )

        atomic_write_json(
            receipt_file,
            final_result,
        )

        final_result[
            "receipt"
        ] = str(
            receipt_file
        )

        return final_result

    except Exception as error:
        return {
            "success":
                False,
            "status":
                "PLATFORM_BRIDGE_EXCEPTION",
            "system":
                SYSTEM_NAME,
            "bridge":
                BRIDGE_NAME,
            "version":
                VERSION,
            "error":
                (
                    f"{type(error).__name__}: "
                    f"{error}"
                ),
            "started_at":
                started_at,
            "finished_at":
                utc_now(),
        }


# ============================================================
# MAJD PLATFORM CLIENT
# ============================================================

class MajdPlatformClient:
    """
    Compatibility client used by the current MAJD AI Agent.

    This does not fake a remote publish.

    It forwards the verified playable package to the same real
    publish_game() implementation used by Bridge 04.
    """

    def publish(
        self,
        package_path: Any,
        manifest: Optional[
            Dict[str, Any]
        ] = None,
        **kwargs: Any,
    ) -> PublicationReceipt:
        actual_manifest = (
            manifest
            if isinstance(
                manifest,
                dict,
            )
            else {}
        )

        metadata = (
            actual_manifest.get(
                "metadata"
            )
            if isinstance(
                actual_manifest.get(
                    "metadata"
                ),
                dict,
            )
            else {}
        )

        job_id = safe_text(
            actual_manifest.get(
                "job_id"
            )
            or metadata.get(
                "job_id"
            ),
            str(
                uuid.uuid4()
            ),
        )

        game_name = safe_text(
            actual_manifest.get(
                "game_name"
            ),
            "MAJD-GAME",
        )

        result = publish_game(
            package_path=
                package_path,
            game_name=
                game_name,
            job_id=
                job_id,
            manifest=
                actual_manifest,
            request=
                {
                    "name":
                        game_name,
                    "job_id":
                        job_id,
                    "manifest":
                        actual_manifest,
                },
        )

        receipt = PublicationReceipt(
            success=bool(
                result.get(
                    "success"
                )
            ),
            status=safe_text(
                result.get(
                    "status"
                ),
                "UNKNOWN",
            ),
            system=safe_text(
                result.get(
                    "system"
                ),
                SYSTEM_NAME,
            ),
            bridge=safe_text(
                result.get(
                    "bridge"
                ),
                BRIDGE_NAME,
            ),
            version=safe_text(
                result.get(
                    "version"
                ),
                VERSION,
            ),
            game_id=result.get(
                "game_id"
            ),
            game_name=result.get(
                "game_name"
            ),
            job_id=result.get(
                "job_id"
            ),
            artifact=result.get(
                "artifact"
            ),
            package_path=str(
                package_path
            ),
            published_directory=result.get(
                "published_directory"
            ),
            game_path=result.get(
                "game_path"
            ),
            public_url=result.get(
                "public_url"
            ),
            metadata=result.get(
                "metadata"
            ),
            error=result.get(
                "error"
            ),
            started_at=result.get(
                "started_at"
            ),
            finished_at=result.get(
                "finished_at"
            ),
            details=result,
        )

        return receipt


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

def publish(
    **kwargs: Any,
) -> Dict[str, Any]:
    return publish_game(
        **kwargs
    )


def send_game(
    **kwargs: Any,
) -> Dict[str, Any]:
    return publish_game(
        **kwargs
    )


def send_to_majd(
    **kwargs: Any,
) -> Dict[str, Any]:
    return publish_game(
        **kwargs
    )


def execute(
    **kwargs: Any,
) -> Dict[str, Any]:
    return publish_game(
        **kwargs
    )


# ============================================================
# HEALTH
# ============================================================

def health() -> Dict[str, Any]:
    return {
        "success": True,
        "system": SYSTEM_NAME,
        "bridge": BRIDGE_NAME,
        "version": VERSION,
        "status": "READY",
        "official_platform_url":
            OFFICIAL_PLATFORM_URL,
        "interfaces": {
            "publish_game":
                callable(
                    publish_game
                ),
            "publish":
                callable(
                    publish
                ),
            "send_game":
                callable(
                    send_game
                ),
            "send_to_majd":
                callable(
                    send_to_majd
                ),
            "execute":
                callable(
                    execute
                ),
            "ManifestBuilder":
                True,
            "PackageBuilder":
                True,
            "MajdPlatformClient":
                True,
        },
        "paths": {
            "root":
                str(
                    ROOT_DIR
                ),
            "public":
                str(
                    PUBLIC_DIR
                ),
            "artifacts":
                str(
                    ARTIFACTS_DIR
                ),
            "state":
                str(
                    STATE_DIR
                ),
        },
        "checked_at":
            utc_now(),
    }


# ============================================================
# CLI
# ============================================================

def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "MAJD OFFICIAL PLATFORM BRIDGE 04"
        )
    )

    parser.add_argument(
        "artifact",
        nargs="?",
        default=None,
        help=(
            "Playable artifact directory"
        ),
    )

    parser.add_argument(
        "--name",
        default="MAJD TEST GAME",
    )

    parser.add_argument(
        "--job-id",
        default=None,
    )

    parser.add_argument(
        "--health",
        action="store_true",
    )

    args = parser.parse_args()

    if args.health:
        result = health()

        print(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )

        return 0

    if not args.artifact:
        parser.error(
            "artifact is required unless --health is used"
        )

    job_id = (
        args.job_id
        or str(
            uuid.uuid4()
        )
    )

    result = publish_game(
        game_dir=Path(
            args.artifact
        ),
        game_name=args.name,
        job_id=job_id,
    )

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
            default=str,
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py
============================================================

OFFICIAL MAJD PLATFORM BRIDGE

المسؤوليات:
- استقبال Playable Artifact الحقيقي من 03.
- التحقق من أن الـArtifact موجود وصالح.
- التحقق من وجود index.html.
- نشر اللعبة داخل public/artifacts.
- إنشاء Game ID ثابت للعملية.
- التحقق من النسخة المنشورة بعد النسخ.
- إنشاء metadata وmanifest للنشر.
- منع النجاح الوهمي.
- إعادة مسار اللعبة المنشورة الحقيقي.
- التوافق مع العقل المدبر 01 و Runtime 06.

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
COPY TO PUBLIC
      ↓
VERIFY PUBLISHED COPY
      ↓
RETURN REAL GAME PATH
"""

from __future__ import annotations

import hashlib
import json
import shutil
import uuid

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ============================================================
# IDENTITY
# ============================================================

SYSTEM_NAME = "MAJD-GAME-FACTORY"

BRIDGE_NAME = "MAJD-OFFICIAL-PLATFORM-BRIDGE"

VERSION = "2.0.0"

OFFICIAL_PLATFORM_URL = "https://majd.shop"


# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent

PUBLIC_DIR = (
    ROOT_DIR
    /
    "public"
)

ARTIFACTS_DIR = (
    PUBLIC_DIR
    /
    "artifacts"
)

STATE_DIR = (
    ROOT_DIR
    /
    "majd_factory_state"
)

PUBLISH_DIR = (
    STATE_DIR
    /
    "published"
)


for directory in (
    PUBLIC_DIR,
    ARTIFACTS_DIR,
    STATE_DIR,
    PUBLISH_DIR,
):

    directory.mkdir(
        parents=True,
        exist_ok=True
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
# PATH NORMALIZATION
# ============================================================

def normalize_artifact_path(
    value: Any
) -> Path:

    path = Path(
        str(
            value
        )
    )

    if not path.is_absolute():

        path = (
            ROOT_DIR
            /
            path
        ).resolve()

    else:

        path = path.resolve()

    return path


# ============================================================
# VERIFY SOURCE ARTIFACT
# ============================================================

def verify_source_artifact(
    artifact: Path
) -> Dict[str, Any]:

    if not artifact.exists():

        return {

            "success":
                False,

            "status":
                "SOURCE_ARTIFACT_NOT_FOUND",

            "artifact":
                str(
                    artifact
                )
        }

    if not artifact.is_dir():

        return {

            "success":
                False,

            "status":
                "SOURCE_ARTIFACT_NOT_DIRECTORY",

            "artifact":
                str(
                    artifact
                )
        }

    index_file = (
        artifact
        /
        "index.html"
    )

    if not index_file.exists():

        return {

            "success":
                False,

            "status":
                "SOURCE_INDEX_NOT_FOUND",

            "artifact":
                str(
                    artifact
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
                "SOURCE_INDEX_EMPTY",

            "artifact":
                str(
                    artifact
                )
        }

    files = [

        path

        for path
        in artifact.rglob(
            "*"
        )

        if path.is_file()
    ]

    if len(
        files
    ) < 2:

        return {

            "success":
                False,

            "status":
                "SOURCE_ARTIFACT_TOO_SMALL",

            "artifact":
                str(
                    artifact
                )
        }

    return {

        "success":
            True,

        "status":
            "SOURCE_ARTIFACT_VERIFIED",

        "artifact":
            str(
                artifact
            ),

        "index":
            str(
                index_file
            ),

        "file_count":
            len(
                files
            )
    }


# ============================================================
# COPY ARTIFACT
# ============================================================

def copy_artifact(
    source: Path,
    destination: Path
) -> None:

    if destination.exists():

        shutil.rmtree(
            destination
        )

    shutil.copytree(
        source,
        destination
    )


# ============================================================
# VERIFY PUBLISHED ARTIFACT
# ============================================================

def verify_published_artifact(
    source: Path,
    destination: Path
) -> Dict[str, Any]:

    if not destination.exists():

        return {

            "success":
                False,

            "status":
                "PUBLISHED_ARTIFACT_NOT_FOUND"
        }

    index_file = (
        destination
        /
        "index.html"
    )

    if not index_file.exists():

        return {

            "success":
                False,

            "status":
                "PUBLISHED_INDEX_NOT_FOUND"
        }

    source_files = {

        str(
            path.relative_to(
                source
            )
        ):
            path

        for path
        in source.rglob(
            "*"
        )

        if path.is_file()
    }

    destination_files = {

        str(
            path.relative_to(
                destination
            )
        ):
            path

        for path
        in destination.rglob(
            "*"
        )

        if path.is_file()
    }

    if (
        set(
            source_files.keys()
        )
        !=
        set(
            destination_files.keys()
        )
    ):

        return {

            "success":
                False,

            "status":
                "PUBLISHED_FILE_SET_MISMATCH",

            "source_count":
                len(
                    source_files
                ),

            "published_count":
                len(
                    destination_files
                )
        }

    mismatches: List[
        Dict[str, Any]
    ] = []

    manifest: List[
        Dict[str, Any]
    ] = []

    for relative_path, source_file in source_files.items():

        destination_file = (
            destination_files[
                relative_path
            ]
        )

        source_hash = (
            sha256_file(
                source_file
            )
        )

        destination_hash = (
            sha256_file(
                destination_file
            )
        )

        manifest.append({

            "path":
                relative_path,

            "size":
                destination_file
                .stat()
                .st_size,

            "sha256":
                destination_hash
        })

        if (
            source_hash
            !=
            destination_hash
        ):

            mismatches.append({

                "path":
                    relative_path,

                "source_sha256":
                    source_hash,

                "published_sha256":
                    destination_hash
            })

    if mismatches:

        return {

            "success":
                False,

            "status":
                "PUBLISHED_HASH_MISMATCH",

            "mismatches":
                mismatches
        }

    return {

        "success":
            True,

        "status":
            "PUBLISHED_ARTIFACT_VERIFIED",

        "index":
            str(
                index_file
            ),

        "manifest":
            manifest
    }


# ============================================================
# GAME ID
# ============================================================

def build_game_id(
    job_id: str
) -> str:

    clean_job_id = (
        str(
            job_id
        )
        .strip()
    )

    if clean_job_id:

        clean_job_id = (
            clean_job_id
            .replace(
                "/",
                "-"
            )
            .replace(
                "\\",
                "-"
            )
        )

        return clean_job_id[:120]

    return str(
        uuid.uuid4()
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
    ] = None
) -> Dict[str, Any]:

    relative_game_path = (
        f"/artifacts/{game_id}/index.html"
    )

    public_url = (
        OFFICIAL_PLATFORM_URL.rstrip("/")
        +
        relative_game_path
    )

    metadata = {

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
            request or {}
    }

    return metadata


# ============================================================
# MAIN PUBLISH FUNCTION
# ============================================================

def publish_game(
    game_dir: Optional[
        Path
    ] = None,
    game_name: str = "MAJD-GAME",
    job_id: str = "",
    artifact: Optional[Any] = None,
    artifact_path: Optional[Any] = None,
    build_path: Optional[Any] = None,
    request: Optional[
        Dict[str, Any]
    ] = None,
    payload: Optional[
        Dict[str, Any]
    ] = None,
    **kwargs: Any
) -> Dict[str, Any]:

    started_at = (
        utc_now()
    )

    source_value = (
        game_dir
        or
        artifact
        or
        artifact_path
        or
        build_path
    )

    if source_value is None:

        return {

            "success":
                False,

            "status":
                "ARTIFACT_ARGUMENT_MISSING",

            "bridge":
                BRIDGE_NAME
        }

    try:

        source = (
            normalize_artifact_path(
                source_value
            )
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

                "success":
                    False,

                "status":
                    source_verification.get(
                        "status",
                        "SOURCE_VERIFICATION_FAILED"
                    ),

                "bridge":
                    BRIDGE_NAME,

                "source_verification":
                    source_verification
            }

        actual_request = (
            request
            or
            payload
            or
            {}
        )

        if (
            (
                not game_name
                or
                game_name
                ==
                "MAJD-GAME"
            )
            and
            isinstance(
                actual_request,
                dict
            )
        ):

            game_name = str(
                actual_request.get(
                    "name"
                )
                or
                game_name
            )

        game_id = (
            build_game_id(
                job_id
            )
        )

        published_dir = (
            ARTIFACTS_DIR
            /
            game_id
        )

        copy_artifact(
            source,
            published_dir
        )

        published_verification = (
            verify_published_artifact(
                source,
                published_dir
            )
        )

        if not published_verification.get(
            "success"
        ):

            return {

                "success":
                    False,

                "status":
                    published_verification.get(
                        "status",
                        "PUBLISH_VERIFICATION_FAILED"
                    ),

                "bridge":
                    BRIDGE_NAME,

                "game_id":
                    game_id,

                "published_directory":
                    str(
                        published_dir
                    ),

                "verification":
                    published_verification
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
                    actual_request
            )
        )

        metadata_file = (
            PUBLISH_DIR
            /
            f"{game_id}.json"
        )

        write_json(
            metadata_file,
            metadata
        )

        return {

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
                utc_now()
        }

    except Exception as error:

        return {

            "success":
                False,

            "status":
                "PLATFORM_BRIDGE_EXCEPTION",

            "bridge":
                BRIDGE_NAME,

            "error":
                (
                    f"{type(error).__name__}: "
                    f"{error}"
                ),

            "finished_at":
                utc_now()
        }


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

def publish(
    **kwargs: Any
) -> Dict[str, Any]:

    return publish_game(
        **kwargs
    )


def send_game(
    **kwargs: Any
) -> Dict[str, Any]:

    return publish_game(
        **kwargs
    )


def send_to_majd(
    **kwargs: Any
) -> Dict[str, Any]:

    return publish_game(
        **kwargs
    )


def execute(
    **kwargs: Any
) -> Dict[str, Any]:

    return publish_game(
        **kwargs
    )


# ============================================================
# CLI TEST
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

        help="Playable artifact directory"
    )

    parser.add_argument(

        "--name",

        default=
            "MAJD TEST GAME"
    )

    parser.add_argument(

        "--job-id",

        default=
            str(
                uuid.uuid4()
            )
    )

    args = parser.parse_args()

    result = publish_game(

        game_dir=
            Path(
                args.artifact
            ),

        game_name=
            args.name,

        job_id=
            args.job_id
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

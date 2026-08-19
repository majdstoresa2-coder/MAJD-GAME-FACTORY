#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py
===================================

OFFICIAL MAJD PLATFORM BRIDGE

المسؤوليات:
- الربط بين MAJD GAME FACTORY ومنصة مجد الرسمية.
- اعتماد https://majd.shop/ كعنوان المنصة الرسمي.
- استقبال ناتج اللعبة الجاهز من منفذ الألعاب الحقيقي 03.
- التحقق من ملفات اللعبة قبل الإرسال.
- إنشاء Manifest رسمي للعبة.
- حساب SHA-256 للملفات.
- تجهيز حزمة النشر.
- إرسال اللعبة إلى API الحقيقي للمنصة عند ضبطه.
- عدم اختراع Endpoint غير موجود.
- دعم وضع التجهيز المحلي إذا لم يتم ضبط API بعد.
- تسجيل جميع عمليات الربط والنشر.
- منع اعتبار اللعبة منشورة قبل استلام نجاح حقيقي من المنصة.

التسلسل:

01 MAJD AI MASTERMIND
        ↓
02 OWNER COMMAND CENTER
        ↓
03 REAL GAME EXECUTOR
        ↓
04 OFFICIAL PLATFORM BRIDGE
        ↓
https://majd.shop/
"""

from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import shutil
import sys
import time
import uuid
import zipfile

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib import request, error


# ============================================================
# OFFICIAL PLATFORM
# ============================================================

MAJD_OFFICIAL_PLATFORM = "https://majd.shop/"

# مهم:
# لا نضع Endpoint افتراضيًا من عندنا.
# عند وجود API حقيقي للمنصة يتم تمريره عبر:
#
# MAJD_PLATFORM_API_ENDPOINT
#
# مثال:
# export MAJD_PLATFORM_API_ENDPOINT="https://...."
#
# لكن لا يتم اعتماد أي عنوان إلا إذا كان موجودًا فعليًا.

MAJD_PLATFORM_API_ENDPOINT = os.getenv(
    "MAJD_PLATFORM_API_ENDPOINT",
    ""
).strip()

MAJD_PLATFORM_API_TOKEN = os.getenv(
    "MAJD_PLATFORM_API_TOKEN",
    ""
).strip()


# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent

BRIDGE_DIR = ROOT_DIR / "majd-platform-bridge"
INCOMING_DIR = BRIDGE_DIR / "incoming"
PACKAGES_DIR = BRIDGE_DIR / "packages"
MANIFESTS_DIR = BRIDGE_DIR / "manifests"
RECEIPTS_DIR = BRIDGE_DIR / "receipts"
LOGS_DIR = BRIDGE_DIR / "logs"
FAILED_DIR = BRIDGE_DIR / "failed"
PUBLISHED_DIR = BRIDGE_DIR / "published"

for directory in [
    BRIDGE_DIR,
    INCOMING_DIR,
    PACKAGES_DIR,
    MANIFESTS_DIR,
    RECEIPTS_DIR,
    LOGS_DIR,
    FAILED_DIR,
    PUBLISHED_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)


# ============================================================
# HELPERS
# ============================================================

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_name(value: str) -> str:
    value = value.strip()

    allowed = []

    for char in value:
        if char.isalnum() or char in ("-", "_", "."):
            allowed.append(char)
        elif char.isspace():
            allowed.append("-")

    result = "".join(allowed).strip("-")

    return result or "majd-game"


def write_json(
    path: Path,
    data: Dict[str, Any]
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with path.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )


def read_json(
    path: Path
) -> Dict[str, Any]:

    with path.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def sha256_file(
    path: Path
) -> str:

    digest = hashlib.sha256()

    with path.open("rb") as file:

        while True:

            chunk = file.read(
                1024 * 1024
            )

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


def sha256_bytes(
    data: bytes
) -> str:

    return hashlib.sha256(
        data
    ).hexdigest()


def log_event(
    event: str,
    data: Optional[Dict[str, Any]] = None
) -> None:

    record = {
        "time": utc_now(),
        "event": event,
        "data": data or {}
    }

    log_file = (
        LOGS_DIR /
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.jsonl"
    )

    with log_file.open(
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            json.dumps(
                record,
                ensure_ascii=False
            )
        )

        file.write("\n")


# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class GameFile:

    path: str
    size: int
    sha256: str
    content_type: str


@dataclass
class GameManifest:

    manifest_version: str

    game_id: str
    game_name: str
    game_version: str

    factory: str
    executor: str
    bridge: str

    official_platform: str

    created_at: str

    build_status: str
    test_status: str
    repair_status: str

    playable_targets: List[str]

    entry_file: Optional[str]

    files: List[Dict[str, Any]]

    metadata: Dict[str, Any]


@dataclass
class PublishReceipt:

    publish_id: str

    game_id: str
    game_name: str

    platform: str

    status: str

    requested_at: str
    completed_at: Optional[str]

    package_sha256: str

    endpoint: Optional[str]

    http_status: Optional[int]

    platform_response: Optional[Any]

    error: Optional[str]


# ============================================================
# GAME VALIDATION
# ============================================================

class GameValidator:

    IGNORE_NAMES = {
        ".git",
        "__pycache__",
        ".DS_Store"
    }

    def validate_directory(
        self,
        game_dir: Path
    ) -> Dict[str, Any]:

        errors: List[str] = []
        warnings: List[str] = []

        if not game_dir.exists():

            errors.append(
                "Game directory does not exist."
            )

            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings
            }

        if not game_dir.is_dir():

            errors.append(
                "Game path is not a directory."
            )

            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings
            }

        files = [
            p for p in game_dir.rglob("*")
            if p.is_file()
            and not any(
                part in self.IGNORE_NAMES
                for part in p.parts
            )
        ]

        if not files:

            errors.append(
                "Game directory contains no files."
            )

        entry_candidates = [
            "index.html",
            "game.html",
            "main.html"
        ]

        found_entry = None

        for candidate in entry_candidates:

            matches = list(
                game_dir.rglob(candidate)
            )

            if matches:

                found_entry = matches[0]
                break

        if found_entry is None:

            warnings.append(
                "No web entry file detected. "
                "This is acceptable for non-web builds."
            )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "entry_file": (
                str(
                    found_entry.relative_to(
                        game_dir
                    )
                )
                if found_entry
                else None
            ),
            "file_count": len(files)
        }


# ============================================================
# FILE INVENTORY
# ============================================================

class FileInventory:

    def collect(
        self,
        game_dir: Path
    ) -> List[GameFile]:

        output: List[GameFile] = []

        for file_path in sorted(
            game_dir.rglob("*")
        ):

            if not file_path.is_file():
                continue

            relative = file_path.relative_to(
                game_dir
            )

            content_type = (
                mimetypes.guess_type(
                    str(file_path)
                )[0]
                or
                "application/octet-stream"
            )

            output.append(
                GameFile(
                    path=str(relative),
                    size=file_path.stat().st_size,
                    sha256=sha256_file(
                        file_path
                    ),
                    content_type=content_type
                )
            )

        return output


# ============================================================
# MANIFEST BUILDER
# ============================================================

class ManifestBuilder:

    def build(
        self,
        game_dir: Path,
        game_name: str,
        game_version: str,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
        build_status: str = "ready",
        test_status: str = "passed",
        repair_status: str = "complete"
    ) -> GameManifest:

        validator = GameValidator()

        validation = (
            validator.validate_directory(
                game_dir
            )
        )

        if not validation["valid"]:

            raise RuntimeError(
                "Game validation failed: "
                +
                "; ".join(
                    validation["errors"]
                )
            )

        inventory = (
            FileInventory().collect(
                game_dir
            )
        )

        game_id = (
            metadata or {}
        ).get(
            "game_id"
        ) or str(
            uuid.uuid4()
        )

        playable_targets = (
            metadata or {}
        ).get(
            "playable_targets",
            [
                "web",
                "desktop",
                "mobile"
            ]
        )

        manifest = GameManifest(

            manifest_version="1.0",

            game_id=game_id,

            game_name=game_name,

            game_version=game_version,

            factory="MAJD-GAME-FACTORY",

            executor=(
                "MAJD-REAL-GAME-EXECUTOR-03.py"
            ),

            bridge=(
                "MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py"
            ),

            official_platform=(
                MAJD_OFFICIAL_PLATFORM
            ),

            created_at=utc_now(),

            build_status=build_status,

            test_status=test_status,

            repair_status=repair_status,

            playable_targets=playable_targets,

            entry_file=validation.get(
                "entry_file"
            ),

            files=[
                asdict(item)
                for item in inventory
            ],

            metadata=metadata or {}
        )

        return manifest


# ============================================================
# PACKAGE BUILDER
# ============================================================

class PackageBuilder:

    def build(
        self,
        game_dir: Path,
        manifest: GameManifest
    ) -> Path:

        package_name = (
            f"{safe_name(manifest.game_name)}"
            f"-{safe_name(manifest.game_version)}"
            f"-{manifest.game_id}.zip"
        )

        package_path = (
            PACKAGES_DIR /
            package_name
        )

        manifest_path = (
            MANIFESTS_DIR /
            f"{manifest.game_id}.json"
        )

        manifest_data = asdict(
            manifest
        )

        write_json(
            manifest_path,
            manifest_data
        )

        with zipfile.ZipFile(
            package_path,
            "w",
            compression=zipfile.ZIP_DEFLATED
        ) as archive:

            for file_path in sorted(
                game_dir.rglob("*")
            ):

                if not file_path.is_file():
                    continue

                relative = (
                    file_path.relative_to(
                        game_dir
                    )
                )

                archive.write(
                    file_path,
                    arcname=str(
                        Path("game") /
                        relative
                    )
                )

            archive.write(
                manifest_path,
                arcname="manifest.json"
            )

        log_event(
            "PACKAGE_CREATED",
            {
                "game_id": manifest.game_id,
                "package": str(
                    package_path
                ),
                "sha256": sha256_file(
                    package_path
                )
            }
        )

        return package_path


# ============================================================
# HTTP CLIENT
# ============================================================

class MajdPlatformClient:

    def __init__(
        self,
        endpoint: str = MAJD_PLATFORM_API_ENDPOINT,
        token: str = MAJD_PLATFORM_API_TOKEN
    ):

        self.endpoint = endpoint.strip()
        self.token = token.strip()

    @property
    def configured(self) -> bool:

        return bool(
            self.endpoint
        )

    def publish(
        self,
        package_path: Path,
        manifest: GameManifest
    ) -> PublishReceipt:

        publish_id = str(
            uuid.uuid4()
        )

        package_data = (
            package_path.read_bytes()
        )

        package_hash = (
            sha256_bytes(
                package_data
            )
        )

        requested_at = utc_now()

        if not self.configured:

            receipt = PublishReceipt(

                publish_id=publish_id,

                game_id=manifest.game_id,

                game_name=manifest.game_name,

                platform=(
                    MAJD_OFFICIAL_PLATFORM
                ),

                status=(
                    "READY_FOR_OFFICIAL_API"
                ),

                requested_at=requested_at,

                completed_at=None,

                package_sha256=package_hash,

                endpoint=None,

                http_status=None,

                platform_response=None,

                error=(
                    "MAJD_PLATFORM_API_ENDPOINT "
                    "is not configured."
                )
            )

            self._save_receipt(
                receipt
            )

            log_event(
                "WAITING_FOR_OFFICIAL_API",
                asdict(receipt)
            )

            return receipt

        boundary = (
            "----MAJDBoundary"
            +
            uuid.uuid4().hex
        )

        body = self._multipart_body(
            boundary=boundary,
            package_data=package_data,
            package_name=package_path.name,
            manifest=manifest
        )

        headers = {
            "Content-Type":
                f"multipart/form-data; boundary={boundary}",

            "Accept":
                "application/json",

            "User-Agent":
                "MAJD-GAME-FACTORY/1.0",

            "X-MAJD-Game-ID":
                manifest.game_id,

            "X-MAJD-Package-SHA256":
                package_hash
        }

        if self.token:

            headers[
                "Authorization"
            ] = (
                f"Bearer {self.token}"
            )

        http_request = request.Request(
            self.endpoint,
            data=body,
            headers=headers,
            method="POST"
        )

        try:

            with request.urlopen(
                http_request,
                timeout=120
            ) as response:

                response_bytes = (
                    response.read()
                )

                response_text = (
                    response_bytes.decode(
                        "utf-8",
                        errors="replace"
                    )
                )

                try:

                    response_data = (
                        json.loads(
                            response_text
                        )
                    )

                except Exception:

                    response_data = (
                        response_text
                    )

                status_code = (
                    response.getcode()
                )

                success = (
                    200
                    <= status_code
                    < 300
                )

                receipt = PublishReceipt(

                    publish_id=publish_id,

                    game_id=manifest.game_id,

                    game_name=manifest.game_name,

                    platform=(
                        MAJD_OFFICIAL_PLATFORM
                    ),

                    status=(
                        "PUBLISHED"
                        if success
                        else
                        "FAILED"
                    ),

                    requested_at=(
                        requested_at
                    ),

                    completed_at=(
                        utc_now()
                    ),

                    package_sha256=(
                        package_hash
                    ),

                    endpoint=(
                        self.endpoint
                    ),

                    http_status=(
                        status_code
                    ),

                    platform_response=(
                        response_data
                    ),

                    error=None
                )

                self._save_receipt(
                    receipt
                )

                return receipt

        except error.HTTPError as exc:

            try:

                error_body = (
                    exc.read()
                    .decode(
                        "utf-8",
                        errors="replace"
                    )
                )

            except Exception:

                error_body = str(
                    exc
                )

            receipt = PublishReceipt(

                publish_id=publish_id,

                game_id=manifest.game_id,

                game_name=manifest.game_name,

                platform=(
                    MAJD_OFFICIAL_PLATFORM
                ),

                status="FAILED",

                requested_at=requested_at,

                completed_at=utc_now(),

                package_sha256=(
                    package_hash
                ),

                endpoint=self.endpoint,

                http_status=exc.code,

                platform_response=None,

                error=error_body
            )

            self._save_receipt(
                receipt
            )

            return receipt

        except Exception as exc:

            receipt = PublishReceipt(

                publish_id=publish_id,

                game_id=manifest.game_id,

                game_name=manifest.game_name,

                platform=(
                    MAJD_OFFICIAL_PLATFORM
                ),

                status="FAILED",

                requested_at=requested_at,

                completed_at=utc_now(),

                package_sha256=(
                    package_hash
                ),

                endpoint=self.endpoint,

                http_status=None,

                platform_response=None,

                error=str(exc)
            )

            self._save_receipt(
                receipt
            )

            return receipt

    def _multipart_body(
        self,
        boundary: str,
        package_data: bytes,
        package_name: str,
        manifest: GameManifest
    ) -> bytes:

        body = bytearray()

        def add_text(
            name: str,
            value: str
        ) -> None:

            body.extend(
                f"--{boundary}\r\n"
                .encode()
            )

            body.extend(
                (
                    f'Content-Disposition: '
                    f'form-data; '
                    f'name="{name}"\r\n\r\n'
                ).encode()
            )

            body.extend(
                value.encode(
                    "utf-8"
                )
            )

            body.extend(
                b"\r\n"
            )

        add_text(
            "manifest",
            json.dumps(
                asdict(manifest),
                ensure_ascii=False
            )
        )

        body.extend(
            f"--{boundary}\r\n"
            .encode()
        )

        body.extend(
            (
                "Content-Disposition: "
                "form-data; "
                f'name="package"; '
                f'filename="{package_name}"'
                "\r\n"
            ).encode()
        )

        body.extend(
            b"Content-Type: application/zip\r\n\r\n"
        )

        body.extend(
            package_data
        )

        body.extend(
            b"\r\n"
        )

        body.extend(
            f"--{boundary}--\r\n"
            .encode()
        )

        return bytes(
            body
        )

    def _save_receipt(
        self,
        receipt: PublishReceipt
    ) -> None:

        receipt_path = (
            RECEIPTS_DIR /
            f"{receipt.publish_id}.json"
        )

        write_json(
            receipt_path,
            asdict(receipt)
        )

        log_event(
            "PUBLISH_RECEIPT",
            asdict(receipt)
        )


# ============================================================
# OFFICIAL BRIDGE
# ============================================================

class MajdOfficialPlatformBridge:

    def __init__(self):

        self.validator = (
            GameValidator()
        )

        self.manifest_builder = (
            ManifestBuilder()
        )

        self.package_builder = (
            PackageBuilder()
        )

        self.client = (
            MajdPlatformClient()
        )

    def publish_game(
        self,
        game_dir: str,
        game_name: str,
        game_version: str = "1.0.0",
        metadata: Optional[
            Dict[str, Any]
        ] = None,
        build_status: str = "ready",
        test_status: str = "passed",
        repair_status: str = "complete"
    ) -> Dict[str, Any]:

        source = Path(
            game_dir
        ).resolve()

        log_event(
            "BRIDGE_REQUEST",
            {
                "game_dir": str(source),
                "game_name": game_name,
                "game_version": game_version
            }
        )

        validation = (
            self.validator
            .validate_directory(
                source
            )
        )

        if not validation[
            "valid"
        ]:

            result = {
                "success": False,
                "status": (
                    "VALIDATION_FAILED"
                ),
                "platform": (
                    MAJD_OFFICIAL_PLATFORM
                ),
                "errors": validation[
                    "errors"
                ],
                "warnings": validation[
                    "warnings"
                ]
            }

            log_event(
                "VALIDATION_FAILED",
                result
            )

            return result

        if build_status.lower() not in {
            "ready",
            "passed",
            "complete",
            "success",
            "successful"
        }:

            return {
                "success": False,
                "status": "BUILD_NOT_READY",
                "platform": (
                    MAJD_OFFICIAL_PLATFORM
                )
            }

        if test_status.lower() not in {
            "passed",
            "success",
            "successful"
        }:

            return {
                "success": False,
                "status": "TESTS_NOT_PASSED",
                "platform": (
                    MAJD_OFFICIAL_PLATFORM
                )
            }

        manifest = (
            self.manifest_builder.build(

                game_dir=source,

                game_name=game_name,

                game_version=game_version,

                metadata=metadata,

                build_status=build_status,

                test_status=test_status,

                repair_status=repair_status
            )
        )

        package = (
            self.package_builder.build(
                source,
                manifest
            )
        )

        receipt = (
            self.client.publish(
                package,
                manifest
            )
        )

        if receipt.status == (
            "PUBLISHED"
        ):

            published_record = {

                "game_id":
                    manifest.game_id,

                "game_name":
                    manifest.game_name,

                "game_version":
                    manifest.game_version,

                "official_platform":
                    MAJD_OFFICIAL_PLATFORM,

                "package":
                    str(package),

                "package_sha256":
                    receipt.package_sha256,

                "publish_id":
                    receipt.publish_id,

                "published_at":
                    receipt.completed_at,

                "platform_response":
                    receipt.platform_response
            }

            write_json(
                PUBLISHED_DIR /
                f"{manifest.game_id}.json",
                published_record
            )

            log_event(
                "GAME_PUBLISHED",
                published_record
            )

            return {
                "success": True,
                "status": "PUBLISHED",
                "platform":
                    MAJD_OFFICIAL_PLATFORM,
                "manifest":
                    asdict(manifest),
                "receipt":
                    asdict(receipt)
            }

        if receipt.status == (
            "READY_FOR_OFFICIAL_API"
        ):

            return {
                "success": True,
                "published": False,
                "status":
                    "READY_FOR_OFFICIAL_API",
                "platform":
                    MAJD_OFFICIAL_PLATFORM,
                "message": (
                    "اللعبة تم التحقق منها "
                    "وتجهيز حزمة النشر، "
                    "لكن API الحقيقي لمنصة مجد "
                    "لم يتم ضبطه بعد."
                ),
                "package":
                    str(package),
                "manifest":
                    asdict(manifest),
                "receipt":
                    asdict(receipt)
            }

        failed_record = {
            "game_id":
                manifest.game_id,
            "game_name":
                manifest.game_name,
            "package":
                str(package),
            "receipt":
                asdict(receipt)
        }

        write_json(
            FAILED_DIR /
            f"{manifest.game_id}.json",
            failed_record
        )

        log_event(
            "PUBLISH_FAILED",
            failed_record
        )

        return {
            "success": False,
            "status":
                "PUBLISH_FAILED",
            "platform":
                MAJD_OFFICIAL_PLATFORM,
            "receipt":
                asdict(receipt)
        }


# ============================================================
# ENTRY FOR FILE 03
# ============================================================

def publish_from_executor(
    game_dir: str,
    game_name: str,
    game_version: str = "1.0.0",
    metadata: Optional[
        Dict[str, Any]
    ] = None
) -> Dict[str, Any]:

    """
    هذه هي نقطة الربط التي يستدعيها
    MAJD-REAL-GAME-EXECUTOR-03.py
    بعد نجاح البناء والاختبار والإصلاح.
    """

    bridge = (
        MajdOfficialPlatformBridge()
    )

    return bridge.publish_game(

        game_dir=game_dir,

        game_name=game_name,

        game_version=game_version,

        metadata=metadata,

        build_status="ready",

        test_status="passed",

        repair_status="complete"
    )


# ============================================================
# OWNER / MASTERMIND ENTRY
# ============================================================

def execute_owner_publish_command(
    command: Dict[str, Any]
) -> Dict[str, Any]:

    game_dir = command.get(
        "game_dir"
    )

    game_name = command.get(
        "game_name"
    )

    game_version = command.get(
        "game_version",
        "1.0.0"
    )

    metadata = command.get(
        "metadata",
        {}
    )

    if not game_dir:

        return {
            "success": False,
            "status":
                "MISSING_GAME_DIRECTORY"
        }

    if not game_name:

        return {
            "success": False,
            "status":
                "MISSING_GAME_NAME"
        }

    return publish_from_executor(

        game_dir=game_dir,

        game_name=game_name,

        game_version=game_version,

        metadata=metadata
    )


# ============================================================
# STATUS
# ============================================================

def bridge_status() -> Dict[str, Any]:

    return {

        "service":
            "MAJD-OFFICIAL-PLATFORM-BRIDGE-04",

        "status":
            "ACTIVE",

        "factory":
            "MAJD-GAME-FACTORY",

        "official_platform":
            MAJD_OFFICIAL_PLATFORM,

        "official_api_configured":
            bool(
                MAJD_PLATFORM_API_ENDPOINT
            ),

        "official_api_endpoint":
            (
                MAJD_PLATFORM_API_ENDPOINT
                if MAJD_PLATFORM_API_ENDPOINT
                else None
            ),

        "executor":
            "MAJD-REAL-GAME-EXECUTOR-03.py",

        "time":
            utc_now()
    }


# ============================================================
# CLI
# ============================================================

def print_json(
    data: Dict[str, Any]
) -> None:

    print(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        )
    )


def main() -> int:

    if len(sys.argv) < 2:

        print_json(
            bridge_status()
        )

        print()

        print(
            "الاستخدام:"
        )

        print(
            "python "
            "MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py "
            "status"
        )

        print(
            "python "
            "MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py "
            'publish "/path/to/game" '
            '"اسم اللعبة" "1.0.0"'
        )

        return 0

    command = (
        sys.argv[1]
        .strip()
        .lower()
    )

    if command == "status":

        print_json(
            bridge_status()
        )

        return 0

    if command == "publish":

        if len(
            sys.argv
        ) < 4:

            print_json({
                "success": False,
                "error": (
                    "يلزم مسار اللعبة "
                    "واسم اللعبة."
                )
            })

            return 1

        game_dir = (
            sys.argv[2]
        )

        game_name = (
            sys.argv[3]
        )

        game_version = (
            sys.argv[4]
            if len(sys.argv) > 4
            else "1.0.0"
        )

        bridge = (
            MajdOfficialPlatformBridge()
        )

        result = (
            bridge.publish_game(
                game_dir=game_dir,
                game_name=game_name,
                game_version=game_version
            )
        )

        print_json(
            result
        )

        return (
            0
            if result.get(
                "success"
            )
            else 1
        )

    print_json({
        "success": False,
        "error":
            f"أمر غير معروف: {command}"
    })

    return 1


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    try:

        exit_code = main()

    except KeyboardInterrupt:

        print_json({
            "success": False,
            "status":
                "INTERRUPTED"
        })

        exit_code = 130

    except Exception as exc:

        log_event(
            "FATAL_ERROR",
            {
                "error": str(exc)
            }
        )

        print_json({
            "success": False,
            "status":
                "FATAL_ERROR",
            "error":
                str(exc)
        })

        exit_code = 1

    raise SystemExit(
        exit_code
    )

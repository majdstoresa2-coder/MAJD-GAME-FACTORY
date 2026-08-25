#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-AI-SOVEREIGN-COMPANY-02.py
============================================================

MAJD AI SOVEREIGN COMPANY
شركة مجد السيادية للإنتاج والهندسة بالذكاء الاصطناعي

ROLE
----
This module is the sovereign company orchestration layer between:

    01 MASTERMIND
          ↓
    02 SOVEREIGN COMPANY
          ↓
    SPECIALIZED AI DEPARTMENTS / REAL ADAPTERS
          ↓
    03 REAL GAME EXECUTOR

PURPOSE
-------
- Define the complete MAJD sovereign company structure.
- Register specialized departments.
- Register capabilities and real adapters.
- Route production work to the correct departments.
- Track capability availability truthfully.
- Prevent fake success.
- Prevent primitive placeholder assets from being accepted as
  production-quality output.
- Provide quality, security and originality gates.
- Prepare the company for image, video, cinema, 3D, audio,
  world generation, game engineering and platform production.
- Keep future capabilities in the architecture without falsely
  reporting them as operational.

SOVEREIGN RULE
--------------
A capability is NEVER considered operational merely because it exists
in this registry.

Operational capability requires:
1. A real adapter.
2. Adapter health check succeeds.
3. Required engine/runtime exists.
4. Required output is produced.
5. Verification succeeds.

NO FAKE READY.
NO FAKE PRODUCTION.
NO PRIMITIVE FALLBACK PRESENTED AS FINAL QUALITY.

This file intentionally uses only Python standard-library components
for the sovereign orchestration layer. Real engines are connected
through adapters.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import traceback
import uuid

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)


# ============================================================
# IDENTITY
# ============================================================

SYSTEM_NAME = "MAJD-GAME-FACTORY"
COMPANY_NAME = "MAJD-AI-SOVEREIGN-COMPANY"
COMPANY_FILE = "MAJD-AI-SOVEREIGN-COMPANY-02.py"
VERSION = "1.0.0"

MASTERMIND_LAYER = "01"
COMPANY_LAYER = "02"
EXECUTOR_LAYER = "03"

DEFAULT_TIMEOUT = 900

DEFAULT_STATE_DIRECTORY = "majd_company_state"
DEFAULT_WORK_DIRECTORY = "majd_company_work"

PRODUCTION_QUALITY_MINIMUM = 0.85
ORIGINALITY_MINIMUM = 0.80
SECURITY_MINIMUM = 0.85


# ============================================================
# TIME
# ============================================================

def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


# ============================================================
# ENUMS
# ============================================================

class CapabilityStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    CONFIGURED = "CONFIGURED"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"
    FAILED = "FAILED"


class DepartmentStatus(str, Enum):
    READY = "READY"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"
    FAILED = "FAILED"


class JobStatus(str, Enum):
    CREATED = "CREATED"
    PLANNING = "PLANNING"
    ROUTING = "ROUTING"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    READY_FOR_EXECUTOR = "READY_FOR_EXECUTOR"
    COMPLETE = "COMPLETE"


class GateDecision(str, Enum):
    PASS = "PASS"
    REJECT = "REJECT"
    REVIEW = "REVIEW"
    UNAVAILABLE = "UNAVAILABLE"


# ============================================================
# HELPERS
# ============================================================

def write_json(
    path: Path,
    data: Mapping[str, Any],
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = path.with_suffix(
        path.suffix + ".tmp"
    )

    with temporary.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            dict(data),
            file,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

    temporary.replace(path)


def read_json(
    path: Path,
    default: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:

    if not path.exists():
        return dict(default or {})

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        if isinstance(data, dict):
            return data

    except Exception:
        pass

    return dict(default or {})


def sha256_file(
    path: Path,
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


def ensure_directory(
    path: Path,
) -> Path:

    path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return path


def safe_identifier(
    value: Any,
) -> str:

    text = str(
        value or "UNKNOWN"
    ).strip()

    result = []

    for character in text:

        if (
            character.isalnum()
            or character in "-_."
        ):
            result.append(character)
        else:
            result.append("-")

    cleaned = "".join(result)

    while "--" in cleaned:
        cleaned = cleaned.replace(
            "--",
            "-",
        )

    cleaned = cleaned.strip(
        "-_."
    )

    return cleaned[:120] or "UNKNOWN"


def command_exists(
    command: str,
) -> bool:

    return bool(
        shutil.which(command)
    )


def python_module_exists(
    module_name: str,
) -> bool:

    try:

        return (
            importlib.util.find_spec(
                module_name
            )
            is not None
        )

    except Exception:

        return False


def normalize_score(
    value: Any,
    default: float = 0.0,
) -> float:

    try:

        number = float(value)

    except Exception:

        return default

    return max(
        0.0,
        min(
            1.0,
            number,
        ),
    )


# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class HealthResult:

    success: bool

    status: str

    message: str = ""

    details: Dict[str, Any] = field(
        default_factory=dict
    )

    checked_at: str = field(
        default_factory=utc_now
    )


@dataclass
class CapabilityDefinition:

    capability_id: str

    name: str

    department_id: str

    description: str

    required: bool = False

    future_ready: bool = True

    status: CapabilityStatus = (
        CapabilityStatus.UNAVAILABLE
    )

    adapter_name: Optional[str] = None

    engine_name: Optional[str] = None

    health: Optional[HealthResult] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class DepartmentDefinition:

    department_id: str

    name: str

    description: str

    capabilities: List[str] = field(
        default_factory=list
    )

    dependencies: List[str] = field(
        default_factory=list
    )

    status: DepartmentStatus = (
        DepartmentStatus.UNAVAILABLE
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class ProductionTask:

    task_id: str

    department_id: str

    capability_id: str

    action: str

    payload: Dict[str, Any]

    required: bool = True

    status: str = "PENDING"

    result: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class ProductionJob:

    job_id: str

    request: Dict[str, Any]

    status: JobStatus

    created_at: str

    updated_at: str

    tasks: List[ProductionTask] = field(
        default_factory=list
    )

    outputs: Dict[str, Any] = field(
        default_factory=dict
    )

    gates: Dict[str, Any] = field(
        default_factory=dict
    )

    errors: List[Dict[str, Any]] = field(
        default_factory=list
    )


@dataclass
class GateResult:

    gate: str

    decision: GateDecision

    score: float

    minimum_score: float

    reasons: List[str] = field(
        default_factory=list
    )

    evidence: Dict[str, Any] = field(
        default_factory=dict
    )

    checked_at: str = field(
        default_factory=utc_now
    )


# ============================================================
# ADAPTER CONTRACT
# ============================================================

class SovereignAdapter:
    """
    Base contract for every real production adapter.

    A subclass must provide a real health check and execute real work.
    """

    adapter_name = "UNIMPLEMENTED"

    engine_name = "UNIMPLEMENTED"

    def health_check(
        self,
    ) -> HealthResult:

        return HealthResult(
            success=False,
            status="UNIMPLEMENTED",
            message=(
                "Adapter does not implement a real health check."
            ),
        )

    def execute(
        self,
        action: str,
        payload: Mapping[str, Any],
        work_dir: Path,
    ) -> Dict[str, Any]:

        raise NotImplementedError(
            "Real adapter execution is not implemented."
        )


# ============================================================
# COMMAND ADAPTER
# ============================================================

class CommandAdapter(
    SovereignAdapter
):
    """
    Generic adapter for a real local executable.

    It does NOT claim the executable can perform a particular production
    task unless the concrete adapter implements execute().
    """

    def __init__(
        self,
        executable: str,
        adapter_name: str,
        engine_name: Optional[str] = None,
        version_args: Optional[
            Sequence[str]
        ] = None,
    ):

        self.executable = executable

        self.adapter_name = (
            adapter_name
        )

        self.engine_name = (
            engine_name
            or executable
        )

        self.version_args = list(
            version_args
            or ["--version"]
        )

    def health_check(
        self,
    ) -> HealthResult:

        executable_path = shutil.which(
            self.executable
        )

        if not executable_path:

            return HealthResult(
                success=False,
                status="EXECUTABLE_NOT_FOUND",
                message=(
                    f"{self.executable} was not found."
                ),
                details={
                    "executable":
                        self.executable,
                },
            )

        try:

            completed = subprocess.run(
                [
                    executable_path,
                    *self.version_args,
                ],
                capture_output=True,
                text=True,
                timeout=30,
                env=os.environ.copy(),
            )

            success = (
                completed.returncode == 0
            )

            return HealthResult(
                success=success,
                status=(
                    "HEALTHY"
                    if success
                    else "HEALTH_CHECK_FAILED"
                ),
                message=(
                    completed.stdout.strip()
                    or completed.stderr.strip()
                    or executable_path
                )[:2000],
                details={
                    "path":
                        executable_path,
                    "returncode":
                        completed.returncode,
                },
            )

        except Exception as error:

            return HealthResult(
                success=False,
                status="HEALTH_CHECK_EXCEPTION",
                message=(
                    f"{type(error).__name__}: "
                    f"{error}"
                ),
            )


# ============================================================
# PYTHON MODULE ADAPTER
# ============================================================

class PythonModuleAdapter(
    SovereignAdapter
):

    def __init__(
        self,
        module_name: str,
        adapter_name: str,
        engine_name: Optional[str] = None,
    ):

        self.module_name = module_name

        self.adapter_name = (
            adapter_name
        )

        self.engine_name = (
            engine_name
            or module_name
        )

    def health_check(
        self,
    ) -> HealthResult:

        exists = python_module_exists(
            self.module_name
        )

        return HealthResult(
            success=exists,
            status=(
                "HEALTHY"
                if exists
                else "MODULE_NOT_FOUND"
            ),
            message=(
                f"Python module {self.module_name} "
                f"{'is available' if exists else 'is unavailable'}."
            ),
            details={
                "module":
                    self.module_name,
            },
        )


# ============================================================
# REAL EXECUTOR 03 ADAPTER
# ============================================================

class RealGameExecutor03Adapter(
    SovereignAdapter
):

    adapter_name = (
        "MAJD-REAL-GAME-EXECUTOR-03"
    )

    engine_name = (
        "MAJD-REAL-GAME-EXECUTOR"
    )

    def __init__(
        self,
        executor_path: Path,
    ):

        self.executor_path = (
            executor_path.resolve()
        )

    def health_check(
        self,
    ) -> HealthResult:

        if not self.executor_path.exists():

            return HealthResult(
                success=False,
                status="EXECUTOR_FILE_NOT_FOUND",
                message=(
                    "03 real game executor file was not found."
                ),
                details={
                    "path":
                        str(
                            self.executor_path
                        ),
                },
            )

        try:

            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "py_compile",
                    str(
                        self.executor_path
                    ),
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            success = (
                completed.returncode == 0
            )

            return HealthResult(
                success=success,
                status=(
                    "HEALTHY"
                    if success
                    else "PYTHON_SYNTAX_FAILED"
                ),
                message=(
                    completed.stderr.strip()
                    or completed.stdout.strip()
                    or "Executor syntax verified."
                ),
                details={
                    "path":
                        str(
                            self.executor_path
                        ),
                    "sha256":
                        (
                            sha256_file(
                                self.executor_path
                            )
                            if success
                            else None
                        ),
                },
            )

        except Exception as error:

            return HealthResult(
                success=False,
                status="EXECUTOR_HEALTH_EXCEPTION",
                message=(
                    f"{type(error).__name__}: "
                    f"{error}"
                ),
            )


# ============================================================
# ADAPTER REGISTRY
# ============================================================

class AdapterRegistry:

    def __init__(
        self,
    ):

        self._adapters: Dict[
            str,
            SovereignAdapter
        ] = {}

    def register(
        self,
        capability_id: str,
        adapter: SovereignAdapter,
    ) -> None:

        self._adapters[
            capability_id
        ] = adapter

    def unregister(
        self,
        capability_id: str,
    ) -> None:

        self._adapters.pop(
            capability_id,
            None,
        )

    def get(
        self,
        capability_id: str,
    ) -> Optional[SovereignAdapter]:

        return self._adapters.get(
            capability_id
        )

    def all(
        self,
    ) -> Dict[
        str,
        SovereignAdapter
    ]:

        return dict(
            self._adapters
        )


# ============================================================
# COMPANY BLUEPRINT
# ============================================================

def build_company_blueprint(
) -> Tuple[
    Dict[str, DepartmentDefinition],
    Dict[str, CapabilityDefinition],
]:

    departments: Dict[
        str,
        DepartmentDefinition
    ] = {}

    capabilities: Dict[
        str,
        CapabilityDefinition
    ] = {}


    def add_department(
        department_id: str,
        name: str,
        description: str,
        dependencies: Optional[
            Iterable[str]
        ] = None,
    ) -> None:

        departments[
            department_id
        ] = DepartmentDefinition(
            department_id=
                department_id,
            name=
                name,
            description=
                description,
            dependencies=list(
                dependencies
                or []
            ),
        )


    def add_capability(
        department_id: str,
        capability_id: str,
        name: str,
        description: str,
        *,
        required: bool = False,
        future_ready: bool = True,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        capability = (
            CapabilityDefinition(
                capability_id=
                    capability_id,
                name=
                    name,
                department_id=
                    department_id,
                description=
                    description,
                required=
                    required,
                future_ready=
                    future_ready,
                metadata=dict(
                    metadata
                    or {}
                ),
            )
        )

        capabilities[
            capability_id
        ] = capability

        departments[
            department_id
        ].capabilities.append(
            capability_id
        )


    # ========================================================
    # SOVEREIGN GOVERNANCE
    # ========================================================

    add_department(
        "SOVEREIGN_GOVERNANCE",
        "MAJD Sovereign Governance",
        (
            "Owner authority, company governance, policy, "
            "permissions and sovereign production control."
        ),
    )

    add_capability(
        "SOVEREIGN_GOVERNANCE",
        "OWNER_COMMAND",
        "Owner Command",
        (
            "Receives authorized owner commands from "
            "text or approved command interfaces."
        ),
        required=True,
    )

    add_capability(
        "SOVEREIGN_GOVERNANCE",
        "AUTHORITY_POLICY",
        "Authority Policy",
        (
            "Controls authority boundaries, permissions "
            "and protected operations."
        ),
        required=True,
    )

    add_capability(
        "SOVEREIGN_GOVERNANCE",
        "AUDIT_TRAIL",
        "Audit Trail",
        (
            "Records production, security, quality and "
            "deployment decisions."
        ),
        required=True,
    )


    # ========================================================
    # AI DIRECTION / PLANNING
    # ========================================================

    add_department(
        "AI_DIRECTION",
        "MAJD AI Direction",
        (
            "Central production planning and specialized "
            "AI direction."
        ),
        dependencies=[
            "SOVEREIGN_GOVERNANCE",
        ],
    )

    for capability_id, name in (
        (
            "AI_DIRECTOR",
            "AI Director",
        ),
        (
            "GAME_DIRECTOR",
            "Game Director",
        ),
        (
            "CREATIVE_DIRECTOR",
            "Creative Director",
        ),
        (
            "ART_DIRECTOR",
            "Art Director",
        ),
        (
            "TECHNICAL_DIRECTOR",
            "Technical Director",
        ),
        (
            "PRODUCTION_MANAGER",
            "Production Manager",
        ),
        (
            "AI_PLANNER",
            "AI Planner",
        ),
        (
            "AI_REVIEWER",
            "AI Reviewer",
        ),
    ):

        add_capability(
            "AI_DIRECTION",
            capability_id,
            name,
            (
                f"{name} specialized sovereign "
                "production responsibility."
            ),
        )


    # ========================================================
    # PLAYER / MARKET INTELLIGENCE
    # ========================================================

    add_department(
        "PLAYER_MARKET_INTELLIGENCE",
        "Player & Market Intelligence",
        (
            "Understands player needs and market patterns "
            "without copying protected products."
        ),
    )

    for capability_id, name in (
        (
            "PLAYER_RESEARCH",
            "Player Research AI",
        ),
        (
            "PLAYER_FEEDBACK",
            "Player Feedback Analysis",
        ),
        (
            "TREND_INTELLIGENCE",
            "Trend Intelligence",
        ),
        (
            "MARKET_RESEARCH",
            "Market Research",
        ),
        (
            "GAME_CONCEPT_INNOVATION",
            "Original Game Concept AI",
        ),
        (
            "COMMUNITY_INTELLIGENCE",
            "Community Intelligence",
        ),
    ):

        add_capability(
            "PLAYER_MARKET_INTELLIGENCE",
            capability_id,
            name,
            (
                f"{name} for original MAJD product "
                "development."
            ),
        )


    # ========================================================
    # WEB RESEARCH / IP
    # ========================================================

    add_department(
        "ORIGINALITY_IP",
        "Originality & Intellectual Property",
        (
            "Researches public information, evaluates "
            "similarity risk and protects MAJD originality."
        ),
    )

    add_capability(
        "ORIGINALITY_IP",
        "WEB_RESEARCH",
        "Web Research AI",
        (
            "Researches public web sources through a "
            "configured real search adapter."
        ),
    )

    add_capability(
        "ORIGINALITY_IP",
        "ORIGINALITY_REVIEW",
        "Originality Review",
        (
            "Reviews whether generated work has an "
            "independent MAJD identity."
        ),
        required=True,
    )

    add_capability(
        "ORIGINALITY_IP",
        "IP_SIMILARITY_REVIEW",
        "IP Similarity Review",
        (
            "Flags potentially problematic similarity "
            "for redesign or appropriate review."
        ),
        required=True,
    )

    add_capability(
        "ORIGINALITY_IP",
        "TRADEMARK_RESEARCH",
        "Trademark Research",
        (
            "Supports trademark/name research using "
            "configured authoritative research sources."
        ),
    )


    # ========================================================
    # WORLD & MAP FACTORY
    # ========================================================

    add_department(
        "WORLD_MAP_FACTORY",
        "MAJD AI World & Map Factory",
        (
            "Designs complete game worlds, strategic maps, "
            "levels and navigable spaces."
        ),
    )

    for capability_id, name in (
        (
            "WORLD_PLANNER",
            "World Planner",
        ),
        (
            "WORLD_MAP_GENERATION",
            "World Map Generation",
        ),
        (
            "LEVEL_DESIGN",
            "Level Design",
        ),
        (
            "STRATEGIC_MAP",
            "Strategic Map Design",
        ),
        (
            "CITY_PLANNING",
            "City Planning",
        ),
        (
            "ROAD_NETWORKS",
            "Road Network Design",
        ),
        (
            "NAVIGATION_MESH",
            "Navigation Mesh",
        ),
        (
            "SPAWN_PLANNING",
            "Spawn Planning",
        ),
        (
            "RESOURCE_PLACEMENT",
            "Resource Placement",
        ),
        (
            "POI_PLANNING",
            "Points of Interest Planning",
        ),
        (
            "WORLD_STREAMING",
            "World Streaming",
        ),
    ):

        add_capability(
            "WORLD_MAP_FACTORY",
            capability_id,
            name,
            (
                f"{name} capability for large, "
                "playable game worlds."
            ),
        )


    # ========================================================
    # ARCHITECTURE
    # ========================================================

    add_department(
        "ARCHITECTURE_FACTORY",
        "MAJD AI Architecture Factory",
        (
            "Architectural and urban production for "
            "buildings, cities and interior spaces."
        ),
    )

    for capability_id, name in (
        (
            "PALACE_DESIGN",
            "Palace Design",
        ),
        (
            "CASTLE_DESIGN",
            "Castle Design",
        ),
        (
            "CITY_ARCHITECTURE",
            "City Architecture",
        ),
        (
            "BUILDING_GENERATION",
            "Building Generation",
        ),
        (
            "INTERIOR_DESIGN",
            "Interior Design",
        ),
        (
            "URBAN_DESIGN",
            "Urban Design",
        ),
        (
            "BRIDGE_DESIGN",
            "Bridge Design",
        ),
        (
            "FORTIFICATION_DESIGN",
            "Fortification Design",
        ),
        (
            "SET_ARCHITECTURE",
            "Cinematic Set Architecture",
        ),
    ):

        add_capability(
            "ARCHITECTURE_FACTORY",
            capability_id,
            name,
            (
                f"{name} for original MAJD worlds."
            ),
        )


    # ========================================================
    # TERRAIN
    # ========================================================

    add_department(
        "TERRAIN_FACTORY",
        "MAJD AI Terrain Factory",
        (
            "Terrain and geological environment production."
        ),
    )

    for capability_id, name in (
        (
            "TERRAIN_GENERATION",
            "Terrain Generation",
        ),
        (
            "MOUNTAIN_GENERATION",
            "Mountain Generation",
        ),
        (
            "VALLEY_GENERATION",
            "Valley Generation",
        ),
        (
            "DESERT_GENERATION",
            "Desert Generation",
        ),
        (
            "CAVE_GENERATION",
            "Cave Generation",
        ),
        (
            "ISLAND_GENERATION",
            "Island Generation",
        ),
        (
            "EROSION_SIMULATION",
            "Erosion Simulation",
        ),
    ):

        add_capability(
            "TERRAIN_FACTORY",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # NATURE / ECOSYSTEM
    # ========================================================

    add_department(
        "NATURE_ECOSYSTEM",
        "MAJD AI Nature & Ecosystem Factory",
        (
            "Produces living natural ecosystems rather than "
            "primitive decorative geometry."
        ),
    )

    for capability_id, name in (
        (
            "TREE_GENERATION",
            "Realistic Tree Generation",
        ),
        (
            "PLANT_GENERATION",
            "Plant Generation",
        ),
        (
            "GRASS_GENERATION",
            "Grass Generation",
        ),
        (
            "FLOWER_GENERATION",
            "Flower Generation",
        ),
        (
            "FOREST_GENERATION",
            "Forest Generation",
        ),
        (
            "WILDLIFE_GENERATION",
            "Wildlife Generation",
        ),
        (
            "BIRD_SYSTEMS",
            "Bird Systems",
        ),
        (
            "AQUATIC_LIFE",
            "Aquatic Life",
        ),
        (
            "INSECT_SYSTEMS",
            "Insect Systems",
        ),
        (
            "ECOSYSTEM_SIMULATION",
            "Ecosystem Simulation",
        ),
        (
            "WIND_VEGETATION",
            "Wind & Vegetation Interaction",
        ),
    ):

        add_capability(
            "NATURE_ECOSYSTEM",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # CLIMATE / WEATHER
    # ========================================================

    add_department(
        "CLIMATE_WEATHER",
        "MAJD AI Climate & Weather",
        (
            "Dynamic climate, weather, seasons and "
            "environmental conditions."
        ),
    )

    for capability_id, name in (
        (
            "SNOW_SYSTEM",
            "Snow System",
        ),
        (
            "ICE_SYSTEM",
            "Ice System",
        ),
        (
            "RAIN_SYSTEM",
            "Rain System",
        ),
        (
            "STORM_SYSTEM",
            "Storm System",
        ),
        (
            "FOG_SYSTEM",
            "Fog System",
        ),
        (
            "CLOUD_SYSTEM",
            "Cloud System",
        ),
        (
            "DAY_NIGHT",
            "Day/Night Cycle",
        ),
        (
            "SEASONS",
            "Season System",
        ),
        (
            "ENVIRONMENTAL_RESPONSE",
            "Environmental Weather Response",
        ),
    ):

        add_capability(
            "CLIMATE_WEATHER",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # WATER
    # ========================================================

    add_department(
        "WATER_FACTORY",
        "MAJD AI Water Factory",
        (
            "Water environment and simulation production."
        ),
    )

    for capability_id, name in (
        (
            "OCEAN_SYSTEM",
            "Ocean System",
        ),
        (
            "RIVER_SYSTEM",
            "River System",
        ),
        (
            "LAKE_SYSTEM",
            "Lake System",
        ),
        (
            "WATERFALL_SYSTEM",
            "Waterfall System",
        ),
        (
            "WAVE_SYSTEM",
            "Wave System",
        ),
        (
            "UNDERWATER_ENVIRONMENT",
            "Underwater Environment",
        ),
    ):

        add_capability(
            "WATER_FACTORY",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # CHARACTER FACTORY
    # ========================================================

    add_department(
        "CHARACTER_FACTORY",
        "MAJD AI Character Factory",
        (
            "Produces game-ready characters and creatures."
        ),
    )

    for capability_id, name in (
        (
            "CHARACTER_DESIGN",
            "Character Design",
        ),
        (
            "HUMAN_GENERATION",
            "Human Generation",
        ),
        (
            "FACE_GENERATION",
            "Face Generation",
        ),
        (
            "BODY_GENERATION",
            "Body Generation",
        ),
        (
            "HAIR_GENERATION",
            "Hair Generation",
        ),
        (
            "SKIN_MATERIAL",
            "Skin Material",
        ),
        (
            "NPC_GENERATION",
            "NPC Generation",
        ),
        (
            "HERO_GENERATION",
            "Hero Generation",
        ),
        (
            "CREATURE_GENERATION",
            "Creature Generation",
        ),
        (
            "ANIMAL_GENERATION",
            "Animal Generation",
        ),
        (
            "FACIAL_EXPRESSION",
            "Facial Expression",
        ),
    ):

        add_capability(
            "CHARACTER_FACTORY",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # FASHION / EQUIPMENT
    # ========================================================

    add_department(
        "FASHION_EQUIPMENT",
        "MAJD AI Fashion & Equipment",
        (
            "Original clothing, armor, accessories and "
            "game equipment production."
        ),
    )

    for capability_id, name in (
        (
            "CLOTHING_DESIGN",
            "Clothing Design",
        ),
        (
            "ARMOR_DESIGN",
            "Armor Design",
        ),
        (
            "ACCESSORY_DESIGN",
            "Accessory Design",
        ),
        (
            "CLOTH_SIMULATION",
            "Cloth Simulation",
        ),
        (
            "EQUIPMENT_DESIGN",
            "Equipment Design",
        ),
        (
            "PROP_DESIGN",
            "Prop Design",
        ),
        (
            "VEHICLE_DESIGN",
            "Vehicle Design",
        ),
    ):

        add_capability(
            "FASHION_EQUIPMENT",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # 3D ASSET FACTORY
    # ========================================================

    add_department(
        "ASSET_3D_FACTORY",
        "MAJD AI 3D Asset Factory",
        (
            "Produces and prepares real game-ready 3D assets."
        ),
    )

    for capability_id, name in (
        (
            "TEXT_TO_3D",
            "Text to 3D",
        ),
        (
            "IMAGE_TO_3D",
            "Image to 3D",
        ),
        (
            "MESH_GENERATION",
            "Mesh Generation",
        ),
        (
            "RETOPOLOGY",
            "Retopology",
        ),
        (
            "UV_UNWRAP",
            "UV Unwrap",
        ),
        (
            "PBR_MATERIALS",
            "PBR Materials",
        ),
        (
            "TEXTURE_GENERATION",
            "Texture Generation",
        ),
        (
            "BAKING",
            "Asset Baking",
        ),
        (
            "LOD_GENERATION",
            "LOD Generation",
        ),
        (
            "GLTF_EXPORT",
            "GLTF/GLB Export",
        ),
        (
            "ASSET_OPTIMIZATION",
            "3D Asset Optimization",
        ),
    ):

        add_capability(
            "ASSET_3D_FACTORY",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # RIGGING / ANIMATION
    # ========================================================

    add_department(
        "ANIMATION_FACTORY",
        "MAJD AI Animation Factory",
        (
            "Rigging, skeletal, facial and gameplay "
            "animation production."
        ),
    )

    for capability_id, name in (
        (
            "AUTO_RIGGING",
            "Automatic Rigging",
        ),
        (
            "SKELETON",
            "Skeleton Generation",
        ),
        (
            "FACIAL_RIG",
            "Facial Rig",
        ),
        (
            "IDLE_ANIMATION",
            "Idle Animation",
        ),
        (
            "WALK_ANIMATION",
            "Walk Animation",
        ),
        (
            "RUN_ANIMATION",
            "Run Animation",
        ),
        (
            "JUMP_ANIMATION",
            "Jump Animation",
        ),
        (
            "COMBAT_ANIMATION",
            "Combat Animation",
        ),
        (
            "CREATURE_ANIMATION",
            "Creature Animation",
        ),
        (
            "CINEMATIC_ANIMATION",
            "Cinematic Animation",
        ),
        (
            "IK_SYSTEM",
            "Inverse Kinematics",
        ),
        (
            "PROCEDURAL_ANIMATION",
            "Procedural Animation",
        ),
    ):

        add_capability(
            "ANIMATION_FACTORY",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # GAME ENGINEERING
    # ========================================================

    add_department(
        "GAME_ENGINEERING",
        "MAJD AI Game Engineering",
        (
            "Core gameplay, game systems and runtime "
            "engineering."
        ),
    )

    for capability_id, name in (
        (
            "GAMEPLAY_ENGINEERING",
            "Gameplay Engineering",
        ),
        (
            "PLAYER_CONTROLLER",
            "Player Controller",
        ),
        (
            "COMBAT_SYSTEM",
            "Combat System",
        ),
        (
            "QUEST_SYSTEM",
            "Quest System",
        ),
        (
            "BUILDING_SYSTEM",
            "Building System",
        ),
        (
            "RESOURCE_SYSTEM",
            "Resource System",
        ),
        (
            "INVENTORY_SYSTEM",
            "Inventory System",
        ),
        (
            "CRAFTING_SYSTEM",
            "Crafting System",
        ),
        (
            "PROGRESSION_SYSTEM",
            "Progression System",
        ),
        (
            "ALLIANCE_SYSTEM",
            "Alliance System",
        ),
        (
            "EVENT_SYSTEM",
            "Event System",
        ),
        (
            "PVE_SYSTEM",
            "PvE System",
        ),
        (
            "PVP_SYSTEM",
            "PvP System",
        ),
    ):

        add_capability(
            "GAME_ENGINEERING",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # PHYSICS
    # ========================================================

    add_department(
        "PHYSICS_ENGINEERING",
        "MAJD AI Physics Engineering",
        (
            "Game physics and environmental interaction."
        ),
    )

    for capability_id, name in (
        (
            "COLLISION",
            "Collision System",
        ),
        (
            "GRAVITY",
            "Gravity System",
        ),
        (
            "CHARACTER_PHYSICS",
            "Character Physics",
        ),
        (
            "VEHICLE_PHYSICS",
            "Vehicle Physics",
        ),
        (
            "RAGDOLL",
            "Ragdoll Physics",
        ),
        (
            "DESTRUCTION_PHYSICS",
            "Destruction Physics",
        ),
        (
            "PHYSICS_INTERACTION",
            "Environment Interaction",
        ),
    ):

        add_capability(
            "PHYSICS_ENGINEERING",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # CAMERA
    # ========================================================

    add_department(
        "CAMERA_ENGINEERING",
        "MAJD AI Camera Engineering",
        (
            "Player, strategic, free and cinematic camera "
            "systems."
        ),
    )

    for capability_id, name in (
        (
            "THIRD_PERSON_CAMERA",
            "Third Person Camera",
        ),
        (
            "FIRST_PERSON_CAMERA",
            "First Person Camera",
        ),
        (
            "STRATEGIC_CAMERA",
            "Strategic Camera",
        ),
        (
            "FREE_CAMERA",
            "Free Camera",
        ),
        (
            "CAMERA_ORBIT",
            "360 Degree Camera Orbit",
        ),
        (
            "CAMERA_PAN",
            "Camera Pan",
        ),
        (
            "CAMERA_ZOOM",
            "Camera Zoom",
        ),
        (
            "PINCH_ZOOM",
            "Mobile Pinch Zoom",
        ),
        (
            "CAMERA_FOLLOW",
            "Optional Camera Follow",
        ),
        (
            "CINEMATIC_CAMERA",
            "Cinematic Camera",
        ),
    ):

        add_capability(
            "CAMERA_ENGINEERING",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # NPC / AGENT AI
    # ========================================================

    add_department(
        "GAME_AGENT_AI",
        "MAJD Game Agent AI",
        (
            "NPC, crowd and game-world intelligent behavior."
        ),
    )

    for capability_id, name in (
        (
            "NPC_BEHAVIOR",
            "NPC Behavior",
        ),
        (
            "ENEMY_AI",
            "Enemy AI",
        ),
        (
            "ALLY_AI",
            "Ally AI",
        ),
        (
            "CROWD_AI",
            "Crowd AI",
        ),
        (
            "PATHFINDING",
            "Pathfinding",
        ),
        (
            "DYNAMIC_BEHAVIOR",
            "Dynamic Behavior",
        ),
    ):

        add_capability(
            "GAME_AGENT_AI",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # MULTIPLAYER
    # ========================================================

    add_department(
        "MULTIPLAYER_ENGINEERING",
        "MAJD Multiplayer Engineering",
        (
            "Networking and multiplayer game systems."
        ),
    )

    for capability_id, name in (
        (
            "REALTIME_NETWORKING",
            "Realtime Networking",
        ),
        (
            "MATCHMAKING",
            "Matchmaking",
        ),
        (
            "LOBBIES",
            "Lobby System",
        ),
        (
            "MULTIPLAYER_STATE",
            "Multiplayer State Synchronization",
        ),
        (
            "GAME_SERVERS",
            "Game Server Runtime",
        ),
    ):

        add_capability(
            "MULTIPLAYER_ENGINEERING",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # IMAGE / ART
    # ========================================================

    add_department(
        "IMAGE_ART_STUDIO",
        "MAJD AI Image & Art Studio",
        (
            "Original visual production for games, platform "
            "and media."
        ),
    )

    for capability_id, name in (
        (
            "IMAGE_GENERATION",
            "Image Generation",
        ),
        (
            "CONCEPT_ART",
            "Concept Art",
        ),
        (
            "KEY_ART",
            "Key Art",
        ),
        (
            "POSTER_GENERATION",
            "Poster Generation",
        ),
        (
            "THUMBNAIL_GENERATION",
            "Thumbnail Generation",
        ),
        (
            "CHARACTER_PORTRAIT",
            "Character Portrait",
        ),
        (
            "BACKGROUND_GENERATION",
            "Background Generation",
        ),
        (
            "ICON_GENERATION",
            "Icon Generation",
        ),
        (
            "LOADING_ART",
            "Loading Screen Art",
        ),
        (
            "MARKETING_ART",
            "Marketing Art",
        ),
    ):

        add_capability(
            "IMAGE_ART_STUDIO",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # UI / UX
    # ========================================================

    add_department(
        "UI_UX_FACTORY",
        "MAJD AI UI/UX Factory",
        (
            "Premium interactive interface production for "
            "platform and games."
        ),
    )

    for capability_id, name in (
        (
            "PLATFORM_UI",
            "Platform UI",
        ),
        (
            "OWNER_DASHBOARD_UI",
            "Owner Dashboard UI",
        ),
        (
            "GAME_UI",
            "Game UI",
        ),
        (
            "HUD_DESIGN",
            "HUD Design",
        ),
        (
            "STORE_UI",
            "Store UI",
        ),
        (
            "MAP_UI",
            "Map UI",
        ),
        (
            "MENU_UI",
            "Menu UI",
        ),
        (
            "RESPONSIVE_UI",
            "Responsive UI",
        ),
        (
            "MOTION_UI",
            "Motion UI",
        ),
        (
            "ANIMATED_BACKGROUND",
            "Animated Background",
        ),
        (
            "MICRO_INTERACTIONS",
            "Micro Interactions",
        ),
    ):

        add_capability(
            "UI_UX_FACTORY",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # CINEMA / VIDEO
    # ========================================================

    add_department(
        "CINEMA_VIDEO_STUDIO",
        "MAJD AI Cinema & Video Studio",
        (
            "Original cinematic and video production."
        ),
    )

    for capability_id, name in (
        (
            "VIDEO_GENERATION",
            "Video Generation",
        ),
        (
            "CINEMATIC_DIRECTION",
            "Cinematic Direction",
        ),
        (
            "STORYBOARD",
            "Storyboard",
        ),
        (
            "SHOT_PLANNING",
            "Shot Planning",
        ),
        (
            "CUTSCENE_GENERATION",
            "Cutscene Generation",
        ),
        (
            "TRAILER_GENERATION",
            "Trailer Generation",
        ),
        (
            "INTRO_GENERATION",
            "Intro Generation",
        ),
        (
            "VIDEO_EDITING",
            "Video Editing",
        ),
        (
            "COLOR_GRADING",
            "Color Grading",
        ),
        (
            "VIRTUAL_PRODUCTION",
            "Virtual Production",
        ),
    ):

        add_capability(
            "CINEMA_VIDEO_STUDIO",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # VFX
    # ========================================================

    add_department(
        "VFX_STUDIO",
        "MAJD AI VFX Studio",
        (
            "Visual effects for gameplay and cinematic "
            "production."
        ),
    )

    for capability_id, name in (
        (
            "FIRE_VFX",
            "Fire VFX",
        ),
        (
            "SMOKE_VFX",
            "Smoke VFX",
        ),
        (
            "MAGIC_VFX",
            "Magic VFX",
        ),
        (
            "WEATHER_VFX",
            "Weather VFX",
        ),
        (
            "WATER_VFX",
            "Water VFX",
        ),
        (
            "PARTICLE_VFX",
            "Particle VFX",
        ),
        (
            "CINEMATIC_VFX",
            "Cinematic VFX",
        ),
    ):

        add_capability(
            "VFX_STUDIO",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # AUDIO / MUSIC / VOICE
    # ========================================================

    add_department(
        "AUDIO_STUDIO",
        "MAJD AI Audio Studio",
        (
            "Voice, music, sound effects and spatial audio "
            "production."
        ),
    )

    for capability_id, name in (
        (
            "VOICE_GENERATION",
            "Voice Generation",
        ),
        (
            "DUBBING",
            "Dubbing",
        ),
        (
            "NARRATION",
            "Narration",
        ),
        (
            "MUSIC_GENERATION",
            "Music Generation",
        ),
        (
            "DYNAMIC_MUSIC",
            "Dynamic Music",
        ),
        (
            "SFX_GENERATION",
            "Sound Effect Generation",
        ),
        (
            "AMBIENT_AUDIO",
            "Ambient Audio",
        ),
        (
            "SPATIAL_AUDIO",
            "Spatial Audio",
        ),
        (
            "AUDIO_MIXING",
            "Audio Mixing",
        ),
        (
            "AUDIO_MASTERING",
            "Audio Mastering",
        ),
        (
            "LIP_SYNC",
            "Lip Sync",
        ),
    ):

        add_capability(
            "AUDIO_STUDIO",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # STORY
    # ========================================================

    add_department(
        "STORY_WRITING",
        "MAJD AI Story & Writing",
        (
            "Original world-building, story and dialogue "
            "production."
        ),
    )

    for capability_id, name in (
        (
            "WORLD_LORE",
            "World Lore",
        ),
        (
            "STORY_GENERATION",
            "Story Generation",
        ),
        (
            "DIALOGUE_GENERATION",
            "Dialogue Generation",
        ),
        (
            "QUEST_WRITING",
            "Quest Writing",
        ),
        (
            "CHARACTER_WRITING",
            "Character Writing",
        ),
        (
            "CINEMATIC_SCRIPT",
            "Cinematic Script",
        ),
        (
            "FACTION_DESIGN",
            "Faction Design",
        ),
    ):

        add_capability(
            "STORY_WRITING",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # VOICE ASSISTANT
    # ========================================================

    add_department(
        "VOICE_ASSISTANT",
        "MAJD Voice & Conversational AI",
        (
            "Voice and conversational command interface "
            "for sovereign owner operations."
        ),
    )

    for capability_id, name in (
        (
            "SPEECH_TO_TEXT",
            "Speech to Text",
        ),
        (
            "COMMAND_UNDERSTANDING",
            "Command Understanding",
        ),
        (
            "VOICE_COMMAND_ROUTING",
            "Voice Command Routing",
        ),
        (
            "TEXT_TO_SPEECH",
            "Text to Speech",
        ),
        (
            "ARABIC_VOICE",
            "Arabic Voice Interface",
        ),
        (
            "MULTILINGUAL_VOICE",
            "Multilingual Voice Interface",
        ),
    ):

        add_capability(
            "VOICE_ASSISTANT",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # PLATFORM ENGINEERING
    # ========================================================

    add_department(
        "PLATFORM_ENGINEERING",
        "MAJD Platform Engineering",
        (
            "Frontend, backend, database and service "
            "engineering for MAJD."
        ),
    )

    for capability_id, name in (
        (
            "FRONTEND_ENGINEERING",
            "Frontend Engineering",
        ),
        (
            "BACKEND_ENGINEERING",
            "Backend Engineering",
        ),
        (
            "API_ENGINEERING",
            "API Engineering",
        ),
        (
            "DATABASE_ENGINEERING",
            "Database Engineering",
        ),
        (
            "REALTIME_SERVICES",
            "Realtime Services",
        ),
        (
            "AUTHENTICATION",
            "Authentication",
        ),
        (
            "STORAGE_ENGINEERING",
            "Storage Engineering",
        ),
        (
            "QUEUE_WORKERS",
            "Queue & Worker Engineering",
        ),
        (
            "CACHE_ENGINEERING",
            "Cache Engineering",
        ),
        (
            "PERFORMANCE_ENGINEERING",
            "Performance Engineering",
        ),
    ):

        add_capability(
            "PLATFORM_ENGINEERING",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # DEVOPS / INFRASTRUCTURE
    # ========================================================

    add_department(
        "INFRASTRUCTURE",
        "MAJD Sovereign Infrastructure",
        (
            "Servers, containers, deployment and operational "
            "infrastructure."
        ),
    )

    for capability_id, name in (
        (
            "SERVER_MANAGEMENT",
            "Server Management",
        ),
        (
            "CONTAINER_RUNTIME",
            "Container Runtime",
        ),
        (
            "REVERSE_PROXY",
            "Reverse Proxy",
        ),
        (
            "CI_CD",
            "CI/CD",
        ),
        (
            "BUILD_INFRASTRUCTURE",
            "Build Infrastructure",
        ),
        (
            "ARTIFACT_STORAGE",
            "Artifact Storage",
        ),
        (
            "DEPLOYMENT",
            "Deployment",
        ),
        (
            "ROLLBACK",
            "Rollback",
        ),
        (
            "SCALING",
            "Scaling",
        ),
        (
            "LOGGING",
            "Logging",
        ),
        (
            "MONITORING",
            "Monitoring",
        ),
        (
            "BACKUP",
            "Backup",
        ),
        (
            "DISASTER_RECOVERY",
            "Disaster Recovery",
        ),
    ):

        add_capability(
            "INFRASTRUCTURE",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # MAINTENANCE
    # ========================================================

    add_department(
        "MAINTENANCE",
        "MAJD AI Maintenance",
        (
            "Detects, diagnoses, repairs and verifies "
            "operational failures."
        ),
    )

    for capability_id, name in (
        (
            "FAULT_DETECTION",
            "Fault Detection",
        ),
        (
            "DIAGNOSTICS",
            "Diagnostics",
        ),
        (
            "AUTO_REPAIR",
            "Automatic Repair",
        ),
        (
            "DEPENDENCY_REPAIR",
            "Dependency Repair",
        ),
        (
            "BUILD_REPAIR",
            "Build Repair",
        ),
        (
            "SERVICE_RECOVERY",
            "Service Recovery",
        ),
        (
            "POST_REPAIR_TEST",
            "Post Repair Verification",
        ),
    ):

        add_capability(
            "MAINTENANCE",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # SECURITY
    # ========================================================

    add_department(
        "SOVEREIGN_SECURITY",
        "MAJD Sovereign Security & Protection",
        (
            "Layered cyber security, detection, containment "
            "and recovery."
        ),
    )

    for capability_id, name in (
        (
            "IAM",
            "Identity & Access Management",
        ),
        (
            "MFA",
            "Multi-Factor Authentication",
        ),
        (
            "SECRETS_MANAGEMENT",
            "Secrets Management",
        ),
        (
            "ENCRYPTION",
            "Encryption",
        ),
        (
            "NETWORK_ISOLATION",
            "Network Isolation",
        ),
        (
            "RATE_LIMITING",
            "Rate Limiting",
        ),
        (
            "ABUSE_PROTECTION",
            "Abuse Protection",
        ),
        (
            "VULNERABILITY_MANAGEMENT",
            "Vulnerability Management",
        ),
        (
            "DEPENDENCY_SECURITY",
            "Dependency Security",
        ),
        (
            "AUDIT_LOGGING",
            "Security Audit Logging",
        ),
        (
            "INTRUSION_DETECTION",
            "Intrusion Detection",
        ),
        (
            "INCIDENT_RESPONSE",
            "Incident Response",
        ),
        (
            "SERVER_HARDENING",
            "Server Hardening",
        ),
        (
            "CONTAINER_HARDENING",
            "Container Hardening",
        ),
        (
            "DATABASE_SECURITY",
            "Database Security",
        ),
        (
            "PAYMENT_SECURITY",
            "Payment Security",
        ),
        (
            "SUPPLY_CHAIN_SECURITY",
            "Supply Chain Security",
        ),
        (
            "SECURITY_RECOVERY",
            "Security Recovery",
        ),
    ):

        add_capability(
            "SOVEREIGN_SECURITY",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # QA
    # ========================================================

    add_department(
        "QUALITY_ASSURANCE",
        "MAJD Sovereign Quality Assurance",
        (
            "Rejects low-quality, broken, unsafe or "
            "unverified production output."
        ),
    )

    for capability_id, name in (
        (
            "VISUAL_QA",
            "Visual QA",
        ),
        (
            "GAMEPLAY_QA",
            "Gameplay QA",
        ),
        (
            "ANIMATION_QA",
            "Animation QA",
        ),
        (
            "WORLD_QA",
            "World QA",
        ),
        (
            "ECOSYSTEM_QA",
            "Ecosystem QA",
        ),
        (
            "CAMERA_QA",
            "Camera QA",
        ),
        (
            "AUDIO_QA",
            "Audio QA",
        ),
        (
            "UI_QA",
            "UI/UX QA",
        ),
        (
            "PERFORMANCE_QA",
            "Performance QA",
        ),
        (
            "MOBILE_QA",
            "Mobile QA",
        ),
        (
            "TABLET_QA",
            "Tablet QA",
        ),
        (
            "PC_QA",
            "PC QA",
        ),
        (
            "BROWSER_QA",
            "Browser QA",
        ),
        (
            "BUILD_QA",
            "Build QA",
        ),
        (
            "SECURITY_QA",
            "Security QA",
        ),
    ):

        add_capability(
            "QUALITY_ASSURANCE",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # ECONOMY / COMMERCE
    # ========================================================

    add_department(
        "ECONOMY_COMMERCE",
        "MAJD Economy & Commerce",
        (
            "Game/platform economy, payments, stores and "
            "commercial operations."
        ),
    )

    for capability_id, name in (
        (
            "WALLET",
            "Wallet",
        ),
        (
            "COINS",
            "Coins",
        ),
        (
            "REWARDS",
            "Rewards",
        ),
        (
            "PACKAGES",
            "Packages",
        ),
        (
            "SUBSCRIPTIONS",
            "Subscriptions",
        ),
        (
            "IN_GAME_PURCHASES",
            "In-Game Purchases",
        ),
        (
            "PAYMENTS",
            "Payments",
        ),
        (
            "REFUNDS",
            "Refunds",
        ),
        (
            "ADS",
            "Advertising",
        ),
        (
            "REWARDED_ADS",
            "Rewarded Advertising",
        ),
        (
            "MARKETPLACE",
            "Marketplace",
        ),
        (
            "FRAUD_CONTROLS",
            "Fraud Controls",
        ),
        (
            "VAT_ZAKAT_LEDGER",
            "VAT/Zakat Ledger Integration",
        ),
    ):

        add_capability(
            "ECONOMY_COMMERCE",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # ANALYTICS
    # ========================================================

    add_department(
        "ANALYTICS_INTELLIGENCE",
        "MAJD Analytics Intelligence",
        (
            "Production, platform and gameplay analytics."
        ),
    )

    for capability_id, name in (
        (
            "PLAYER_ANALYTICS",
            "Player Analytics",
        ),
        (
            "GAME_ANALYTICS",
            "Game Analytics",
        ),
        (
            "PLATFORM_ANALYTICS",
            "Platform Analytics",
        ),
        (
            "ERROR_ANALYTICS",
            "Error Analytics",
        ),
        (
            "PERFORMANCE_ANALYTICS",
            "Performance Analytics",
        ),
        (
            "RELEASE_ANALYTICS",
            "Release Analytics",
        ),
        (
            "QUALITY_ANALYTICS",
            "Quality Analytics",
        ),
    ):

        add_capability(
            "ANALYTICS_INTELLIGENCE",
            capability_id,
            name,
            f"{name} capability.",
        )


    # ========================================================
    # BUILD / EXECUTION / PUBLISH
    # ========================================================

    add_department(
        "PRODUCTION_EXECUTION",
        "MAJD Production Execution",
        (
            "Real build, executor integration, packaging "
            "and publication."
        ),
    )

    add_capability(
        "PRODUCTION_EXECUTION",
        "REAL_GAME_EXECUTOR",
        "03 Real Game Executor",
        (
            "Connects to MAJD-REAL-GAME-EXECUTOR-03.py "
            "for real game build execution."
        ),
        required=True,
    )

    add_capability(
        "PRODUCTION_EXECUTION",
        "REAL_BUILD",
        "Real Build",
        (
            "Produces verifiable build artifacts."
        ),
        required=True,
    )

    add_capability(
        "PRODUCTION_EXECUTION",
        "PACKAGING",
        "Packaging",
        (
            "Packages verified production artifacts."
        ),
    )

    add_capability(
        "PRODUCTION_EXECUTION",
        "PUBLISHING",
        "Publishing",
        (
            "Publishes only approved and verified releases."
        ),
    )

    add_capability(
        "PRODUCTION_EXECUTION",
        "POST_RELEASE_MONITORING",
        "Post Release Monitoring",
        (
            "Monitors deployed production releases."
        ),
    )


    # ========================================================
    # FUTURE ADVANCED
    # ========================================================

    add_department(
        "ADVANCED_FUTURE",
        "MAJD Advanced Future Systems",
        (
            "Reserved architecture for future advanced "
            "production capabilities."
        ),
    )

    for capability_id, name in (
        (
            "DIGITAL_HUMANS",
            "Digital Humans",
        ),
        (
            "PROCEDURAL_CITIES",
            "Procedural Cities",
        ),
        (
            "CROWD_SIMULATION",
            "Crowd Simulation",
        ),
        (
            "DIGITAL_TWINS",
            "Digital Twins",
        ),
        (
            "XR_PRODUCTION",
            "XR / VR / AR Production",
        ),
        (
            "RENDER_FARM",
            "Render Farm",
        ),
        (
            "MOTION_CAPTURE",
            "Motion Capture Pipeline",
        ),
        (
            "CUSTOM_MAJD_MODELS",
            "Custom MAJD AI Models",
        ),
        (
            "ADVANCED_SIMULATION",
            "Advanced Simulation",
        ),
    ):

        add_capability(
            "ADVANCED_FUTURE",
            capability_id,
            name,
            f"{name} reserved capability.",
            future_ready=True,
        )


    return (
        departments,
        capabilities,
    )


# ============================================================
# COMPANY RUNTIME
# ============================================================

class MajdSovereignCompany:

    def __init__(
        self,
        root_dir: Optional[str] = None,
        state_dir: Optional[str] = None,
        work_dir: Optional[str] = None,
    ):

        self.root_dir = Path(
            root_dir
            or Path(__file__).resolve().parent
        ).resolve()

        self.state_dir = ensure_directory(
            Path(
                state_dir
                or (
                    self.root_dir
                    /
                    DEFAULT_STATE_DIRECTORY
                )
            ).resolve()
        )

        self.work_dir = ensure_directory(
            Path(
                work_dir
                or (
                    self.root_dir
                    /
                    DEFAULT_WORK_DIRECTORY
                )
            ).resolve()
        )

        (
            self.departments,
            self.capabilities,
        ) = build_company_blueprint()

        self.adapters = AdapterRegistry()

        self.started_at = utc_now()

        self.company_state_file = (
            self.state_dir
            /
            "company-state.json"
        )

        self.jobs_dir = ensure_directory(
            self.state_dir
            /
            "jobs"
        )

        self.audit_file = (
            self.state_dir
            /
            "audit.jsonl"
        )

        self._register_builtin_adapters()

        self.refresh_health()

        self.save_company_state()


    # ========================================================
    # AUDIT
    # ========================================================

    def audit(
        self,
        event: str,
        payload: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> None:

        record = {
            "time":
                utc_now(),
            "system":
                SYSTEM_NAME,
            "company":
                COMPANY_NAME,
            "event":
                event,
            "payload":
                dict(
                    payload
                    or {}
                ),
        }

        self.audit_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.audit_file.open(
            "a",
            encoding="utf-8",
        ) as file:

            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                    default=str,
                )
            )

            file.write("\n")


    # ========================================================
    # BUILTIN ADAPTERS
    # ========================================================

    def _register_builtin_adapters(
        self,
    ) -> None:

        executor_candidates = [
            self.root_dir
            /
            "MAJD-REAL-GAME-EXECUTOR-03.py",

            self.root_dir
            /
            "03"
            /
            "MAJD-REAL-GAME-EXECUTOR-03.py",
        ]

        for candidate in executor_candidates:

            if candidate.exists():

                self.adapters.register(
                    "REAL_GAME_EXECUTOR",
                    RealGameExecutor03Adapter(
                        candidate
                    ),
                )

                break


        if command_exists("node"):

            self.adapters.register(
                "REAL_BUILD",
                CommandAdapter(
                    executable="node",
                    adapter_name=(
                        "NODE-RUNTIME"
                    ),
                    engine_name="Node.js",
                ),
            )


        if command_exists("docker"):

            self.adapters.register(
                "CONTAINER_RUNTIME",
                CommandAdapter(
                    executable="docker",
                    adapter_name=(
                        "DOCKER-RUNTIME"
                    ),
                    engine_name="Docker",
                ),
            )


        if command_exists("ffmpeg"):

            self.adapters.register(
                "VIDEO_EDITING",
                CommandAdapter(
                    executable="ffmpeg",
                    adapter_name=(
                        "FFMPEG-VIDEO"
                    ),
                    engine_name="FFmpeg",
                    version_args=[
                        "-version",
                    ],
                ),
            )

            self.adapters.register(
                "AUDIO_MIXING",
                CommandAdapter(
                    executable="ffmpeg",
                    adapter_name=(
                        "FFMPEG-AUDIO"
                    ),
                    engine_name="FFmpeg",
                    version_args=[
                        "-version",
                    ],
                ),
            )


        if command_exists("blender"):

            self.adapters.register(
                "MESH_GENERATION",
                CommandAdapter(
                    executable="blender",
                    adapter_name=(
                        "BLENDER-3D"
                    ),
                    engine_name="Blender",
                    version_args=[
                        "--version",
                    ],
                ),
            )


        if command_exists("godot"):

            self.adapters.register(
                "GAMEPLAY_ENGINEERING",
                CommandAdapter(
                    executable="godot",
                    adapter_name=(
                        "GODOT-GAME-ENGINE"
                    ),
                    engine_name="Godot",
                    version_args=[
                        "--version",
                    ],
                ),
            )

        elif command_exists("godot4"):

            self.adapters.register(
                "GAMEPLAY_ENGINEERING",
                CommandAdapter(
                    executable="godot4",
                    adapter_name=(
                        "GODOT4-GAME-ENGINE"
                    ),
                    engine_name="Godot 4",
                    version_args=[
                        "--version",
                    ],
                ),
            )


    # ========================================================
    # EXTERNAL ADAPTER REGISTRATION
    # ========================================================

    def register_adapter(
        self,
        capability_id: str,
        adapter: SovereignAdapter,
    ) -> None:

        if capability_id not in self.capabilities:

            raise KeyError(
                f"Unknown capability: {capability_id}"
            )

        self.adapters.register(
            capability_id,
            adapter,
        )

        self.audit(
            "ADAPTER_REGISTERED",
            {
                "capability_id":
                    capability_id,
                "adapter":
                    adapter.adapter_name,
                "engine":
                    adapter.engine_name,
            },
        )

        self.refresh_health()

        self.save_company_state()


    # ========================================================
    # HEALTH
    # ========================================================

    def refresh_health(
        self,
    ) -> Dict[str, Any]:

        for capability_id, capability in (
            self.capabilities.items()
        ):

            adapter = self.adapters.get(
                capability_id
            )

            if adapter is None:

                capability.status = (
                    CapabilityStatus.UNAVAILABLE
                )

                capability.adapter_name = None
                capability.engine_name = None

                capability.health = (
                    HealthResult(
                        success=False,
                        status="NO_REAL_ADAPTER",
                        message=(
                            "No real adapter is registered "
                            "for this capability."
                        ),
                    )
                )

                continue


            capability.adapter_name = (
                adapter.adapter_name
            )

            capability.engine_name = (
                adapter.engine_name
            )


            try:

                health = (
                    adapter.health_check()
                )

            except Exception as error:

                health = HealthResult(
                    success=False,
                    status=(
                        "ADAPTER_HEALTH_EXCEPTION"
                    ),
                    message=(
                        f"{type(error).__name__}: "
                        f"{error}"
                    ),
                )


            capability.health = health


            if health.success:

                capability.status = (
                    CapabilityStatus.AVAILABLE
                )

            else:

                capability.status = (
                    CapabilityStatus.FAILED
                )


        self._refresh_department_statuses()

        return self.health_report()


    def _refresh_department_statuses(
        self,
    ) -> None:

        for department in (
            self.departments.values()
        ):

            states = [
                self.capabilities[
                    capability_id
                ].status
                for capability_id
                in department.capabilities
            ]

            if not states:

                department.status = (
                    DepartmentStatus.UNAVAILABLE
                )

                continue


            available_count = sum(
                state
                in (
                    CapabilityStatus.AVAILABLE,
                    CapabilityStatus.CONFIGURED,
                )
                for state
                in states
            )

            failed_count = sum(
                state
                ==
                CapabilityStatus.FAILED
                for state
                in states
            )


            if available_count == len(states):

                department.status = (
                    DepartmentStatus.READY
                )

            elif available_count > 0:

                department.status = (
                    DepartmentStatus.DEGRADED
                )

            elif failed_count > 0:

                department.status = (
                    DepartmentStatus.FAILED
                )

            else:

                department.status = (
                    DepartmentStatus.UNAVAILABLE
                )


    # ========================================================
    # REPORTS
    # ========================================================

    def health_report(
        self,
    ) -> Dict[str, Any]:

        status_counts: Dict[
            str,
            int
        ] = {}

        for capability in (
            self.capabilities.values()
        ):

            key = capability.status.value

            status_counts[key] = (
                status_counts.get(
                    key,
                    0,
                )
                +
                1
            )


        department_counts: Dict[
            str,
            int
        ] = {}

        for department in (
            self.departments.values()
        ):

            key = department.status.value

            department_counts[key] = (
                department_counts.get(
                    key,
                    0,
                )
                +
                1
            )


        return {
            "system":
                SYSTEM_NAME,

            "company":
                COMPANY_NAME,

            "version":
                VERSION,

            "time":
                utc_now(),

            "capabilities_total":
                len(
                    self.capabilities
                ),

            "departments_total":
                len(
                    self.departments
                ),

            "capability_status":
                status_counts,

            "department_status":
                department_counts,
        }


    def company_manifest(
        self,
    ) -> Dict[str, Any]:

        return {
            "system":
                SYSTEM_NAME,

            "company":
                COMPANY_NAME,

            "file":
                COMPANY_FILE,

            "version":
                VERSION,

            "architecture": {
                "mastermind":
                    MASTERMIND_LAYER,

                "company":
                    COMPANY_LAYER,

                "executor":
                    EXECUTOR_LAYER,
            },

            "root_dir":
                str(
                    self.root_dir
                ),

            "state_dir":
                str(
                    self.state_dir
                ),

            "work_dir":
                str(
                    self.work_dir
                ),

            "started_at":
                self.started_at,

            "health":
                self.health_report(),

            "departments": {
                department_id:
                    asdict(
                        department
                    )
                for (
                    department_id,
                    department
                )
                in self.departments.items()
            },

            "capabilities": {
                capability_id:
                    asdict(
                        capability
                    )
                for (
                    capability_id,
                    capability
                )
                in self.capabilities.items()
            },
        }


    def save_company_state(
        self,
    ) -> None:

        write_json(
            self.company_state_file,
            self.company_manifest(),
        )


    # ========================================================
    # CAPABILITY REQUIREMENT
    # ========================================================

    def require_capability(
        self,
        capability_id: str,
    ) -> CapabilityDefinition:

        capability = self.capabilities.get(
            capability_id
        )

        if capability is None:

            raise RuntimeError(
                f"Unknown capability: {capability_id}"
            )


        if capability.status not in (
            CapabilityStatus.AVAILABLE,
            CapabilityStatus.CONFIGURED,
        ):

            raise RuntimeError(
                (
                    f"Capability {capability_id} "
                    f"is not operational. "
                    f"Status={capability.status.value}"
                )
            )


        adapter = self.adapters.get(
            capability_id
        )

        if adapter is None:

            raise RuntimeError(
                (
                    f"Capability {capability_id} "
                    "has no real adapter."
                )
            )


        return capability


    # ========================================================
    # EXECUTE CAPABILITY
    # ========================================================

    def execute_capability(
        self,
        capability_id: str,
        action: str,
        payload: Mapping[str, Any],
        job_id: str,
    ) -> Dict[str, Any]:

        self.require_capability(
            capability_id
        )

        adapter = self.adapters.get(
            capability_id
        )

        if adapter is None:

            raise RuntimeError(
                "Adapter unexpectedly unavailable."
            )


        capability_work_dir = (
            self.work_dir
            /
            safe_identifier(
                job_id
            )
            /
            safe_identifier(
                capability_id
            )
        )

        capability_work_dir.mkdir(
            parents=True,
            exist_ok=True,
        )


        started = time.time()


        try:

            result = adapter.execute(
                action=action,
                payload=dict(
                    payload
                ),
                work_dir=
                    capability_work_dir,
            )

        except NotImplementedError as error:

            result = {
                "success":
                    False,
                "status":
                    "EXECUTION_NOT_IMPLEMENTED",
                "error":
                    str(error),
            }

        except Exception as error:

            result = {
                "success":
                    False,
                "status":
                    "ADAPTER_EXECUTION_EXCEPTION",
                "error":
                    (
                        f"{type(error).__name__}: "
                        f"{error}"
                    ),
                "traceback":
                    traceback.format_exc(),
            }


        result = dict(
            result
            or {}
        )

        result.setdefault(
            "success",
            False,
        )

        result.setdefault(
            "capability_id",
            capability_id,
        )

        result.setdefault(
            "adapter",
            adapter.adapter_name,
        )

        result.setdefault(
            "engine",
            adapter.engine_name,
        )

        result.setdefault(
            "duration_seconds",
            time.time() - started,
        )


        self.audit(
            "CAPABILITY_EXECUTION",
            {
                "job_id":
                    job_id,
                "capability_id":
                    capability_id,
                "action":
                    action,
                "success":
                    bool(
                        result.get(
                            "success"
                        )
                    ),
                "status":
                    result.get(
                        "status"
                    ),
            },
        )


        return result


    # ========================================================
    # REQUEST ANALYSIS
    # ========================================================

    def analyze_request(
        self,
        request: Mapping[str, Any],
    ) -> Dict[str, Any]:

        request_data = dict(
            request
            or {}
        )

        request_type = str(
            request_data.get(
                "type",
                "UNKNOWN",
            )
        ).upper()


        requested_capabilities: List[
            str
        ] = []


        if request_type in (
            "CREATE_GAME",
            "BUILD_GAME",
            "GENERATE_GAME",
        ):

            requested_capabilities.extend(
                [
                    "GAME_DIRECTOR",
                    "CREATIVE_DIRECTOR",
                    "ART_DIRECTOR",
                    "WORLD_PLANNER",
                    "WORLD_MAP_GENERATION",
                    "LEVEL_DESIGN",
                    "GAMEPLAY_ENGINEERING",
                    "PLAYER_CONTROLLER",
                    "THIRD_PERSON_CAMERA",
                    "CAMERA_ORBIT",
                    "CAMERA_ZOOM",
                    "PINCH_ZOOM",
                    "VISUAL_QA",
                    "GAMEPLAY_QA",
                    "BUILD_QA",
                    "ORIGINALITY_REVIEW",
                    "IP_SIMILARITY_REVIEW",
                    "REAL_GAME_EXECUTOR",
                    "REAL_BUILD",
                ]
            )


        if request_data.get(
            "realistic_characters"
        ):

            requested_capabilities.extend(
                [
                    "CHARACTER_DESIGN",
                    "HUMAN_GENERATION",
                    "FACE_GENERATION",
                    "BODY_GENERATION",
                    "HAIR_GENERATION",
                    "SKIN_MATERIAL",
                    "AUTO_RIGGING",
                    "SKELETON",
                    "IDLE_ANIMATION",
                    "WALK_ANIMATION",
                    "RUN_ANIMATION",
                ]
            )


        if request_data.get(
            "world"
        ) or request_data.get(
            "open_world"
        ):

            requested_capabilities.extend(
                [
                    "WORLD_PLANNER",
                    "WORLD_MAP_GENERATION",
                    "TERRAIN_GENERATION",
                    "CITY_PLANNING",
                    "ROAD_NETWORKS",
                    "POI_PLANNING",
                ]
            )


        if request_data.get(
            "realistic_nature"
        ):

            requested_capabilities.extend(
                [
                    "TREE_GENERATION",
                    "PLANT_GENERATION",
                    "GRASS_GENERATION",
                    "FOREST_GENERATION",
                    "WILDLIFE_GENERATION",
                    "ECOSYSTEM_SIMULATION",
                ]
            )


        if request_data.get(
            "weather"
        ):

            requested_capabilities.extend(
                [
                    "RAIN_SYSTEM",
                    "SNOW_SYSTEM",
                    "FOG_SYSTEM",
                    "CLOUD_SYSTEM",
                    "DAY_NIGHT",
                    "SEASONS",
                ]
            )


        if request_data.get(
            "cinematic"
        ):

            requested_capabilities.extend(
                [
                    "CINEMATIC_DIRECTION",
                    "STORYBOARD",
                    "SHOT_PLANNING",
                    "CUTSCENE_GENERATION",
                    "CINEMATIC_ANIMATION",
                    "CINEMATIC_VFX",
                ]
            )


        if request_data.get(
            "generate_images"
        ):

            requested_capabilities.append(
                "IMAGE_GENERATION"
            )


        if request_data.get(
            "generate_video"
        ):

            requested_capabilities.append(
                "VIDEO_GENERATION"
            )


        if request_data.get(
            "voice"
        ):

            requested_capabilities.extend(
                [
                    "VOICE_GENERATION",
                    "DUBBING",
                ]
            )


        if request_data.get(
            "music"
        ):

            requested_capabilities.append(
                "MUSIC_GENERATION"
            )


        if request_data.get(
            "web_research"
        ):

            requested_capabilities.append(
                "WEB_RESEARCH"
            )


        requested_capabilities = list(
            dict.fromkeys(
                requested_capabilities
            )
        )


        operational = []

        unavailable = []


        for capability_id in (
            requested_capabilities
        ):

            capability = self.capabilities.get(
                capability_id
            )

            if capability is None:

                unavailable.append(
                    {
                        "capability_id":
                            capability_id,
                        "reason":
                            "UNKNOWN_CAPABILITY",
                    }
                )

                continue


            if capability.status in (
                CapabilityStatus.AVAILABLE,
                CapabilityStatus.CONFIGURED,
            ):

                operational.append(
                    capability_id
                )

            else:

                unavailable.append(
                    {
                        "capability_id":
                            capability_id,
                        "status":
                            capability.status.value,
                        "reason":
                            (
                                capability.health.status
                                if capability.health
                                else "NO_HEALTH"
                            ),
                    }
                )


        return {
            "request_type":
                request_type,

            "requested_capabilities":
                requested_capabilities,

            "operational":
                operational,

            "unavailable":
                unavailable,

            "all_required_operational":
                len(
                    unavailable
                )
                ==
                0,
        }


    # ========================================================
    # PRODUCTION PLAN
    # ========================================================

    def create_production_plan(
        self,
        request: Mapping[str, Any],
    ) -> Dict[str, Any]:

        analysis = self.analyze_request(
            request
        )

        stages = [
            {
                "stage":
                    "RESEARCH",
                "departments": [
                    "PLAYER_MARKET_INTELLIGENCE",
                    "ORIGINALITY_IP",
                ],
            },
            {
                "stage":
                    "DIRECTION",
                "departments": [
                    "AI_DIRECTION",
                ],
            },
            {
                "stage":
                    "WORLD",
                "departments": [
                    "WORLD_MAP_FACTORY",
                    "ARCHITECTURE_FACTORY",
                    "TERRAIN_FACTORY",
                    "NATURE_ECOSYSTEM",
                    "CLIMATE_WEATHER",
                    "WATER_FACTORY",
                ],
            },
            {
                "stage":
                    "ASSETS",
                "departments": [
                    "CHARACTER_FACTORY",
                    "FASHION_EQUIPMENT",
                    "ASSET_3D_FACTORY",
                    "ANIMATION_FACTORY",
                    "IMAGE_ART_STUDIO",
                ],
            },
            {
                "stage":
                    "GAME_ENGINEERING",
                "departments": [
                    "GAME_ENGINEERING",
                    "PHYSICS_ENGINEERING",
                    "CAMERA_ENGINEERING",
                    "GAME_AGENT_AI",
                    "MULTIPLAYER_ENGINEERING",
                ],
            },
            {
                "stage":
                    "EXPERIENCE",
                "departments": [
                    "UI_UX_FACTORY",
                    "STORY_WRITING",
                    "AUDIO_STUDIO",
                    "CINEMA_VIDEO_STUDIO",
                    "VFX_STUDIO",
                ],
            },
            {
                "stage":
                    "EXECUTION",
                "departments": [
                    "PRODUCTION_EXECUTION",
                ],
            },
            {
                "stage":
                    "QUALITY_SECURITY",
                "departments": [
                    "QUALITY_ASSURANCE",
                    "SOVEREIGN_SECURITY",
                    "ORIGINALITY_IP",
                ],
            },
            {
                "stage":
                    "OPERATIONS",
                "departments": [
                    "INFRASTRUCTURE",
                    "MAINTENANCE",
                    "ANALYTICS_INTELLIGENCE",
                ],
            },
        ]


        return {
            "success":
                True,

            "status":
                "PLAN_CREATED",

            "company":
                COMPANY_NAME,

            "request":
                dict(
                    request
                ),

            "analysis":
                analysis,

            "stages":
                stages,

            "created_at":
                utc_now(),
        }


    # ========================================================
    # QUALITY GATES
    # ========================================================

    def visual_quality_gate(
        self,
        report: Mapping[str, Any],
    ) -> GateResult:

        score = normalize_score(
            report.get(
                "visual_quality_score"
            ),
            0.0,
        )

        reasons = []


        if report.get(
            "primitive_placeholder_assets"
        ):

            reasons.append(
                (
                    "Primitive placeholder assets "
                    "cannot be accepted as final production."
                )
            )


        if report.get(
            "broken_assets"
        ):

            reasons.append(
                "Broken visual assets detected."
            )


        if score < (
            PRODUCTION_QUALITY_MINIMUM
        ):

            reasons.append(
                (
                    "Visual quality score is below "
                    "production minimum."
                )
            )


        decision = (
            GateDecision.PASS
            if not reasons
            else GateDecision.REJECT
        )


        return GateResult(
            gate="VISUAL_QUALITY",
            decision=decision,
            score=score,
            minimum_score=(
                PRODUCTION_QUALITY_MINIMUM
            ),
            reasons=reasons,
            evidence=dict(
                report
            ),
        )


    def originality_gate(
        self,
        report: Mapping[str, Any],
    ) -> GateResult:

        score = normalize_score(
            report.get(
                "originality_score"
            ),
            0.0,
        )

        reasons = []


        if report.get(
            "high_similarity_risk"
        ):

            reasons.append(
                (
                    "Potentially problematic similarity "
                    "was detected."
                )
            )


        if report.get(
            "known_asset_copy"
        ):

            reasons.append(
                (
                    "Known copied asset or protected "
                    "material was reported."
                )
            )


        if score < ORIGINALITY_MINIMUM:

            reasons.append(
                (
                    "Originality score is below "
                    "the required minimum."
                )
            )


        decision = (
            GateDecision.PASS
            if not reasons
            else GateDecision.REJECT
        )


        return GateResult(
            gate="ORIGINALITY_IP",
            decision=decision,
            score=score,
            minimum_score=
                ORIGINALITY_MINIMUM,
            reasons=reasons,
            evidence=dict(
                report
            ),
        )


    def security_gate(
        self,
        report: Mapping[str, Any],
    ) -> GateResult:

        score = normalize_score(
            report.get(
                "security_score"
            ),
            0.0,
        )

        reasons = []


        if report.get(
            "critical_vulnerability"
        ):

            reasons.append(
                "Critical vulnerability detected."
            )


        if report.get(
            "secret_exposure"
        ):

            reasons.append(
                "Secret exposure detected."
            )


        if score < SECURITY_MINIMUM:

            reasons.append(
                (
                    "Security score is below "
                    "the required minimum."
                )
            )


        decision = (
            GateDecision.PASS
            if not reasons
            else GateDecision.REJECT
        )


        return GateResult(
            gate="SECURITY",
            decision=decision,
            score=score,
            minimum_score=
                SECURITY_MINIMUM,
            reasons=reasons,
            evidence=dict(
                report
            ),
        )


    # ========================================================
    # PLACEHOLDER PROTECTION
    # ========================================================

    def reject_fake_production(
        self,
        production_result: Mapping[
            str,
            Any
        ],
    ) -> GateResult:

        reasons: List[str] = []


        if production_result.get(
            "fake_success"
        ):

            reasons.append(
                "Production reported fake success."
            )


        if production_result.get(
            "placeholder_as_final"
        ):

            reasons.append(
                (
                    "Placeholder content was presented "
                    "as final production."
                )
            )


        primitive_types = {
            "capsule",
            "sphere",
            "box",
            "cone",
            "primitive-placeholder",
        }


        final_asset_types = set(
            str(item).lower()
            for item
            in production_result.get(
                "final_asset_types",
                [],
            )
        )


        primitive_final = (
            primitive_types
            &
            final_asset_types
        )


        if primitive_final:

            reasons.append(
                (
                    "Primitive geometry was declared "
                    "as final production asset: "
                    +
                    ", ".join(
                        sorted(
                            primitive_final
                        )
                    )
                )
            )


        decision = (
            GateDecision.PASS
            if not reasons
            else GateDecision.REJECT
        )


        return GateResult(
            gate="REAL_PRODUCTION",
            decision=decision,
            score=(
                1.0
                if not reasons
                else 0.0
            ),
            minimum_score=1.0,
            reasons=reasons,
            evidence=dict(
                production_result
            ),
        )


    # ========================================================
    # JOB STORAGE
    # ========================================================

    def _job_path(
        self,
        job_id: str,
    ) -> Path:

        return (
            self.jobs_dir
            /
            (
                safe_identifier(
                    job_id
                )
                +
                ".json"
            )
        )


    def save_job(
        self,
        job: ProductionJob,
    ) -> None:

        job.updated_at = utc_now()

        write_json(
            self._job_path(
                job.job_id
            ),
            asdict(
                job
            ),
        )


    def load_job(
        self,
        job_id: str,
    ) -> Optional[Dict[str, Any]]:

        path = self._job_path(
            job_id
        )

        if not path.exists():
            return None

        return read_json(path)


    # ========================================================
    # CREATE JOB
    # ========================================================

    def create_job(
        self,
        request: Mapping[str, Any],
        job_id: Optional[str] = None,
    ) -> ProductionJob:

        actual_job_id = (
            str(
                job_id
                or uuid.uuid4()
            )
        )


        job = ProductionJob(
            job_id=
                actual_job_id,
            request=
                dict(
                    request
                ),
            status=
                JobStatus.CREATED,
            created_at=
                utc_now(),
            updated_at=
                utc_now(),
        )


        self.save_job(job)


        self.audit(
            "JOB_CREATED",
            {
                "job_id":
                    actual_job_id,
                "request_type":
                    request.get(
                        "type"
                    ),
            },
        )


        return job


    # ========================================================
    # PRE-FLIGHT
    # ========================================================

    def production_preflight(
        self,
        request: Mapping[str, Any],
    ) -> Dict[str, Any]:

        self.refresh_health()

        plan = self.create_production_plan(
            request
        )

        analysis = plan[
            "analysis"
        ]


        blocking = []


        for item in analysis[
            "unavailable"
        ]:

            capability_id = (
                item.get(
                    "capability_id"
                )
            )

            capability = (
                self.capabilities.get(
                    str(
                        capability_id
                    )
                )
            )

            if (
                capability
                and
                capability.required
            ):

                blocking.append(
                    item
                )


        return {
            "success":
                len(
                    blocking
                )
                ==
                0,

            "status":
                (
                    "PREFLIGHT_READY"
                    if not blocking
                    else "PREFLIGHT_BLOCKED"
                ),

            "analysis":
                analysis,

            "blocking":
                blocking,

            "plan":
                plan,

            "checked_at":
                utc_now(),
        }


    # ========================================================
    # SOVEREIGN REQUEST ENTRY
    # ========================================================

    def receive_request(
        self,
        request: Mapping[str, Any],
        job_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        job = self.create_job(
            request=request,
            job_id=job_id,
        )


        job.status = (
            JobStatus.PLANNING
        )

        self.save_job(job)


        preflight = (
            self.production_preflight(
                request
            )
        )


        job.outputs[
            "preflight"
        ] = preflight


        if not preflight.get(
            "success"
        ):

            job.status = (
                JobStatus.REJECTED
            )

            job.errors.append(
                {
                    "status":
                        "MISSING_REQUIRED_CAPABILITIES",
                    "blocking":
                        preflight.get(
                            "blocking",
                            [],
                        ),
                }
            )

            self.save_job(job)


            self.audit(
                "JOB_PREFLIGHT_REJECTED",
                {
                    "job_id":
                        job.job_id,
                    "blocking":
                        preflight.get(
                            "blocking",
                            [],
                        ),
                },
            )


            return {
                "success":
                    False,

                "status":
                    "MISSING_REQUIRED_CAPABILITIES",

                "job_id":
                    job.job_id,

                "preflight":
                    preflight,
            }


        job.status = (
            JobStatus.READY_FOR_EXECUTOR
        )

        self.save_job(job)


        self.audit(
            "JOB_READY_FOR_EXECUTOR",
            {
                "job_id":
                    job.job_id,
            },
        )


        return {
            "success":
                True,

            "status":
                "READY_FOR_EXECUTOR",

            "job_id":
                job.job_id,

            "preflight":
                preflight,

            "message":
                (
                    "Company planning layer accepted "
                    "the request. Real production must "
                    "still be executed and verified."
                ),
        }


    # ========================================================
    # STATUS
    # ========================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        self.refresh_health()

        return self.company_manifest()


# ============================================================
# PUBLIC COMPANY API
# ============================================================

_COMPANY_INSTANCE: Optional[
    MajdSovereignCompany
] = None


def get_company(
    root_dir: Optional[str] = None,
) -> MajdSovereignCompany:

    global _COMPANY_INSTANCE


    if _COMPANY_INSTANCE is None:

        _COMPANY_INSTANCE = (
            MajdSovereignCompany(
                root_dir=root_dir
            )
        )


    return _COMPANY_INSTANCE


def company_status(
    root_dir: Optional[str] = None,
) -> Dict[str, Any]:

    company = get_company(
        root_dir=root_dir
    )

    return company.status()


def company_health(
    root_dir: Optional[str] = None,
) -> Dict[str, Any]:

    company = get_company(
        root_dir=root_dir
    )

    return company.refresh_health()


def submit_sovereign_request(
    request: Mapping[str, Any],
    job_id: Optional[str] = None,
    root_dir: Optional[str] = None,
) -> Dict[str, Any]:

    company = get_company(
        root_dir=root_dir
    )

    return company.receive_request(
        request=request,
        job_id=job_id,
    )


def create_company_plan(
    request: Mapping[str, Any],
    root_dir: Optional[str] = None,
) -> Dict[str, Any]:

    company = get_company(
        root_dir=root_dir
    )

    return company.create_production_plan(
        request
    )


# ============================================================
# SELF TEST
# ============================================================

def run_self_test(
    root_dir: Optional[str] = None,
) -> Dict[str, Any]:

    started = time.time()


    try:

        company = (
            MajdSovereignCompany(
                root_dir=root_dir
            )
        )


        health = (
            company.refresh_health()
        )


        required_capabilities = [
            capability
            for capability
            in company.capabilities.values()
            if capability.required
        ]


        required_report = []


        for capability in (
            required_capabilities
        ):

            required_report.append(
                {
                    "capability_id":
                        capability.capability_id,
                    "status":
                        capability.status.value,
                    "health":
                        (
                            asdict(
                                capability.health
                            )
                            if capability.health
                            else None
                        ),
                }
            )


        return {
            "success":
                True,

            "status":
                "SELF_TEST_COMPLETE",

            "system":
                SYSTEM_NAME,

            "company":
                COMPANY_NAME,

            "version":
                VERSION,

            "python":
                sys.version,

            "platform":
                platform.platform(),

            "health":
                health,

            "required_capabilities":
                required_report,

            "duration_seconds":
                time.time()
                -
                started,
        }


    except Exception as error:

        return {
            "success":
                False,

            "status":
                "SELF_TEST_FAILED",

            "error":
                (
                    f"{type(error).__name__}: "
                    f"{error}"
                ),

            "traceback":
                traceback.format_exc(),

            "duration_seconds":
                time.time()
                -
                started,
        }


# ============================================================
# CLI
# ============================================================

def main() -> int:

    parser = argparse.ArgumentParser(
        description=(
            "MAJD AI SOVEREIGN COMPANY 02"
        )
    )


    parser.add_argument(
        "--root",
        default=str(
            Path(__file__)
            .resolve()
            .parent
        ),
        help=(
            "MAJD GAME FACTORY root directory."
        ),
    )


    parser.add_argument(
        "--status",
        action="store_true",
        help=(
            "Print complete company status."
        ),
    )


    parser.add_argument(
        "--health",
        action="store_true",
        help=(
            "Run capability health checks."
        ),
    )


    parser.add_argument(
        "--self-test",
        action="store_true",
        help=(
            "Run sovereign company self test."
        ),
    )


    parser.add_argument(
        "--list-departments",
        action="store_true",
        help=(
            "List all MAJD company departments."
        ),
    )


    parser.add_argument(
        "--list-capabilities",
        action="store_true",
        help=(
            "List all MAJD company capabilities."
        ),
    )


    parser.add_argument(
        "--request-json",
        default=None,
        help=(
            "Submit a sovereign production request "
            "as a JSON string."
        ),
    )


    args = parser.parse_args()


    company = MajdSovereignCompany(
        root_dir=args.root
    )


    if args.health:

        result = (
            company.refresh_health()
        )


    elif args.self_test:

        result = run_self_test(
            root_dir=args.root
        )


    elif args.list_departments:

        result = {
            "success":
                True,

            "departments": [
                {
                    "id":
                        department.department_id,

                    "name":
                        department.name,

                    "status":
                        department.status.value,

                    "capabilities":
                        len(
                            department.capabilities
                        ),
                }

                for department
                in company.departments.values()
            ],
        }


    elif args.list_capabilities:

        result = {
            "success":
                True,

            "capabilities": [
                {
                    "id":
                        capability.capability_id,

                    "name":
                        capability.name,

                    "department":
                        capability.department_id,

                    "status":
                        capability.status.value,

                    "required":
                        capability.required,

                    "adapter":
                        capability.adapter_name,

                    "engine":
                        capability.engine_name,
                }

                for capability
                in company.capabilities.values()
            ],
        }


    elif args.request_json:

        try:

            request = json.loads(
                args.request_json
            )


            if not isinstance(
                request,
                dict,
            ):

                raise ValueError(
                    (
                        "--request-json must "
                        "contain a JSON object."
                    )
                )


            result = (
                company.receive_request(
                    request
                )
            )


        except Exception as error:

            result = {
                "success":
                    False,

                "status":
                    "INVALID_REQUEST_JSON",

                "error":
                    (
                        f"{type(error).__name__}: "
                        f"{error}"
                    ),
            }


    else:

        result = (
            company.status()
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
            "success",
            True,
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

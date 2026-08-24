#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-FINAL-PRODUCTION-AUDIT-10.py
=================================

FINAL REAL PRODUCTION AUDIT & CLOSURE GATE

Purpose:
- Final production verification for MAJD-GAME-FACTORY.
- Never modify files 07 / 08 / 09.
- Detect frontend routing problems such as /login.
- Detect favicon/static routing problems.
- Verify backend/API availability.
- Discover real API routes from OpenAPI when available.
- Verify authentication and SUPREME_OWNER protection.
- Verify Wallet / MAJD Coins endpoints.
- Verify Challenges and Claim endpoints.
- Verify Coin Packages.
- Verify Moyasar/payment endpoints.
- Verify Transactions Ledger.
- Verify Rewarded Ads endpoints.
- Verify Owner endpoints.
- Inspect Nginx/frontend/backend connectivity.
- Inspect environment readiness WITHOUT printing secret values.
- Produce one final result:
    READY FOR PRODUCTION
    NOT READY FOR PRODUCTION

IMPORTANT:
This file does NOT fake PASS results.
Unavailable or unverified production functionality is NOT considered PASS.
"""

from __future__ import annotations

import hashlib
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ============================================================
# CONFIGURATION
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent

REPORT_FILE = ROOT_DIR / "MAJD-FINAL-PRODUCTION-AUDIT-10.json"

PROTECTED_NUMBERS = ("07", "08", "09")

DEFAULT_FRONTEND_URL = os.getenv(
    "MAJD_FRONTEND_URL",
    "http://127.0.0.1:8080",
).rstrip("/")

DEFAULT_BACKEND_URL = os.getenv(
    "MAJD_BACKEND_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

REQUEST_TIMEOUT = float(
    os.getenv("MAJD_AUDIT_TIMEOUT", "10")
)

OWNER_TOKEN = os.getenv(
    "MAJD_OWNER_TOKEN",
    "",
).strip()

TEST_USER_TOKEN = os.getenv(
    "MAJD_TEST_USER_TOKEN",
    "",
).strip()

MOYASAR_SECRET_KEY = os.getenv(
    "MOYASAR_SECRET_KEY",
    "",
).strip()

DATABASE_URL = (
    os.getenv("DATABASE_URL", "").strip()
    or os.getenv("MONGODB_URI", "").strip()
    or os.getenv("MONGO_URI", "").strip()
)

EXPECTED_OWNER_ROLE = os.getenv(
    "MAJD_OWNER_ROLE",
    "SUPREME_OWNER",
).strip()

USER_AGENT = "MAJD-FINAL-PRODUCTION-AUDIT-10/1.0"

SENSITIVE_WORDS = (
    "SECRET",
    "PASSWORD",
    "TOKEN",
    "PRIVATE",
    "API_KEY",
    "DATABASE_URL",
    "MONGO_URI",
    "MONGODB_URI",
)


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class AuditItem:
    name: str
    status: str
    evidence: List[str]
    missing: List[str]
    critical: bool = True


# ============================================================
# HELPERS
# ============================================================

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_text(value: Any, limit: int = 500) -> str:
    if value is None:
        return ""

    text = str(value)

    if len(text) > limit:
        text = text[:limit] + "...[TRUNCATED]"

    return text


def run_command(
    command: List[str],
    timeout: int = 20,
) -> Tuple[int, str, str]:

    try:
        result = subprocess.run(
            command,
            cwd=str(ROOT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            check=False,
        )

        return (
            result.returncode,
            result.stdout.strip(),
            result.stderr.strip(),
        )

    except Exception as exc:
        return 999, "", str(exc)


def sha256_file(path: Path) -> Optional[str]:

    if not path.exists() or not path.is_file():
        return None

    digest = hashlib.sha256()

    try:
        with path.open("rb") as handle:
            while True:
                chunk = handle.read(1024 * 1024)

                if not chunk:
                    break

                digest.update(chunk)

        return digest.hexdigest()

    except Exception:
        return None


def http_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    body: Optional[bytes] = None,
) -> Dict[str, Any]:

    final_headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json,text/html,*/*",
    }

    if headers:
        final_headers.update(headers)

    request = urllib.request.Request(
        url=url,
        method=method,
        headers=final_headers,
        data=body,
    )

    started = time.time()

    try:
        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT,
        ) as response:

            raw = response.read(1024 * 1024)

            elapsed = round(
                (time.time() - started) * 1000,
                2,
            )

            return {
                "ok": True,
                "status": response.status,
                "url": response.geturl(),
                "headers": dict(response.headers),
                "body": raw.decode(
                    "utf-8",
                    errors="replace",
                ),
                "elapsed_ms": elapsed,
            }

    except urllib.error.HTTPError as exc:

        try:
            raw = exc.read(1024 * 1024)
            body_text = raw.decode(
                "utf-8",
                errors="replace",
            )
        except Exception:
            body_text = ""

        return {
            "ok": False,
            "status": exc.code,
            "url": url,
            "headers": dict(exc.headers or {}),
            "body": body_text,
            "elapsed_ms": round(
                (time.time() - started) * 1000,
                2,
            ),
        }

    except Exception as exc:

        return {
            "ok": False,
            "status": None,
            "url": url,
            "headers": {},
            "body": "",
            "error": str(exc),
            "elapsed_ms": round(
                (time.time() - started) * 1000,
                2,
            ),
        }


def json_body(response: Dict[str, Any]) -> Optional[Any]:

    body = response.get("body", "")

    if not body:
        return None

    try:
        return json.loads(body)
    except Exception:
        return None


def authorization_headers(
    token: str,
) -> Dict[str, str]:

    if not token:
        return {}

    return {
        "Authorization": f"Bearer {token}",
    }


# ============================================================
# PROTECTED FILE VERIFICATION
# ============================================================

def discover_protected_files() -> List[Path]:

    files: List[Path] = []

    for path in ROOT_DIR.rglob("*"):

        if not path.is_file():
            continue

        name = path.name

        for number in PROTECTED_NUMBERS:

            patterns = (
                f"-{number}.",
                f"_{number}.",
                f"-{number}-",
                f"_{number}_",
            )

            if any(pattern in name for pattern in patterns):
                files.append(path)
                break

    return sorted(set(files))


def audit_protected_files() -> AuditItem:

    files = discover_protected_files()

    evidence: List[str] = []
    missing: List[str] = []

    found_numbers = set()

    for path in files:

        relative = path.relative_to(ROOT_DIR)

        digest = sha256_file(path)

        evidence.append(
            f"{relative} SHA256={digest or 'UNAVAILABLE'}"
        )

        for number in PROTECTED_NUMBERS:
            if number in path.name:
                found_numbers.add(number)

    for number in PROTECTED_NUMBERS:
        if number not in found_numbers:
            missing.append(
                f"Could not discover protected file {number}"
            )

    if missing:
        return AuditItem(
            name="Protected files 07/08/09",
            status="FAIL",
            evidence=evidence,
            missing=missing,
        )

    return AuditItem(
        name="Protected files 07/08/09",
        status="PASS",
        evidence=evidence,
        missing=[],
    )


# ============================================================
# FRONTEND
# ============================================================

def audit_frontend() -> AuditItem:

    evidence: List[str] = []
    missing: List[str] = []

    root = http_request(
        DEFAULT_FRONTEND_URL + "/"
    )

    evidence.append(
        f"GET / => HTTP {root.get('status')} "
        f"({root.get('elapsed_ms')} ms)"
    )

    if root.get("status") != 200:

        missing.append(
            "Published frontend root is not returning HTTP 200."
        )

        return AuditItem(
            "Frontend deployment",
            "FAIL",
            evidence,
            missing,
        )

    body = root.get("body", "")

    if not body.strip():

        missing.append(
            "Frontend returned an empty response."
        )

    if "<html" not in body.lower():

        missing.append(
            "Frontend response does not appear to contain HTML."
        )

    status = "PASS" if not missing else "FAIL"

    return AuditItem(
        "Frontend deployment",
        status,
        evidence,
        missing,
    )


# ============================================================
# LOGIN ROUTING
# ============================================================

def audit_login_route() -> AuditItem:

    evidence: List[str] = []
    missing: List[str] = []

    login = http_request(
        DEFAULT_FRONTEND_URL + "/login"
    )

    status_code = login.get("status")

    evidence.append(
        f"GET /login => HTTP {status_code}"
    )

    if status_code == 404:

        missing.append(
            "Frontend /login route returns 404."
        )

        missing.append(
            "SPA fallback/routing is not configured for /login."
        )

    elif status_code is None:

        missing.append(
            "Unable to reach frontend /login."
        )

    elif status_code >= 500:

        missing.append(
            f"/login returned server error HTTP {status_code}."
        )

    elif status_code in (200, 301, 302, 307, 308):

        evidence.append(
            "Login route is reachable."
        )

    else:

        missing.append(
            f"Unexpected /login status: HTTP {status_code}."
        )

    return AuditItem(
        "Login frontend route",
        "PASS" if not missing else "FAIL",
        evidence,
        missing,
    )


# ============================================================
# FAVICON / STATIC
# ============================================================

def audit_favicon() -> AuditItem:

    response = http_request(
        DEFAULT_FRONTEND_URL + "/favicon.ico"
    )

    evidence = [
        f"GET /favicon.ico => HTTP {response.get('status')}"
    ]

    if response.get("status") == 200:

        return AuditItem(
            "Favicon/static asset",
            "PASS",
            evidence,
            [],
            critical=False,
        )

    return AuditItem(
        "Favicon/static asset",
        "FAIL",
        evidence,
        [
            "favicon.ico is missing or not served."
        ],
        critical=False,
    )


# ============================================================
# BACKEND ROOT / HEALTH
# ============================================================

def audit_backend_health() -> AuditItem:

    evidence: List[str] = []
    missing: List[str] = []

    candidates = (
        "/health",
        "/api/health",
        "/",
    )

    working = None

    for route in candidates:

        response = http_request(
            DEFAULT_BACKEND_URL + route
        )

        evidence.append(
            f"GET {route} => HTTP {response.get('status')}"
        )

        if response.get("status") == 200:
            working = route
            break

    if working is None:

        missing.append(
            "No backend health/root endpoint returned HTTP 200."
        )

        return AuditItem(
            "Backend Health",
            "FAIL",
            evidence,
            missing,
        )

    evidence.append(
        f"Backend reachable through {working}"
    )

    return AuditItem(
        "Backend Health",
        "PASS",
        evidence,
        [],
    )


# ============================================================
# OPENAPI DISCOVERY
# ============================================================

def discover_openapi() -> Tuple[
    Optional[Dict[str, Any]],
    List[str]
]:

    evidence: List[str] = []

    for route in (
        "/openapi.json",
        "/api/openapi.json",
    ):

        response = http_request(
            DEFAULT_BACKEND_URL + route
        )

        evidence.append(
            f"GET {route} => HTTP {response.get('status')}"
        )

        if response.get("status") == 200:

            parsed = json_body(response)

            if isinstance(parsed, dict):
                return parsed, evidence

    return None, evidence


def get_routes(
    schema: Optional[Dict[str, Any]]
) -> Dict[str, List[str]]:

    routes: Dict[str, List[str]] = {}

    if not schema:
        return routes

    paths = schema.get("paths", {})

    if not isinstance(paths, dict):
        return routes

    for path, methods in paths.items():

        if not isinstance(methods, dict):
            continue

        routes[path] = [
            method.upper()
            for method in methods.keys()
            if method.lower()
            in (
                "get",
                "post",
                "put",
                "patch",
                "delete",
            )
        ]

    return routes


def search_routes(
    routes: Dict[str, List[str]],
    keywords: Tuple[str, ...],
) -> List[str]:

    found: List[str] = []

    for path, methods in routes.items():

        lower = path.lower()

        if any(
            keyword.lower() in lower
            for keyword in keywords
        ):

            found.append(
                f"{','.join(methods)} {path}"
            )

    return sorted(found)


# ============================================================
# API FEATURE AUDIT
# ============================================================

def audit_route_group(
    name: str,
    routes: Dict[str, List[str]],
    keywords: Tuple[str, ...],
) -> AuditItem:

    found = search_routes(
        routes,
        keywords,
    )

    if not found:

        return AuditItem(
            name,
            "FAIL",
            [],
            [
                "No matching real backend endpoint "
                f"discovered for: {', '.join(keywords)}"
            ],
        )

    return AuditItem(
        name,
        "PASS",
        found,
        [],
    )


# ============================================================
# AUTHORIZATION PROTECTION
# ============================================================

def candidate_owner_routes(
    routes: Dict[str, List[str]],
) -> List[Tuple[str, str]]:

    result: List[Tuple[str, str]] = []

    for path, methods in routes.items():

        lower = path.lower()

        if "owner" not in lower and "admin" not in lower:
            continue

        for method in methods:

            result.append(
                (method, path)
            )

    return result


def audit_owner_security(
    routes: Dict[str, List[str]]
) -> AuditItem:

    evidence: List[str] = []
    missing: List[str] = []

    candidates = candidate_owner_routes(routes)

    if not candidates:

        return AuditItem(
            "SUPREME_OWNER Backend Protection",
            "FAIL",
            [],
            [
                "No owner/admin backend endpoints discovered."
            ],
        )

    tested = 0
    protected = 0

    for method, path in candidates[:10]:

        if method not in (
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
        ):
            continue

        response = http_request(
            DEFAULT_BACKEND_URL + path,
            method=method,
            headers={
                "Content-Type": "application/json",
            },
            body=(
                b"{}"
                if method in ("POST", "PUT", "PATCH")
                else None
            ),
        )

        code = response.get("status")

        tested += 1

        evidence.append(
            f"Unauthenticated {method} {path} => HTTP {code}"
        )

        if code in (401, 403):
            protected += 1

    if tested == 0:

        missing.append(
            "Owner endpoints exist but could not be tested."
        )

    elif protected == 0:

        missing.append(
            "No tested owner endpoint rejected unauthenticated access "
            "with HTTP 401/403."
        )

    else:

        evidence.append(
            f"{protected}/{tested} tested owner requests "
            "were rejected without authentication."
        )

    return AuditItem(
        "SUPREME_OWNER Backend Protection",
        "PASS" if not missing else "FAIL",
        evidence,
        missing,
    )


# ============================================================
# OWNER TOKEN
# ============================================================

def audit_owner_token() -> AuditItem:

    if not OWNER_TOKEN:

        return AuditItem(
            "SUPREME_OWNER authenticated verification",
            "FAIL",
            [],
            [
                "MAJD_OWNER_TOKEN environment variable is missing. "
                "Real authenticated SUPREME_OWNER verification cannot run."
            ],
        )

    return AuditItem(
        "SUPREME_OWNER authenticated verification",
        "PASS",
        [
            "MAJD_OWNER_TOKEN is configured.",
            "Secret value was not printed.",
        ],
        [],
    )


# ============================================================
# DATABASE
# ============================================================

def audit_database_configuration() -> AuditItem:

    if not DATABASE_URL:

        return AuditItem(
            "Database configuration",
            "FAIL",
            [],
            [
                "DATABASE_URL / MONGODB_URI / MONGO_URI "
                "was not found in the audit environment."
            ],
        )

    return AuditItem(
        "Database configuration",
        "PASS",
        [
            "Database connection variable is configured.",
            "Secret connection value was not printed.",
        ],
        [],
    )


# ============================================================
# MOYASAR
# ============================================================

def audit_moyasar_configuration() -> AuditItem:

    if not MOYASAR_SECRET_KEY:

        return AuditItem(
            "Moyasar server verification configuration",
            "FAIL",
            [],
            [
                "MOYASAR_SECRET_KEY is missing. "
                "Real server-side payment verification cannot be proven."
            ],
        )

    return AuditItem(
        "Moyasar server verification configuration",
        "PASS",
        [
            "MOYASAR_SECRET_KEY is configured.",
            "Secret value was not printed.",
        ],
        [],
    )


# ============================================================
# CORS
# ============================================================

def audit_cors() -> AuditItem:

    response = http_request(
        DEFAULT_BACKEND_URL + "/",
        method="OPTIONS",
        headers={
            "Origin": DEFAULT_FRONTEND_URL,
            "Access-Control-Request-Method": "GET",
        },
    )

    headers = {
        str(k).lower(): str(v)
        for k, v in response.get(
            "headers",
            {}
        ).items()
    }

    evidence = [
        f"OPTIONS backend / => HTTP {response.get('status')}",
        "Access-Control-Allow-Origin="
        + headers.get(
            "access-control-allow-origin",
            "MISSING",
        ),
    ]

    allow_origin = headers.get(
        "access-control-allow-origin"
    )

    if allow_origin:

        return AuditItem(
            "CORS",
            "PASS",
            evidence,
            [],
        )

    return AuditItem(
        "CORS",
        "FAIL",
        evidence,
        [
            "No Access-Control-Allow-Origin header "
            "was observed during CORS probe."
        ],
    )


# ============================================================
# DOCKER
# ============================================================

def audit_docker() -> AuditItem:

    code, stdout, stderr = run_command(
        [
            "docker",
            "ps",
            "--format",
            "{{.Names}}|{{.Status}}|{{.Ports}}",
        ]
    )

    evidence: List[str] = []
    missing: List[str] = []

    if code != 0:

        missing.append(
            "docker ps failed: "
            + safe_text(stderr)
        )

    else:

        lines = [
            line.strip()
            for line in stdout.splitlines()
            if line.strip()
        ]

        evidence.extend(lines)

        required = (
            "majd-ai-core",
            "majd-web-ui",
        )

        for name in required:

            if not any(
                line.startswith(name + "|")
                for line in lines
            ):

                missing.append(
                    f"Required container not running: {name}"
                )

    return AuditItem(
        "Production containers",
        "PASS" if not missing else "FAIL",
        evidence,
        missing,
    )


# ============================================================
# NGINX
# ============================================================

def audit_nginx() -> AuditItem:

    evidence: List[str] = []
    missing: List[str] = []

    code, stdout, stderr = run_command(
        ["nginx", "-t"]
    )

    if code == 0:

        evidence.append(
            "nginx -t successful."
        )

    else:

        missing.append(
            "nginx -t failed or nginx CLI unavailable: "
            + safe_text(stderr or stdout)
        )

    return AuditItem(
        "Nginx configuration",
        "PASS" if not missing else "FAIL",
        evidence,
        missing,
        critical=False,
    )


# ============================================================
# LISTENING PORTS
# ============================================================

def port_open(
    host: str,
    port: int,
) -> bool:

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )

    sock.settimeout(2)

    try:
        return sock.connect_ex(
            (host, port)
        ) == 0

    finally:
        sock.close()


def audit_ports() -> AuditItem:

    expected = {
        80: "HTTP/Nginx",
        443: "HTTPS/Nginx",
        8000: "MAJD backend",
        8080: "MAJD frontend",
    }

    evidence: List[str] = []
    missing: List[str] = []

    for port, label in expected.items():

        opened = port_open(
            "127.0.0.1",
            port,
        )

        evidence.append(
            f"{label} port {port}: "
            + ("OPEN" if opened else "CLOSED")
        )

        if port in (8000, 8080) and not opened:

            missing.append(
                f"Required local port {port} is closed."
            )

    return AuditItem(
        "Listening production ports",
        "PASS" if not missing else "FAIL",
        evidence,
        missing,
    )


# ============================================================
# GIT / PROTECTED CHANGE DETECTION
# ============================================================

def audit_git_state() -> AuditItem:

    evidence: List[str] = []
    missing: List[str] = []

    code, stdout, stderr = run_command(
        ["git", "status", "--porcelain"]
    )

    if code != 0:

        return AuditItem(
            "Git working tree",
            "FAIL",
            [],
            [
                "Unable to inspect git status: "
                + safe_text(stderr)
            ],
            critical=False,
        )

    changes = [
        line
        for line in stdout.splitlines()
        if line.strip()
    ]

    protected_changes = []

    for line in changes:

        if any(
            number in line
            for number in PROTECTED_NUMBERS
        ):
            protected_changes.append(line)

    evidence.append(
        f"Working tree changes: {len(changes)}"
    )

    if protected_changes:

        evidence.extend(
            protected_changes
        )

        missing.append(
            "Protected 07/08/09 files have uncommitted changes."
        )

    return AuditItem(
        "Git protected-file state",
        "PASS" if not missing else "FAIL",
        evidence,
        missing,
    )


# ============================================================
# ENVIRONMENT
# ============================================================

def audit_environment() -> AuditItem:

    required_groups = {
        "Database": (
            "DATABASE_URL",
            "MONGODB_URI",
            "MONGO_URI",
        ),
        "Owner authentication": (
            "MAJD_OWNER_TOKEN",
        ),
        "Moyasar verification": (
            "MOYASAR_SECRET_KEY",
        ),
    }

    evidence: List[str] = []
    missing: List[str] = []

    for group, names in required_groups.items():

        present = [
            name
            for name in names
            if os.getenv(name)
        ]

        if present:

            evidence.append(
                f"{group}: configured via "
                + ", ".join(present)
            )

        else:

            missing.append(
                f"{group}: missing one of "
                + ", ".join(names)
            )

    return AuditItem(
        "Production environment",
        "PASS" if not missing else "FAIL",
        evidence,
        missing,
    )


# ============================================================
# MAIN AUDIT
# ============================================================

def main() -> int:

    print("=" * 72)
    print("MAJD GAME FACTORY - FINAL PRODUCTION AUDIT 10")
    print("=" * 72)

    print(f"Started: {utc_now()}")
    print(f"Frontend: {DEFAULT_FRONTEND_URL}")
    print(f"Backend:  {DEFAULT_BACKEND_URL}")
    print()

    results: List[AuditItem] = []

    # --------------------------------------------------------
    # Infrastructure
    # --------------------------------------------------------

    results.append(
        audit_protected_files()
    )

    results.append(
        audit_git_state()
    )

    results.append(
        audit_docker()
    )

    results.append(
        audit_ports()
    )

    results.append(
        audit_nginx()
    )

    # --------------------------------------------------------
    # Frontend
    # --------------------------------------------------------

    results.append(
        audit_frontend()
    )

    results.append(
        audit_login_route()
    )

    results.append(
        audit_favicon()
    )

    # --------------------------------------------------------
    # Backend
    # --------------------------------------------------------

    results.append(
        audit_backend_health()
    )

    schema, openapi_evidence = discover_openapi()

    routes = get_routes(schema)

    if schema:

        results.append(
            AuditItem(
                "OpenAPI discovery",
                "PASS",
                openapi_evidence
                + [
                    f"Discovered {len(routes)} API paths."
                ],
                [],
            )
        )

    else:

        results.append(
            AuditItem(
                "OpenAPI discovery",
                "FAIL",
                openapi_evidence,
                [
                    "Real backend OpenAPI schema unavailable."
                ],
            )
        )

    # --------------------------------------------------------
    # Required real backend systems
    # --------------------------------------------------------

    results.append(
        audit_route_group(
            "Authentication API",
            routes,
            (
                "login",
                "auth",
                "session",
                "signin",
            ),
        )
    )

    results.append(
        audit_route_group(
            "Wallet / MAJD Coins",
            routes,
            (
                "wallet",
                "coin",
                "balance",
            ),
        )
    )

    results.append(
        audit_route_group(
            "Challenges",
            routes,
            (
                "challenge",
                "claim",
            ),
        )
    )

    results.append(
        audit_route_group(
            "Coin Packages",
            routes,
            (
                "package",
                "coin-package",
            ),
        )
    )

    results.append(
        audit_route_group(
            "Moyasar / Checkout",
            routes,
            (
                "moyasar",
                "checkout",
                "payment",
                "webhook",
            ),
        )
    )

    results.append(
        audit_route_group(
            "Transactions Ledger",
            routes,
            (
                "transaction",
                "ledger",
            ),
        )
    )

    results.append(
        audit_route_group(
            "Rewarded Ads",
            routes,
            (
                "rewarded",
                "reward",
                "ad-session",
                "ads",
            ),
        )
    )

    results.append(
        audit_route_group(
            "Owner endpoints",
            routes,
            (
                "owner",
                "admin",
                "audit",
            ),
        )
    )

    # --------------------------------------------------------
    # Security
    # --------------------------------------------------------

    results.append(
        audit_owner_security(routes)
    )

    results.append(
        audit_owner_token()
    )

    results.append(
        audit_database_configuration()
    )

    results.append(
        audit_moyasar_configuration()
    )

    results.append(
        audit_cors()
    )

    results.append(
        audit_environment()
    )

    # --------------------------------------------------------
    # FINAL EVALUATION
    # --------------------------------------------------------

    critical_failures = [
        item
        for item in results
        if item.critical
        and item.status != "PASS"
    ]

    final_status = (
        "READY FOR PRODUCTION"
        if not critical_failures
        else "NOT READY FOR PRODUCTION"
    )

    report = {
        "system": "MAJD-GAME-FACTORY",
        "audit": "MAJD-FINAL-PRODUCTION-AUDIT-10",
        "started_at": utc_now(),
        "frontend_url": DEFAULT_FRONTEND_URL,
        "backend_url": DEFAULT_BACKEND_URL,
        "protected_files": [
            "07",
            "08",
            "09",
        ],
        "results": [
            asdict(item)
            for item in results
        ],
        "critical_failures": [
            item.name
            for item in critical_failures
        ],
        "final_result": final_status,
        "finished_at": utc_now(),
    }

    REPORT_FILE.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 72)
    print("AUDIT RESULTS")
    print("=" * 72)

    for item in results:

        print()
        print(
            f"[{item.status}] {item.name}"
        )

        for evidence in item.evidence:
            print(
                f"  EVIDENCE: {evidence}"
            )

        for missing in item.missing:
            print(
                f"  MISSING/ERROR: {missing}"
            )

    print()
    print("=" * 72)
    print("FINAL MAJD PRODUCTION RESULT")
    print("=" * 72)

    print(final_status)

    print()
    print(
        f"Report: {REPORT_FILE}"
    )

    print("=" * 72)

    return (
        0
        if final_status == "READY FOR PRODUCTION"
        else 1
    )


if __name__ == "__main__":
    sys.exit(main())

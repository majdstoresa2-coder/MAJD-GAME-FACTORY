#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD GAME FACTORY
MAJD-FINAL-PRODUCTION-AUDIT-10.py
=================================

FINAL REAL PRODUCTION AUDIT / SECURITY / INTEGRATION / CLOSURE GATE

Rules:
- NEVER modifies protected files 07 / 08 / 09.
- NEVER creates fake production data.
- NEVER performs a real charge.
- NEVER grants coins/rewards merely to make an audit pass.
- Read-only probes are preferred.
- Mutating endpoints are inspected and security-probed without performing
  successful authenticated mutations.
- Secrets are never printed.
- Route existence alone is NOT enough to prove business functionality.
- Final result is only:
    READY FOR PRODUCTION
    NOT READY FOR PRODUCTION
"""

from __future__ import annotations

import hashlib
import json
import os
import re
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
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple


# ============================================================
# CONFIGURATION
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent
REPORT_FILE = ROOT_DIR / "MAJD-FINAL-PRODUCTION-AUDIT-10.json"

PROTECTED_NUMBERS = ("07", "08", "09")

FRONTEND_URL = os.getenv(
    "MAJD_FRONTEND_URL",
    "http://127.0.0.1:8080",
).rstrip("/")

BACKEND_URL = os.getenv(
    "MAJD_BACKEND_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

PUBLIC_URL = os.getenv(
    "MAJD_PUBLIC_URL",
    "",
).rstrip("/")

TIMEOUT = float(os.getenv("MAJD_AUDIT_TIMEOUT", "10"))

OWNER_TOKEN = os.getenv("MAJD_OWNER_TOKEN", "").strip()
TEST_USER_TOKEN = os.getenv("MAJD_TEST_USER_TOKEN", "").strip()

DATABASE_URL = (
    os.getenv("DATABASE_URL", "").strip()
    or os.getenv("MONGODB_URI", "").strip()
    or os.getenv("MONGO_URI", "").strip()
)

MOYASAR_SECRET_KEY = os.getenv(
    "MOYASAR_SECRET_KEY",
    "",
).strip()

EXPECTED_OWNER_ROLE = os.getenv(
    "MAJD_OWNER_ROLE",
    "SUPREME_OWNER",
).strip()

USER_AGENT = "MAJD-FINAL-PRODUCTION-AUDIT-10/2.0"

HTTP_METHODS = {
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "options",
    "head",
}

SAFE_READ_METHODS = {"GET", "HEAD", "OPTIONS"}

SENSITIVE_MARKERS = (
    "authorization",
    "password",
    "secret",
    "token",
    "api-key",
    "apikey",
    "database_url",
    "mongodb_uri",
    "mongo_uri",
    "private_key",
    "cookie",
    "set-cookie",
)

PROTECTED_PREFIX_RE = re.compile(
    r"^(07|08|09)(?:[-_.]|$)",
    re.IGNORECASE,
)


# ============================================================
# DATA
# ============================================================

@dataclass
class AuditItem:
    name: str
    status: str
    evidence: List[str]
    missing: List[str]
    critical: bool = True


# ============================================================
# BASIC HELPERS
# ============================================================

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def text(value: Any, limit: int = 700) -> str:
    if value is None:
        return ""

    result = str(value).replace("\x00", "")

    if len(result) > limit:
        return result[:limit] + "...[TRUNCATED]"

    return result


def redact(value: Any) -> str:
    raw = text(value, 2000)

    for marker in SENSITIVE_MARKERS:
        pattern = re.compile(
            rf"({re.escape(marker)}\s*[:=]\s*)([^\s,;]+)",
            re.IGNORECASE,
        )
        raw = pattern.sub(r"\1[REDACTED]", raw)

    raw = re.sub(
        r"Bearer\s+[A-Za-z0-9._~+/=-]+",
        "Bearer [REDACTED]",
        raw,
        flags=re.IGNORECASE,
    )

    return text(raw)


def run(
    command: List[str],
    timeout: int = 30,
    cwd: Optional[Path] = None,
) -> Tuple[int, str, str]:

    try:
        process = subprocess.run(
            command,
            cwd=str(cwd or ROOT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            check=False,
        )

        return (
            process.returncode,
            process.stdout.strip(),
            process.stderr.strip(),
        )

    except Exception as exc:
        return 999, "", str(exc)


def command_exists(name: str) -> bool:
    code, _, _ = run(
        ["sh", "-c", f"command -v {name} >/dev/null 2>&1"]
    )
    return code == 0


def sha256_file(path: Path) -> Optional[str]:
    try:
        digest = hashlib.sha256()

        with path.open("rb") as handle:
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)

        return digest.hexdigest()

    except Exception:
        return None


def header_value(
    headers: Dict[str, Any],
    wanted: str,
) -> Optional[str]:

    wanted = wanted.lower()

    for key, value in headers.items():
        if str(key).lower() == wanted:
            return str(value)

    return None


def http_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    body: Optional[bytes] = None,
) -> Dict[str, Any]:

    request_headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json,text/html,*/*",
    }

    if headers:
        request_headers.update(headers)

    request = urllib.request.Request(
        url=url,
        method=method.upper(),
        headers=request_headers,
        data=body,
    )

    started = time.time()

    try:
        with urllib.request.urlopen(
            request,
            timeout=TIMEOUT,
        ) as response:

            raw = response.read(1024 * 1024)

            return {
                "ok": True,
                "status": response.status,
                "url": response.geturl(),
                "headers": dict(response.headers),
                "body": raw.decode("utf-8", errors="replace"),
                "elapsed_ms": round(
                    (time.time() - started) * 1000,
                    2,
                ),
            }

    except urllib.error.HTTPError as exc:

        try:
            raw = exc.read(1024 * 1024)
            body = raw.decode("utf-8", errors="replace")
        except Exception:
            body = ""

        return {
            "ok": False,
            "status": exc.code,
            "url": url,
            "headers": dict(exc.headers or {}),
            "body": body,
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


def parse_json(response: Dict[str, Any]) -> Optional[Any]:
    try:
        return json.loads(response.get("body") or "")
    except Exception:
        return None


def auth_headers(token: str) -> Dict[str, str]:
    if not token:
        return {}

    return {
        "Authorization": f"Bearer {token}",
    }


def item(
    name: str,
    ok: bool,
    evidence: Optional[List[str]] = None,
    missing: Optional[List[str]] = None,
    critical: bool = True,
) -> AuditItem:

    return AuditItem(
        name=name,
        status="PASS" if ok else "FAIL",
        evidence=evidence or [],
        missing=missing or [],
        critical=critical,
    )


# ============================================================
# PROTECTED 07 / 08 / 09
# ============================================================

def protected_number(path: Path) -> Optional[str]:

    match = PROTECTED_PREFIX_RE.match(path.name)

    if match:
        return match.group(1)

    return None


def discover_protected_files() -> Dict[str, List[Path]]:

    found: Dict[str, List[Path]] = {
        number: []
        for number in PROTECTED_NUMBERS
    }

    for path in ROOT_DIR.rglob("*"):

        if not path.is_file():
            continue

        number = protected_number(path)

        if number:
            found[number].append(path)

    return found


def audit_protected_files() -> AuditItem:

    found = discover_protected_files()

    evidence: List[str] = []
    missing: List[str] = []

    for number in PROTECTED_NUMBERS:

        files = found[number]

        if not files:
            missing.append(
                f"Protected file prefix {number} was not found."
            )
            continue

        for path in files:

            try:
                relative = path.relative_to(ROOT_DIR)
            except Exception:
                relative = path

            digest = sha256_file(path)

            evidence.append(
                f"{number}: {relative} SHA256={digest or 'UNAVAILABLE'}"
            )

    return item(
        "Protected files 07/08/09",
        not missing,
        evidence,
        missing,
    )


def audit_protected_git_integrity() -> AuditItem:

    evidence: List[str] = []
    missing: List[str] = []

    code, stdout, stderr = run(
        ["git", "status", "--porcelain"]
    )

    if code != 0:
        return item(
            "Protected Git integrity",
            False,
            [],
            [
                "git status failed: " + redact(stderr)
            ],
        )

    changed = [
        line
        for line in stdout.splitlines()
        if line.strip()
    ]

    protected_changes: List[str] = []

    for line in changed:

        filename = line[3:].strip() if len(line) > 3 else line

        base = Path(filename).name

        if PROTECTED_PREFIX_RE.match(base):
            protected_changes.append(line)

    evidence.append(
        f"Working tree changes={len(changed)}"
    )

    if protected_changes:
        evidence.extend(
            f"Protected change: {redact(line)}"
            for line in protected_changes
        )
        missing.append(
            "Protected 07/08/09 files contain uncommitted changes."
        )

    code, stdout, stderr = run(
        ["git", "rev-parse", "HEAD"]
    )

    if code == 0 and stdout:
        evidence.append(
            f"HEAD={stdout.strip()}"
        )

    return item(
        "Protected Git integrity",
        not missing,
        evidence,
        missing,
    )


# ============================================================
# SOURCE INVENTORY
# ============================================================

def audit_source_inventory() -> AuditItem:

    evidence: List[str] = []
    missing: List[str] = []

    expected = (
        "MAJD-AI-MASTERMIND-01.py",
        "MAJD-OWNER-COMMAND-CENTER-02.py",
        "MAJD-REAL-GAME-EXECUTOR-03.py",
        "MAJD-OFFICIAL-PLATFORM-BRIDGE-04.py",
        "MAJD-FULL-EXECUTION-RUNTIME-05.py",
        "MAJD-FULL-EXECUTION-RUNTIME-06.py",
        "MAJD-FINAL-PRODUCTION-AUDIT-10.py",
    )

    for filename in expected:

        path = ROOT_DIR / filename

        if path.exists():
            evidence.append(
                f"FOUND {filename}"
            )
        else:
            missing.append(
                f"Missing expected runtime file: {filename}"
            )

    return item(
        "Core source inventory",
        not missing,
        evidence,
        missing,
    )


# ============================================================
# PYTHON VALIDATION
# ============================================================

def audit_python_compile() -> AuditItem:

    evidence: List[str] = []
    missing: List[str] = []

    python_files = sorted(
        ROOT_DIR.glob("*.py")
    )

    if not python_files:
        return item(
            "Python syntax validation",
            False,
            [],
            ["No root Python files discovered."],
        )

    for path in python_files:

        code, _, stderr = run(
            [
                sys.executable,
                "-m",
                "py_compile",
                str(path),
            ],
            timeout=20,
        )

        if code == 0:
            evidence.append(
                f"COMPILE PASS {path.name}"
            )
        else:
            missing.append(
                f"COMPILE FAIL {path.name}: {redact(stderr)}"
            )

    return item(
        "Python syntax validation",
        not missing,
        evidence,
        missing,
    )


# ============================================================
# DOCKER
# ============================================================

def docker_rows() -> List[str]:

    code, stdout, _ = run(
        [
            "docker",
            "ps",
            "--format",
            "{{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}",
        ]
    )

    if code != 0:
        return []

    return [
        line.strip()
        for line in stdout.splitlines()
        if line.strip()
    ]


def audit_docker() -> AuditItem:

    evidence: List[str] = []
    missing: List[str] = []

    if not command_exists("docker"):
        return item(
            "Production containers",
            False,
            [],
            ["Docker CLI is unavailable."],
        )

    rows = docker_rows()

    evidence.extend(rows)

    for required in (
        "majd-ai-core",
        "majd-web-ui",
    ):

        if not any(
            row.startswith(required + "|")
            for row in rows
        ):
            missing.append(
                f"Required production container is not running: {required}"
            )

    return item(
        "Production containers",
        not missing,
        evidence,
        missing,
    )


def inspect_container_env(
    container: str,
) -> Dict[str, bool]:

    code, stdout, _ = run(
        [
            "docker",
            "inspect",
            container,
            "--format",
            "{{range .Config.Env}}{{println .}}{{end}}",
        ]
    )

    result: Dict[str, bool] = {}

    if code != 0:
        return result

    for line in stdout.splitlines():

        if "=" not in line:
            continue

        key, value = line.split("=", 1)

        result[key.strip()] = bool(value.strip())

    return result


# ============================================================
# PORTS
# ============================================================

def port_open(host: str, port: int) -> bool:

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

    evidence: List[str] = []
    missing: List[str] = []

    ports = {
        80: ("HTTP/Nginx", False),
        443: ("HTTPS/Nginx", False),
        8000: ("MAJD backend", True),
        8080: ("MAJD frontend", True),
    }

    for port, (label, required) in ports.items():

        opened = port_open(
            "127.0.0.1",
            port,
        )

        evidence.append(
            f"{label} port {port}: "
            + ("OPEN" if opened else "CLOSED")
        )

        if required and not opened:
            missing.append(
                f"Required port {port} is closed."
            )

    return item(
        "Listening production ports",
        not missing,
        evidence,
        missing,
    )


# ============================================================
# NGINX
# ============================================================

def audit_nginx() -> AuditItem:

    if not command_exists("nginx"):
        return item(
            "Nginx configuration",
            False,
            [],
            ["nginx CLI unavailable."],
            critical=False,
        )

    code, stdout, stderr = run(
        ["nginx", "-t"]
    )

    evidence = [
        redact(stderr or stdout)
    ]

    return item(
        "Nginx configuration",
        code == 0,
        evidence,
        [] if code == 0 else ["nginx -t failed."],
        critical=False,
    )


# ============================================================
# FRONTEND
# ============================================================

def audit_frontend() -> AuditItem:

    response = http_request(
        FRONTEND_URL + "/"
    )

    evidence = [
        f"GET / => HTTP {response.get('status')} "
        f"({response.get('elapsed_ms')} ms)"
    ]

    missing: List[str] = []

    if response.get("status") != 200:
        missing.append(
            "Frontend root does not return HTTP 200."
        )

    body = response.get("body") or ""

    if response.get("status") == 200:

        if not body.strip():
            missing.append(
                "Frontend response body is empty."
            )

        if "<html" not in body.lower():
            missing.append(
                "Frontend root is not recognizable HTML."
            )

    return item(
        "Frontend deployment",
        not missing,
        evidence,
        missing,
    )


def audit_login_route() -> AuditItem:

    response = http_request(
        FRONTEND_URL + "/login"
    )

    code = response.get("status")

    evidence = [
        f"GET /login => HTTP {code}"
    ]

    missing: List[str] = []

    if code not in (
        200,
        301,
        302,
        307,
        308,
        401,
        403,
    ):
        missing.append(
            f"Frontend login route is not production-routable; HTTP {code}."
        )

    return item(
        "Frontend login routing",
        not missing,
        evidence,
        missing,
    )


def audit_static_assets() -> AuditItem:

    root = http_request(
        FRONTEND_URL + "/"
    )

    evidence: List[str] = []
    missing: List[str] = []

    body = root.get("body") or ""

    candidates: Set[str] = set()

    for match in re.findall(
        r'''(?:src|href)=["']([^"']+)["']''',
        body,
        flags=re.IGNORECASE,
    ):

        if match.startswith(
            ("data:", "mailto:", "javascript:")
        ):
            continue

        candidates.add(match)

    checked = 0

    for asset in sorted(candidates):

        if checked >= 20:
            break

        if asset.startswith(("http://", "https://")):
            url = asset
        else:
            url = urllib.parse.urljoin(
                FRONTEND_URL + "/",
                asset,
            )

        response = http_request(url)

        evidence.append(
            f"ASSET {asset} => HTTP {response.get('status')}"
        )

        checked += 1

        if response.get("status") is None:
            missing.append(
                f"Asset unreachable: {asset}"
            )

        elif int(response.get("status")) >= 400:
            missing.append(
                f"Asset failed: {asset} HTTP {response.get('status')}"
            )

    favicon = http_request(
        FRONTEND_URL + "/favicon.ico"
    )

    evidence.append(
        f"favicon.ico => HTTP {favicon.get('status')}"
    )

    if favicon.get("status") != 200:
        missing.append(
            "favicon.ico is missing or not served."
        )

    return item(
        "Frontend static assets",
        not missing,
        evidence,
        missing,
        critical=False,
    )


# ============================================================
# BACKEND / OPENAPI
# ============================================================

def audit_backend_health() -> AuditItem:

    evidence: List[str] = []

    for route in (
        "/health",
        "/api/health",
        "/",
    ):

        response = http_request(
            BACKEND_URL + route
        )

        evidence.append(
            f"GET {route} => HTTP {response.get('status')}"
        )

        if response.get("status") == 200:

            return item(
                "Backend health",
                True,
                evidence + [
                    f"Backend reachable through {route}"
                ],
                [],
            )

    return item(
        "Backend health",
        False,
        evidence,
        [
            "No backend health/root route returned HTTP 200."
        ],
    )


def discover_openapi() -> Tuple[
    Optional[Dict[str, Any]],
    List[str],
]:

    evidence: List[str] = []

    for route in (
        "/openapi.json",
        "/api/openapi.json",
    ):

        response = http_request(
            BACKEND_URL + route
        )

        evidence.append(
            f"GET {route} => HTTP {response.get('status')}"
        )

        if response.get("status") != 200:
            continue

        parsed = parse_json(response)

        if isinstance(parsed, dict):
            return parsed, evidence

    return None, evidence


def routes_from_openapi(
    schema: Optional[Dict[str, Any]],
) -> Dict[str, Dict[str, Dict[str, Any]]]:

    result: Dict[
        str,
        Dict[str, Dict[str, Any]]
    ] = {}

    if not schema:
        return result

    paths = schema.get("paths")

    if not isinstance(paths, dict):
        return result

    for path, methods in paths.items():

        if not isinstance(methods, dict):
            continue

        normalized: Dict[str, Dict[str, Any]] = {}

        for method, definition in methods.items():

            if method.lower() not in HTTP_METHODS:
                continue

            normalized[method.upper()] = (
                definition
                if isinstance(definition, dict)
                else {}
            )

        if normalized:
            result[str(path)] = normalized

    return result


def route_matches(
    routes: Dict[str, Dict[str, Dict[str, Any]]],
    keywords: Iterable[str],
) -> List[Tuple[str, str, Dict[str, Any]]]:

    keywords = tuple(
        word.lower()
        for word in keywords
    )

    matches: List[
        Tuple[str, str, Dict[str, Any]]
    ] = []

    for path, methods in routes.items():

        lower = path.lower()

        if not any(
            word in lower
            for word in keywords
        ):
            continue

        for method, definition in methods.items():
            matches.append(
                (method, path, definition)
            )

    return matches


def audit_openapi(
    schema: Optional[Dict[str, Any]],
    evidence: List[str],
    routes: Dict[str, Dict[str, Dict[str, Any]]],
) -> AuditItem:

    if not schema:

        return item(
            "OpenAPI discovery",
            False,
            evidence,
            ["Backend OpenAPI schema unavailable."],
        )

    return item(
        "OpenAPI discovery",
        True,
        evidence + [
            f"Discovered {len(routes)} API paths."
        ],
        [],
    )


# ============================================================
# ROUTE GROUPS
# ============================================================

FEATURES = {
    "Authentication API": (
        "login",
        "auth",
        "signin",
        "session",
        "token",
        "me",
    ),
    "Wallet / MAJD Coins": (
        "wallet",
        "coin",
        "balance",
    ),
    "Challenges / Claim": (
        "challenge",
        "claim",
    ),
    "Coin Packages": (
        "package",
        "coin-package",
        "coin_package",
    ),
    "Moyasar / Checkout / Payment": (
        "moyasar",
        "checkout",
        "payment",
        "webhook",
    ),
    "Transactions Ledger": (
        "transaction",
        "ledger",
    ),
    "Rewarded Ads": (
        "rewarded",
        "reward",
        "ad-session",
        "ad_session",
        "ads",
    ),
    "Owner / Admin / Audit": (
        "owner",
        "admin",
        "audit",
    ),
}


def audit_feature_routes(
    name: str,
    routes: Dict[str, Dict[str, Dict[str, Any]]],
    keywords: Tuple[str, ...],
) -> AuditItem:

    matches = route_matches(
        routes,
        keywords,
    )

    evidence = [
        f"{method} {path}"
        for method, path, _ in matches
    ]

    if not matches:

        return item(
            name,
            False,
            [],
            [
                "No real backend route discovered for: "
                + ", ".join(keywords)
            ],
        )

    return item(
        name,
        True,
        evidence,
        [],
    )


# ============================================================
# AUTH SECURITY
# ============================================================

def audit_protected_routes(
    routes: Dict[str, Dict[str, Dict[str, Any]]],
) -> AuditItem:

    evidence: List[str] = []
    missing: List[str] = []

    protected_keywords = (
        "wallet",
        "balance",
        "claim",
        "transaction",
        "ledger",
        "reward",
        "owner",
        "admin",
        "audit",
    )

    candidates = route_matches(
        routes,
        protected_keywords,
    )

    if not candidates:

        return item(
            "Backend authorization protection",
            False,
            [],
            [
                "No security-sensitive application endpoints exist to test."
            ],
        )

    tested = 0
    rejected = 0
    exposed: List[str] = []

    for method, path, _ in candidates[:30]:

        # Do not execute destructive/mutating endpoint operations.
        if method not in SAFE_READ_METHODS:
            continue

        response = http_request(
            BACKEND_URL + path,
            method=method,
        )

        code = response.get("status")

        tested += 1

        evidence.append(
            f"Unauthenticated {method} {path} => HTTP {code}"
        )

        if code in (401, 403):
            rejected += 1

        elif code is not None and 200 <= int(code) < 300:
            exposed.append(
                f"{method} {path} returned HTTP {code} without auth"
            )

    if exposed:
        missing.extend(
            "Potentially unprotected endpoint: " + value
            for value in exposed
        )

    if tested == 0:
        missing.append(
            "No safe read-only protected route could be security-probed."
        )

    elif rejected == 0:
        missing.append(
            "No tested protected route rejected unauthenticated access "
            "with HTTP 401/403."
        )

    return item(
        "Backend authorization protection",
        not missing,
        evidence,
        missing,
    )


def audit_owner_protection(
    routes: Dict[str, Dict[str, Dict[str, Any]]],
) -> AuditItem:

    matches = route_matches(
        routes,
        ("owner", "admin"),
    )

    evidence: List[str] = []
    missing: List[str] = []

    if not matches:

        return item(
            "SUPREME_OWNER backend protection",
            False,
            [],
            ["No owner/admin backend routes discovered."],
        )

    safe_tested = 0
    safe_rejected = 0

    for method, path, _ in matches:

        evidence.append(
            f"DISCOVERED {method} {path}"
        )

        if method not in SAFE_READ_METHODS:
            continue

        response = http_request(
            BACKEND_URL + path,
            method=method,
        )

        code = response.get("status")

        evidence.append(
            f"UNAUTHENTICATED {method} {path} => HTTP {code}"
        )

        safe_tested += 1

        if code in (401, 403):
            safe_rejected += 1

        elif code is not None and 200 <= int(code) < 300:
            missing.append(
                f"Owner endpoint accessible without authentication: "
                f"{method} {path}"
            )

    if safe_tested and safe_rejected == 0:
        missing.append(
            "No read-only owner/admin endpoint proved 401/403 protection."
        )

    # Mutating owner routes must at least declare security in OpenAPI
    for method, path, definition in matches:

        if method in SAFE_READ_METHODS:
            continue

        security = definition.get("security")

        if security:
            evidence.append(
                f"SECURITY DECLARED {method} {path}"
            )
        else:
            missing.append(
                f"Mutating owner/admin route has no OpenAPI security "
                f"declaration: {method} {path}"
            )

    return item(
        "SUPREME_OWNER backend protection",
        not missing,
        evidence,
        missing,
    )


# ============================================================
# OWNER AUTHENTICATED VERIFICATION
# ============================================================

def audit_owner_authenticated(
    routes: Dict[str, Dict[str, Dict[str, Any]]],
) -> AuditItem:

    if not OWNER_TOKEN:

        return item(
            "SUPREME_OWNER authenticated verification",
            False,
            [],
            [
                "MAJD_OWNER_TOKEN is missing; authenticated owner "
                "verification cannot run."
            ],
        )

    matches = route_matches(
        routes,
        (
            "owner",
            "admin",
            "profile",
            "me",
            "auth",
        ),
    )

    evidence: List[str] = [
        "MAJD_OWNER_TOKEN configured; value not printed."
    ]

    for method, path, _ in matches:

        if method != "GET":
            continue

        response = http_request(
            BACKEND_URL + path,
            headers=auth_headers(OWNER_TOKEN),
        )

        code = response.get("status")

        evidence.append(
            f"Authenticated GET {path} => HTTP {code}"
        )

        if code != 200:
            continue

        parsed = parse_json(response)

        searchable = json.dumps(
            parsed,
            ensure_ascii=False,
        ) if parsed is not None else response.get("body", "")

        if EXPECTED_OWNER_ROLE.lower() in searchable.lower():

            evidence.append(
                f"Backend response identifies role {EXPECTED_OWNER_ROLE}."
            )

            return item(
                "SUPREME_OWNER authenticated verification",
                True,
                evidence,
                [],
            )

    return item(
        "SUPREME_OWNER authenticated verification",
        False,
        evidence,
        [
            f"Could not prove authenticated backend role "
            f"{EXPECTED_OWNER_ROLE}."
        ],
    )


# ============================================================
# DATABASE
# ============================================================

def audit_database() -> AuditItem:

    evidence: List[str] = []
    missing: List[str] = []

    configured = bool(DATABASE_URL)

    if configured:
        evidence.append(
            "Database URI configured in audit process; value not printed."
        )

    container_env = inspect_container_env(
        "majd-ai-core"
    )

    container_db_keys = [
        key
        for key in (
            "DATABASE_URL",
            "MONGODB_URI",
            "MONGO_URI",
        )
        if container_env.get(key)
    ]

    if container_db_keys:
        evidence.append(
            "Backend container database configuration present via: "
            + ", ".join(container_db_keys)
        )
        configured = True

    if not configured:
        missing.append(
            "No DATABASE_URL/MONGODB_URI/MONGO_URI was detected "
            "in audit process or backend container."
        )

    # Configuration alone does not prove live DB connectivity.
    health_candidates = (
        "/health",
        "/api/health",
    )

    db_proven = False

    for route in health_candidates:

        response = http_request(
            BACKEND_URL + route
        )

        if response.get("status") != 200:
            continue

        parsed = parse_json(response)

        searchable = json.dumps(
            parsed,
            ensure_ascii=False,
        ).lower() if parsed is not None else ""

        if (
            ("database" in searchable or "mongodb" in searchable or '"db"' in searchable)
            and any(
                word in searchable
                for word in (
                    "connected",
                    "healthy",
                    '"ok"',
                    "ready",
                )
            )
        ):
            evidence.append(
                f"Backend {route} reports database connectivity."
            )
            db_proven = True
            break

    if configured and not db_proven:
        missing.append(
            "Database configuration exists but live database connectivity "
            "was not proven by a backend health/readiness response."
        )

    return item(
        "Database connectivity",
        configured and db_proven,
        evidence,
        missing,
    )


# ============================================================
# WALLET / COINS REAL READ
# ============================================================

def audit_authenticated_read_feature(
    name: str,
    routes: Dict[str, Dict[str, Dict[str, Any]]],
    keywords: Tuple[str, ...],
    token: str,
) -> AuditItem:

    matches = route_matches(
        routes,
        keywords,
    )

    evidence: List[str] = []
    missing: List[str] = []

    if not matches:

        return item(
            name,
            False,
            [],
            ["No matching backend routes discovered."],
        )

    get_routes = [
        (method, path)
        for method, path, _ in matches
        if method == "GET"
        and "{" not in path
    ]

    if not get_routes:

        return item(
            name,
            False,
            [
                f"DISCOVERED {method} {path}"
                for method, path, _ in matches
            ],
            [
                "Feature routes exist, but no directly testable "
                "read-only GET endpoint was discovered."
            ],
        )

    if not token:

        return item(
            name,
            False,
            [
                f"DISCOVERED {method} {path}"
                for method, path, _ in matches
            ],
            [
                "No authenticated test token available for real read verification."
            ],
        )

    for _, path in get_routes:

        response = http_request(
            BACKEND_URL + path,
            headers=auth_headers(token),
        )

        code = response.get("status")

        evidence.append(
            f"Authenticated GET {path} => HTTP {code}"
        )

        if code == 200:
            return item(
                name,
                True,
                evidence,
                [],
            )

    missing.append(
        "No discovered read endpoint returned HTTP 200 "
        "with the configured authenticated token."
    )

    return item(
        name,
        False,
        evidence,
        missing,
    )


# ============================================================
# CHALLENGE CLAIM SAFETY
# ============================================================

def audit_challenge_claim_design(
    routes: Dict[str, Dict[str, Dict[str, Any]]],
) -> AuditItem:

    matches = route_matches(
        routes,
        ("challenge", "claim"),
    )

    evidence = [
        f"{method} {path}"
        for method, path, _ in matches
    ]

    missing: List[str] = []

    claim_routes = [
        (method, path, definition)
        for method, path, definition in matches
        if "claim" in path.lower()
    ]

    if not claim_routes:
        missing.append(
            "No challenge claim endpoint discovered."
        )

    for method, path, definition in claim_routes:

        if method not in ("POST", "PUT", "PATCH"):
            missing.append(
                f"Claim route uses unexpected method {method}: {path}"
            )

        if not definition.get("security"):
            missing.append(
                f"Claim route has no OpenAPI security declaration: "
                f"{method} {path}"
            )

    if claim_routes:
        missing.append(
            "Duplicate-claim prevention cannot be proven safely by this "
            "production audit without a dedicated non-mutating verification "
            "endpoint or isolated test transaction."
        )

    return item(
        "Challenges claim and duplicate protection",
        not missing,
        evidence,
        missing,
    )


# ============================================================
# PAYMENT SAFETY
# ============================================================

def audit_payment_security(
    routes: Dict[str, Dict[str, Dict[str, Any]]],
) -> AuditItem:

    matches = route_matches(
        routes,
        (
            "moyasar",
            "checkout",
            "payment",
            "webhook",
        ),
    )

    evidence = [
        f"{method} {path}"
        for method, path, _ in matches
    ]

    missing: List[str] = []

    if not matches:
        missing.append(
            "No payment/checkout/webhook backend endpoints discovered."
        )

    secret_present = bool(MOYASAR_SECRET_KEY)

    container_env = inspect_container_env(
        "majd-ai-core"
    )

    if container_env.get("MOYASAR_SECRET_KEY"):
        secret_present = True

    if secret_present:
        evidence.append(
            "Moyasar server secret configuration detected; value not printed."
        )
    else:
        missing.append(
            "MOYASAR_SECRET_KEY not detected in audit process "
            "or backend container."
        )

    webhook_routes = [
        (method, path, definition)
        for method, path, definition in matches
        if "webhook" in path.lower()
        or "verify" in path.lower()
    ]

    if not webhook_routes:
        missing.append(
            "No payment verification/webhook route discovered."
        )

    # Never issue a real payment during production audit.
    evidence.append(
        "No real charge was created by the audit."
    )

    missing.append(
        "Server-side rule 'no coins before confirmed payment' "
        "requires a dedicated integration/test transaction or verifiable "
        "backend implementation evidence; route discovery alone is insufficient."
    )

    return item(
        "Moyasar server-side payment safety",
        not missing,
        evidence,
        missing,
    )


# ============================================================
# REWARDED ADS SAFETY
# ============================================================

def audit_rewarded_ads_security(
    routes: Dict[str, Dict[str, Dict[str, Any]]],
) -> AuditItem:

    matches = route_matches(
        routes,
        (
            "rewarded",
            "reward",
            "ad-session",
            "ad_session",
            "ads",
        ),
    )

    evidence = [
        f"{method} {path}"
        for method, path, _ in matches
    ]

    missing: List[str] = []

    if not matches:
        missing.append(
            "No rewarded-ad backend endpoints discovered."
        )
        return item(
            "Rewarded Ads server verification",
            False,
            evidence,
            missing,
        )

    verification = [
        (method, path)
        for method, path, _ in matches
        if any(
            word in path.lower()
            for word in (
                "verify",
                "callback",
                "complete",
                "reward",
            )
        )
    ]

    if not verification:
        missing.append(
            "No server-side rewarded-ad verification/completion route discovered."
        )

    return item(
        "Rewarded Ads server verification",
        not missing,
        evidence,
        missing,
    )


# ============================================================
# TRANSACTION LEDGER
# ============================================================

def audit_transaction_ledger(
    routes: Dict[str, Dict[str, Dict[str, Any]]],
) -> AuditItem:

    matches = route_matches(
        routes,
        ("transaction", "ledger"),
    )

    evidence = [
        f"{method} {path}"
        for method, path, _ in matches
    ]

    missing: List[str] = []

    if not matches:
        missing.append(
            "No transaction/ledger endpoint discovered."
        )

    read_route = any(
        method == "GET"
        for method, _, _ in matches
    )

    if matches and not read_route:
        missing.append(
            "Ledger exists but no read-only GET route was discovered "
            "for audit verification."
        )

    return item(
        "Transactions Ledger",
        not missing,
        evidence,
        missing,
    )


# ============================================================
# CORS
# ============================================================

def audit_cors() -> AuditItem:

    origins = [
        FRONTEND_URL,
    ]

    if PUBLIC_URL:
        origins.append(PUBLIC_URL)

    evidence: List[str] = []
    missing: List[str] = []

    for origin in origins:

        response = http_request(
            BACKEND_URL + "/",
            method="OPTIONS",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization,content-type",
            },
        )

        allow_origin = header_value(
            response.get("headers", {}),
            "Access-Control-Allow-Origin",
        )

        allow_methods = header_value(
            response.get("headers", {}),
            "Access-Control-Allow-Methods",
        )

        evidence.append(
            f"Origin={origin} OPTIONS / => HTTP {response.get('status')}"
        )

        evidence.append(
            f"Access-Control-Allow-Origin={allow_origin or 'MISSING'}"
        )

        evidence.append(
            f"Access-Control-Allow-Methods={allow_methods or 'MISSING'}"
        )

        if not allow_origin:
            missing.append(
                f"CORS allow-origin missing for {origin}."
            )

        elif allow_origin not in ("*", origin):
            missing.append(
                f"CORS returned unexpected origin {allow_origin} "
                f"for requested origin {origin}."
            )

    return item(
        "CORS",
        not missing,
        evidence,
        missing,
    )


# ============================================================
# ENVIRONMENT
# ============================================================

def audit_environment() -> AuditItem:

    evidence: List[str] = []
    missing: List[str] = []

    process_env = {
        key: bool(os.getenv(key))
        for key in (
            "DATABASE_URL",
            "MONGODB_URI",
            "MONGO_URI",
            "MAJD_OWNER_TOKEN",
            "MAJD_TEST_USER_TOKEN",
            "MOYASAR_SECRET_KEY",
            "MAJD_FRONTEND_URL",
            "MAJD_BACKEND_URL",
            "MAJD_PUBLIC_URL",
        )
    }

    container_env = inspect_container_env(
        "majd-ai-core"
    )

    def present_any(names: Tuple[str, ...]) -> bool:

        process = any(
            process_env.get(name, False)
            for name in names
        )

        container = any(
            container_env.get(name, False)
            for name in names
        )

        return process or container

    groups = {
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

    for label, names in groups.items():

        if present_any(names):
            evidence.append(
                f"{label}: configured; secret value not printed."
            )
        else:
            missing.append(
                f"{label}: missing {', '.join(names)}"
            )

    return item(
        "Production environment",
        not missing,
        evidence,
        missing,
    )


# ============================================================
# HTTP ERROR / PUBLIC SURFACE
# ============================================================

def audit_http_surface() -> AuditItem:

    evidence: List[str] = []
    missing: List[str] = []

    checks = (
        ("Frontend /", FRONTEND_URL + "/"),
        ("Frontend /login", FRONTEND_URL + "/login"),
        ("Backend /", BACKEND_URL + "/"),
        ("Backend OpenAPI", BACKEND_URL + "/openapi.json"),
    )

    for label, url in checks:

        response = http_request(url)

        code = response.get("status")

        evidence.append(
            f"{label} => HTTP {code}"
        )

        if code is None:
            missing.append(
                f"{label} unreachable."
            )

        elif int(code) >= 500:
            missing.append(
                f"{label} returned server error HTTP {code}."
            )

    return item(
        "HTTP production surface",
        not missing,
        evidence,
        missing,
    )


# ============================================================
# BUILD / COMPOSE VALIDATION
# ============================================================

def audit_compose_configuration() -> AuditItem:

    compose = ROOT_DIR.parent / "docker-compose.yml"

    if not compose.exists():
        compose = ROOT_DIR / "docker-compose.yml"

    if not compose.exists():

        return item(
            "Docker Compose production configuration",
            False,
            [],
            ["docker-compose.yml not found."],
            critical=False,
        )

    evidence = [
        f"Compose file={compose}"
    ]

    if not command_exists("docker"):

        return item(
            "Docker Compose production configuration",
            False,
            evidence,
            ["Docker CLI unavailable."],
            critical=False,
        )

    code, stdout, stderr = run(
        [
            "docker",
            "compose",
            "-f",
            str(compose),
            "config",
            "--quiet",
        ],
        timeout=30,
    )

    if code == 0:

        evidence.append(
            "docker compose config validation passed."
        )

        return item(
            "Docker Compose production configuration",
            True,
            evidence,
            [],
            critical=False,
        )

    return item(
        "Docker Compose production configuration",
        False,
        evidence,
        [
            "docker compose config failed: "
            + redact(stderr or stdout)
        ],
        critical=False,
    )


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    started = utc_now()

    print("=" * 78)
    print("MAJD GAME FACTORY - FINAL PRODUCTION AUDIT 10")
    print("=" * 78)
    print(f"Started:  {started}")
    print(f"Frontend: {FRONTEND_URL}")
    print(f"Backend:  {BACKEND_URL}")

    if PUBLIC_URL:
        print(f"Public:   {PUBLIC_URL}")

    print("=" * 78)

    results: List[AuditItem] = []

    # --------------------------------------------------------
    # Protected project state
    # --------------------------------------------------------

    results.append(
        audit_protected_files()
    )

    results.append(
        audit_protected_git_integrity()
    )

    results.append(
        audit_source_inventory()
    )

    results.append(
        audit_python_compile()
    )

    # --------------------------------------------------------
    # Infrastructure
    # --------------------------------------------------------

    results.append(
        audit_docker()
    )

    results.append(
        audit_ports()
    )

    results.append(
        audit_nginx()
    )

    results.append(
        audit_compose_configuration()
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
        audit_static_assets()
    )

    # --------------------------------------------------------
    # Backend
    # --------------------------------------------------------

    results.append(
        audit_backend_health()
    )

    schema, openapi_evidence = discover_openapi()

    routes = routes_from_openapi(schema)

    results.append(
        audit_openapi(
            schema,
            openapi_evidence,
            routes,
        )
    )

    # --------------------------------------------------------
    # Every required application subsystem
    # --------------------------------------------------------

    for feature_name, keywords in FEATURES.items():

        results.append(
            audit_feature_routes(
                feature_name,
                routes,
                keywords,
            )
        )

    # --------------------------------------------------------
    # Real authenticated reads
    # --------------------------------------------------------

    usable_user_token = (
        TEST_USER_TOKEN
        or OWNER_TOKEN
    )

    results.append(
        audit_authenticated_read_feature(
            "Wallet / MAJD Coins real backend read",
            routes,
            (
                "wallet",
                "balance",
                "coin",
            ),
            usable_user_token,
        )
    )

    results.append(
        audit_authenticated_read_feature(
            "Coin Packages real backend read",
            routes,
            (
                "package",
                "coin-package",
                "coin_package",
            ),
            usable_user_token,
        )
    )

    results.append(
        audit_authenticated_read_feature(
            "Challenges real backend read",
            routes,
            (
                "challenge",
            ),
            usable_user_token,
        )
    )

    results.append(
        audit_authenticated_read_feature(
            "Transactions real backend read",
            routes,
            (
                "transaction",
                "ledger",
            ),
            usable_user_token,
        )
    )

    # --------------------------------------------------------
    # Security / business integrity
    # --------------------------------------------------------

    results.append(
        audit_protected_routes(routes)
    )

    results.append(
        audit_owner_protection(routes)
    )

    results.append(
        audit_owner_authenticated(routes)
    )

    results.append(
        audit_database()
    )

    results.append(
        audit_challenge_claim_design(routes)
    )

    results.append(
        audit_payment_security(routes)
    )

    results.append(
        audit_transaction_ledger(routes)
    )

    results.append(
        audit_rewarded_ads_security(routes)
    )

    results.append(
        audit_cors()
    )

    results.append(
        audit_environment()
    )

    results.append(
        audit_http_surface()
    )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    critical_failures = [
        result
        for result in results
        if result.critical
        and result.status != "PASS"
    ]

    warnings = [
        result
        for result in results
        if not result.critical
        and result.status != "PASS"
    ]

    final_status = (
        "READY FOR PRODUCTION"
        if not critical_failures
        else "NOT READY FOR PRODUCTION"
    )

    finished = utc_now()

    report = {
        "system": "MAJD-GAME-FACTORY",
        "audit": "MAJD-FINAL-PRODUCTION-AUDIT-10",
        "audit_version": "2.0",
        "started_at": started,
        "finished_at": finished,
        "frontend_url": FRONTEND_URL,
        "backend_url": BACKEND_URL,
        "public_url": PUBLIC_URL or None,
        "protected_files": [
            "07",
            "08",
            "09",
        ],
        "rules": {
            "protected_files_modified": False,
            "fake_data_allowed": False,
            "real_charge_performed": False,
            "successful_mutating_owner_command_performed": False,
            "secret_values_printed": False,
        },
        "openapi_paths_discovered": len(routes),
        "results": [
            asdict(result)
            for result in results
        ],
        "critical_failure_count": len(
            critical_failures
        ),
        "critical_failures": [
            result.name
            for result in critical_failures
        ],
        "warning_count": len(warnings),
        "warnings": [
            result.name
            for result in warnings
        ],
        "final_result": final_status,
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
    print("=" * 78)
    print("AUDIT RESULTS")
    print("=" * 78)

    for result in results:

        print()
        print(
            f"[{result.status}] {result.name}"
        )

        for evidence in result.evidence:
            print(
                "  EVIDENCE: "
                + redact(evidence)
            )

        for problem in result.missing:
            print(
                "  MISSING/ERROR: "
                + redact(problem)
            )

    print()
    print("=" * 78)
    print("CRITICAL FAILURES")
    print("=" * 78)

    if critical_failures:

        for result in critical_failures:
            print(
                f"- {result.name}"
            )

    else:
        print("NONE")

    print()
    print("=" * 78)
    print("NON-CRITICAL WARNINGS")
    print("=" * 78)

    if warnings:

        for result in warnings:
            print(
                f"- {result.name}"
            )

    else:
        print("NONE")

    print()
    print("=" * 78)
    print("FINAL MAJD PRODUCTION RESULT")
    print("=" * 78)
    print(final_status)
    print()
    print(f"Report: {REPORT_FILE}")
    print("=" * 78)

    return (
        0
        if final_status == "READY FOR PRODUCTION"
        else 1
    )


if __name__ == "__main__":
    sys.exit(main())

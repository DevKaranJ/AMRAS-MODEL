#!/usr/bin/env python3
"""
AMRAS Interactive Setup & Launch Script
========================================
Cross-platform (Linux / macOS / Windows) script that:
  1. Checks prerequisites (Python, Poetry, FFmpeg, Tesseract)
  2. Installs project dependencies via Poetry
  3. Prompts for every required configuration value
  4. Writes the values to a .env file
  5. Runs database migrations
  6. Optionally runs the test suite
  7. Starts the AMRAS API server

Run from the project root:
    python setup.py

The script is idempotent — safe to run multiple times.
Existing .env values are preserved unless you explicitly overwrite them.
"""

from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Optional

# ──────────────────────────────────────────────────────────────────────────────
# Colours (disabled automatically on Windows when ANSI is unavailable)
# ──────────────────────────────────────────────────────────────────────────────
_USE_COLOUR = sys.stdout.isatty() and platform.system() != "Windows"


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _USE_COLOUR else text


def green(t: str) -> str:   return _c("32", t)
def yellow(t: str) -> str:  return _c("33", t)
def red(t: str) -> str:     return _c("31", t)
def bold(t: str) -> str:    return _c("1",  t)
def cyan(t: str) -> str:    return _c("36", t)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.resolve()
ENV_FILE = ROOT / ".env"
ENV_EXAMPLE = ROOT / ".env.example"


def _run(cmd: list[str], check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:  # type: ignore[type-arg]
    """Run a subprocess, streaming output unless capture=True."""
    return subprocess.run(
        cmd,
        check=check,
        capture_output=capture,
        text=True,
        cwd=ROOT,
    )


def _heading(text: str) -> None:
    width = 72
    print()
    print(cyan("─" * width))
    print(cyan(f"  {text}"))
    print(cyan("─" * width))


def _ok(msg: str) -> None:
    print(f"  {green('✔')} {msg}")


def _warn(msg: str) -> None:
    print(f"  {yellow('⚠')} {msg}")


def _err(msg: str) -> None:
    print(f"  {red('✖')} {msg}")


def _ask(prompt: str, default: str = "", secret: bool = False) -> str:
    """Prompt the user; returns stripped input or default."""
    display_default = "****" if (secret and default) else default
    suffix = f" [{display_default}]" if default else ""
    try:
        if secret:
            import getpass
            value = getpass.getpass(f"  {bold('?')} {prompt}{suffix}: ").strip()
        else:
            value = input(f"  {bold('?')} {prompt}{suffix}: ").strip()
    except (KeyboardInterrupt, EOFError):
        print()
        sys.exit(0)
    return value or default


def _confirm(prompt: str, default: bool = True) -> bool:
    yn = "Y/n" if default else "y/N"
    raw = _ask(f"{prompt} ({yn})")
    if not raw:
        return default
    return raw.lower().startswith("y")


# ──────────────────────────────────────────────────────────────────────────────
# Step 1 – Prerequisites
# ──────────────────────────────────────────────────────────────────────────────

def _python_version_ok() -> bool:
    return sys.version_info >= (3, 12)


def _check_tool(name: str, *args: str, min_version: Optional[str] = None) -> bool:
    """Return True if *name* is on PATH and (optionally) meets min_version."""
    path = shutil.which(name)
    if not path:
        return False
    if min_version and args:
        try:
            result = _run([name, *args], check=False, capture=True)
            output = result.stdout + result.stderr
            # Extract first X.Y.Z from output
            match = re.search(r"(\d+)\.(\d+)", output)
            if match:
                major, minor = int(match.group(1)), int(match.group(2))
                req_major, req_minor = (int(p) for p in min_version.split(".")[:2])
                return (major, minor) >= (req_major, req_minor)
        except Exception:
            pass
    return True


def check_prerequisites() -> None:
    _heading("Step 1 — Checking prerequisites")
    errors: list[str] = []

    # Python
    if _python_version_ok():
        _ok(f"Python {sys.version.split()[0]}")
    else:
        _err(f"Python 3.12+ required (found {sys.version.split()[0]})")
        errors.append("python")

    # Poetry
    if _check_tool("poetry", "--version", min_version="2.0"):
        result = _run(["poetry", "--version"], capture=True, check=False)
        _ok(result.stdout.strip() or "Poetry found")
    else:
        _err("Poetry 2.0+ not found. Install from https://python-poetry.org/docs/#installation")
        errors.append("poetry")

    # FFmpeg (required for video processing)
    if _check_tool("ffmpeg", "-version"):
        _ok("FFmpeg found")
    else:
        _warn(
            "FFmpeg not found — video rendering will not work.\n"
            "    Ubuntu/Debian: sudo apt install ffmpeg\n"
            "    macOS:         brew install ffmpeg\n"
            "    Windows:       https://ffmpeg.org/download.html"
        )

    # Tesseract (required for OCR)
    if _check_tool("tesseract", "--version"):
        _ok("Tesseract found")
    else:
        _warn(
            "Tesseract not found — OCR will not work.\n"
            "    Ubuntu/Debian: sudo apt install tesseract-ocr tesseract-ocr-eng\n"
            "    macOS:         brew install tesseract\n"
            "    Windows:       https://github.com/tesseract-ocr/tesseract"
        )

    if errors:
        print()
        _err("Required tools are missing. Please install them and re-run setup.py.")
        sys.exit(1)


# ──────────────────────────────────────────────────────────────────────────────
# Step 2 – Install dependencies
# ──────────────────────────────────────────────────────────────────────────────

def install_dependencies() -> None:
    _heading("Step 2 — Installing dependencies")
    print("  Running: poetry install  (this may take a minute on first run)\n")
    try:
        _run(["poetry", "install"])
        _ok("Dependencies installed")
    except subprocess.CalledProcessError:
        _err("poetry install failed. Check the output above for details.")
        sys.exit(1)


# ──────────────────────────────────────────────────────────────────────────────
# Step 3 – Configure .env
# ──────────────────────────────────────────────────────────────────────────────

def _read_env() -> dict[str, str]:
    """Read existing .env into a dict. Keys are uppercased."""
    env: dict[str, str] = {}
    if not ENV_FILE.exists():
        return env
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def _write_env(env: dict[str, str]) -> None:
    """Serialise env dict back to .env, preserving comments from .env.example."""
    # Start from example if .env doesn't exist yet, else keep current file
    if ENV_FILE.exists():
        template = ENV_FILE.read_text(encoding="utf-8")
    elif ENV_EXAMPLE.exists():
        template = ENV_EXAMPLE.read_text(encoding="utf-8")
    else:
        template = ""

    lines = template.splitlines()
    result: list[str] = []
    written: set[str] = set()

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            result.append(line)
            continue
        if "=" in stripped:
            key = stripped.split("=", 1)[0].strip().lstrip("#").strip()
            if key in env:
                result.append(f"{key}={env[key]}")
                written.add(key)
            else:
                result.append(line)
        else:
            result.append(line)

    # Append any keys that weren't in the template
    for key, val in env.items():
        if key not in written:
            result.append(f"{key}={val}")

    ENV_FILE.write_text("\n".join(result) + "\n", encoding="utf-8")


def _gen_api_key() -> str:
    """Generate a cryptographically random 32-byte hex API key."""
    import secrets
    return secrets.token_hex(32)


def configure_env() -> None:
    _heading("Step 3 — Configuration")

    existing = _read_env()
    new_env = dict(existing)  # start with existing values

    print(textwrap.dedent("""\
      We'll now ask for the required settings.
      Press Enter to keep the current/default value shown in brackets.
    """))

    # ── API Key ──────────────────────────────────────────────────────────────
    print(bold("  API Security"))
    current_key = existing.get("AMRAS_API_KEY", "")
    if current_key and current_key != "change-me-to-a-strong-random-secret":
        _ok(f"AMRAS_API_KEY is already set (****{current_key[-4:]})")
    else:
        suggested = _gen_api_key()
        print(f"  {yellow('!')} A strong API key is required. We can generate one for you.")
        use_generated = _confirm("  Generate a random API key automatically?", default=True)
        if use_generated:
            new_env["AMRAS_API_KEY"] = suggested
            _ok(f"Generated API key: {suggested[:8]}…{suggested[-4:]} (saved to .env)")
        else:
            while True:
                key = _ask("Enter your API key (min 16 characters)", secret=True)
                if len(key) >= 16:
                    new_env["AMRAS_API_KEY"] = key
                    break
                _err("API key must be at least 16 characters.")

    # ── CORS Origins ─────────────────────────────────────────────────────────
    print()
    print(bold("  CORS Origins"))
    origins = _ask(
        "Allowed origins (comma-separated, or * for all)",
        default=existing.get("AMRAS_ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080"),
    )
    new_env["AMRAS_ALLOWED_ORIGINS"] = origins

    # ── Database ─────────────────────────────────────────────────────────────
    print()
    print(bold("  Database"))
    print(f"  {cyan('SQLite')} is the default for local development.")
    print(f"  For production, use {cyan('PostgreSQL')}.")
    db_choice = _ask(
        "Database type",
        default="sqlite",
    ).lower()

    if db_choice.startswith("p"):
        host = _ask("  PostgreSQL host", default="localhost")
        port = _ask("  PostgreSQL port", default="5432")
        user = _ask("  PostgreSQL user", default="amras")
        password = _ask("  PostgreSQL password", secret=True)
        dbname = _ask("  PostgreSQL database name", default="amras")
        new_env["DB__URL"] = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"
    else:
        default_sqlite = existing.get("DB__URL", "sqlite+aiosqlite:///./dev.db")
        db_url = _ask("SQLite database path (URL)", default=default_sqlite)
        new_env["DB__URL"] = db_url

    # ── AI Provider ──────────────────────────────────────────────────────────
    print()
    print(bold("  AI Provider"))
    print(
        f"  Choose {cyan('local')} to run with the built-in mock provider (no API key needed).\n"
        f"  Choose {cyan('openai')}, {cyan('anthropic')}, etc. to use cloud providers."
    )
    ai_provider = _ask("AI provider", default=existing.get("AI__PROVIDER", "local")).lower()
    new_env["AI__PROVIDER"] = ai_provider

    if ai_provider != "local":
        ai_key = _ask(f"  API key for {ai_provider}", secret=True,
                      default=existing.get("AI__API_KEY", ""))
        new_env["AI__API_KEY"] = ai_key
        ai_model = _ask("  Model name", default=existing.get("AI__MODEL", ""))
        new_env["AI__MODEL"] = ai_model
        ai_base = _ask("  Base URL (leave blank for default)", default=existing.get("AI__BASE_URL", ""))
        new_env["AI__BASE_URL"] = ai_base
    else:
        new_env.setdefault("AI__PROVIDER", "local")

    # ── Debug mode ───────────────────────────────────────────────────────────
    print()
    debug = _confirm("  Enable DEBUG mode? (exposes /vision/debug/* endpoints)", default=False)
    new_env["DEBUG"] = "true" if debug else "false"

    # Write
    _write_env(new_env)
    _ok(f".env written to {ENV_FILE}")


# ──────────────────────────────────────────────────────────────────────────────
# Step 4 – Database migrations
# ──────────────────────────────────────────────────────────────────────────────

def run_migrations() -> None:
    _heading("Step 4 — Database migrations")
    print("  Running: poetry run alembic upgrade head\n")
    try:
        _run(["poetry", "run", "alembic", "upgrade", "head"])
        _ok("Database schema is up to date")
    except subprocess.CalledProcessError:
        _err("Migration failed. Check the output above.")
        _err("If the database schema is already at the latest version, this is safe to ignore.")
        if not _confirm("  Continue anyway?", default=True):
            sys.exit(1)


# ──────────────────────────────────────────────────────────────────────────────
# Step 5 – Optional tests
# ──────────────────────────────────────────────────────────────────────────────

def run_tests() -> None:
    _heading("Step 5 — Test suite (optional)")
    if not _confirm("  Run the test suite to verify the setup?", default=True):
        _warn("Skipped")
        return
    print()
    try:
        _run(["poetry", "run", "pytest", "tests/", "-v", "--tb=short"])
        _ok("All tests passed")
    except subprocess.CalledProcessError:
        _warn("Some tests failed. The application may still work — check the output above.")


# ──────────────────────────────────────────────────────────────────────────────
# Step 6 – Launch
# ──────────────────────────────────────────────────────────────────────────────

def launch_server() -> None:
    _heading("Step 6 — Launching AMRAS API server")

    host = _ask("Host to bind to", default="0.0.0.0")
    port = _ask("Port", default="8000")
    reload = _confirm("  Enable auto-reload? (recommended for development)", default=True)

    cmd = [
        "poetry", "run", "uvicorn",
        "app.api.main:app",
        "--host", host,
        "--port", port,
    ]
    if reload:
        cmd.append("--reload")

    print()
    print(f"  {bold('Starting:')} {' '.join(cmd)}")
    print(f"  {green('API docs:')}   http://{host}:{port}/docs")
    print(f"  {green('Health:  ')}   http://{host}:{port}/health")
    print()
    print(f"  {yellow('Press Ctrl-C to stop the server.')}")
    print()

    try:
        _run(cmd, check=False)
    except KeyboardInterrupt:
        print()
        _ok("Server stopped.")


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    print()
    print(bold(cyan("━" * 72)))
    print(bold(cyan("  AMRAS — AI Manga Recap Automation System")))
    print(bold(cyan("  Interactive Setup & Launch")))
    print(bold(cyan("━" * 72)))
    print(textwrap.dedent(f"""
      Repository : https://github.com/DevKaranJ/AMRAS-MODEL
      Docs       : {ROOT}/README.md
      API docs   : http://localhost:8000/docs  (after launch)
    """))

    check_prerequisites()
    install_dependencies()
    configure_env()
    run_migrations()
    run_tests()

    print()
    _heading("Setup complete!")
    _ok("AMRAS is configured and ready.")

    if _confirm("\n  Launch the API server now?", default=True):
        launch_server()
    else:
        print()
        print(f"  To start manually, run:")
        print(f"    {cyan('poetry run uvicorn app.api.main:app --reload')}")
        print()


if __name__ == "__main__":
    main()

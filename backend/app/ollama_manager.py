from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from typing import Iterable, List, Optional

import httpx

DEFAULT_OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")


def is_server_up(base_url: str, timeout_s: float = 1.0) -> bool:
    try:
        with httpx.Client(timeout=timeout_s) as client:
            r = client.get(f"{base_url}/api/version")
            return r.status_code == 200
    except Exception:
        return False


def start_server_background() -> Optional[subprocess.Popen]:
    try:
        # Start `ollama serve` detached; stderr/stdout to devnull
        devnull = open(os.devnull, "wb")
        proc = subprocess.Popen(
            ["ollama", "serve"],
            stdout=devnull,
            stderr=devnull,
            stdin=subprocess.DEVNULL,
            close_fds=True,
        )
        return proc
    except FileNotFoundError:
        return None


def ensure_server(base_url: str, wait_seconds: float = 20.0) -> bool:
    if is_server_up(base_url):
        return True

    proc = start_server_background()
    if proc is None:
        return False

    # Poll until server is reachable
    start = time.time()
    while time.time() - start < wait_seconds:
        if is_server_up(base_url):
            return True
        time.sleep(0.5)
    return is_server_up(base_url)


def list_models(base_url: str) -> List[str]:
    try:
        with httpx.Client(timeout=5.0) as client:
            r = client.get(f"{base_url}/api/tags")
            r.raise_for_status()
            data = r.json()
            models = data.get("models") or []
            names = []
            for m in models:
                name = m.get("name")
                if name:
                    names.append(name)
            return names
    except Exception:
        return []


def pull_model(base_url: str, model: str, quiet: bool = False) -> bool:
    # POST /api/pull streams JSON lines with status updates and ends with status: success
    try:
        with httpx.Client(timeout=None) as client:
            with client.stream("POST", f"{base_url}/api/pull", json={"name": model}) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                    except Exception:
                        # Non-JSON line; skip
                        continue
                    status = event.get("status") or ""
                    if not quiet and status:
                        # Best-effort progress message to stdout
                        print(f"[{model}] {status}")
                    if status == "success":
                        return True
        return False
    except Exception:
        return False


def ensure_models(base_url: str, models: Iterable[str], quiet: bool = False) -> List[str]:
    installed = set(list_models(base_url))
    ensured: List[str] = []
    for model in models:
        if model in installed:
            ensured.append(model)
            continue
        ok = pull_model(base_url, model, quiet=quiet)
        if ok:
            ensured.append(model)
    return ensured


def cli_main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Ensure Ollama server and pull required models")
    parser.add_argument("--host", default=DEFAULT_OLLAMA_HOST, help="Ollama base URL, e.g. http://127.0.0.1:11434")
    parser.add_argument("--model", action="append", dest="models", help="Model to ensure (can repeat)")
    parser.add_argument("--quiet", action="store_true", help="Reduce output noise")

    args = parser.parse_args(argv)
    base_url = args.host

    if not ensure_server(base_url):
        print("Could not start or reach Ollama server. Is ollama installed?", file=sys.stderr)
        return 2

    models = args.models or []
    if not models:
        # Fallback to env defaults
        default_model = os.getenv("DEFAULT_MODEL", "qwen2.5:7b-instruct")
        embed_model = os.getenv("EMBED_MODEL", "nomic-embed-text")
        models = [default_model, embed_model]

    ensured = ensure_models(base_url, models, quiet=args.quiet)
    missing = [m for m in models if m not in ensured]
    if missing:
        print(f"Failed to ensure models: {missing}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"Ensured models: {ensured}")
    return 0


if __name__ == "__main__":
    raise SystemExit(cli_main())

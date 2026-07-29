#!/usr/bin/env python3

import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
REQUESTS = ROOT / "requests"
OUTPUTS = ROOT / "outputs"
OUTPUTS.mkdir(exist_ok=True)


def safe_name(value):
    value = (value or "video").lower()
    value = re.sub(r"[^a-z0-9áéíóúñü]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value[:60] or "video"


def write_json(name, payload):
    target = OUTPUTS / name
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"wrote": str(target)}, ensure_ascii=False))


def latest_request():
    files = sorted(REQUESTS.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    nested = sorted(REQUESTS.glob("**/*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    candidates = []
    seen = set()
    for path in files + nested:
        if path not in seen:
            candidates.append(path)
            seen.add(path)
    if not candidates:
        raise FileNotFoundError("No hay solicitudes JSON en requests/")
    return candidates[0]


def http_json(method, url, token, payload):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=180) as response:
        raw = response.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def download(url, target):
    req = urllib.request.Request(url, headers={"User-Agent": "uptobe-video-workflow"})
    with urllib.request.urlopen(req, timeout=600) as response:
        target.write_bytes(response.read())
    if not target.exists() or target.stat().st_size == 0:
        raise RuntimeError(f"Archivo vacío: {target}")


def save_base64(value, target):
    target.write_bytes(base64.b64decode(value))
    if not target.exists() or target.stat().st_size == 0:
        raise RuntimeError(f"Archivo vacío: {target}")


def main():
    request_path = latest_request()
    payload = json.loads(request_path.read_text(encoding="utf-8"))
    title = payload.get("title") or request_path.stem
    basename = safe_name(title)
    endpoint = os.environ.get("VIDEO_API_ENDPOINT", "").strip()
    token = os.environ.get("VIDEO_API_TOKEN", "").strip()

    manifest = {
        "request_file": str(request_path),
        "title": title,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "started",
        "files": [],
    }

    if not endpoint:
        manifest["status"] = "blocked"
        manifest["error"] = "Falta el secreto VIDEO_API_ENDPOINT en GitHub. No se genera placeholder."
        write_json("diagnostico.json", manifest)
        return 0

    try:
        response = http_json("POST", endpoint, token, payload)
        manifest["provider_response_keys"] = sorted(response.keys())

        targets = [
            ("mp4_url", OUTPUTS / f"{basename}.mp4"),
            ("video_url", OUTPUTS / f"{basename}.mp4"),
            ("webm_url", OUTPUTS / f"{basename}.webm"),
            ("poster_url", OUTPUTS / f"{basename}.jpg"),
        ]
        for key, target in targets:
            url = response.get(key)
            if url and not target.exists():
                download(url, target)
                manifest["files"].append({"key": key, "path": str(target), "bytes": target.stat().st_size})

        b64_targets = [
            ("mp4_base64", OUTPUTS / f"{basename}.mp4"),
            ("webm_base64", OUTPUTS / f"{basename}.webm"),
            ("poster_base64", OUTPUTS / f"{basename}.jpg"),
        ]
        for key, target in b64_targets:
            value = response.get(key)
            if value and not target.exists():
                save_base64(value, target)
                manifest["files"].append({"key": key, "path": str(target), "bytes": target.stat().st_size})

        if not manifest["files"]:
            manifest["status"] = "blocked"
            manifest["error"] = "El proveedor respondió sin URL/base64 de vídeo real. No se genera placeholder."
        else:
            manifest["status"] = "succeeded"
        write_json("manifest.json", manifest)
        return 0
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        manifest["status"] = "failed"
        manifest["error"] = f"HTTP {error.code}: {detail}"
        write_json("diagnostico.json", manifest)
        return 1
    except Exception as error:
        manifest["status"] = "failed"
        manifest["error"] = str(error)
        write_json("diagnostico.json", manifest)
        return 1


if __name__ == "__main__":
    sys.exit(main())

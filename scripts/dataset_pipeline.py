#!/usr/bin/env python3
"""ATHARVADRISHTI reproducible dataset acquisition and audit pipeline."""

from __future__ import annotations
import argparse
import csv
import hashlib
import json
import os
import urllib.request
import zipfile
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "metadata" / "dataset_sources.json"
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
META = ROOT / "data" / "metadata"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}

def registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))

def source(source_id):
    for item in registry()["sources"]:
        if item["id"] == source_id:
            return item
    raise SystemExit("Unknown source: " + source_id)

def init_dirs():
    buckets = ["commercial_candidate", "research_only", "plantvillage",
               "plantdoc", "mendeley", "plantwild", "custom_field"]
    processed = ["gate", "plant_part", "crop", "leaf_condition",
                 "fruit_condition", "flower_condition", "pest",
                 "segmentation", "severity"]
    for bucket in buckets:
        (RAW / bucket).mkdir(parents=True, exist_ok=True)
    for name in processed:
        (PROCESSED / name).mkdir(parents=True, exist_ok=True)
    META.mkdir(parents=True, exist_ok=True)

def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()

def perceptual_hash(path, size=16):
    if Image is None:
        return ""
    try:
        with Image.open(path) as image:
            image = image.convert("L").resize((size, size))
            pixels = list(image.getdata())
        average = sum(pixels) / len(pixels)
        bits = "".join("1" if value >= average else "0" for value in pixels)
        return format(int(bits, 2), "x")
    except Exception:
        return ""

def safe_extract(archive, destination):
    destination = destination.resolve()
    with zipfile.ZipFile(archive) as zf:
        for member in zf.infolist():
            target = (destination / member.filename).resolve()
            if not str(target).startswith(str(destination) + os.sep):
                raise RuntimeError("Unsafe ZIP member: " + member.filename)
        zf.extractall(destination)

def download(source_id):
    init_dirs()
    item = source(source_id)
    url = item.get("download_url")
    folder = RAW / item["bucket"] / source_id
    folder.mkdir(parents=True, exist_ok=True)
    if not url:
        print("No direct download URL configured.")
        print("Official source:", item["official_url"])
        print("Place the downloaded data under:", folder)
        return
    filename = url.split("/")[-1].split("?")[0] or (source_id + ".download")
    archive = folder / filename
    if archive.exists():
        print("Already exists:", archive)
        return
    request = urllib.request.Request(
        url, headers={"User-Agent": "ATHARVADRISHTI-dataset-pipeline/1.0"}
    )
    print("Downloading:", url)
    with urllib.request.urlopen(request, timeout=120) as response, archive.open("wb") as out:
        while chunk := response.read(1024 * 1024):
            out.write(chunk)
    print("Saved:", archive)
    print("SHA256:", sha256(archive))
    if archive.suffix.lower() == ".zip":
        extracted = folder / "extracted"
        extracted.mkdir(exist_ok=True)
        safe_extract(archive, extracted)
        print("Extracted:", extracted)

def image_paths(source_id=None):
    roots = [RAW]
    if source_id:
        item = source(source_id)
        roots = [RAW / item["bucket"] / source_id]
    for root in roots:
        if root.exists():
            for path in root.rglob("*"):
                if path.is_file() and path.suffix.lower() in IMAGE_EXTS:
                    yield path

def audit(source_id=None):
    init_dirs()
    rows = []
    for path in image_paths(source_id):
        item = source(source_id) if source_id else None
        row = {
            "image_id": hashlib.sha1(str(path).encode()).hexdigest(),
            "source_dataset": item["id"] if item else "unknown",
            "source_license": item["license_status"] if item else "UNKNOWN",
            "source_original_path": str(path.relative_to(ROOT)),
            "source_label": path.parent.name,
            "sha256": "",
            "perceptual_hash": "",
            "width": "",
            "height": "",
            "format": "",
            "valid_image": False,
            "review_status": "unreviewed",
            "notes": ""
        }
        try:
            row["sha256"] = sha256(path)
            row["perceptual_hash"] = perceptual_hash(path)
            if Image is not None:
                with Image.open(path) as image:
                    image.verify()
                with Image.open(path) as image:
                    row["width"], row["height"] = image.size
                    row["format"] = image.format
                row["valid_image"] = True
            else:
                row["notes"] = "Pillow unavailable; install project requirements."
        except Exception as exc:
            row["notes"] = "unreadable: " + type(exc).__name__
        rows.append(row)
    name = "image_audit.csv" if not source_id else "image_audit_" + source_id + ".csv"
    write_csv(META / name, rows)
    print("Audited", len(rows), "images ->", META / name)

def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

def manifest():
    audit_file = META / "image_audit.csv"
    if not audit_file.exists():
        audit()
    with audit_file.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    counts = {}
    for row in rows:
        key = row.get("sha256", "")
        counts[key] = counts.get(key, 0) + 1
    for row in rows:
        row["duplicate_sha256"] = str(counts.get(row.get("sha256", ""), 0) > 1)
    write_csv(META / "image_manifest.csv", rows)
    print("Manifest:", META / "image_manifest.csv")
    print("Exact duplicate rows:", sum(r["duplicate_sha256"] == "True" for r in rows))

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    p = sub.add_parser("download"); p.add_argument("source_id")
    p = sub.add_parser("audit"); p.add_argument("--source", dest="source_id")
    sub.add_parser("manifest")
    args = parser.parse_args()
    if args.command == "init":
        init_dirs()
    elif args.command == "download":
        download(args.source_id)
    elif args.command == "audit":
        audit(args.source_id)
    elif args.command == "manifest":
        manifest()

if __name__ == "__main__":
    main()

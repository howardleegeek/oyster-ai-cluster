#!/usr/bin/env python3
"""Ingest 3 product renders into assets/ with canonical names.

Drop the three renders (any order) into assets_inbox/ then run:
  python3 scripts/ingest_oyster_views.py

Heuristic classification is based on the non-black bounding box aspect ratio:
- Top view: very wide and short bbox
- Side view: very tall and thin bbox
- Back view: everything else

This avoids manual renaming and keeps the site stable.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "assets_inbox"
ASSETS = ROOT / "assets"

OUT_NAMES = {
    "back": "oyster-back.png",
    "side": "oyster-side.png",
    "top": "oyster-top.png",
}

SUPPORTED = {".png", ".jpg", ".jpeg", ".webp"}


@dataclass(frozen=True)
class ImgInfo:
    path: Path
    w: int
    h: int
    bbox_w: int
    bbox_h: int
    aspect: float


def bbox_aspect(im: Image.Image) -> tuple[int, int, float]:
    arr = np.array(im.convert("RGBA"))
    rgb = arr[..., :3]
    # Treat near-black as background.
    mask = (rgb > 12).any(axis=2)
    ys, xs = np.where(mask)
    if xs.size == 0:
        return 0, 0, 0.0
    x0, x1 = int(xs.min()), int(xs.max())
    y0, y1 = int(ys.min()), int(ys.max())
    bw = (x1 - x0 + 1)
    bh = (y1 - y0 + 1)
    return bw, bh, (bw / bh if bh else 0.0)


def classify(info: ImgInfo) -> str:
    # Extreme ratios are unambiguous.
    if info.aspect >= 4.0 and info.bbox_h <= info.h * 0.35:
        return "top"
    if info.aspect <= 0.35 and info.bbox_w <= info.w * 0.35:
        return "side"
    return "back"


def main() -> int:
    INBOX.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)

    imgs = [p for p in INBOX.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED]
    if len(imgs) < 3:
        print(f"Need 3 images in {INBOX} (found {len(imgs)}).")
        return 2

    # Prefer larger files first.
    imgs.sort(key=lambda p: p.stat().st_size, reverse=True)

    infos: list[ImgInfo] = []
    for p in imgs:
        try:
            im = Image.open(p)
            w, h = im.size
            bw, bh, ar = bbox_aspect(im)
            infos.append(ImgInfo(p, w, h, bw, bh, ar))
        except Exception:
            continue

    if len(infos) < 3:
        print("Could not read 3 valid images from inbox.")
        return 3

    picked = infos[:8]  # allow a few extras in case of misclass
    buckets: dict[str, list[ImgInfo]] = {"back": [], "side": [], "top": []}
    for info in picked:
        buckets[classify(info)].append(info)

    # Resolve collisions by picking the one with the most non-black area.
    def score(info: ImgInfo) -> int:
        return info.bbox_w * info.bbox_h

    chosen: dict[str, ImgInfo] = {}
    for k in ("back", "side", "top"):
        if not buckets[k]:
            continue
        chosen[k] = sorted(buckets[k], key=score, reverse=True)[0]

    # If anything missing, fall back to best remaining by score.
    remaining = [i for i in picked if i.path not in {c.path for c in chosen.values()}]
    remaining.sort(key=score, reverse=True)
    for k in ("back", "side", "top"):
        if k in chosen:
            continue
        if not remaining:
            break
        chosen[k] = remaining.pop(0)

    if set(chosen.keys()) != {"back", "side", "top"}:
        print("Classification failed. Found:")
        for k, v in chosen.items():
            print("-", k, v.path)
        return 4

    for k, info in chosen.items():
        outp = ASSETS / OUT_NAMES[k]
        im = Image.open(info.path).convert("RGBA")
        im.save(outp)
        print(f"Wrote {k:4s} -> {outp} ({info.w}x{info.h}, bbox {info.bbox_w}x{info.bbox_h}, aspect {info.aspect:.3f})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

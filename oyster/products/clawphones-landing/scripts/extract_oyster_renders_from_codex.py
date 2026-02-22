#!/usr/bin/env python3
"""Extract 3 oyster renders from the Codex desktop app screen.

This script uses GUI automation + computer vision to:
1) Focus the Codex app
2) Find the message around '可以用一下这些照片'
3) Screenshot the screen
4) Detect the 3 large square image blocks and crop them into assets_inbox/
5) Call ingest_oyster_views.py to write canonical assets/oyster-*.png

If detection fails, it retries with small scroll adjustments.

Note: This is best-effort; if your Codex window layout is unusual, it may need tuning.
"""

from __future__ import annotations

import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

# Load DesktopController from the bundled Codex skill.
import sys
import subprocess
SKILL_DIR = Path("/Users/howardli/.codex/skills/desktop-control").resolve()
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))
from __init__ import DesktopController  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "assets_inbox"
OUTDIR.mkdir(parents=True, exist_ok=True)

CAP = ROOT / "_codex_capture.png"
DEBUG = ROOT / "_codex_detect_debug.png"


def _sleep(s: float) -> None:
    time.sleep(s)


def detect_squares(img_bgr: np.ndarray) -> list[tuple[int, int, int, int, float]]:
    """Return candidate square rects (x,y,w,h,score)."""
    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # Phase 1: connected components on non-black pixels (works for borderless images).
    mask = (gray > 18).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8), iterations=1)
    num, labels, stats, _centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)

    cc = []
    for i in range(1, num):
        x, y, cw, ch, area = stats[i].tolist()
        if cw < 260 or ch < 260:
            continue
        ar = cw / float(ch)
        if ar < 0.82 or ar > 1.22:
            continue
        if x + cw / 2 < w * 0.22:
            continue  # skip left sidebar region
        if cw > w * 0.8 and ch > h * 0.8:
            continue
        roi = gray[y : y + ch, x : x + cw]
        std = float(np.std(roi))
        mean = float(np.mean(roi))
        # Prefer large and with some contrast (device silhouette).
        score = (cw * ch) * (std + 1.0) * (0.2 + min(mean / 255.0, 1.0))
        cc.append((x, y, cw, ch, score))

    # If we already have enough plausible squares, return them.
    cc.sort(key=lambda r: r[4], reverse=True)
    if len(cc) >= 3:
        return cc[:8]

    # Edge-based detection.
    edges = cv2.Canny(gray, 40, 120)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)

    cnts, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cands = []
    for c in cnts:
        x, y, cw, ch = cv2.boundingRect(c)
        if cw < 220 or ch < 220:
            continue
        ar = cw / float(ch)
        if ar < 0.85 or ar > 1.18:
            continue
        # Reject huge container-like squares (rare)
        if cw > w * 0.75 and ch > h * 0.75:
            continue

        roi = gray[y : y + ch, x : x + cw]
        if roi.size == 0:
            continue
        # Score: prefer large, with some contrast (not pure black)
        mean = float(np.mean(roi))
        std = float(np.std(roi))
        area = cw * ch
        score = area * (std + 1.0) * (0.3 + min(mean / 255.0, 1.0))
        cands.append((x, y, cw, ch, score))

    # De-duplicate overlapping rects by NMS-like sweep
    cands.sort(key=lambda r: r[4], reverse=True)
    picked: list[tuple[int, int, int, int, float]] = []

    def iou(a, b) -> float:
        ax, ay, aw, ah, _ = a
        bx, by, bw, bh, _ = b
        x1 = max(ax, bx)
        y1 = max(ay, by)
        x2 = min(ax + aw, bx + bw)
        y2 = min(ay + ah, by + bh)
        inter = max(0, x2 - x1) * max(0, y2 - y1)
        if inter == 0:
            return 0.0
        ua = aw * ah + bw * bh - inter
        return inter / float(ua)

    for r in cands:
        if all(iou(r, p) < 0.35 for p in picked):
            picked.append(r)
        if len(picked) >= 8:
            break

    # Prefer rects in the main content area (avoid left sidebar)
    def content_score(r):
        x, y, rw, rh, score = r
        cx = x + rw / 2
        penalty = 1.0
        if cx < w * 0.18:
            penalty *= 0.4
        if y < h * 0.10:
            penalty *= 0.6
        return score * penalty

    picked.sort(key=content_score, reverse=True)
    return picked


def crop_and_write(img_rgb: np.ndarray, rects: list[tuple[int, int, int, int, float]]) -> list[Path]:
    out_paths = []
    for i, (x, y, rw, rh, _score) in enumerate(rects[:3], start=1):
        pad = int(min(rw, rh) * 0.02)
        x0 = max(0, x - pad)
        y0 = max(0, y - pad)
        x1 = min(img_rgb.shape[1], x + rw + pad)
        y1 = min(img_rgb.shape[0], y + rh + pad)
        crop = img_rgb[y0:y1, x0:x1]
        p = OUTDIR / f"codex_crop_{i}.png"
        Image.fromarray(crop).save(p)
        out_paths.append(p)
    return out_paths


def main() -> int:
    dc = DesktopController(failsafe=True, require_approval=False)

    # Focus Codex.
    # On macOS, "activate" does not always make the app frontmost (esp. across Spaces),
    # so we also force frontmost via System Events.
    for _ in range(2):
        try:
            subprocess.run(
                ["osascript", "-e", 'tell application "Codex" to activate'],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass
        try:
            subprocess.run(
                ["osascript", "-e", 'tell application "System Events" to set frontmost of process "Codex" to true'],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            break
        except Exception:
            _sleep(0.2)
    _sleep(0.8)

    # Clear inbox from previous attempts.
    for p in OUTDIR.glob("*.png"):
        try:
            p.unlink()
        except Exception:
            pass

    def try_find_and_capture() -> bool:
        # Cmd+F, type query, Enter, then Esc.
        dc.hotkey("command", "f")
        _sleep(0.2)
        dc.type_text("可以用一下这些照片")
        _sleep(0.1)
        dc.press("enter")
        _sleep(0.6)
        dc.press("escape")
        _sleep(0.2)

        dc.screenshot(filename=str(CAP))

        img = cv2.imread(str(CAP), cv2.IMREAD_COLOR)
        if img is None:
            return False

        rects = detect_squares(img)
        # Write debug overlay
        dbg = img.copy()
        for (x, y, rw, rh, _s) in rects[:8]:
            cv2.rectangle(dbg, (x, y), (x + rw, y + rh), (0, 255, 255), 2)
        cv2.imwrite(str(DEBUG), dbg)

        if len(rects) >= 3:
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            crops = crop_and_write(rgb, rects)
            # Run ingestion to map to back/side/top.
            subprocess.run(["python3", str(ROOT / "scripts/ingest_oyster_views.py")], check=False)
            print("CAPTURE", CAP)
            print("DEBUG", DEBUG)
            for p in crops:
                print("CROP", p)
            return True
        return False

    # Step 1: brute-force click likely thread rows in left sidebar to reach the right conversation.
    # Coordinates are tuned for a 1710x1107 screen capture with Codex in a window.
    click_x = 145
    candidate_ys = list(range(650, 1030, 24))  # sweep the threads list area
    for y in candidate_ys:
        dc.click(click_x, y)
        _sleep(0.45)
        if try_find_and_capture():
            return 0

    # Step 2: try some scroll adjustments and retry.
    for delta in (-18, -28, -36, 22, 30):
        dc.scroll(delta)
        _sleep(0.5)
        if try_find_and_capture():
            return 0

    print("Failed to detect 3 square image blocks. See:")
    print(CAP)
    print(DEBUG)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

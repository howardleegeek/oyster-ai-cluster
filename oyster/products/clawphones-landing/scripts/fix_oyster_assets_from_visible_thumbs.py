#!/usr/bin/env python3
"""
Fix assets/oyster-*.png by extracting 3 square-ish image thumbnails currently visible
in the Codex app window and classifying them as back/side/top via ingest_oyster_views.py.

This avoids relying on Codex sidebar navigation or AppleScript keystroke injection.
It works as long as the message containing the 3 renders is reachable by scrolling.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

import sys

SKILL_DIR = Path("/Users/howardli/.codex/skills/desktop-control").resolve()
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))
from __init__ import DesktopController  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
CAP = ROOT / "_codex_window_capture.png"
DBG = ROOT / "_codex_thumb_detect.png"
INBOX = ROOT / "assets_inbox"
INBOX.mkdir(parents=True, exist_ok=True)


def _sleep(s: float) -> None:
    time.sleep(s)


def focus_codex() -> None:
    subprocess.run(["osascript", "-e", 'tell application "Codex" to activate'], check=False)
    subprocess.run(["osascript", "-e", 'tell application "System Events" to set frontmost of process "Codex" to true'], check=False)
    _sleep(0.6)


def codex_window_info() -> tuple[int, dict]:
    code = r"""
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
wins = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
best=None
bestb=None
for w in wins:
    if w.get('kCGWindowOwnerName') != 'Codex':
        continue
    alpha = float(w.get('kCGWindowAlpha', 1.0))
    if alpha < 0.5:
        continue
    b = dict(w.get('kCGWindowBounds', {}))
    area = float(b.get('Width',0))*float(b.get('Height',0))
    if not best or area > best[0]:
        best = (area, int(w.get('kCGWindowNumber')))
        bestb = b
print(best[1] if best else -1)
print(bestb if bestb else {})
"""
    out = subprocess.check_output(["python3", "-c", code]).decode().splitlines()
    wid = int(out[0].strip())
    bounds = eval(out[1].strip()) if len(out) > 1 else {}
    if wid <= 0 or not bounds:
        raise RuntimeError("Could not locate Codex window")
    return wid, bounds


def capture_window(wid: int) -> None:
    subprocess.run(["/usr/sbin/screencapture", "-x", "-l", str(wid), str(CAP)], check=True)


def click_in_window(bounds: dict, cap_size: tuple[int, int], x_px: int, y_px: int, dc: DesktopController) -> None:
    cap_w, cap_h = cap_size
    bw = float(bounds.get("Width"))
    bh = float(bounds.get("Height"))
    scale_x = cap_w / bw if bw else 2.0
    scale_y = cap_h / bh if bh else 2.0
    sx = float(bounds.get("X")) + (x_px / scale_x)
    sy = float(bounds.get("Y")) + (y_px / scale_y)
    dc.click(int(sx), int(sy))


def detect_square_thumbnails(img_bgr: np.ndarray) -> list[tuple[int, int, int, int, float]]:
    """
    Detect square-ish blocks in the main content area; returns (x,y,w,h,score).
    This is intentionally permissive; we later take the largest non-overlapping 3.
    """
    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    mask = (gray > 18).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8), iterations=1)

    num, _labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    cands: list[tuple[int, int, int, int, float]] = []
    for i in range(1, num):
        x, y, cw, ch, _area = stats[i].tolist()
        if cw < 180 or ch < 180:
            continue
        ar = cw / float(ch)
        if ar < 0.86 or ar > 1.18:
            continue
        # exclude left sidebar
        if x + cw / 2 < w * 0.28:
            continue
        # exclude very top (nav)
        if y < h * 0.08:
            continue
        roi = gray[y : y + ch, x : x + cw]
        std = float(np.std(roi))
        mean = float(np.mean(roi))
        score = (cw * ch) * (std + 1.0) * (0.2 + min(mean / 255.0, 1.0))
        cands.append((x, y, cw, ch, score))

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

    # Prefer upper content area first (where the attachment strip likely is)
    picked.sort(key=lambda r: (r[1], r[0]))
    return picked


def crop_largest_square_viewer(img_bgr: np.ndarray) -> Image.Image | None:
    """When a thumbnail is opened, crop the largest centered square-ish block."""
    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    mask = (gray > 18).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8), iterations=1)
    num, _labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)

    best = None
    for i in range(1, num):
        x, y, cw, ch, _area = stats[i].tolist()
        if cw < 520 or ch < 520:
            continue
        ar = cw / float(ch)
        if ar < 0.86 or ar > 1.18:
            continue
        cx = x + cw / 2
        cy = y + ch / 2
        center_penalty = abs(cx - w / 2) + abs(cy - h / 2)
        score = (cw * ch) - center_penalty * 60
        if best is None or score > best[0]:
            best = (score, x, y, cw, ch)

    if best is None:
        return None

    _score, x, y, cw, ch = best
    pad = int(min(cw, ch) * 0.01)
    x0 = max(0, x - pad)
    y0 = max(0, y - pad)
    x1 = min(w, x + cw + pad)
    y1 = min(h, y + ch + pad)

    rgb = cv2.cvtColor(img_bgr[y0:y1, x0:x1], cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def main() -> int:
    dc = DesktopController(failsafe=True, require_approval=False)

    focus_codex()
    wid, bounds = codex_window_info()

    # Best-effort: jump near the message containing the 3 renders.
    # This relies on Codex using a standard Cmd+F find UI.
    capture_window(wid)
    base0 = cv2.imread(str(CAP), cv2.IMREAD_COLOR)
    if base0 is not None:
        click_in_window(bounds, (base0.shape[1], base0.shape[0]), int(base0.shape[1] * 0.70), int(base0.shape[0] * 0.25), dc)
        _sleep(0.2)
        dc.hotkey("command", "f")
        _sleep(0.25)
        dc.type_text("可以用一下这些照片")
        _sleep(0.1)
        dc.press("enter")
        _sleep(0.9)
        dc.press("escape")
        _sleep(0.25)

    # Clear inbox old renders.
    for p in INBOX.glob("render_*.png"):
        try:
            p.unlink()
        except Exception:
            pass

    # Try to find the 3 renders by scrolling up until we see 3 big square thumbs.
    for attempt in range(1, 45):
        capture_window(wid)
        base = cv2.imread(str(CAP), cv2.IMREAD_COLOR)
        if base is None:
            continue

        thumbs = detect_square_thumbnails(base)
        dbg = base.copy()
        for (x, y, cw, ch, _s) in thumbs:
            cv2.rectangle(dbg, (x, y), (x + cw, y + ch), (0, 255, 255), 3)
        cv2.putText(dbg, f"attempt={attempt} thumbs={len(thumbs)}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
        cv2.imwrite(str(DBG), dbg)

        if len(thumbs) >= 3:
            # Take the 3 largest squares by area and click them left-to-right.
            top3 = sorted(thumbs, key=lambda r: r[2] * r[3], reverse=True)[:3]
            top3.sort(key=lambda r: (r[0], r[1]))

            renders: list[Path] = []
            for i, (x, y, cw, ch, _s) in enumerate(top3, start=1):
                click_in_window(bounds, (base.shape[1], base.shape[0]), x + cw // 2, y + ch // 2, dc)
                _sleep(0.7)

                capture_window(wid)
                viewer = cv2.imread(str(CAP), cv2.IMREAD_COLOR)
                if viewer is None:
                    dc.press("escape")
                    _sleep(0.2)
                    continue

                crop = crop_largest_square_viewer(viewer)
                if crop is None:
                    dc.press("escape")
                    _sleep(0.2)
                    continue

                outp = INBOX / f"render_{i}.png"
                crop.save(outp)
                renders.append(outp)

                dc.press("escape")
                _sleep(0.35)

            if len(renders) == 3:
                subprocess.run(["python3", str(ROOT / "scripts/ingest_oyster_views.py")], check=False)
                return 0

        # Scroll up (older messages).
        # Click the conversation area first to ensure wheel affects the right pane.
        click_in_window(bounds, (base.shape[1], base.shape[0]), int(base.shape[1] * 0.72), int(base.shape[0] * 0.65), dc)
        _sleep(0.15)
        dc.scroll(18)  # positive = up on macOS for PyAutoGUI
        _sleep(0.5)

    print("failed; see", DBG)
    return 3


if __name__ == "__main__":
    raise SystemExit(main())

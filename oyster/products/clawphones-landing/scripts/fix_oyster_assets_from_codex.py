#!/usr/bin/env python3
"""Fix assets/oyster-*.png by extracting the 3 renders from the Codex app window.

This is an automation workaround for when the original 3 renders are only available
inside the Codex conversation UI.

Strategy:
1) Force Codex frontmost.
2) Screenshot the Codex window (not full screen) via `screencapture -l <windowId>`.
3) Template-match the sidebar row text for the thread `AI 手机 ClawPhone` and click it.
4) Cmd+F search for `oyster-top.png` to jump near the attachments.
5) Detect the 3 square thumbnails in the conversation area.
6) Open each thumbnail, screenshot the window, crop the largest square (viewer), save to assets_inbox/.
7) Run ingest_oyster_views.py to classify and write:
   assets/oyster-back.png, assets/oyster-side.png, assets/oyster-top.png

Notes:
- AppleScript keystrokes are blocked (Accessibility), so we use PyAutoGUI via DesktopController.
- This is best-effort; it retries a few times with minor scrolling.
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
DBG = ROOT / "_codex_oyster_fix_debug.png"
TPL_ROW = ROOT / "_tpl_ai_thread_row.png"  # sidebar row crop that includes 'AI 手机 ClawPhone'
INBOX = ROOT / "assets_inbox"
INBOX.mkdir(parents=True, exist_ok=True)


def _sleep(s: float) -> None:
    time.sleep(s)


def focus_codex() -> None:
    subprocess.run(["osascript", "-e", 'tell application "Codex" to activate'], check=False)
    subprocess.run(["osascript", "-e", 'tell application "System Events" to set frontmost of process "Codex" to true'], check=False)
    _sleep(0.6)


def frontmost_app() -> str:
    try:
        out = subprocess.check_output(
            ["osascript", "-e", 'tell application "System Events" to get name of first application process whose frontmost is true']
        ).decode().strip()
        return out
    except Exception:
        return ""


def codex_window_info() -> tuple[int, dict]:
    code = r'''
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
'''
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


def canny(img_bgr: np.ndarray) -> np.ndarray:
    g = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    g = cv2.GaussianBlur(g, (3, 3), 0)
    return cv2.Canny(g, 40, 120)


def match_sidebar_ai_thread(img_bgr: np.ndarray, tpl_bgr: np.ndarray) -> tuple[float, tuple[int, int], tuple[int, int]]:
    """Return (score, (x,y), (tw,th)) in *window capture pixel coords* for the best match."""
    h, w = img_bgr.shape[:2]
    roi = img_bgr[:, : int(w * 0.42)]

    te = canny(tpl_bgr)
    ie = canny(roi)

    res = cv2.matchTemplate(ie, te, cv2.TM_CCOEFF_NORMED)
    _minv, maxv, _minloc, maxloc = cv2.minMaxLoc(res)
    tw, th = tpl_bgr.shape[1], tpl_bgr.shape[0]
    return float(maxv), (int(maxloc[0]), int(maxloc[1])), (tw, th)


def detect_square_thumbnails(img_bgr: np.ndarray) -> list[tuple[int, int, int, int, float]]:
    """Detect square-ish blocks in main content area; returns (x,y,w,h,score)."""
    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    mask = (gray > 18).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8), iterations=1)

    num, _labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    cands = []
    for i in range(1, num):
        x, y, cw, ch, area = stats[i].tolist()
        if cw < 260 or ch < 260:
            continue
        ar = cw / float(ch)
        if ar < 0.85 or ar > 1.18:
            continue
        # ignore sidebar
        if x + cw / 2 < w * 0.25:
            continue
        # ignore very top nav area
        if y < h * 0.08:
            continue
        roi = gray[y : y + ch, x : x + cw]
        std = float(np.std(roi))
        mean = float(np.mean(roi))
        score = (cw * ch) * (std + 1.0) * (0.2 + min(mean / 255.0, 1.0))
        cands.append((x, y, cw, ch, score))

    cands.sort(key=lambda r: r[4], reverse=True)

    picked = []

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
        if len(picked) >= 6:
            break

    # Keep left-to-right order for clicking.
    picked.sort(key=lambda r: (r[0], r[1]))
    return picked


def crop_largest_square_viewer(img_bgr: np.ndarray) -> Image.Image | None:
    """When image viewer modal is open, crop the largest square-ish block."""
    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    mask = (gray > 18).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8), iterations=1)
    num, _labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)

    best = None
    for i in range(1, num):
        x, y, cw, ch, area = stats[i].tolist()
        if cw < 700 or ch < 700:
            continue
        ar = cw / float(ch)
        if ar < 0.85 or ar > 1.18:
            continue
        # prefer center
        cx = x + cw / 2
        cy = y + ch / 2
        center_penalty = abs(cx - w / 2) + abs(cy - h / 2)
        score = (cw * ch) - center_penalty * 80
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

    # Ensure Codex frontmost.
    for _ in range(3):
        focus_codex()
        if frontmost_app() == "Codex":
            break
        _sleep(0.3)

    wid, bounds = codex_window_info()
    capture_window(wid)
    img = cv2.imread(str(CAP), cv2.IMREAD_COLOR)
    if img is None:
        print("capture failed")
        return 2

    tpl = cv2.imread(str(TPL_ROW), cv2.IMREAD_COLOR)
    if tpl is None:
        print("missing template", TPL_ROW)
        return 3

    score, (mx, my), (tw, th) = match_sidebar_ai_thread(img, tpl)

    dbg = img.copy()
    cv2.rectangle(dbg, (mx, my), (mx + tw, my + th), (0, 255, 255), 3)
    cv2.putText(dbg, f"ai_row_match={score:.3f}", (mx, max(30, my - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
    cv2.imwrite(str(DBG), dbg)

    if score < 0.45:
        print("could not locate AI thread row; see", DBG)
        return 4

    # Click the row.
    click_in_window(bounds, (img.shape[1], img.shape[0]), mx + tw // 2, my + th // 2, dc)
    _sleep(0.8)

    # Jump near the attachments.
    focus_codex()
    dc.hotkey("command", "f")
    _sleep(0.2)
    dc.type_text("oyster-top.png")
    _sleep(0.1)
    dc.press("enter")
    _sleep(0.9)
    dc.press("escape")
    _sleep(0.2)

    # Now locate three thumbnails and open each.
    for p in INBOX.glob("render_*.png"):
        try:
            p.unlink()
        except Exception:
            pass

    for attempt, scroll in enumerate((0, -14, -18), start=1):
        if scroll != 0:
            # click conversation area before scroll
            wid, bounds = codex_window_info()
            capture_window(wid)
            img0 = cv2.imread(str(CAP), cv2.IMREAD_COLOR)
            if img0 is not None:
                click_in_window(bounds, (img0.shape[1], img0.shape[0]), int(img0.shape[1] * 0.72), int(img0.shape[0] * 0.60), dc)
                _sleep(0.15)
                dc.scroll(scroll)
                _sleep(0.4)

        wid, bounds = codex_window_info()
        capture_window(wid)
        base = cv2.imread(str(CAP), cv2.IMREAD_COLOR)
        if base is None:
            continue

        thumbs = detect_square_thumbnails(base)
        # draw debug boxes
        dbg2 = base.copy()
        for (x, y, cw, ch, _s) in thumbs:
            cv2.rectangle(dbg2, (x, y), (x + cw, y + ch), (0, 255, 255), 3)
        cv2.putText(dbg2, f"thumbs={len(thumbs)}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
        cv2.imwrite(str(DBG), dbg2)

        if len(thumbs) < 3:
            continue

        # Use the top-3 largest by area.
        thumbs2 = sorted(thumbs, key=lambda r: r[2] * r[3], reverse=True)[:3]
        # stable order
        thumbs2.sort(key=lambda r: (r[0], r[1]))

        renders: list[Path] = []
        for i, (x, y, cw, ch, _s) in enumerate(thumbs2, start=1):
            # open thumbnail
            click_in_window(bounds, (base.shape[1], base.shape[0]), x + cw // 2, y + ch // 2, dc)
            _sleep(0.6)

            wid2, _bounds2 = codex_window_info()
            capture_window(wid2)
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
            _sleep(0.3)

        if len(renders) == 3:
            # Put into inbox as generic names for ingest script
            # (ingest script reads whatever is in assets_inbox/)
            subprocess.run(["python3", str(ROOT / "scripts/ingest_oyster_views.py")], check=False)
            return 0

    print("failed to extract 3 renders; debug:", DBG)
    return 5


if __name__ == "__main__":
    raise SystemExit(main())

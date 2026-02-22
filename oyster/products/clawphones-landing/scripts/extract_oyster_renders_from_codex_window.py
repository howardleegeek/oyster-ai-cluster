#!/usr/bin/env python3
"""Extract the three oyster renders from the *Codex window* by screenshotting the window via screencapture.

Rationale:
- PyAutoGUI full-screen screenshots were often capturing Chrome.
- We can reliably identify the Codex window id via Quartz and capture just that window.

Workflow:
1) Activate Codex and force frontmost.
2) Capture Codex window to _codex_window_capture.png
3) Find the conversation containing 3 square renders by using Cmd+F inside Codex (best-effort)
4) Capture again and detect 3 large square image blocks; crop them into assets_inbox/
5) Run ingest_oyster_views.py to overwrite assets/oyster-*.png

If step 3 cannot navigate, you can manually open the correct thread once; this script then succeeds.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / 'assets_inbox'
OUTDIR.mkdir(parents=True, exist_ok=True)
CAP = ROOT / '_codex_window_capture.png'
DBG = ROOT / '_codex_window_detect.png'


def focus_codex() -> None:
    subprocess.run(["osascript", "-e", 'tell application "Codex" to activate'], check=False)
    subprocess.run(["osascript", "-e", 'tell application "System Events" to set frontmost of process "Codex" to true'], check=False)
    time.sleep(0.8)


def get_codex_window_id() -> int:
    # Use Quartz to identify the largest visible Codex window.
    code = r'''
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
wins = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
best=None
for w in wins:
    if w.get('kCGWindowOwnerName') != 'Codex':
        continue
    alpha = float(w.get('kCGWindowAlpha', 1.0))
    if alpha < 0.5:
        continue
    b = dict(w.get('kCGWindowBounds', {}))
    area = float(b.get('Width',0))*float(b.get('Height',0))
    if not best or area > best[0]:
        best=(area, int(w.get('kCGWindowNumber')))
print(best[1] if best else -1)
'''
    out = subprocess.check_output(["python3", "-c", code]).decode().strip()
    wid = int(out)
    if wid <= 0:
        raise RuntimeError('Could not find Codex window id')
    return wid


def capture_window(wid: int) -> None:
    subprocess.run(["/usr/sbin/screencapture", "-x", "-l", str(wid), str(CAP)], check=True)


def detect_square_blocks(img_bgr: np.ndarray) -> list[tuple[int,int,int,int,float]]:
    h,w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    mask = (gray > 18).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9,9), np.uint8), iterations=1)
    num, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    cands=[]
    for i in range(1, num):
        x,y,cw,ch,area = stats[i].tolist()
        if cw < 500 or ch < 500:
            continue
        ar = cw/float(ch)
        if ar < 0.86 or ar > 1.18:
            continue
        # exclude left sidebar
        if x + cw/2 < w*0.25:
            continue
        roi = gray[y:y+ch, x:x+cw]
        std=float(np.std(roi)); mean=float(np.mean(roi))
        score=(cw*ch)*(std+1.0)*(0.2+min(mean/255.0,1.0))
        cands.append((x,y,cw,ch,score))
    cands.sort(key=lambda r:r[4], reverse=True)
    # simple NMS
    picked=[]
    def iou(a,b):
        ax,ay,aw,ah,_=a; bx,by,bw,bh,_=b
        x1=max(ax,bx); y1=max(ay,by)
        x2=min(ax+aw,bx+bw); y2=min(ay+ah,by+bh)
        inter=max(0,x2-x1)*max(0,y2-y1)
        if inter==0: return 0.0
        ua=aw*ah+bw*bh-inter
        return inter/ua
    for r in cands:
        if all(iou(r,p)<0.35 for p in picked):
            picked.append(r)
        if len(picked)>=6:
            break
    return picked


def crop_write(img_rgb: np.ndarray, rects) -> None:
    # clear old
    for p in OUTDIR.glob('codex_window_crop_*.png'):
        try:
            p.unlink()
        except Exception:
            pass
    for i,(x,y,cw,ch,_s) in enumerate(rects[:3], start=1):
        pad=int(min(cw,ch)*0.02)
        x0=max(0,x-pad); y0=max(0,y-pad)
        x1=min(img_rgb.shape[1], x+cw+pad)
        y1=min(img_rgb.shape[0], y+ch+pad)
        crop=img_rgb[y0:y1, x0:x1]
        Image.fromarray(crop).save(OUTDIR/f'codex_window_crop_{i}.png')


def send_cmd_f(query: str) -> None:
    # Use AppleScript to send Cmd+F, type query, Enter, Esc.
    script = f'''
    tell application "System Events"
      tell process "Codex"
        keystroke "f" using command down
        delay 0.2
        keystroke "{query}"
        delay 0.1
        key code 36
        delay 0.6
        key code 53
      end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=False)
    time.sleep(0.3)


def main() -> int:
    focus_codex()
    wid = get_codex_window_id()

    # best-effort: jump to the message with images
    send_cmd_f('可以用一下这些照片')

    capture_window(wid)
    img = cv2.imread(str(CAP), cv2.IMREAD_COLOR)
    if img is None:
        print('capture failed')
        return 2

    rects = detect_square_blocks(img)
    dbg = img.copy()
    for (x,y,cw,ch,_s) in rects:
        cv2.rectangle(dbg,(x,y),(x+cw,y+ch),(0,255,255),3)
    cv2.imwrite(str(DBG), dbg)

    if len(rects) < 3:
        print('not enough squares; open the thread with the 3 renders, then rerun')
        print('cap', CAP)
        print('dbg', DBG)
        return 3

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    crop_write(rgb, rects)

    subprocess.run(["python3", str(ROOT/'scripts/ingest_oyster_views.py')], check=False)
    print('cap', CAP)
    print('dbg', DBG)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

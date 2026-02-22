#!/usr/bin/env python3
"""Bring Codex to front, click a known thread row in the left sidebar (template match), then stop.

This gives us a stable location before we run extraction.
"""

from __future__ import annotations

import time
from pathlib import Path
import subprocess

import cv2
import numpy as np
from PIL import Image

import sys
SKILL_DIR = Path("/Users/howardli/.codex/skills/desktop-control").resolve()
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))
from __init__ import DesktopController  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
CAP = ROOT / "_codex_sidebar.png"
TPL = ROOT / "_tmpl_thread_row.png"
DBG = ROOT / "_codex_sidebar_match.png"


def main() -> int:
    dc = DesktopController(failsafe=True, require_approval=False)

    for app in ("Codex", "OpenAI Codex"):
        try:
            subprocess.run(["osascript", "-e", f'tell application "{app}" to activate'], check=True)
            break
        except Exception:
            continue
    time.sleep(0.8)

    # take screenshot
    dc.screenshot(filename=str(CAP))

    img = cv2.imread(str(CAP), cv2.IMREAD_COLOR)
    tpl = cv2.imread(str(TPL), cv2.IMREAD_COLOR)
    if img is None or tpl is None:
        print('missing capture/template')
        return 2

    # Focus search on left 40% of the screen
    h,w = img.shape[:2]
    roi = img[:, : int(w*0.42)]

    res = cv2.matchTemplate(roi, tpl, cv2.TM_CCOEFF_NORMED)
    minv, maxv, minloc, maxloc = cv2.minMaxLoc(res)
    print('match', maxv, 'at', maxloc)

    # draw debug
    th, tw = tpl.shape[:2]
    dbg = img.copy()
    x,y = maxloc
    cv2.rectangle(dbg, (x, y), (x+tw, y+th), (0,255,255), 3)
    cv2.imwrite(str(DBG), dbg)

    if maxv < 0.55:
        print('match too low, see', DBG)
        return 3

    # click center
    cx = x + tw//2
    cy = y + th//2
    dc.click(cx, cy)
    time.sleep(0.6)
    print('clicked', cx, cy)
    print('cap', CAP)
    print('dbg', DBG)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

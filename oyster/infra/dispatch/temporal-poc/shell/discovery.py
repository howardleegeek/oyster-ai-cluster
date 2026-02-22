"""
Lightweight discovery utility used by tests to simulate file-content based
keyword matching. It scans a directory tree and counts keyword matches per file.
"""

from typing import List, Dict
import os


def discover(root_dir: str, keywords: List[str]) -> Dict:
    """Scan root_dir for keywords and return results with telemetry stats.

    Returns a dict with keys:
      - results: list of { 'path': str, 'matches': int }
      - stats: { 'scanned_files': int, 'files_with_matches': int, 'total_matches': int }
    """
    if not os.path.isdir(root_dir):
        raise ValueError(f"root_dir must be a directory: {root_dir}")

    scanned_files = 0
    files_with_matches = 0
    total_matches = 0
    files_map: List[Dict] = []

    # Traverse the directory tree and count keyword occurrences per file
    for dirpath, _dirnames, filenames in os.walk(root_dir):
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            scanned_files += 1
            try:
                with open(fpath, "r", errors="ignore") as f:
                    content = f.read()
            except OSError:
                # If a file can't be read for any reason, skip it silently
                continue

            match_count = 0
            if content:
                # naive substring search; counts overlapping occurrences per keyword
                for kw in keywords:
                    if kw:
                        match_count += content.count(kw)

            if match_count > 0:
                files_with_matches += 1
                total_matches += match_count
                files_map.append({"path": fpath, "matches": match_count})

    return {
        "results": files_map,
        "stats": {
            "scanned_files": scanned_files,
            "files_with_matches": files_map.__len__(),
            "total_matches": total_matches,
        },
    }

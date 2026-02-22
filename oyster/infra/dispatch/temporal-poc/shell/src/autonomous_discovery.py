"""Autonomous Discovery
Concrete, minimal utilities to define and run an "autonomous discovery" scan
across a codebase. This scans for simple keyword patterns that indicate places
where autonomous discovery-related logic may live (e.g. discovery patterns,
autonomous components, namespaces, workers, etc.).

The goal is to provide a deterministic, testable way to describe what files and
patterns participate in autonomous discovery without refactoring or adding
external dependencies.
"""

from __future__ import annotations

import os
import re
from typing import Dict, List, Optional

DEFAULT_EXTENSIONS: List[str] = [".py", ".yaml", ".yml", ".json", ".md"]

# Keywords/patterns considered as indicators of autonomous discovery related code
DEFAULT_KEYWORDS: List[Dict[str, str]] = [
    {"name": "autonomous", "regex": r"\bautonomous\b"},
    {"name": "autodiscover", "regex": r"\bautodiscover\b"},
    {"name": "discover", "regex": r"\bdiscover\b"},
    {"name": "discovery", "regex": r"\bdiscovery\b"},
    {"name": "edge_case", "regex": r"edge[-_ ]case"},
    {"name": "namespace", "regex": r"\bnamespace\b"},
    {"name": "worker", "regex": r"\bworker\b"},
]


def _iter_files(root: str, extensions: Optional[set | List[str]] = None) -> List[str]:
    exts: set = set([e.lower() for e in (extensions or DEFAULT_EXTENSIONS)])
    files: List[str] = []
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            if os.path.splitext(fname)[1].lower() in exts:
                files.append(os.path.join(dirpath, fname))
    return files


def discover(
    root: str = ".",
    extensions: Optional[List[str]] = None,
    keywords: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, object]:
    """Scan the given root for lines matching discovery-related patterns.

    Returns a dictionary with a root and a mapping of relative file paths to
    their matching lines. Each match includes the line number, the keyword name,
    and the raw line content.
    """
    exts = set([e.lower() for e in (extensions or DEFAULT_EXTENSIONS)])
    kw = keywords or DEFAULT_KEYWORDS
    # Precompile regexes for speed; guard against missing regex strings
    compiled = []
    for k in kw:
        name = k.get("name")
        regex_str = k.get("regex")
        if isinstance(regex_str, str) and regex_str:
            compiled.append((name, re.compile(regex_str, re.IGNORECASE)))

    files_map: Dict[str, List[Dict[str, object]]] = {}
    result: Dict[str, object] = {"root": root, "files": files_map}
    # Extra diagnostic metadata for debugging and exploration without impacting
    # existing consumers that rely on the primary return shape.
    scanned_files_count: int = 0
    total_matches: int = 0

    for file_path in _iter_files(root, exts):
        scanned_files_count += 1
        rel = os.path.relpath(file_path, root)
        matches: List[Dict[str, object]] = []
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for idx, line in enumerate(f, start=1):
                    for name, regex in compiled:
                        if regex.search(line):
                            matches.append(
                                {
                                    "line": idx,
                                    "keyword": name,
                                    "line_text": line.rstrip("\n"),
                                }
                            )
        except OSError:
            # If a file can't be read for some reason, skip it gracefully
            continue

        if matches:
            files_map[rel] = matches
            total_matches += len(matches)

    # Attach lightweight provenance stats. This is non-breaking for existing
    # callers and can help diagnose issues around discovery coverage.
    result["stats"] = {
        "scanned_files": scanned_files_count,
        "files_with_matches": len(files_map),
        "total_matches": total_matches,
    }

    return result


def report(discovery_result: Dict[str, object]) -> str:
    lines: List[str] = []
    root = discovery_result.get("root")
    files_obj = discovery_result.get("files")
    files: Dict[str, List[Dict[str, object]]] = (
        files_obj if isinstance(files_obj, dict) else {}
    )
    total_matches = (
        sum(len(v) for v in files.values()) if isinstance(files, dict) else 0
    )
    lines.append(f"Autonomous Discovery report for root: {root}")
    lines.append(f"Total files with matches: {len(files)}")
    lines.append(f"Total matches: {total_matches}")
    for path, matches in files.items():
        lines.append(f"- {path} (matches: {len(matches)})")
        for m in matches:
            lines.append(f"  line {m['line']}: [{m['keyword']}] {m['line_text']}")
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    res = discover(root=args.root)
    print(report(res))

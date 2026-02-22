import os
import tempfile
from discovery import discover


def _write(path: str, content: str) -> None:
    with open(path, "w") as f:
        f.write(content)


def test_discover_counts_keywords():
    with tempfile.TemporaryDirectory() as root:
        # Create a simple tree with three files
        os.makedirs(os.path.join(root, "subdir"), exist_ok=True)

        f1 = os.path.join(root, "a.txt")
        f2 = os.path.join(root, "b.txt")
        f3 = os.path.join(root, "subdir", "c.txt")

        _write(f1, "alpha beta gamma")
        _write(f2, "beta delta")
        _write(f3, "epsilon zeta")

        keywords = ["beta", "gamma"]
        res = discover(root, keywords)

        assert isinstance(res, dict)
        assert "stats" in res and "results" in res

        stats = res["stats"]
        # There are 3 files scanned, 2 files with matches (a.txt and b.txt),
        # and total matches = 3 (beta and gamma in a.txt => 2; beta in b.txt => 1)
        assert stats["scanned_files"] == 3
        assert stats["files_with_matches"] == 2
        assert stats["total_matches"] == 3

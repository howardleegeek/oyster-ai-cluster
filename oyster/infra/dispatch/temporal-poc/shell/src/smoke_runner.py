import subprocess
from pathlib import Path


def run_smoke_command(cmd: str = "echo 'hello' > /tmp/test.txt") -> int:
    """
    Execute a deterministic smoke command using a shell.
    Returns the exit code of the command.
    """
    # Use bash -lc to ensure shell redirection works deterministically
    result = subprocess.run(["bash", "-lc", cmd], capture_output=True, text=True)
    return result.returncode


def smoke_result_path(path: str = "/tmp/test.txt") -> Path:
    return Path(path)


def verify_smoke_result(path: str = "/tmp/test.txt", expected: str = "hello") -> bool:
    p = smoke_result_path(path)
    if not p.exists():
        return False
    try:
        content = p.read_text().strip()
        return content == expected
    except Exception:
        return False


def run_smoke_and_verify(cmd: str = "echo 'hello' > /tmp/test.txt") -> bool:
    """
    Convenience: run the smoke command and verify its side-effect.
    Returns True if command succeeded and content is as expected.
    """
    code = run_smoke_command(cmd)
    if code != 0:
        return False
    return verify_smoke_result()

import os

from src.smoke_runner import run_smoke_and_verify


def test_smoke_pipeline_basic_echo():
    # Ensure cleanup before test
    test_path = "/tmp/test.txt"
    if os.path.exists(test_path):
        os.remove(test_path)
    ok = run_smoke_and_verify()
    assert ok, "Smoke test did not complete successfully"
    # Cleanup after test
    if os.path.exists(test_path):
        os.remove(test_path)

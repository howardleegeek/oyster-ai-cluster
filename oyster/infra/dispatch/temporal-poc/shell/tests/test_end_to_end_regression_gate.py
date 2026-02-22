import os

from src.smoke_runner import run_smoke_command, run_smoke_and_verify


def test_end_to_end_regression_gate_cleanup_init_sequence():
    test_path = "/tmp/test.txt"
    # Ensure clean slate
    if os.path.exists(test_path):
        os.remove(test_path)
    # Init step: create a sentinel file
    code = run_smoke_command("echo 'init' > /tmp/test.txt")
    assert code == 0, "Init step failed to create sentinel file"
    # End-to-end gate: run the deterministic smoke test and verify it completes deterministically.
    ok = run_smoke_and_verify()
    assert ok, "End-to-end regression gate failed during smoke step"
    # Cleanup after test
    if os.path.exists(test_path):
        os.remove(test_path)

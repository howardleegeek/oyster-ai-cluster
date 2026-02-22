import subprocess

with open("/tmp/procs.txt", "w") as f:
    out = subprocess.check_output(["ps", "auxww"]).decode("utf-8")
    f.write(out)

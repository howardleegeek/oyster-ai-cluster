import os
import glob

files = glob.glob("*/tasks/*/task.log")
files.sort(key=os.path.getmtime, reverse=True)
with open("recent_logs.txt", "w") as f:
    for file in files[:5]:
        f.write(f"{file}: {os.path.getmtime(file)}\n")

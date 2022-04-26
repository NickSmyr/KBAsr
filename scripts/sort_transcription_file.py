import sys
import re

filename = sys.argv[1]
with open(filename, "r") as f:
    lines = f.readlines()

pat = re.compile("file_(\d+)\.wav")

lines = sorted(lines, key=lambda x: int(pat.search(x).groups()[0]))
with open(filename + "_sorted", "w") as f:
    f.writelines(lines)

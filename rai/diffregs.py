#!/usr/bin/python
import sys, struct, difflib
from rai import *

rai = load_default_rai()

dumpa = open(sys.argv[2]).read()
dumpb = open(sys.argv[3]).read()

space = rai.chip_spaces[sys.argv[1]]

def split(s):
    return s.replace("\n", "\n\r").split("\r")

for addr in range(0, len(dumpa), 4):
    va = struct.unpack("<I", dumpa[addr:addr+4])[0]
    vb = struct.unpack("<I", dumpb[addr:addr+4])[0]

    if va == vb:
        continue

    try:
        reg = space.addrs[addr]

    except KeyError:
        print "-UNK[0x%x]: 0x%x" % (addr, va)
        print "+UNK[0x%x]: 0x%x" % (addr, vb)
        print
        continue
    la = split(reg.value(va))
    lb = split(reg.value(vb))
    s = difflib.unified_diff(la[1:], lb[1:])
    sys.stdout.write("-%s" % la[0])
    sys.stdout.write("+%s" % lb[0])
    for line in s:
        if line and (line[0] not in "+- " or line in ("+++ \n", "--- \n")):
            continue
        sys.stdout.write(line)
    print

#!/usr/bin/python3
import sys, struct, difflib
from rai import *

rai = load_default_rai()

dumpa = open(sys.argv[2], "rb").read()

space = rai.chip_spaces[sys.argv[1]]

for addr in range(0, len(dumpa), 4):
    va = struct.unpack("<I", dumpa[addr:addr+4])[0]

    try:
        reg = space.addrs[addr]

    except KeyError:
        print("UNK[0x%x]: 0x%x" % (addr, va))
        print("")
        continue

    print(reg.value(va))

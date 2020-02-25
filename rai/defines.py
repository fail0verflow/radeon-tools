#!/usr/bin/python3
import sys
from rai import *

rai = load_default_rai()

space = sys.argv[1]

try:
    space = rai.chip_spaces[space]
except KeyError:
    print("Unknown ChipSpace")
    sys.exit(0)

for addr, reg in sorted(space.addrs.items()):
    print("#define %s 0x%x" % (reg.name, addr))

for addr, reg in sorted(space.addrs.items()):
    print("""    dev_info(rdev->dev, "  %s=0x%%08X\\n",
        RREG32(%s));
""" % (reg.name, reg.name))

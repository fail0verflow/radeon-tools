#!/usr/bin/python
import sys
from rai import *
rai = load_default_rai()

space = sys.argv[1]

try:
    space = rai.chip_spaces[space]
except KeyError:
    print "Unknown ChipSpace"
    sys.exit(0)

for addr, reg in sorted(space.addrs.items()):
    print "0x%x %s" % (addr, reg.name)

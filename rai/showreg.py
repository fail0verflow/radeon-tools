#!/usr/bin/python
import sys
from rai import *

rai = load_default_rai()

space = sys.argv[1]
addr = sys.argv[2]
if "<<" in addr:
    a,b = addr.split("<<")
    addr = int(a, 0) << int(b,0)
else:
    addr = int(addr,0)

try:
    space = rai.chip_spaces[space]
except KeyError:
    print "Unknown ChipSpace"
    sys.exit(0)

try:
    reg = space.addrs[addr]
except KeyError:
    print "Unknown Register"
    sys.exit(0)

if len(sys.argv) < 4:
    print reg
else:
    print reg.value(int(sys.argv[3], 0))

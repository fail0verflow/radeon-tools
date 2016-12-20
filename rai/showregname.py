#!/usr/bin/python
import sys
from rai import *
rai = load_default_rai()

reg = sys.argv[1]

for bname, block in rai.blocks.items():
    if reg in block.registers:
        break
else:
    print "Unknown register"
    sys.exit(0)

reg = block.registers[reg]

if len(sys.argv) < 3:
    print reg
else:
    print reg.value(int(sys.argv[2], 0))

#!/usr/bin/python3
import pickle

def it(s, pfx="  "):
    return pfx + str(s).replace("\n", "\n"+pfx)[:-len(pfx)]

class RAI(object):
    def __init__(self):
        self.chip_info = None
        self.chip_spaces = {}
        self.blocks = {}
    def __str__(self):
        return "\n".join([
            "ChipInfo:", it(self.chip_info), "",
            "ChipSpaces:", it(self.chip_spaces), "",
            "Blocks:"] + [
                "* %s\n%s" % (k, it(v))
                for k,v in self.blocks.items()])

class ChipInfo(dict):
    def __str__(self):
        return "\n".join(
            "%s: %s" % (k, ", ".join(map(repr,v)))
            for k,v in self.items())

class ChipSpaces(dict):
    def __str__(self):
        return "\n".join(
            "%s:\n%s\n" % (k, it(v))
            for k,v in sorted(self.items()))

class ChipSpace(dict):
    def __str__(self):
        return "\n".join(
            "%s: %s" % (k, repr(v))
            for k,v in self.items())

class Block(object):
    def __str__(self):
        return "\n".join(
            "- %s: %s" % (k, repr(v))
            for k,v in self.info.items()) + "\n\nRegisters:\n" + "\n".join(
                "%s" % (it(v))
            for k,v in sorted(self.registers.items()))

class Register(object):
    def __str__(self, v = None):
        aa = ",".join("%s:0x%x" % a for a in self.addrs)
        s = "%s (%s) %dbit%s:%s\n" % (self.name, aa, self.width,
                                    (" (%s)" % self.flags
                                     if self.flags else ''),
                                    " 0x%x" % v if v is not None else '')
        for i in self.fields:
            s += it(i.__str__(v))
        return s
    def value(self, v):
        return self.__str__(v)

class Field(object):
    def __str__(self, v = None):
        if self.hi == self.lo:
            b = "%d" % self.hi
        else:
            b = "%d:%d" % (self.hi, self.lo)
        name = self.name
        if self.flags:
            name += "(%s)" % self.flags
        if v is None:
            s = "%6s  %s\n" % (b, name)
        else:
            v = (v >> self.lo) & ((1 << (self.hi - self.lo + 1)) - 1)
            s = "%6s  %s = 0x%x\n" % (b, name, v)
        if self.type in ('INDEX', 'DATA'):
            s += "        - %s: %s\n" % (self.type, self.target)
        elif self.type == 'ALPHA':
            for i in sorted(self.values.items()):
                if v is None or v == i[0]:
                    s += "        - %d: %s\n" % (i[0],
                            i[1].replace("\n", "\n             "))
        return s
    def value(self):
        return self.__str__(v)

class Range(tuple):
    pass

def load_default_rai():
    return pickle.load(open("bonaire.pickle", "rb"))


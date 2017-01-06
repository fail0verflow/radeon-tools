#!/usr/bin/python2
import sys, struct, os.path

packet3 = {
    0x10: "NOP",
    0x11: "SET_BASE",
    0x12: "CLEAR_STATE",
    0x13: "INDEX_BUFFER_SIZE",
    0x15: "DISPATCH_DIRECT",
    0x16: "DISPATCH_INDIRECT",
    0x17: "INDIRECT_BUFFER_END",
    0x1D: "ATOMIC_GDS",
    0x1E: "ATOMIC_MEM",
    0x1F: "OCCLUSION_QUERY",
    0x20: "SET_PREDICATION",
    0x21: "REG_RMW",
    0x22: "COND_EXEC",
    0x23: "PRED_EXEC",
    0x24: "DRAW_INDIRECT",
    0x25: "DRAW_INDEX_INDIRECT",
    0x26: "INDEX_BASE",
    0x27: "DRAW_INDEX_2",
    0x28: "CONTEXT_CONTROL",
    0x2A: "INDEX_TYPE",
    0x2B: "DRAW_INDEX",
    0x2C: "DRAW_INDIRECT_MULTI",
    0x2D: "DRAW_INDEX_AUTO",
    0x2E: "DRAW_INDEX_IMMD",
    0x2F: "NUM_INSTANCES",
    0x30: "DRAW_INDEX_MULTI_AUTO",
    0x32: "INDIRECT_BUFFER_32",
    0x33: "INDIRECT_BUFFER_CONST",
    0x34: "STRMOUT_BUFFER_UPDATE",
    0x35: "DRAW_INDEX_OFFSET_2",
    0x36: "DRAW_PREAMBLE",
    0x37: "WRITE_DATA",
    0x38: "DRAW_INDEX_INDIRECT_MULTI",
    0x39: "MEM_SEMAPHORE",
    0x3A: "MPEG_INDEX",
    0x3B: "COPY_DW",
    0x3C: "WAIT_REG_MEM",
    0x3D: "MEM_WRITE",
    0x3F: "INDIRECT_BUFFER_3F",
    0x40: "COPY_DATA",
    0x41: "CP_DMA",
    0x42: "PFP_SYNC_ME",
    0x43: "SURFACE_SYNC",
    0x44: "ME_INITIALIZE",
    0x45: "COND_WRITE",
    0x46: "EVENT_WRITE",
    0x47: "EVENT_WRITE_EOP",
    0x48: "EVENT_WRITE_EOS",
    0x49: "RELEASE_MEM",
    0x4A: "PREAMBLE_CNTL",
    0x50: "DMA_DATA",
    0x57: "ONE_REG_WRITE",
    0x58: "AQUIRE_MEM",
    0x59: "REWIND",
    0x5E: "LOAD_UCONFIG_REG",
    0x5F: "LOAD_SH_REG",
    0x60: "LOAD_CONFIG_REG",
    0x61: "LOAD_CONTEXT_REG",
    0x68: "SET_CONFIG_REG",
    0x69: "SET_CONTEXT_REG",
    0x6A: "SET_ALU_CONST",
    0x6B: "SET_BOOL_CONST",
    0x6C: "SET_LOOP_CONST",
    0x6D: "SET_RESOURCE",
    0x6E: "SET_SAMPLER",
    0x6F: "SET_CTL_CONST",
    0x73: "SET_CONTEXT_REG_INDIRECT",
    0x76: "SET_SH_REG",
    0x77: "SET_SH_REG_OFFSET",
    0x78: "SET_QUEUE_REG",
    0x79: "SET_UCONFIG_REG",
    0x7D: "SCRATCH_RAM_WRITE",
    0x7E: "SCRATCH_RAM_READ",
    0x80: "LOAD_CONST_RAM",
    0x81: "WRITE_CONST_RAM",
    0x83: "DUMP_CONST_RAM",
    0x84: "INCREMENT_CE_COUNTER",
    0x85: "INCREMENT_DE_COUNTER",
    0x86: "WAIT_ON_CE_COUNTER",
    0x88: "WAIT_ON_DE_COUNTER_DIFF",
    0x8B: "SWITCH_BUFFER",
}

def s16(d):
    return d - 0x10000 if d >= 0x8000 else d

def loc(off):
    return labels.get(off, "0x%x"%off)

lastadd = None

def addlabel(off):
    global labels
    if off not in labels:
        labels[off] = True

def dis(off, inst):
    global lastadd
    # .... .... .... .... .... .... .... ....
    #        ss ssdd dd
    rs = (inst >> 22) & 0xf
    rd = (inst >> 18) & 0xf
    rx = (inst >> 14) & 0xf

    imm = inst & 0xffff
    a = (inst >> 26)
    b = (inst >> 16) & 0x3
    tgt = ["", "reg", "mem", "unk"][b]
    c = inst & 0x3fff

    opc_r = opc_i = [
        # 32-bit instructions
        None, "add", "sub", None,
        "lsl", "lsr", None, None,
        None, "and", "orr", "eor",
        # Set to 1 if cond is true
        "seteq", "setne", "setgt", "setge",

        # Multiply (16x16 bit?)
        "mul",

        # Double (64-bit) versions
        "addd", "subd", None,
        "lsld", "lsrd", None, None,
        None, "andd", "orrd", "eord",
        "seteqd", "setned", "setgtd", "setged",
    ]
    if a == 0:
        return "nop"
    elif a == 0x1f:
        # Register-register instructions
        if c == 1 and rd == 0:
            # Register-register move (actually add with r0 which is always 0)
            return "mov r%d, r%d" % (rx, rs)
        if c < len(opc_r) and opc_r[c] is not None:
            return "%s r%d, r%d, r%d" % (opc_r[c], rx, rs, rd)
        else:
            return "  dw 0x%x  #rs=%d rd=%d rx=%d a=0x%x c=0x%x" % (inst, rs, rd, rx, a, c)
    elif (a,b) == (0x6,0):
        # Logical shift right and AND
        return "lsra r%d, r%d, #%d, #0x%x" % (rd, rs, imm&0x1f, imm>>5)
    elif (a,b) == (0x7,0):
        # AND with mask (all-1 bits surrounding shifted imm)
        val = (0xffffffff ^ ((0x7ff ^ (imm>>5)) << (imm&0x1f))) & 0xffffffff
        return "and r%d, r%d, #0x%x" % (rd, rs, val)
    elif (a,b) == (0x8,0):
        # OR with shifted imm
        if rs == 0:
            return "mov r%d, #0x%x" % (rd, (imm>>5) << (imm&0x1f))
        else:
            return "orr r%d, r%d, #0x%x" % (rd, rs, (imm>>5) << (imm&0x1f))
    elif (a,b) == (0x16,0):
        # See lsra
        return "lsrad r%d, r%d, #%d, #0x%x" % (rd, rs, imm&0x3f, imm>>6)
    elif (a,b) == (0x17,0):
        # See AND with mask above
        val = (0xffffffffffffffff ^ ((0x3ff ^ (imm>>6)) << (imm&0x3f))) & 0xffffffffffffffff
        return "andd r%d, r%d, #0x%x" % (rd, rs, val)
    elif (a,b) == (0x18,0):
        # OR with shifted imm
        if rs == 0:
            return "mov r%d, #0x%x" % (rd, (imm>>6) << (imm&0x3f))
        else:
            return "orrd r%d, r%d, #0x%x" % (rd, rs, (imm>>6) << (imm&0x3f))
    elif b == 0 and a < len(opc_i) and opc_i[a] is not None:
        # Register-immediate instructions
        if a == 1:
            lastadd = (rd, imm)
        if a == 1 and rs == 0:
            return "mov r%d, #0x%x" % (rd, imm)
        elif opc_i[a][:2] == "ls":
            return "%s r%d, r%d, #%d" % (opc_i[a], rd, rs, imm)
        else:
            return "%s r%d, r%d, #0x%x" % (opc_i[a], rd, rs, imm)
    elif b == 1 and a in (0x1, 0x2, 0x11, 0x12):
        # Register-immediate instructions (sign-extended arg)
        imm = s16(imm)
        if a == 1 and rs == 0:
            return "mov r%d, #0x%x" % (rd, s16(imm))
        elif imm < 0:
            return "%s r%d, r%d, #-0x%x" % (opc_i[a], rd, rs, -imm)
        else:
            return "%s r%d, r%d, #0x%x" % (opc_i[a], rd, rs, imm)
    elif b == 1 and a in (0x9, 0xa, 0xb):
        # Register-immediate logical instructions (sign-extended arg)
        imm = s16(imm)
        return "%s r%d, r%d, #0x%x" % (opc_i[a], rd, rs, s16(imm) & 0xffffffff)
    elif b == 1 and a in (0x19, 0x1a, 0x1b):
        # Register-immediate 64-bit logical instructions (sign-extended arg)
        imm = s16(imm)
        return "%s r%d, r%d, #0x%x" % (opc_i[a], rd, rs, s16(imm) & 0xffffffffffffffff)
    elif (a,b,rs,rd) == (0x20, 0,0,0):
        # Branch
        addlabel(imm)
        return "b %s  " % (loc(imm))
    elif (a,b,rd,imm) == (0x21, 0,0,0):
        # Branch register
        if lastadd is not None and lastadd[0] == rs:
            labels[lastadd[1]] = "_jmptab_0x%x" % lastadd[1]
        return "b r%d" % (rs)
    elif (a,b,rs,rd,imm) == (0x22, 0,0,0,0):
        # Branch jumptable
        return "btab\n"
    elif (a,b,rs,rd) == (0x23, 0,0,0):
        # Branch and link (call)
        addlabel(imm)
        return "bl %s  " % (loc(imm))
    elif (a,b,rs,rd,imm) == (0x24, 0,0,0,0):
        # Return
        return "ret\n"
    elif (a,b,rd) == (0x25, 0,0):
        # Compare and Branch if Zero
        addlabel(s16(imm)+off)
        return "cbz r%d, %s" % (rs, loc(s16(imm)+off))
    elif (a,b,rd) == (0x26, 0,0):
        # Compare and Branch if Nonzero
        addlabel(s16(imm)+off)
        return "cbnz r%d, %s" % (rs, loc(s16(imm)+off))
    elif (a,rs) == (0x30,0):
        # Load immediate (other half may be 0000 or ffff)
        if b == 0:
            return "mov r%d, #0x%x" % (rd, imm)
        elif b == 1:
            return "mov r%d, #0x%x" % (rd, imm | 0xffff0000)
        elif b == 2:
            return "mov r%d, #0x%x" % (rd, imm<<16)
        elif b == 3:
            return "mov r%d, #0x%x" % (rd, (imm<<16) | 0xffff)
    elif 0x31 <= a <= 0x35:
        # Load/Store (word, double)
        # stm = store multiple (ctr register = num times) for streaming data
        op = ["ldw", "ldd", "stw", "std", "stm"][a - 0x31]
        if op[:2] == "st":
            return "%s r%d, %s[r%d, #0x%x]" % (op, rs, tgt, rd, imm)
        else:
            return "%s r%d, %s[r%d, #0x%x]" % (op, rd, tgt, rs, imm)
    elif a == 0x36:
        # Store immediate
        return "stw #0x%x, %s[r%d, #0x%x]" % (rs, tgt, rd, imm)
    elif (a,b,rs,imm) == (0x37, 2, 0, 0):
        # Move from counter
        return "mov r%d, ctr" % rd
    elif (a,b,rd,imm) == (0x37, 3, 0, 0):
        # Move to counter
        return "mov ctr, r%d" % rs
    elif (a,b,rd,imm) == (0x37, 1, 0, 0):
        # Pop stack
        return "push r%d" % rs
    elif (a,b,rs,imm) == (0x37, 0, 0, 0):
        # Pop stack
        return "pop r%d" % rd

    return "  dw 0x%x  #rs=%d rd=%d a=0x%x b=0x%x, imm=0x%x" % (inst, rs, rd, a, b, imm)

def jmptab(val):
    hi = val >> 16
    lo = val & 0xffff
    if hi in packet3:
        return "[%s] = %s" % (packet3[hi], loc(lo))
    else:
        return "[0x%x] = %s" % (hi, loc(lo))

FMT = ">I"

with open(sys.argv[1], "r") as fd:
    base = os.path.split(sys.argv[1])[-1]
    if base.lower() == base:
        fd.read(0x100)
        FMT = "<I"
    data = fd.read()

total_size = len(data)
code_size = total_size & ~0xfff
jmptab_size = total_size & 0xfff

lpref = "start"
lct = 0
labels = {}
jtab = set()
for i in range(code_size, total_size, 4):
    val = struct.unpack(FMT, data[i:i+4])[0]
    hi = val >> 16
    lo = val & 0xffff
    labels[lo] = packet3.get(hi, "PKT_0x%x"%hi)
    jtab.add(lo)

# first pass, find labels
for i in range(0, total_size, 4):
    inst = struct.unpack(FMT, data[i:i+4])[0]
    if i < code_size:
        dis(i/4, inst)

# second pass, assign labels
for i in range(0, total_size, 4):
    inst = struct.unpack(FMT, data[i:i+4])[0]
    if i/4 in jtab:
        lct = 0
        lpref = labels[i/4]
    if i/4 in labels and labels[i/4] == True:
        labels[i/4] = "_%s_%d" % (lpref, lct)
        lct += 1
    if i < code_size:
        dis(i/4, inst)

# third pass, disassemble
for i in range(0, total_size, 4):
    inst = struct.unpack(FMT, data[i:i+4])[0]
    if i/4 in labels:
        if i/4 in jtab:
            print
        print labels[i/4] + ":"
    if i < code_size:
        print "    %s" % (dis(i/4, inst))
    else:
        print "#J%s" % (jmptab(inst))

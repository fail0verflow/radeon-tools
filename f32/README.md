## F32 disassembler

This is a disassembler for the Radeon "microcode" processor, which seems to be
internally called F32 (even though it's a 64-bit processor). This disassembler
can handle firmware for CE, ME, MEC, PFP, RLC in the CI (Sea Islands) GPU series
and probably others. SDMA uses a related but incompatible variant, so will not
work.

The instruction syntax follows ARM mnemonics where practical. Read the code to
understand how some of the more exotic encodings work (e.g. 64-bit AND masks)
and what the non-ARM mnemonics mean.

Note that some registers are special:

* r0 is always zero
* r1 is a magic register that pulls dwords off of the command queue when read
* r2 contains the current command header, and the processor knows how to decode
  the packet header format. When the `btab` instruction is executed, it looks up
  the packet in an out of band jump table (at the end of the firmware) and jumps
  to that address.

### Usage

```shell
$ python f32dis.py /lib/firmware/radeon/LIVERPOOL_pfp.bin
   0  c4340025 | ldw r13, [r0, #0x25]
   1  c438001e | ldw r14, [r0, #0x1e]
   2  9740000b | cbz r13, 0xd
   3  9780000f | cbz r14, 0x12
   4  c42f03e7 | ldw r11, unk[r0, #0x3e7]
[...]
```

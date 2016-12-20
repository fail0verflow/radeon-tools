## Radeon RAI tools

These scripts will parse an AMD RAI format register description file and then
allow you to use it to inspect register offsets and dumps.

### Usage

You need PLY installed (`pip install ply`) for this to work.

Obtain a RAI file (e.g. bonaire.rai) and parse it into pickle format:

```shell
$ python raiparse.py bonaire.rai bonaire.pickle
```

Then you can explain individual registers by offset or name:

```shell
$ python showreg.py GpuF0Reg '0xb02<<2' 
- or -
$ python showregname.py HDP_NONSURFACE_INFO
HDP_NONSURFACE_INFO (GpuF0Reg:0x2c08,GpuF1Reg:0x2c08) 32bit:
       0  NONSURF_ADDR_TYPE
          - 0: physical address with no translation. 
          - 1: virtual address, requires page table translation. 
     4:1  NONSURF_ARRAY_MODE
          - 0: ARRAY_LINEAR_GENERAL: Unaligned linear array 
          - 1: ARRAY_LINEAR_ALIGNED: Aligned linear array
[...]
```

Or dump the entire address list:

```shell
$ python addresslist.py GpuF0Reg
0x0 MM_INDEX
0x4 MM_DATA
0x18 MM_INDEX_HI
0x30 PCIE_INDEX_2
0x34 PCIE_DATA_2
0x38 PCIE_INDEX
0x3c PCIE_DATA
0x9c BIF_RFE_SNOOP_REG
0x180 CC_TST_EFUSE0_RM
0x184 CC_TST_EFUSE1_MISC
[...]
```

Or get a bunch of C-style #defines and debug print calls, suitable for kernel
driver debugging:

```shell
$ python defines.py GpuF0Reg
#define MM_INDEX 0x0
#define MM_DATA 0x4
#define MM_INDEX_HI 0x18
[...]
    dev_info(rdev->dev, "  CP_HYP_REG_PRIV_LEVEL_D=0x%08X\n",
        RREG32(CP_HYP_REG_PRIV_LEVEL_D));

    dev_info(rdev->dev, "  SQ_HV_VMID_CTRL=0x%08X\n",
        RREG32(SQ_HV_VMID_CTRL));

    dev_info(rdev->dev, "  GFX_PIPE_PRIORITY=0x%08X\n",
        RREG32(GFX_PIPE_PRIORITY));
```

You can also dump the entire database:

```shell
$ python dumpmap.py GpuF0Reg
ChipInfo:
  RELEASE: 'Chip Spec 0.28'
  ASIC_VENDOR_ID: 4098
  CHIP_NAME: 'bonaire'
  ASIC_DEVICE_ID: 26144, 26657, 26146, 26147, 26148, 26149, 26150, 26151, 26152, 26153, 26154, 26155, 26156, 26157, 26158, 26159, 26160, 26161, 26162, 26163, 26164, 26165, 26166, 26167, 26168, 26169, 26170, 26171, 26172, 26173, 26174, 26175
  DESCRIPTION: 'R8xx GPU Chi

ChipSpaces:
  AudioPcie:
    DESCRIPTION: 'Audio Function PCI Express Configuration Space'
[...]
```

If you take some live register dumps from the hardware, you can decode them
into readable form:

```shell
$ python dumpregs.py GpuF0Reg examples/regs_linux.dump
MM_INDEX (GpuBlockIO:0x0,GpuF0Reg:0x0,GpuF1Reg:0x0) 32bit: 0x6998
    30:0  MM_OFFSET = 0x6998
      31  MM_APER = 0x0
          - 0: Register Aperture 
[...]
```

And diff two dumps:

```diff
$ python diffregs.py GpuF0Reg examples/regs_fbsd.dump examples/regs_linux.dump
-MM_INDEX (GpuBlockIO:0x0,GpuF0Reg:0x0,GpuF1Reg:0x0) 32bit: 0x6610
+MM_INDEX (GpuBlockIO:0x0,GpuF0Reg:0x0,GpuF1Reg:0x0) 32bit: 0x6998
-    30:0  MM_OFFSET = 0x6610
+    30:0  MM_OFFSET = 0x6998
       31  MM_APER = 0x0
           - 0: Register Aperture 
 
-MM_DATA (GpuBlockIO:0x4,GpuF0Reg:0x4,GpuF1Reg:0x4) 32bit: 0x87800
+MM_DATA (GpuBlockIO:0x4,GpuF0Reg:0x4,GpuF1Reg:0x4) 32bit: 0x4000200
-    31:0  MM_DATA = 0x87800
+    31:0  MM_DATA = 0x4000200
[...]
```

These examples all load `bonaire.pickle` by default. You can change that in
`rai.py`.

## Firmware resizing tool

This is a simple tool to adjust the size of GPU firmware. It only works with
new-style (lowercase) firmware files. You can use it to expand or reduce the
size of a firmware image to adapt it to a different chip. Obviously, this only
works if the actual contents of the image are small enough to fit in the target
size.

### Usage

To convert Bonaire firmware to work on Liverpool:

```shell
python2 resize_firmware.py bonaire_pfp.bin 17024 liverpool_pfp.bin
python2 resize_firmware.py bonaire_me.bin 17024 liverpool_me.bin
cp bonaire_ce.bin liverpool_ce.bin  # already the correct size
```

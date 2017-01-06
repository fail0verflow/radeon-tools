import zlib, sys, struct 

want_size = int(sys.argv[2]) - 0x100
want_blob_sz = want_size & ~0xfff
want_jt_sz = want_size & 0xfff

print "want: 0x%x / 0x%x / 0x%x (total, blob, jt)" % (want_size, want_blob_sz, want_jt_sz)

with open(sys.argv[1], "rb") as fd:
    hdr = fd.read(0x20)
    sub_hdr = fd.read(0xe0)
    ucode = fd.read()

total_size, p1, ucode_size = struct.unpack("<I16sI8x", hdr)
ucode_feature_version = struct.unpack("<I", sub_hdr[:4])[0]
assert total_size == len(ucode) + 0x100
assert ucode_size == total_size - 0x100

ucode_blob_sz = ucode_size & ~0xfff
ucode_jt_sz = ucode_size & 0xfff
ucode_blob = ucode[:ucode_blob_sz]
ucode_jt = ucode[ucode_blob_sz:]

print "have: 0x%x / 0x%x / 0x%x (total, blob, jt)" % (ucode_size, ucode_blob_sz, ucode_jt_sz)

if ucode_blob_sz < want_blob_sz:
    ucode_blob += "\x00" * (want_blob_sz - ucode_blob_sz)
elif ucode_blob_sz > want_blob_sz:
    ucode_blob = ucode_blob[:want_blob_sz]

if ucode_jt_sz < want_jt_sz:
    ucode_jt += ucode_jt[-4:] * ((want_jt_sz - ucode_jt_sz) / 4)
elif ucode_jt_sz > want_jt_sz:
    ucode_jt = ucode_jt[:want_jt_sz]

sub_hdr = struct.pack("<III212x", ucode_feature_version, want_blob_sz / 4, want_jt_sz / 4)
payload = sub_hdr + ucode_blob + ucode_jt
assert len(payload) == want_size + 0xe0
crc = zlib.crc32(payload)

hdr = struct.pack("<I16sIII", len(payload) + 0x20, p1, want_size, 0x100, crc & 0xffffffff)

with open(sys.argv[3], "wb") as fd:
    fd.write(hdr)
    fd.write(payload)

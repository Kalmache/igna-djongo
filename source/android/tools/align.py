# Recopie l'APK en alignant sur 4 octets les fichiers non compressés (comme zipalign),
# et ajoute classes.dex. Usage : python3 align.py <entrée.apk> <classes.dex> <sortie.apk>
#                     ou : python3 align.py --check <fichier.apk>
import struct, sys, zipfile


def check(path):
    bad = []
    with open(path, "rb") as f, zipfile.ZipFile(path) as z:
        for i in z.infolist():
            if i.compress_type != zipfile.ZIP_STORED:
                continue
            f.seek(i.header_offset)
            h = f.read(30)
            n, e = struct.unpack("<HH", h[26:30])
            if (i.header_offset + 30 + n + e) % 4:
                bad.append(i.filename)
    print("alignement OK" if not bad else "NON aligné : %s" % bad)
    return not bad


if sys.argv[1] == "--check":
    sys.exit(0 if check(sys.argv[2]) else 1)

src, dex, out = sys.argv[1:4]
with zipfile.ZipFile(src) as zin, open(out, "wb") as raw:
    zout = zipfile.ZipFile(raw, "w")
    items = [(i, zin.read(i)) for i in zin.infolist()]
    items.append((zipfile.ZipInfo("classes.dex", (2008, 1, 1, 0, 0, 0)), open(dex, "rb").read()))
    for info, data in items:
        zi = zipfile.ZipInfo(info.filename, info.date_time)
        zi.external_attr = 0o644 << 16
        stored = info.filename == "resources.arsc" or info.filename.endswith(".png") or info.compress_type == zipfile.ZIP_STORED
        zi.compress_type = zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED
        if stored:
            pos = raw.tell() + 30 + len(info.filename.encode())
            zi.extra = b"\0" * ((4 - pos % 4) % 4)
        zout.writestr(zi, data)
    zout.close()
check(out)

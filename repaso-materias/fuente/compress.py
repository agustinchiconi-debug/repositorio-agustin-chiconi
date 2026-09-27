"""Comprime las imágenes de img/ (guarda los originales en img_orig/ la primera vez).
- Figuras y tablas (PNG): máx. 1100 px de ancho, paleta de 64 colores.
- Fotos (JPG): máx. 1000 px de ancho, calidad 72.
"""
import os, shutil
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
IMG, ORIG = os.path.join(HERE, "img"), os.path.join(HERE, "img_orig")
if not os.path.isdir(ORIG):
    shutil.copytree(IMG, ORIG)

antes = despues = 0
for f in sorted(os.listdir(ORIG)):
    src, dst = os.path.join(ORIG, f), os.path.join(IMG, f)
    antes += os.path.getsize(src)
    im = Image.open(src)
    if f.lower().endswith(".png"):
        im = im.convert("RGB")
        if im.width > 1100:
            im = im.resize((1100, round(im.height * 1100 / im.width)), Image.LANCZOS)
        im = im.quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        im.save(dst, optimize=True)
    else:
        im = im.convert("RGB")
        if im.width > 1000:
            im = im.resize((1000, round(im.height * 1000 / im.width)), Image.LANCZOS)
        im.save(dst, quality=72, optimize=True, progressive=True)
    despues += os.path.getsize(dst)
print(f"imágenes: {antes/1024:.0f} KB -> {despues/1024:.0f} KB ({100*despues/antes:.0f} %)")

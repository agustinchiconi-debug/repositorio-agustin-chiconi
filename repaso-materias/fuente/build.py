"""Arma el HTML autocontenido (imágenes en base64) a partir de index.html + img/.
Escribe la versión final en el Escritorio y una copia en el scratchpad para el visor."""
import base64, os, re, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
DST = r"C:\Users\pc\Desktop\Facultad\Repaso de materias.html"
VIEW = os.path.join(os.path.dirname(HERE), "Repaso de materias.html")

src = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()


def nbsp_miles(txt):
    """Separador de miles sin corte de línea: "4 700" pasa a "4\u00a0700".
    Solo toca el texto: no entra en etiquetas, MathML, script ni style."""
    prot = re.compile(r"(<math\b.*?</math>|<script\b.*?</script>|<style\b.*?</style>|<[^>]+>)", re.S)
    num = re.compile(r"(?<![\d,.])\d{1,3}(?:[ \u202f]\d{3})+(?!\d)")
    parts = prot.split(txt)
    for k in range(0, len(parts), 2):
        parts[k] = num.sub(lambda m: re.sub(r"[ \u202f]", "\u00a0", m.group(0)), parts[k])
    return "".join(parts)


src = nbsp_miles(src)

def embed(m):
    p = os.path.join(HERE, m.group(1))
    mime = "image/jpeg" if p.lower().endswith((".jpg", ".jpeg")) else "image/png"
    return 'src="data:%s;base64,%s"' % (mime, base64.b64encode(open(p, "rb").read()).decode())

body = re.sub(r'src="(img/[^"]+)"', embed, src)
title = re.search(r"<title>.*?</title>", body, re.S).group(0)
body = body.replace(title, "", 1)
head = []
for pat in [r'<meta name="description"[^>]*>', r'<link rel="preconnect"[^>]*>', r'<link rel="stylesheet"[^>]*>', r"<style>.*?</style>"]:
    for m in re.findall(pat, body, re.S):
        head.append(m)
        body = body.replace(m, "", 1)
reset = ('<style>html{color-scheme:light}:root{padding-top:env(safe-area-inset-top,0px);'
         'padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}'
         '[hidden]{display:none!important}</style>')
out = ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
       + title + "\n" + reset + "\n" + "\n".join(head) + "\n</head>\n<body>\n" + body.strip() + "\n</body>\n</html>\n")
VAULT = r"G:\Mi unidad\Cerebro 2.0\1.2 INGENIERÍA\1.2.5 FACULTAD\Repaso de materias.html"
open(DST, "w", encoding="utf-8").write(out)
shutil.copyfile(DST, VIEW)
shutil.copyfile(DST, VAULT)
# respaldo de la fuente editable en el vault (el scratchpad se pierde entre sesiones)
SRC_BAK = os.path.join(os.path.dirname(VAULT), "_fuente Repaso de materias")
if os.path.abspath(HERE) != os.path.abspath(SRC_BAK):
    os.makedirs(SRC_BAK, exist_ok=True)
    for f in ("index.html", "build.py"):
        shutil.copyfile(os.path.join(HERE, f), os.path.join(SRC_BAK, f))
    shutil.copytree(os.path.join(HERE, "img"), os.path.join(SRC_BAK, "img"), dirs_exist_ok=True)
print("OK", os.path.getsize(DST) // 1024, "KB ·", out.count("data:image"), "imágenes")

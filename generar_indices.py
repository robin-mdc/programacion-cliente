# Robin Jack (2026)

"""Genera los index.html (raíz, temas y subcarpetas) y corrige el <head> de cada ejercicio.

Se ejecuta solo en GitHub Actions en cada push (.github/workflows/pages.yml),
pero también se puede ejecutar a mano para verlo en local: python generar_indices.py

Si un index.html contiene <!-- manual --> no se sobrescribe.
"""
import html
import re
from pathlib import Path

RAIZ = Path(__file__).parent
AUTOR = "Robin Jack"
ICONO = "assets/icons/smiley.png"
ESTILO = "style.css"
MARCA_MANUAL = "<!-- manual -->"

# Carpetas extras a mostrar además de tema_X:
# "carpeta": ("Título tarjeta", "Descripción")
EXTRAS = {
    "en_clase": ("Ejercicios en Clase", "Actividades realizadas con Yil en clase :^)"),
}

# Descripción de cada carpeta (ruta relativa a la raíz, con /)
DESCRIPCIONES = {
    "tema_1": "Sintaxis del lenguaje JavaScript",
    "tema_2": "Tema 2",
    "tema_3": "Tema 3",
}

# Título de cada grupo de ejercicios según el prefijo del archivo.
# Se busca primero "carpeta/prefijo" y luego "prefijo".
GRUPOS = {
    "tema_1/propuestos": "Ejercicios propuestos Pagina 35",
    "propuestos": "Ejercicios propuestos",
    "actividad": "Actividades",
    "otros": "Ejercicios",
}

# Carpetas que nunca se recorren
IGNORAR = {"assets"}


def natural(texto):
    # para orden natural 1-10
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", str(texto))]


def esc(texto):
    return html.escape(str(texto))


def bonito(nombre):
    return nombre.replace("_", " ").capitalize()


def ruta(carpeta):
    return carpeta.relative_to(RAIZ).as_posix()


def prefijo_raiz(carpeta):
    # "../" tantas veces como niveles hay hasta la raíz
    return "../" * len(carpeta.relative_to(RAIZ).parts)


def numero_tema(carpeta):
    m = re.fullmatch(r"tema_(\d+)", carpeta.relative_to(RAIZ).parts[0])
    return int(m.group(1)) if m else None


def subcarpetas(carpeta):
    return sorted(
        (d for d in carpeta.iterdir()
         if d.is_dir() and d.name not in IGNORAR and not d.name.startswith((".", "_"))),
        key=natural,
    )


def carpetas_principales():
    temas = [d for d in subcarpetas(RAIZ) if re.fullmatch(r"tema_\d+", d.name)]
    extras = [RAIZ / c for c in EXTRAS if (RAIZ / c).is_dir()]
    return temas + extras


def head(titulo, pre, descripcion):
    return f"""<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(titulo)}</title>
  <link rel="icon" href="{pre}{ICONO}">
  <link rel="stylesheet" href="{pre}{ESTILO}">
  <meta name="description" content="{esc(descripcion)}">
  <meta name="author" content="{AUTOR}">
</head>"""


def pagina_raiz():
    tarjetas = []
    for d in carpetas_principales():
        n = numero_tema(d)
        if n is not None:
            tarjetas.append((f"{n:02d}", f"Tema {n}", DESCRIPCIONES.get(d.name, ""), d.name))
        else:
            titulo, desc = EXTRAS[d.name]
            tarjetas.append(("★", titulo, desc, d.name))

    cards = "\n".join(
        f"""    <a class="card" href="{esc(c)}/index.html">
      <span class="num">{esc(num)}</span>
      <h2>{esc(tit)}</h2>
      <p>{esc(desc)}</p>
    </a>"""
        for num, tit, desc, c in tarjetas
    )
    return f"""<!DOCTYPE html>
<html lang="es">
{head("DWEC · Desarrollo Web en Entorno Cliente", "", "Ejercicios de DWEC")}
<body>
  <header>
    <h1>Desarrollo Web en Entorno Cliente</h1>
    <p>2º DAW · Robin Jack Schilmöller</p>
  </header>

  <main class="grid">
{cards}
  </main>

  <footer>Curso 2026/27</footer>
</body>
</html>
"""


def nombre_carpeta(carpeta):
    # "Tema 3 · Practica almacenamiento"
    partes = carpeta.relative_to(RAIZ).parts
    n = numero_tema(carpeta)
    primero = f"Tema {n}" if n is not None else EXTRAS.get(partes[0], (bonito(partes[0]),))[0]
    return " · ".join([primero] + [bonito(p) for p in partes[1:]])


def pagina_carpeta(carpeta):
    archivos = sorted(
        (f for f in carpeta.glob("*.html") if f.name != "index.html"),
        key=lambda f: natural(f.name),
    )
    grupos = {}  # prefijo -> [(etiqueta, href, clase)]
    for f in archivos:
        m = re.fullmatch(r"(.+)_(\d+)", f.stem)
        if m:
            prefijo, etiqueta = m.group(1), f"Actividad {int(m.group(2))}"
        else:
            prefijo, etiqueta = "otros", f.stem.replace("_", " ")
        grupos.setdefault(prefijo, []).append((etiqueta, f.name, "archivo"))

    subs = subcarpetas(carpeta)
    if subs:
        grupos["carpetas"] = [(d.name.replace("_", " "), f"{d.name}/index.html", "carpeta") for d in subs]

    bloques = []
    for prefijo, items in grupos.items():
        titulo = GRUPOS.get(f"{ruta(carpeta)}/{prefijo}") or GRUPOS.get(prefijo) or bonito(prefijo)
        lis = "\n".join(
            f'      <li><a class="{c}" href="{esc(h)}">{esc(e)}</a></li>' for e, h, c in items
        )
        bloques.append(f'    <h3>{esc(titulo)}</h3>\n    <ul class="list">\n{lis}\n    </ul>')

    nombre = nombre_carpeta(carpeta)
    desc = DESCRIPCIONES.get(ruta(carpeta), "")
    return f"""<!DOCTYPE html>
<html lang="es">
{head(f"{nombre} · DWEC", prefijo_raiz(carpeta), desc or nombre)}
<body>
  <header>
    <a class="back" href="../index.html">← Volver</a>
    <h1>{esc(nombre)}</h1>
    <p>{esc(desc)}</p>
  </header>

  <main>
{chr(10).join(bloques)}
  </main>
</body>
</html>
"""


def arreglar_head(archivo):
    """Corrige rutas de icono/estilo según la profundidad y añade las etiquetas que falten."""
    texto = archivo.read_text(encoding="utf-8")
    m = re.search(r"<head>(.*?)</head>", texto, re.S | re.I)
    if not m:
        return False
    original = cabeza = m.group(1)
    pre = prefijo_raiz(archivo.parent)

    cabeza = re.sub(r'(<link[^>]*rel="icon"[^>]*href=")[^"]*(")', rf"\g<1>{pre}{ICONO}\g<2>", cabeza)
    cabeza = re.sub(r'(<link[^>]*href=")[^"]*style\.css(")', rf"\g<1>{pre}{ESTILO}\g<2>", cabeza)

    # placeholder "tnx" de plantilla.html -> número de tema
    n = numero_tema(archivo.parent)
    if n is not None:
        cabeza = re.sub(r"(<title>.*?)tnx", rf"\g<1>{n}", cabeza)
        cabeza = re.sub(r'(<meta name="description"[^>]*?)tnx', rf"\g<1>{n}", cabeza)

    faltan = []
    if "charset" not in cabeza:
        faltan.append('<meta charset="UTF-8">')
    if 'name="viewport"' not in cabeza:
        faltan.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    if 'rel="icon"' not in cabeza:
        faltan.append(f'<link rel="icon" href="{pre}{ICONO}">')
    if "style.css" not in cabeza:
        faltan.append(f'<link rel="stylesheet" href="{pre}{ESTILO}">')
    if 'name="author"' not in cabeza:
        faltan.append(f'<meta name="author" content="{AUTOR}">')
    if faltan:
        cabeza = cabeza.rstrip() + "".join(f"\n    {t}" for t in faltan) + "\n"

    if cabeza == original:
        return False
    archivo.write_text(texto[:m.start(1)] + cabeza + texto[m.end(1):], encoding="utf-8")
    return True


def escribir_index(carpeta, contenido):
    destino = carpeta / "index.html"
    if destino.exists() and MARCA_MANUAL in destino.read_text(encoding="utf-8"):
        print(f"· {ruta(destino)} (manual, no se toca)")
        return
    destino.write_text(contenido, encoding="utf-8")
    print(f"✔ {ruta(destino)}")


def recorrer(carpeta):
    escribir_index(carpeta, pagina_carpeta(carpeta))
    for f in sorted(carpeta.glob("*.html"), key=natural):
        if f.name != "index.html" and arreglar_head(f):
            print(f"  ✎ head de {ruta(f)}")
    for d in subcarpetas(carpeta):
        recorrer(d)


def main():
    escribir_index(RAIZ, pagina_raiz())
    for d in carpetas_principales():
        recorrer(d)


if __name__ == "__main__":
    main()

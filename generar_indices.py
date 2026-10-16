# Robin Jack (2026)

"""Genera index.html de la raíz y de cada tema. Ejecutar antes de cada commit."""
import html
import re
from pathlib import Path

RAIZ = Path(__file__).parent

# Carpetas extras a mostrar además de tema_X:
# "carpeta": ("Título tarjeta", "Descripción")
EXTRAS = {
    "en_clase": ("Ejercicios en Clase", "Actividades realizadas en clase con Yil :)")
}

# Descripción de cada tema
DESCRIPCIONES = {
    "tema_1": "tema 1",
    "tema_2": "tema 2",
}

# Título de cada grupo de ejercicios según el prefijo del archivo
GRUPOS = {
    "propuestos": "Ejercicios propuestos",
}


def natural(texto):
    # para orden natural 1-10
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", str(texto))]


def esc(texto):
    return html.escape(str(texto))


def pagina_raiz():
    tarjetas = []
    temas = sorted(
        (d for d in RAIZ.iterdir() if d.is_dir() and re.fullmatch(r"tema_\d+", d.name)),
        key=natural,
    )
    for d in temas:
        n = re.search(r"\d+", d.name).group()
        tarjetas.append((f"{int(n):02d}", f"Tema {int(n)}", DESCRIPCIONES.get(d.name, ""), d.name))
    for carpeta, (titulo, desc) in EXTRAS.items():
        if (RAIZ / carpeta).is_dir():
            tarjetas.append(("★", titulo, desc, carpeta))

    cards = "\n".join(
        f"""        <a class="card" href="{esc(c)}/index.html">
            <span class="num">{esc(num)}</span>
            <h2>{esc(tit)}</h2>
            <p>{esc(desc)}</p>
        </a>"""
        for num, tit, desc, c in tarjetas
    )
    return f"""<!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>DWEC · Desarrollo Web en Entorno Cliente</title>
            <link rel="icon" href="assets/icons/smiley.png">
            <meta name="description" content="Ejercicios de DWEC">
            <meta name="author" content="Robin Jack">
            <link rel="stylesheet" href="style.css">
        </head>
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


def titulo_de(archivo):
    m = re.search(r"<title>(.*?)</title>", archivo.read_text(encoding="utf-8"), re.S)
    return m.group(1).strip() if m else archivo.stem.replace("_", " ").capitalize()


def pagina_tema(carpeta):
    archivos = sorted(
        (f for f in carpeta.glob("*.html") if f.name != "index.html"),
        key=lambda f: natural(f.name),
    )
    grupos = {}  # prefijo -> [(etiqueta, archivo)]
    for f in archivos:
        m = re.fullmatch(r"(.+)_(\d+)", f.stem)
        if m:
            prefijo, etiqueta = m.group(1), f"Actividad {int(m.group(2))}"
        else:
            prefijo, etiqueta = "otros", titulo_de(f)
        grupos.setdefault(prefijo, []).append((etiqueta, f.name))

    bloques = []
    for prefijo, items in grupos.items():
        titulo = GRUPOS.get(prefijo, prefijo.replace("_", " ").capitalize())
        lis = "\n".join(f'      <li><a href="{esc(n)}">{esc(e)}</a></li>' for e, n in items)
        bloques.append(f'    <h3>{esc(titulo)}</h3>\n    <ul class="list">\n{lis}\n    </ul>')

    n = int(re.search(r"\d+", carpeta.name).group())
    return f"""<!DOCTYPE html>
        <html lang="es">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Tema {n} · DWEC</title>
        <link rel="stylesheet" href="../style.css">
        </head>
        <body>
        <header>
            <a class="back" href="../index.html">← Volver</a>
            <h1>Tema {n}</h1>
            <p>{esc(DESCRIPCIONES.get(carpeta.name, ""))}</p>
        </header>

        <main>
        {chr(10).join(bloques)}
        </main>
        </body>
        </html>
        """


def main():
    (RAIZ / "index.html").write_text(pagina_raiz(), encoding="utf-8")
    print("✔ index.html (raíz)")
    carpetas = [d for d in RAIZ.iterdir() if d.is_dir() and re.fullmatch(r"tema_\d+", d.name)]
    carpetas += [RAIZ / c for c in EXTRAS if (RAIZ / c).is_dir()]
    for d in sorted(carpetas, key=natural):
        (d / "index.html").write_text(pagina_tema(d), encoding="utf-8")
        print(f"✔ {d.name}/index.html")


if __name__ == "__main__":
    main()
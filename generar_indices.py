# Robin Jack (2026)

"""Genera el index.html de cada carpeta con ejercicios y ajusta lo justo de cada ejercicio.

Se ejecuta solo en GitHub Actions en cada push (.github/workflows/pages.yml),
pero también se puede ejecutar a mano para verlo en local: python generar_indices.py

- Los índices generados llevan la marca <!-- generado -->. Un index.html sin ella se
  considera hecho a mano (un proyecto): no se toca, no se entra en su carpeta y solo se enlaza.
- De cada ejercicio solo se modifican, si existen: <title>, la description, las rutas
  del icono y de style.css, y el enlace de vuelta (<a class="back">).
- En los índices cada ejercicio se lista con el texto de su primer encabezado (h1..h6)
  y, debajo, el nombre del archivo.
"""
import html
import re
from pathlib import Path

RAIZ = Path(__file__).parent
AUTOR = "Robin Jack"
ICONO = "assets/icons/smiley.png"
ESTILO = "style.css"
MARCA = "<!-- generado -->"
REPO = "https://github.com/robin-mdc/programacion-cliente"

# Carpetas o archivos que no se muestran ni se modifican.
# Por nombre (en cualquier nivel) o por ruta relativa a la raíz: "tema_2/borrador.html"
IGNORAR = {"assets", "plantilla.html"}

# Opcionales, por ruta relativa a la raíz. Sin título se usa el nombre de la carpeta.
TITULOS = {
    "en_clase": "Ejercicios en clase",
}
DESCRIPCIONES = {
    "tema_1": "Sintaxis del lenguaje JavaScript",
    "en_clase": "Actividades realizadas con Yil en clase :^)",
}


def natural(p):
    # orden natural: propuestos_2 antes que propuestos_10
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", p.name.lower())]


def esc(texto):
    return html.escape(str(texto))


def ruta(p):
    return p.relative_to(RAIZ).as_posix()


def titulo(p):
    # "tema_3" -> "Tema 3", "lista_de_tareas.html" -> "Lista de tareas"
    return TITULOS.get(ruta(p)) or p.stem.replace("_", " ").capitalize()


def nombre(carpeta):
    # "Tema 3 · Practica almacenamiento"
    partes = carpeta.relative_to(RAIZ).parts
    return " · ".join(titulo(RAIZ.joinpath(*partes[:i + 1])) for i in range(len(partes)))


def a_raiz(carpeta):
    return "../" * len(carpeta.relative_to(RAIZ).parts)


def contenido(carpeta):
    """Subcarpetas y ejercicios de una carpeta, sin lo ignorado."""
    visibles = sorted(
        (p for p in carpeta.iterdir()
         if not p.name.startswith((".", "_")) and p.name not in IGNORAR and ruta(p) not in IGNORAR),
        key=natural,
    )
    carpetas = [p for p in visibles if p.is_dir()]
    ejercicios = [p for p in visibles if p.suffix == ".html" and p.name != "index.html"]
    return carpetas, ejercicios


def leer(archivo):
    return archivo.read_bytes().decode("utf-8")


def escribir(archivo, texto):
    """Escribe solo si cambia. Devuelve True si ha escrito."""
    if archivo.exists() and leer(archivo).replace("\r\n", "\n") == texto.replace("\r\n", "\n"):
        return False
    archivo.write_bytes(texto.encode("utf-8"))
    return True


def es_manual(carpeta):
    indice = carpeta / "index.html"
    return indice.exists() and MARCA not in leer(indice)


def encabezado(texto):
    """Texto del primer <h1>..<h6> del ejercicio (suele ser su título), o None."""
    cuerpo = re.sub(r"<script.*?</script>|<!--.*?-->", "", texto, flags=re.S | re.I)
    m = re.search(r"<h([1-6])[^>]*>(.*?)</h\1>", cuerpo, re.S | re.I)
    limpio = " ".join(html.unescape(re.sub(r"<[^>]+>", "", m.group(2))).split()) if m else ""
    return limpio or None


def pagina(tit, pre, desc, cuerpo):
    return f"""<!DOCTYPE html>
{MARCA}
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(tit)}</title>
  <link rel="icon" href="{pre}{ICONO}">
  <link rel="stylesheet" href="{pre}{ESTILO}">
  <meta name="description" content="{esc(desc)}">
  <meta name="author" content="{AUTOR}">
</head>
<body class="indice">
{cuerpo}</body>
</html>
"""


def fila(clase, href, tit, archivo, info=""):
    info = f'<span class="info">{esc(info)}</span>' if info else ""
    return (f'      <li><a class="fila {clase}" href="{esc(href)}"><span class="nombre">{esc(tit)}</span>'
            f'<span class="ruta">{esc(archivo)}</span>{info}</a></li>\n')


def pagina_carpeta(carpeta, carpetas, ejercicios):
    """carpetas: [(carpeta, info)], ejercicios: [(archivo, título)]. Las carpetas van arriba."""
    partes = carpeta.relative_to(RAIZ).parts
    migas = [f'<a href="{a_raiz(carpeta)}index.html">inicio</a>']
    migas += [f'<a href="{"../" * (len(partes) - i)}index.html">{esc(p)}</a>' for i, p in enumerate(partes[:-1], 1)]
    migas.append(f"<span>{esc(partes[-1])}</span>")
    desc = DESCRIPCIONES.get(ruta(carpeta), "")
    filas = [fila("carpeta", f"{d.name}/index.html", titulo(d), d.name + "/", info) for d, info in carpetas]
    filas += [fila("archivo", f.name, tit, f.name) for f, tit in ejercicios]
    cuerpo = f"""  <header class="cabecera">
    <div>
      <nav class="migas">{" / ".join(migas)}</nav>
      <h1>{esc(nombre(carpeta))}</h1>
      <p>{esc(desc)}</p>
    </div>
  </header>

  <main>
    <ul class="explorador">
{"".join(filas)}    </ul>
  </main>
""".replace("      <p></p>\n", "")
    return pagina(f"{nombre(carpeta)} · DWEC", a_raiz(carpeta), desc or nombre(carpeta), cuerpo)


def pagina_raiz(carpetas):
    """carpetas: [(carpeta, info)]"""
    tarjetas = []
    for d, info in carpetas:
        m = re.fullmatch(r"tema_(\d+)", d.name)
        num = f"{int(m.group(1)):02d}" if m else "★"
        tarjetas.append(f"""    <a class="card" href="{esc(d.name)}/index.html">
      <span class="num">{num}</span>
      <h2>{esc(titulo(d))}</h2>
      <p>{esc(DESCRIPCIONES.get(d.name) or info)}</p>
    </a>
""")
    cuerpo = f"""  <header class="cabecera">
    <div>
      <p class="sobretitulo">2º DAW · Curso 2026/27</p>
      <h1>Desarrollo Web en Entorno Cliente</h1>
      <p>Robin Jack Schilmöller</p>
    </div>
    <a class="repo" href="{REPO}">Repositorio</a>
  </header>

  <main class="grid">
{"".join(tarjetas)}  </main>
"""
    return pagina("DWEC · Desarrollo Web en Entorno Cliente", "", "Ejercicios de DWEC", cuerpo)


def ajustar_ejercicio(archivo, texto):
    """Devuelve el texto cambiando solo title, description, icono, estilo y enlace de vuelta (si existen)."""
    carpeta = archivo.parent
    pre = a_raiz(carpeta)
    cambios = [
        (r"(<title>).*?(</title>)", titulo(archivo)),
        (r'(<meta[^>]*name="description"[^>]*content=")[^"]*(")', f"Ejercicio de {nombre(carpeta)}"),
        (r'(<link[^>]*rel="icon"[^>]*href=")[^"]*(")', pre + ICONO),
        (r'(<link[^>]*href=")[^"]*style\.css(")', pre + ESTILO),
        (r'(<a[^>]*class="back"[^>]*href=")[^"]*(")', "index.html"),
        (r'(<a[^>]*class="back"[^>]*>).*?(</a>)', f"← Volver a {titulo(carpeta)}"),
    ]
    for patron, valor in cambios:
        texto = re.sub(patron, lambda m: m.group(1) + esc(valor) + m.group(2), texto, count=1, flags=re.S | re.I)
    return texto


def recorrer(carpeta):
    """Genera el índice de la carpeta y de sus subcarpetas.
    Devuelve un texto para quien la enlace ("3 elementos"), o None si no hay nada que enlazar."""
    if es_manual(carpeta):
        print(f"· {ruta(carpeta)}/index.html (hecho a mano, no se toca)")
        return "proyecto"
    carpetas, archivos = contenido(carpeta)
    carpetas = [(d, info) for d in carpetas if (info := recorrer(d))]
    ejercicios = []
    for f in archivos:
        original = leer(f)
        texto = ajustar_ejercicio(f, original)
        if texto != original:
            f.write_bytes(texto.encode("utf-8"))
            print(f"  ✎ {ruta(f)}")
        ejercicios.append((f, encabezado(texto) or titulo(f)))
    n = len(carpetas) + len(ejercicios)
    if not n:
        return None
    if escribir(carpeta / "index.html", pagina_carpeta(carpeta, carpetas, ejercicios)):
        print(f"✔ {ruta(carpeta)}/index.html")
    return "1 elemento" if n == 1 else f"{n} elementos"


def main():
    carpetas = [(d, info) for d in contenido(RAIZ)[0] if (info := recorrer(d))]
    carpetas.sort(key=lambda c: not c[0].name.startswith("tema_"))  # los temas primero
    if es_manual(RAIZ):
        print("· index.html (hecho a mano, no se toca)")
    elif escribir(RAIZ / "index.html", pagina_raiz(carpetas)):
        print("✔ index.html")


if __name__ == "__main__":
    main()

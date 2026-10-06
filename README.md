# Desarrollo Web en Entorno Cliente (DWEC)

 
Actividades y ejercicios del módulo **Desarrollo Web en Entorno Cliente**, 2º curso del grado superior de Desarrollo de Aplicaciones Web (DAW).


## Table of Contents
- [Website](#-website)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Project structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🔗 Website

👉 **https://robin-mdc.github.io/programacion-cliente/**

## Prerequisites

- A web browser (Chrome, Firefox or Edge).
- Git to clone the repository.

No external dependencies are needed: the project is plain HTML, CSS and JavaScript.

## Setup

1. Clone the repository:

```bash
   git clone https://github.com/robin-mdc/programacion-cliente.git
   cd programacion-cliente
```

2. Open `index.html` in your browser (double-click it).

3. On the main page, select a topic to see its activities.
4. To check the exercises that print to the console (`propuestos_4.html`), open the browser developer tools (`F12`) and go to the **Console** tab.

## Project structure

Each topic has its own folder with its activities:

```
├── index.html      ← main page (grid of topics)
├── style.css       ← shared styles
├── assets/         ← shared images and icons
├── tema_1/
├── tema_2/
└── ...
```

## Troubleshooting

**Nothing appears when running a console exercise**
The output is not shown on the page. Open the developer tools (`F12`), go to the **Console** tab and reload the page (`F5`).

**Images or styles load locally but not on GitHub Pages**
GitHub Pages is case-sensitive, while Windows is not. Check that every path in the HTML matches the exact file name, including uppercase and lowercase letters (e.g. `assets/Logo.png` ≠ `assets/logo.png`).

**Changes are not visible after pushing**
GitHub Pages can take a few minutes to redeploy. If the old version still appears, force a reload without cache with `Ctrl + F5`.

## Contributing

For contributing please read [CONTRIBUTING.md](CONTRIBUTING.md) for the branching strategy, commit conventions and pull request guidelines.
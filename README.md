# Laberintos y rutas alternativas

**Proyecto 1 de Teoría de Grafos · INFO1158**

Simulador de una red de pasillos de sentido único. Un robot debe desplazarse desde una entrada hasta una salida, y la aplicación permite estudiar cómo cambian sus rutas cuando se bloquean o agregan conexiones.

El proyecto combina **modelación matemática**, **algoritmos de grafos** y una **interfaz web con Python y Flask**. El informe técnico se desarrolla en LaTeX.

## El problema

El análisis de la red responde tres preguntas:

| Pregunta | Resultado esperado |
|---|---|
| ¿Cómo llegar usando la menor cantidad de pasillos? | Un camino mínimo y su longitud. |
| ¿Cuántas rutas pueden coexistir sin compartir pasillos? | Una familia máxima de caminos disjuntos en arcos. |
| ¿Cuántos pasillos es necesario bloquear para impedir la llegada? | Un conjunto mínimo de arcos que desconecte la entrada de la salida. |

La longitud de una ruta se mide por su **cantidad de arcos**. Las coordenadas y las distancias físicas del dibujo sirven para representar la red.

## Conceptos de teoría de grafos

La red se modela como un grafo dirigido **G = (V, E)**, con entrada **s** y salida **t**.

| Concepto | Aplicación en el simulador |
|---|---|
| Vértices y arcos | Los vértices representan espacios o cruces. Cada arco representa un pasillo orientado. |
| Adyacencia y orientación | Un arco `(u, v)` permite desplazarse de `u` a `v`. |
| Alcanzabilidad | Determina si existe algún camino dirigido desde la entrada hasta la salida. |
| Camino mínimo | BFS explora por capas para encontrar una ruta con el menor número de arcos. |
| Reconstrucción del camino | Los predecesores guardados durante BFS permiten recuperar la secuencia de vértices. |
| Disjunción en arcos | Las rutas independientes pueden compartir vértices y utilizan pasillos distintos. |
| Flujo máximo y corte mínimo | La capacidad unitaria permite relacionar la máxima cantidad de rutas con el mínimo bloqueo que las interrumpe. |

El modelo inicial tiene **11 vértices y 18 arcos**, con todos los vértices incidentes a algún pasillo. Sus restricciones incluyen extremos distintos y ausencia de lazos, duplicados y arcos recíprocos. Dos rutas dirigidas con arcos distintos certifican que admite al menos dos alternativas.

## Estado de implementación

| Componente | Estado actual |
|---|---|
| Carga y validación del grafo | Implementado. Incluye validación de los pasillos bloqueados. |
| BFS y reconstrucción de una ruta mínima | Implementado con código propio. |
| Servidor Flask y análisis mediante JSON | Implementado. |
| Página para ejecutar escenarios de prueba | Implementada. Muestra ruta, distancia y datos intercambiados. |
| Pruebas automatizadas | Disponibles para el modelo, BFS y la API. |
| Informe técnico | Borrador LaTeX con modelo y BFS documentados. |
| Flujo máximo, familia de rutas y corte mínimo | Pendiente de implementación para redes conectadas. |
| Plano interactivo y controles de edición | Pendientes de integración. |

> **Resultados pendientes y desconexión**
>
> En una red conectada, `caminos`, `maximo` y `corte` permanecen en `null` mientras esos cálculos estén pendientes. Si no existe un camino, la respuesta incluye `ruta: null`, `distancia: null`, cero rutas y un corte vacío.

## Puesta en marcha

**Requisitos** — Python 3.10 o posterior y las dependencias de [requirements.txt](requirements.txt).

Los comandos se ejecutan desde la raíz del repositorio.

### Windows · PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app app run
```

Si Python está disponible mediante el comando `python`, puede utilizarse `python -m venv .venv` para crear el entorno. Una vez creado, los comandos llaman directamente a su ejecutable.

<details>
<summary><strong>macOS y Linux</strong></summary>

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m flask --app app run
```

</details>

Abrir **[http://127.0.0.1:5000](http://127.0.0.1:5000)** en el navegador. El servidor permanece activo mientras la terminal esté abierta y se detiene con `Ctrl+C`.

## Escenarios de prueba

La página incluye cinco configuraciones. El bloqueo y el atajo se aplican de forma independiente a la red original, manteniendo los extremos `s` y `t`.

| Configuración | Camino mínimo obtenido | Longitud |
|---|---|---|
| Red original | `s → A → D → t` | 3 |
| Bloqueo de `D → t` | `s → B → F → I → t` | 4 |
| Alta de `C → t` | `s → C → t` | 2 |
| Bloqueo de las dos entradas de `t` | Sin camino disponible | Sin valor |
| Caso manual de seis vértices | `s → a → c → t` | 3 |

Los datos base están en [casos.json](casos.json). La página permite consultar el JSON enviado al servidor y su respuesta para contrastar el modelo con el cálculo.

## Organización del código

| Archivo o carpeta | Responsabilidad |
|---|---|
| [app.py](app.py) | Rutas HTTP y conexión entre la interfaz y el motor. |
| [modelo.py](modelo.py) | Carga de casos y validación del inventario de pasillos. |
| [algoritmos.py](algoritmos.py) | Búsqueda BFS, reconstrucción del camino y función `resolver`. |
| [casos.json](casos.json) | Red original y caso manual independiente. |
| [templates/](templates/) | Estructura HTML de la página. |
| [static/](static/) | Estilos y comunicación JavaScript con Flask. |
| [tests/](tests/) | Pruebas automatizadas del avance. |
| [informe/](informe/) | Fuente LaTeX del informe técnico. |

## API de análisis

| Método | Ruta | Función |
|---|---|---|
| `GET` | `/` | Mostrar la página de prueba. |
| `GET` | `/casos/<nombre>` | Obtener un caso guardado, como `original` o `manual`. |
| `POST` | `/analizar` | Validar el grafo y calcular los resultados disponibles. |

Cada solicitud de análisis contiene el estado completo de la red. Los pasillos bloqueados permanecen en el inventario, y el algoritmo utiliza sus arcos activos. El campo `activo` es opcional y su valor predeterminado es `true`.

<details>
<summary><strong>Ejemplo de entrada y respuesta</strong></summary>

Enviar el siguiente objeto a `/analizar` con `Content-Type: application/json`.

```json
{
  "vertices": ["s", "a", "t"],
  "entrada": "s",
  "salida": "t",
  "arcos": [
    {"origen": "s", "destino": "a", "activo": true},
    {"origen": "a", "destino": "t", "activo": true}
  ]
}
```

Respuesta de la implementación actual:

```json
{
  "ruta": ["s", "a", "t"],
  "distancia": 2,
  "caminos": null,
  "maximo": null,
  "corte": null,
  "calculos_pendientes": ["rutas_disjuntas", "corte_minimo"]
}
```

Al completar los algoritmos, `caminos` contendrá listas de vértices, `maximo` será la cantidad de caminos y `corte` contendrá pares dirigidos. `calculos_pendientes` enumera los cálculos que todavía faltan.

Los límites de tamaño y la ausencia de vértices aislados se verifican en la configuración inicial. Las solicitudes de análisis permiten otras cantidades, manteniendo las restricciones de extremos distintos, lazos, duplicados y recíprocos.

Una solicitud inválida devuelve **HTTP 400** con `{"error": "mensaje"}`. Un caso inexistente devuelve **HTTP 404**. La existencia de una ruta se determina mediante el campo `ruta`.

</details>

## Verificación

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

En macOS o Linux se utiliza `.venv/bin/python` con los mismos argumentos.

Las pruebas comprueban las restricciones del modelo, el certificado inicial de dos rutas, las distancias mínimas, bloqueos y restablecimientos, ciclos, cambios de extremos, desconexión y errores de entrada HTTP.

## Informe técnico

La fuente editable está en [informe/informe.tex](informe/informe.tex). Documenta el modelo propuesto, la representación dirigida, BFS y los resultados del primer bloque. También identifica las secciones pendientes de investigación y verificación completa.

Con una instalación de LaTeX, ejecutar dos veces desde la raíz del repositorio:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=informe informe/informe.tex
```

El PDF se genera en `informe/informe.pdf`. La configuración de Git excluye los PDF y los archivos temporales de compilación de esa carpeta.

## Referencias

- **Enunciado del Proyecto 1 de INFO1158**, *Simulador interactivo de laberintos y rutas alternativas*, páginas 2–5.
- **MIT 6.006** — Demaine, Ku y Solomon (2020). [Lecture 9. Breadth-First Search](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/196a95604877d326c6586e60477b59d4_MIT6_006S20_lec9.pdf).
- **Pallets** — [Instalación de Flask](https://flask.palletsprojects.com/en/stable/installation/) y [Quickstart](https://flask.palletsprojects.com/en/stable/quickstart/).

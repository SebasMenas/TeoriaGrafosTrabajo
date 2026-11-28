# Laberintos y rutas alternativas

**Proyecto 1 de Teoría de Grafos · INFO1158**<br>
Universidad Católica de Temuco · Escuela de Informática<br>
**Equipo:** Cristian Cáceres, Ariel Díaz, Gustavo Martínez y Sebastián Mena.<br>
**Docente:** Elliott Mardones Arias.<br>
**Fecha de entrega:** 26 de noviembre de 2026.

Simulador interactivo de una red de pasillos de sentido único para robots de inspección en un centro de almacenamiento logístico. La aplicación permite modificar la red y analizar en tiempo real:

- el camino de menor longitud entre la entrada y la salida;
- la cantidad máxima de rutas independientes que no comparten pasillos;
- el corte mínimo de pasillos cuya eliminación desconecta la salida.

El backend utiliza Python y Flask; el frontend utiliza JavaScript nativo y SVG. BFS y Edmonds–Karp están implementados en el repositorio, sin NetworkX ni otras librerías de grafos.

## Contenido

- [Requisitos](#requisitos)
- [Puesta en marcha](#puesta-en-marcha)
- [Uso de la interfaz](#uso-de-la-interfaz)
- [Modelo y restricciones](#modelo-y-restricciones)
- [Algoritmos](#algoritmos)
- [API HTTP](#api-http)
- [Pruebas y verificación](#pruebas-y-verificación)
- [Casos de estudio](#casos-de-estudio)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Informe técnico](#informe-técnico)
- [Solución de problemas](#solución-de-problemas)

## Requisitos

- Python 3.10 o posterior.
- Flask 3.1.3, declarado en [`requirements.txt`](requirements.txt).
- Navegador web moderno.
- Opcional: una distribución LaTeX con `pdflatex` para recompilar el informe.

`requirements.txt` declara Flask como única dependencia directa. Werkzeug se instala automáticamente como dependencia transitiva de Flask.

## Puesta en marcha

### Windows · PowerShell

```powershell
# 1. Crear el entorno virtual
py -3 -m venv .venv

# 2. Activarlo
.\.venv\Scripts\Activate.ps1

# 3. Instalar dependencias
python -m pip install -r requirements.txt

# 4. Iniciar el servidor
python -m flask --app app run
```

Si PowerShell bloquea la activación del entorno virtual, ejecuta estos comandos en la misma terminal y vuelve al paso 2:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
# 1. Crear el entorno virtual
python3 -m venv .venv

# 2. Activarlo
source .venv/bin/activate

# 3. Instalar dependencias
python -m pip install -r requirements.txt

# 4. Iniciar el servidor
python -m flask --app app run
```

Abre <http://127.0.0.1:5000> en el navegador. Para detener el servidor, pulsa `Ctrl+C` en la terminal.

Si el puerto 5000 está ocupado, inicia Flask en otro puerto:

```powershell
python -m flask --app app run --port 5001
```

```bash
python -m flask --app app run --port 5001
```

En ese caso, abre <http://127.0.0.1:5001>.

## Uso de la interfaz

1. **Selecciona la red base:** `Red original (11 espacios)` o `Caso manual (6 espacios)`.
2. **Modifica los pasillos:**
   - Haz clic sobre un arco del plano o usa su interruptor para bloquearlo o restablecerlo.
   - Usa el formulario para agregar un pasillo dirigido.
   - Cambia los vértices de entrada y salida desde los selectores.
3. **Pulsa Recalcular:** la interfaz envía el estado completo de la red a `POST /analizar`.
4. **Selecciona un modo de visualización:**
   - **Normal:** muestra la red sin resaltar una solución.
   - **Camino mínimo:** resalta en verde la ruta más corta.
   - **Rutas disjuntas:** diferencia en azul y oro los caminos de la familia máxima.
   - **Corte mínimo:** marca en rojo discontinuo los pasillos críticos.

El estado siempre se comunica con texto además del color. Las modificaciones se conservan únicamente en la sesión del navegador: **no se guardan en disco ni en una base de datos**. Recargar la página o reiniciar el servidor restaura el caso base.

## Modelo y restricciones

El grafo dirigido se representa con un objeto JSON:

```json
{
  "vertices": ["s", "a", "b", "t"],
  "entrada": "s",
  "salida": "t",
  "arcos": [
    {"origen": "s", "destino": "a", "activo": true},
    {"origen": "s", "destino": "b", "activo": true},
    {"origen": "a", "destino": "t", "activo": true},
    {"origen": "b", "destino": "t", "activo": true}
  ]
}
```

Reglas de validación:

- `vertices` debe contener al menos dos nombres únicos y no vacíos.
- `entrada` y `salida` deben existir en `vertices` y ser distintos.
- Cada arco debe unir vértices existentes y distintos.
- No se admiten lazos, arcos repetidos ni pares recíprocos.
- `activo` debe ser booleano; si se omite, se interpreta como `true`.
- Los arcos bloqueados siguen formando parte del inventario y también se validan.
- Las ediciones pueden crear ciclos o dejar vértices aislados.
- La red original cargada desde `casos.json` debe tener 10–12 vértices, 14–20 arcos activos y ningún vértice aislado.

## Algoritmos

| Cálculo | Implementación | Resultado |
|---|---|---|
| Camino mínimo | BFS con cola FIFO, distancias y reconstrucción por predecesores | Ruta con menor cantidad de arcos |
| Rutas independientes | Flujo máximo con capacidades unitarias mediante Edmonds–Karp | Familia máxima de caminos sin arcos compartidos |
| Corte mínimo | BFS final sobre la red residual y arcos salientes del conjunto alcanzable | Conjunto mínimo de arcos que desconecta `s` de `t` |

Las rutas pueden compartir vértices, pero no arcos. Por el teorema de flujo máximo–corte mínimo, el tamaño de la familia máxima coincide con la cardinalidad del corte mínimo.

La función `resolver(grafo)` recibe el objeto completo y lee `entrada` y `salida` desde ese objeto. No recibe ambos vértices como parámetros separados ni modifica los datos de entrada.

## API HTTP

Con el servidor ejecutándose en `http://127.0.0.1:5000`:

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Sirve la interfaz HTML. |
| `GET` | `/casos/<nombre>` | Devuelve una copia del caso `original` o `manual`. |
| `POST` | `/analizar` | Valida el grafo recibido y devuelve los tres cálculos. |

### Obtener un caso

```bash
curl -sS http://127.0.0.1:5000/casos/original
```

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/casos/original" -Method Get |
  ConvertTo-Json -Depth 10
```

Un caso inexistente devuelve HTTP 404:

```json
{"error":"Ese caso no existe."}
```

### Analizar un grafo

El siguiente comando obtiene la red original y la envía directamente a `/analizar`:

```bash
curl -sS http://127.0.0.1:5000/casos/original | curl -sS -X POST -H "Content-Type: application/json" --data-binary @- http://127.0.0.1:5000/analizar
```

En PowerShell:

```powershell
$grafo = Invoke-RestMethod -Uri "http://127.0.0.1:5000/casos/original" -Method Get
$respuesta = Invoke-RestMethod `
  -Uri "http://127.0.0.1:5000/analizar" `
  -Method Post `
  -ContentType "application/json" `
  -Body ($grafo | ConvertTo-Json -Depth 10)
$respuesta | ConvertTo-Json -Depth 10
```

Respuesta de la red original:

```json
{
  "ruta": ["s", "A", "D", "t"],
  "distancia": 3,
  "caminos": [
    ["s", "A", "D", "t"],
    ["s", "B", "F", "I", "t"]
  ],
  "maximo": 2,
  "corte": [["D", "t"], ["I", "t"]],
  "calculos_pendientes": []
}
```

| Campo | Tipo | Significado |
|---|---|---|
| `ruta` | `string[]` o `null` | Camino mínimo desde `entrada` hasta `salida`. |
| `distancia` | `number` o `null` | Cantidad de arcos de `ruta`; `null` si no hay conexión. |
| `caminos` | `string[][]` | Familia máxima de caminos disjuntos en arcos. |
| `maximo` | `number` | Cantidad de caminos de `caminos`; equivale al flujo máximo unitario. |
| `corte` | `string[][]` | Pares `[origen, destino]` del corte mínimo. |
| `calculos_pendientes` | `any[]` | Reservado para cálculos diferidos; actualmente siempre `[]`. |

Si no existe conexión, la respuesta usa `ruta: null`, `distancia: null`, `caminos: []`, `maximo: 0`, `corte: []` y `calculos_pendientes: []`.

Los errores de JSON, tipo de contenido o validación devuelven HTTP 400 con una clave `error`:

```json
{"error":"La entrada y la salida deben ser distintas."}
```

## Pruebas y verificación

### Suite unitaria

Ejecuta las 16 pruebas del modelo, los algoritmos y la API Flask:

```powershell
python -m unittest discover -s tests -v
```

```bash
python3 -m unittest discover -s tests -v
```

### Verificación matemática

El script evalúa cinco escenarios mediante `app.test_client()`, comprueba los certificados de flujo y corte y enumera exhaustivamente los caminos simples con DFS y retroceso:

```powershell
python verificar_informe.py
```

```bash
python3 verificar_informe.py
```

El script sobrescribe [`verificacion-resultados.json`](verificacion-resultados.json) con las trazas obtenidas en esa ejecución.

### Comprobación HTTP de T03

Con Flask ejecutándose en otra terminal:

```powershell
python relevos/T03/verificar_api.py
```

```bash
python3 relevos/T03/verificar_api.py
```

Para usar otro puerto, pasa la URL como argumento:

```powershell
python relevos/T03/verificar_api.py http://127.0.0.1:5001
```

```bash
python3 relevos/T03/verificar_api.py http://127.0.0.1:5001
```

## Casos de estudio

Los valores siguientes se obtienen de [`verificar_informe.py`](verificar_informe.py) y se contrastan con las respuestas conservadas en [`relevos/T03`](relevos/T03).

| Escenario | Arcos activos | Conexión | Distancia mínima | Caminos simples | Máx. rutas disjuntas | Corte mínimo |
|---|---:|---|---:|---:|---:|---|
| Original | 18 | Sí | 3 | 14 | 2 | `{(D,t), (I,t)}` |
| Bloqueo `D → t` | 17 | Sí | 4 | 10 | 1 | `{(I,t)}` |
| Atajo `C → t` | 19 | Sí | 2 | 15 | 3 | `{(s,A), (s,B), (s,C)}` |
| Caso manual | 7 | Sí | 3 | 3 | 2 | `{(s,a), (s,b)}` |
| Sin conexión | 16 | No | sin valor | 0 | 0 | `∅` |

La diferencia entre “caminos simples” y “rutas disjuntas” es central: contar todas las rutas posibles no mide la redundancia operativa, porque varias pueden depender del mismo pasillo.

## Estructura del repositorio

```text
TeoriaGrafosTrabajo/
├── algoritmos.py                 # BFS, Edmonds–Karp, descomposición de flujo y corte
├── app.py                        # Rutas HTTP de Flask
├── modelo.py                     # Carga de casos y validación del grafo
├── casos.json                    # Red original y caso manual
├── verificar_informe.py          # Verificación matemática y enumeración exhaustiva
├── verificacion-resultados.json  # Resultados generados por el verificador
├── requirements.txt              # Dependencia directa: Flask
├── guia_defensa.md               # Guion para la defensa presencial
├── relevos/T03/                  # Entradas, respuestas y comprobación HTTP de T03
├── static/
│   ├── estilos.css               # Estilos, paleta y resaltados
│   ├── inicio.js                 # Estado de la interfaz y eventos
│   └── js/
│       ├── grafo.js              # Renderizado SVG y resaltado de soluciones
│       └── posiciones.js         # Coordenadas de los vértices
├── templates/
│   └── index.html                # Plantilla y controles de la aplicación
├── tests/
│   ├── test_avance.py            # Modelo, BFS, validaciones y API
│   └── test_flujo_unitario.py     # Flujo, disyunción, corte y cancelación residual
└── informe/
    ├── informe.tex               # Fuente del informe técnico
    └── informe.pdf               # Informe compilado
```

## Informe técnico

El informe final está disponible en [`informe/informe.pdf`](informe/informe.pdf). La fuente LaTeX está en [`informe/informe.tex`](informe/informe.tex) e incluye la modelación, los algoritmos, la red residual, los cinco escenarios, conclusiones y referencias.

Para recompilarlo desde la raíz del repositorio, con `pdflatex` instalado:

```bash
pdflatex -output-directory=informe informe/informe.tex
pdflatex -output-directory=informe informe/informe.tex
```

La segunda pasada actualiza el índice y las referencias cruzadas. También puedes consultar [`guia_defensa.md`](guia_defensa.md) para preparar la presentación.

## Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `flask` no se reconoce | El entorno virtual no está activado o no se usa el intérprete del proyecto | Ejecuta `python -m flask --app app run` dentro del entorno virtual. |
| PowerShell bloquea `Activate.ps1` | Política de ejecución de Windows | Usa `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` y vuelve a activar el entorno. |
| El navegador no abre la aplicación | Flask no está ejecutándose o usa otro puerto | Revisa la terminal y abre la URL exacta que muestra Flask. |
| `POST /analizar` devuelve 400 | JSON inválido, `Content-Type` incorrecto o grafo fuera de las restricciones | Envía `Content-Type: application/json` y revisa `vertices`, `entrada`, `salida` y `arcos`. |
| Los cambios desaparecen | La aplicación no persiste datos | Es el comportamiento esperado; cada análisis recibe el grafo completo en la solicitud. |
| `pdflatex` no se reconoce | No hay una distribución LaTeX instalada | Instala MiKTeX o TeX Live; el PDF ya está incluido en el repositorio. |

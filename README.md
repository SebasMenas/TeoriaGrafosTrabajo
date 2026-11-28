# Laberintos y rutas alternativas

**Proyecto 1 de Teoría de Grafos · INFO1158**  
*Universidad Católica de Temuco · Escuela de Informática*  
**Equipo de desarrollo:** Cristian Cáceres, Ariel Díaz, Gustavo Martínez y Sebastián Mena.  
**Docente:** Elliott Mardones Arias.  
**Fecha de entrega:** 26 de noviembre de 2026.

Simulador interactivo de una red de pasillos de sentido único para robots de inspección en un centro de almacenamiento logístico. Permite estudiar en tiempo real el camino de menor longitud, la cantidad máxima de rutas independientes que no comparten pasillos y los cortes críticos que interrumpen la conectividad ante contingencias.

El proyecto combina **modelación matemática rigurosa**, **algoritmos de optimización de redes con código propio** (BFS y Edmonds–Karp unitario), una **interfaz web interactiva con Python, Flask y SVG**, y un **informe técnico completo en LaTeX**.

---

## 1. El problema y objetivos del análisis

El sistema responde a tres interrogantes fundamentales:

| Objetivo | Definición matemática | Procedimiento algorítmico implementado |
|---|---|---|
| **Camino mínimo** | $d_G(s, t) = \min \{ \|E(P)\| \}$ | Búsqueda en anchura (**BFS**) con reconstrucción por predecesores. |
| **Rutas independientes** | $\max \{ \|\mathcal{P}\| : E(P_i) \cap E(P_j) = \varnothing \}$ | Formulación de **Flujo Máximo con capacidades unitarias** (Edmonds–Karp). |
| **Corte mínimo** | $\min \{ \|C\| : G - C \text{ desconecta } s \text{ de } t \}$ | Identificación constructiva de arcos salientes desde el conjunto alcanzable residual $S$. |

---

## 2. Estado del proyecto (100% Completado)

| Componente | Estado | Descripción técnica |
|---|---|---|
| **Modelo y validaciones** | **Completado** | Validación de extremos, rechazo de lazos, arcos múltiples y recíprocos en `modelo.py`. |
| **Camino mínimo (BFS)** | **Completado** | Exploración por capas y reconstrucción de camino en $O(\|V\| + \|E\|)$ en `algoritmos.py`. |
| **Flujo unitario y rutas** | **Completado** | Edmonds–Karp con red residual directa e inversa y descomposición de caminos en `algoritmos.py`. |
| **Corte mínimo constructivo** | **Completado** | Obtención del corte saliente desde la residual final ($|f_{\max}| = \|C\|$). |
| **Plano interactivo SVG** | **Completado** | Visualización gráfica del laberinto, bloqueo/restablecimiento con interruptores y alta de arcos. |
| **Resaltado de soluciones** | **Completado** | Selector dinámico para destacar: *Camino mínimo* (verde), *Rutas disjuntas* (azul/oro) y *Corte mínimo* (rojo discontinuo). |
| **Suite de pruebas** | **Completado** | 16 pruebas automatizadas con `unittest` en `tests/`. |
| **Verificación matemática** | **Completado** | Script `verificar_informe.py` que comprueba los 5 casos y realiza enumeración exhaustiva por retroceso. |
| **Informe técnico LaTeX** | **Completado** | Documento formal de 14 páginas compilado en `informe/informe.pdf` con portada institucional, índice, teoría profunda y conclusiones exclusivas. |

---

## 3. Puesta en marcha

**Requisitos:** Python 3.10 o posterior.

### Linux / macOS

```bash
# 1. Crear y activar entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Iniciar el servidor web
flask --app app run
```

### Windows · PowerShell

```powershell
# 1. Crear y activar entorno virtual
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Iniciar el servidor web
flask --app app run
```

Abrir **[http://127.0.0.1:5000](http://127.0.0.1:5000)** en el navegador.

---

## 4. Uso de la interfaz interactiva

1. **Seleccionar red base:** En el panel superior, elige entre la `Red original (11 espacios)` o el `Caso manual (6 espacios)`.
2. **Edición dinámica:**
   - **Bloquear/Restablecer:** Haz clic directamente sobre cualquier arco en el plano o utiliza los interruptores accesibles.
   - **Agregar pasillo:** Selecciona origen y destino para crear un nuevo pasillo dirigido (valida lazos y duplicados).
   - **Cambiar extremos:** Modifica libremente el vértice de entrada ($s$) y de salida ($t$).
3. **Analizar resultados:** Pulsa el botón **Recalcular** para consultar al servidor.
4. **Visualizar soluciones en el plano:** Usa la barra de modos de vista para alternar entre:
   - **Normal:** Plano limpio con arcos activos y bloqueados.
   - **Camino mínimo:** Resalta la ruta más corta en verde.
   - **Rutas disjuntas:** Resalta la familia máxima de caminos independientes diferenciados en azul y oro.
   - **Corte mínimo:** Destaca en rojo punteado los pasillos críticos cuya eliminación aísla la salida.

---

## 5. Verificación reproducible y pruebas automatizadas

El proyecto cuenta con dos mecanismos complementarios de verificación:

### A. Suite de pruebas unitarias (`unittest`)
Ejecuta las 16 pruebas automatizadas que validan la API Flask, el modelo y los algoritmos:
```bash
python3 -m unittest discover -s tests -v
```

### B. Script de verificación matemática y enumeración exhaustiva
Evalúa los 5 escenarios mediante `app.test_client()` y contrasta la solución con una **enumeración exhaustiva por retroceso (DFS)**, demostrando que contar caminos simples no equivale a redundancia real:
```bash
python3 verificar_informe.py
```

**Resultados certificados por el script:**
```text
==============================================================================
 VERIFICACIÓN MATEMÁTICA Y REPRODUCIBILIDAD (INFO1158 - PROYECTO 1)
==============================================================================
Entorno: app.test_client() (ejecución sin servidor externo)

Caso            Activos    Caminos    Distancia  Disjuntos    Corte Mín 
------------------------------------------------------------------------------
original        18         14         3          2            2         
bloqueo         17         10         4          1            1         
atajo           19         15         2          3            3         
manual          7          3          3          2            2         
sin_conexion    16         0          Sin ruta   0            0         
------------------------------------------------------------------------------
Todos los certificados matemáticos y enumeraciones fueron validados.
Resultados guardados exitosamente en: verificacion-resultados.json
==============================================================================
```

---

## 6. Organización del repositorio

```text
TeoriaGrafosTrabajo/
├── algoritmos.py               # BFS, flujo unitario (Edmonds-Karp), descomposición y corte
├── app.py                      # Rutas HTTP Flask (GET /, GET /casos/<id>, POST /analizar)
├── modelo.py                   # Carga de casos y validación estricta de restricciones
├── casos.json                  # Definición de la red original (11 nodos) y caso manual (6 nodos)
├── verificar_informe.py        # Script de verificación y enumeración matemática exhaustiva
├── verificacion-resultados.json# Trazas y certificados de los 5 casos validados
├── requirements.txt            # Dependencias del proyecto (Flask y Werkzeug)
├── static/
│   ├── estilos.css             # Estilos de la app, paleta compartida y resaltados
│   ├── inicio.js               # Controlador de interfaz, eventos y modos de visualización
│   └── js/
│       ├── grafo.js            # Renderizado SVG del plano y funciones de resaltado
│       └── posiciones.js       # Coordenadas visuales de los nodos
├── templates/
│   └── index.html              # Plantilla HTML con defs de flechas y controles
├── tests/
│   ├── test_avance.py          # Pruebas de BFS, modelo, validaciones y API
│   └── test_flujo_unitario.py  # Pruebas de flujo, disyunción, corte y caso de cancelación
└── informe/
    ├── informe.tex             # Código fuente LaTeX del informe técnico completo
    └── informe.pdf             # Informe técnico final compilado (14 páginas)
```

---

## 7. Compilación del informe técnico

Para compilar el informe desde el código fuente LaTeX:
```bash
cd informe
pdflatex informe.tex
pdflatex informe.tex
```
El documento resultante `informe.pdf` incluye portada institucional, índice general, fundamentación teórica, caso manual con tabla de cancelación residual, conclusiones en página exclusiva y referencias académicas consolidadas.

# Guía de Ensayo y Defensa Presencial (12 Minutos)

**INFO1158 · Teoría de Grafos · Proyecto 1**  
**Equipo:** Gustavo Martínez, Ariel Díaz, Cristian Cáceres y Sebastián Mena.  
**Docente:** Elliott Mardones Arias.  
**Duración máxima:** 12 minutos (Ensayo calibrado a 11 minutos).

---

## 1. Cronograma de Intervención por Minuto

```text
[0:00 - 2:00]  Gustavo Martínez   --> Problema del almacén y modelo matemático inicial (11 vértices, 18 arcos)
[2:00 - 4:30]  Ariel Díaz          --> BFS vs DFS, flujo unitario (Edmonds-Karp) y caso manual con cancelación
[4:30 - 7:00]  Cristian Cáceres    --> Recorrido por la interfaz web, plano SVG y resaltados visuales
[7:00 - 9:00]  Sebastián Mena      --> Modificaciones en vivo (bloqueo D->t, atajo C->t y desconexión)
[9:00 - 11:00] Los cuatro          --> Cierre teórico (Menger, 14 vs 2 caminos) y preguntas del docente
```

---

## 2. Guion Detallado por Integrante

### Minuto 0:00 a 2:00 · Gustavo Martínez (Problema y Modelo)
* **Objetivo:** Establecer el contexto logístico real y demostrar que el modelo satisface el 100% de las restricciones de la pauta.
* **Puntos clave a decir:**
  1. *"Buenas tardes profesor. Nuestro proyecto modela el sistema de desplazamiento de robots de inspección en un centro de almacenamiento con pasillos de sentido único."*
  2. *"Definimos el grafo dirigido $G_0 = (V, E_0)$ donde los vértices representan áreas o intersecciones y los arcos pasillos orientados. La longitud se mide en cantidad de pasillos (arcos)."*
  3. *"El modelo inicial cumple estrictamente las restricciones del enunciado:*
     - *11 vértices (pauta pide entre 10 y 12).*
     - *18 arcos activos (pauta pide entre 14 y 20).*
     - *Sin lazos reflexivos, sin arcos repetidos ni recíprocos (antiparalelos).*
     - *Ningún vértice aislado: todo espacio tiene al menos una conexión entrante o saliente.*
     - *Certificado de redundancia inicial: los caminos $s \to A \to D \to t$ y $s \to B \to F \to I \to t$ no comparten ningún pasillo, demostrando que existen al menos dos rutas independientes."*
  4. *"El problema nos pide responder tres cosas: el camino más corto, el máximo número de rutas independientes y el corte mínimo de pasillos que aíslen la salida. Doy paso a Ariel para explicar los algoritmos."*

---

### Minuto 2:00 a 4:30 · Ariel Díaz (Algoritmos y Red Residual)
* **Objetivo:** Defender la selección de algoritmos propios y explicar con maestría la cancelación en la red residual.
* **Puntos clave a decir:**
  1. *"Para el camino mínimo comparamos BFS y DFS:*
     - *Seleccionamos **BFS** porque explora por capas concéntricas de distancia creciente mediante una cola FIFO, garantizando el camino con menor número de arcos en grafos no ponderados en tiempo $O(|V| + |E|)$.*
     - *DFS no garantiza optimalidad porque profundiza en una rama arbitraria."*
  2. *"Para la familia máxima de rutas independientes comparamos enumeración exhaustiva frente a flujo unitario:*
     - *La enumeración exhaustiva por retroceso (backtracking) explora un espacio de $2^P$ combinaciones. Funciona en grafos pequeños, pero es exponencial e inviable para recalcular en tiempo real.*
     - *Seleccionamos **Edmonds–Karp con capacidades unitarias ($c=1$)**: opera en tiempo fuertemente polinómico $O((k+1)(|V| + |E|))$ y entrega tanto las rutas como el corte mínimo."*
  3. *"**Por qué se necesita la red residual (El caso manual de 6 nodos):**"*
     - *(Mostrar la Figura 2 o apuntar al código/informe)*:
     - *"Una estrategia voraz (greedy) que elija el camino mínimo $s \to a \to c \to t$ consumiría los arcos $(s,a)$ y $(c,t)$, dejando solo 1 camino disponible."*
     - *"Edmonds–Karp resuelve esto algebraicamente: al saturar $a \to c$, la red residual crea un **arco inverso** $c \to a$. En el segundo aumento por $s \to b \to c \to a \to d \to t$, el paso por $c \to a$ **cancela** el flujo en $a \to c$ (pasa de 1 a 0), reasignando las conexiones hacia dos rutas disjuntas óptimas: $P_1 = s \to a \to d \to t$ y $P_2 = s \to b \to c \to t$."*
  4. *"Doy paso a Cristian para ver el simulador en funcionamiento."*

---

### Minuto 4:30 a 7:00 · Cristian Cáceres (Demostración de la Interfaz)
* **Objetivo:** Mostrar que el software está 100% desarrollado con código propio (Flask, JavaScript nativo y SVG) y cumple con el resaltado gráfico.
* **Acciones en pantalla:**
  1. Tener abierto el navegador en `http://127.0.0.1:5000` en pantalla completa (`F11`).
  2. *"La aplicación fue construida con Python y Flask en el backend, y JavaScript nativo manipulando SVG en el frontend, sin NetworkX ni librerías externas."*
  3. Cargar la **Red original**:
     - Mostrar el plano dirigido SVG con los 11 nodos y 18 pasillos.
     - Pulsar **Recalcular** y mostrar el panel de resultados: distancia 3, máximo 2 rutas, corte de tamaño 2.
  4. Demostrar la **barra de modos de visualización** sobre el plano:
     - Clic en **Camino mínimo:** *"El sistema resalta en verde el trayecto óptimo $s \to A \to D \to t$."*
     - Clic en **Rutas disjuntas:** *"Destaca las dos rutas independientes: una en azul ($s \to B \to F \to I \to t$) y otra en verde ($s \to A \to D \to t$), mostrando que no comparten pasillos."*
     - Clic en **Corte mínimo:** *"Destaca en rojo punteado los pasillos críticos $\{(D,t), (I,t)\}$, que corresponden a las dos entradas de $t$."*
  5. Clic en **Normal:** *"Vuelve a la vista limpia. Ahora Sebastián mostrará cómo responde la red ante modificaciones en tiempo real."*

---

### Minuto 7:00 a 9:00 · Sebastián Mena (Modificaciones en Vivo)
* **Objetivo:** Demostrar la simulación de modificaciones exigida por la pauta (bloqueo, atajo y desconexión), interpretando los cambios.
* **Acciones en pantalla:**
  1. **Modificación 1: Bloqueo de pasillo ($D \to t$)**:
     - Hacer clic sobre el arco $D \to t$ en el plano o usar el interruptor en el panel.
     - Mostrar que el arco pasa a gris punteado y el estado se marca como *Desactualizado*.
     - Pulsar **Recalcular**.
     - Explicar: *"Al bloquear $D \to t$, la distancia mínima aumenta a 4 ($s \to B \to F \to I \to t$). La salida sigue siendo alcanzable, pero perdimos redundancia: el máximo de rutas disjuntas cae de 2 a 1, y el corte mínimo se reduce a $\{(I,t)\}$ porque es el único pasillo que sostiene la llegada a la salida."*
  2. **Modificación 2: Habilitación de atajo ($C \to t$)**:
     - Restaurar la red con el botón superior.
     - En el formulario de agregar pasillo, seleccionar origen `C` y destino `t`, y pulsar **Agregar pasillo**.
     - Pulsar **Recalcular**.
     - Explicar: *"El nuevo pasillo $C \to t$ crea la ruta directa $s \to C \to t$ de longitud 2. Ahora coexisten 3 rutas disjuntas en arcos en paralelo, y el corte mínimo aumenta a 3 pasillos."*
  3. **Modificación 3: Red desconectada**:
     - Bloquear $D \to t$ e $I \to t$.
     - Recalcular y mostrar: *"La aplicación detecta que $t$ es inalcanzable; devuelve distancia null, 0 rutas y corte vacío (0 pasillos), porque la red ya está interrumpida y no requiere bloqueos adicionales."*

---

### Minuto 9:00 a 11:00 · Los Cuatro (Cierre Teórico y Preguntas)
* **El gran argumento de cierre (Gustavo o Ariel):**
  - *"Queremos destacar una conclusión matemática fundamental del informe:*
  - *En la red original encontramos mediante enumeración exhaustiva **14 caminos simples diferentes**, pero **únicamente 2 pueden operar en paralelo sin compartir pasillos**.*
  - *Tras el bloqueo de $D \to t$, siguen existiendo **10 caminos simples**, pero todos dependen de $I \to t$, por lo que la redundancia real es solo 1.*
  - *Esto prueba que contar caminos posibles en un centro logístico es engañoso: la verdadera capacidad operativa está determinada por los caminos disjuntos y por la dualidad del corte mínimo ($|f_{\max}| = \min |C|$)."*
* **Cierre:** *"Quedamos atentos a sus preguntas, profesor."*

---

## 3. Banco de Preguntas Trampa del Docente y Respuestas

| Pregunta del profesor | Quién responde | Respuesta precisa |
|---|---|---|
| *"¿Por qué no usaron Dijkstra en lugar de BFS?"* | **Ariel** | "Porque en este modelo todos los pasillos tienen peso uniforme (1 arco = 1 unidad de distancia). BFS resuelve caminos mínimos en grafos no ponderados en tiempo lineal $O(\|V\| + \|E\|)$, mientras que Dijkstra requeriría una cola de prioridad con costo $O((\|V\| + \|E\|) \log \|V\|)$, introduciendo una sobrecarga innecesaria." |
| *"¿Cómo garantizan que los caminos extraídos no compartan arcos si dos rutas se cruzan en un vértice?"* | **Gustavo o Ariel** | "La pauta permite que las rutas compartan vértices, pero no arcos. En la formulación de flujo unitario, la restricción de capacidad $0 \le f(u,v) \le 1$ se aplica sobre cada **arco**, lo que asegura que ningún pasillo transporte más de una unidad de flujo. Al extraer caminos con BFS y eliminar inmediatamente los arcos recorridos del flujo residual, se garantiza que cada camino pertenezca a una partición disjunta en arcos." |
| *"¿Cómo obtuvieron el corte mínimo desde el código?"* | **Ariel o Sebastián** | "Cuando Edmonds–Karp finaliza porque ya no existen caminos de aumento hacia $t$, ejecutamos un BFS final sobre la red residual. El conjunto de nodos alcanzables desde $s$ define el subconjunto $S$. El corte mínimo $C$ son todos los arcos originales activos que parten de $S$ y llegan a $V \setminus S$. Por el teorema de corte mínimo, todos esos arcos están saturados y suman exactamente el valor del flujo máximo." |
| *"¿Cómo validaron que los resultados no fueran producto de suerte o de un solo caso?"* | **Sebastián** | "Desarrollamos el script `verificar_informe.py` que evalúa las 5 configuraciones mediante `app.test_client()` de Flask y contrasta los resultados contra un algoritmo independiente de DFS con retroceso. Las pruebas unitarias comprueban la disyunción formal de conjuntos y la desconexión estricta en $G - C$." |

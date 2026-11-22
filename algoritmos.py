"""Ruta mínima, caminos disjuntos en arcos y corte mínimo del laberinto."""

from collections import deque

from modelo import validar_grafo


def bfs(adyacencia, entrada):
    """Explora vecinos de salida por capas y devuelve padres y distancias.

    adyacencia asocia cada vértice a sus vecinos iterables. entrada pertenece
    al diccionario. Solo los vértices alcanzados aparecen en los resultados.
    El padre de entrada es None. La cola FIFO evita saltarse capas de distancia.
    """
    padres = {entrada: None}
    distancias = {entrada: 0}
    cola = deque([entrada])

    while cola:
        actual = cola.popleft()
        for vecino in adyacencia[actual]:
            if vecino not in padres:
                # Se marca al encolar para visitar cada vértice una sola vez.
                padres[vecino] = actual
                distancias[vecino] = distancias[actual] + 1
                cola.append(vecino)
    return padres, distancias


def reconstruir_camino(padres, salida):
    """Devuelve la cadena desde la raíz de BFS hasta salida, o None si no llegó."""
    if salida not in padres:
        return None
    camino = []
    actual = salida
    while actual is not None:
        camino.append(actual)
        actual = padres[actual]
    camino.reverse()
    return camino


def flujo_unitario(adyacencia, entrada, salida):
    """Devuelve el flujo máximo unitario y los vértices alcanzables al terminar.

    Recibe las listas de vecinos activos de un grafo validado y dos extremos
    distintos. El flujo es un diccionario (origen, destino) -> 0 o 1 para cada
    arco original. El segundo resultado corresponde al último BFS residual.
    """
    arcos = [(origen, destino) for origen, vecinos in adyacencia.items()
             for destino in vecinos]
    residual = {v: {} for v in adyacencia}
    for origen, destino in arcos:
        residual[origen][destino] = 1
        residual[destino][origen] = 0

    while True:
        disponibles = {
            v: [vecino for vecino, capacidad in vecinos.items() if capacidad > 0]
            for v, vecinos in residual.items()
        }
        padres, _ = bfs(disponibles, entrada)
        camino = reconstruir_camino(padres, salida)
        if camino is None:
            flujo = {(u, v): 1 - residual[u][v] for u, v in arcos}
            return flujo, set(padres)

        for origen, destino in zip(camino, camino[1:]):
            residual[origen][destino] -= 1
            # Un paso inverso positivo permite cancelar el envío anterior.
            residual[destino][origen] += 1


def extraer_caminos(vertices, flujo, entrada, salida):
    """Separa el flujo unitario en caminos dirigidos disjuntos en arcos.

    Recibe los vértices y el flujo sobre los arcos originales. Devuelve listas
    de vértices de entrada a salida. Los ciclos residuales de flujo se omiten.
    """
    positivos = {v: {} for v in vertices}
    for (origen, destino), valor in flujo.items():
        if valor == 1:
            positivos[origen][destino] = None

    caminos = []
    while True:
        padres, _ = bfs(positivos, entrada)
        camino = reconstruir_camino(padres, salida)
        if camino is None:
            return caminos
        caminos.append(camino)
        for origen, destino in zip(camino, camino[1:]):
            del positivos[origen][destino]


def resolver(grafo):
    """Devuelve ruta mínima, distancia, caminos disjuntos, máximo y corte.

    Recibe el grafo JSON con vértices, inventario de arcos y extremos. Solo usa
    arcos activos para los cálculos. ValueError indica que la entrada es inválida.
    """
    validar_grafo(grafo)
    vertices = grafo["vertices"]
    entrada = grafo["entrada"]
    salida = grafo["salida"]
    adyacencia = {v: [] for v in vertices}
    for arco in grafo["arcos"]:
        if arco.get("activo", True):
            adyacencia[arco["origen"]].append(arco["destino"])

    padres, distancias = bfs(adyacencia, entrada)
    ruta = reconstruir_camino(padres, salida)
    if ruta is None:
        return {
            "ruta": None, "distancia": None, "caminos": [],
            "maximo": 0, "corte": [], "calculos_pendientes": [],
        }
    flujo, alcanzables = flujo_unitario(adyacencia, entrada, salida)
    caminos = extraer_caminos(vertices, flujo, entrada, salida)
    corte = [
        [origen, destino] for origen, destino in flujo
        if origen in alcanzables and destino not in alcanzables
    ]
    return {
        "ruta": ruta,
        "distancia": distancias[salida],
        "caminos": caminos,
        "maximo": len(caminos),
        "corte": corte,
        "calculos_pendientes": [],
    }

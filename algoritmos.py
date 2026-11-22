"""Primer avance del motor. BFS, reconstrucción y contrato para la integración."""

from collections import deque

from modelo import validar_grafo


def bfs(adyacencia, entrada):
    """Explora vecinos de salida por capas y devuelve padres y distancias.

    adyacencia es un diccionario vértice -> lista de vecinos. entrada pertenece
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


def resolver(grafo):
    """Valida el grafo y devuelve los resultados disponibles en este avance.

    La distancia mínima cuenta arcos activos. ValueError indica datos inválidos.
    En una red conectada, caminos/maximo/corte quedan en None mientras Ariel
    implementa flujo. calculos_pendientes permite mostrarlo explícitamente.
    Si no hay ruta, la familia y el corte vacíos ya son resultados exactos.
    """
    validar_grafo(grafo)
    adyacencia = {v: [] for v in grafo["vertices"]}
    for arco in grafo["arcos"]:
        if arco.get("activo", True):
            adyacencia[arco["origen"]].append(arco["destino"])

    padres, distancias = bfs(adyacencia, grafo["entrada"])
    ruta = reconstruir_camino(padres, grafo["salida"])
    if ruta is None:
        return {
            "ruta": None, "distancia": None, "caminos": [],
            "maximo": 0, "corte": [], "calculos_pendientes": [],
        }
    return {
        "ruta": ruta,
        "distancia": distancias[grafo["salida"]],
        "caminos": None,
        "maximo": None,
        "corte": None,
        "calculos_pendientes": ["rutas_disjuntas", "corte_minimo"],
    }

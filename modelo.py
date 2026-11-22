"""Carga y validación del inventario de pasillos dirigidos del laberinto."""

import json
from pathlib import Path


def validar_grafo(grafo):
    """Valida un grafo JSON sin modificarlo y lanza ValueError si es inválido.

    Recibe vertices, arcos, entrada y salida. Un arco puede omitir activo,
    que significa True. Revisa también los pasillos bloqueados para impedir
    duplicados y recíprocos en el inventario que se puede restablecer.
    Los límites de tamaño y los aislados se verifican al cargar la red inicial.
    """
    if not isinstance(grafo, dict):
        raise ValueError("El grafo debe ser un objeto JSON.")

    vertices = grafo.get("vertices")
    if not isinstance(vertices, list) or len(vertices) < 2:
        raise ValueError("vertices debe ser una lista de al menos dos espacios.")
    if any(not isinstance(v, str) or not v.strip() for v in vertices):
        raise ValueError("Cada vértice debe tener un nombre de texto no vacío.")
    if len(set(vertices)) != len(vertices):
        raise ValueError("Los nombres de los vértices deben ser únicos.")

    entrada = grafo.get("entrada")
    salida = grafo.get("salida")
    if entrada not in vertices or salida not in vertices:
        raise ValueError("La entrada y la salida deben pertenecer a vertices.")
    if entrada == salida:
        raise ValueError("La entrada y la salida deben ser distintas.")

    arcos = grafo.get("arcos")
    if not isinstance(arcos, list):
        raise ValueError("arcos debe ser una lista de pasillos dirigidos.")

    pares = set()
    for arco in arcos:
        if not isinstance(arco, dict):
            raise ValueError("Cada arco debe ser un objeto con origen y destino.")
        origen = arco.get("origen")
        destino = arco.get("destino")
        if origen not in vertices or destino not in vertices:
            raise ValueError("Los extremos de cada arco deben pertenecer a vertices.")
        if origen == destino:
            raise ValueError("Un pasillo debe unir vértices distintos. No se admiten lazos.")
        if not isinstance(arco.get("activo", True), bool):
            raise ValueError("activo debe ser true o false.")
        if (origen, destino) in pares:
            raise ValueError(f"El pasillo {origen} → {destino} está repetido.")
        if (destino, origen) in pares:
            raise ValueError(f"El pasillo {origen} → {destino} tiene un recíproco.")
        pares.add((origen, destino))


def cargar_caso(nombre="original"):
    """Devuelve una copia del caso guardado o lanza KeyError si no existe.

    Lee casos.json junto al módulo, independientemente de la carpeta actual.
    Revisa estructura y, para original, cantidades e incidencia iniciales.
    La familia de dos rutas iniciales se certifica en las pruebas y el informe.
    """
    ruta = Path(__file__).with_name("casos.json")
    with ruta.open(encoding="utf-8") as archivo:
        grafo = json.load(archivo)[nombre]
    validar_grafo(grafo)

    if nombre == "original":
        vertices = grafo["vertices"]
        arcos = grafo["arcos"]
        if not 10 <= len(vertices) <= 12 or not 14 <= len(arcos) <= 20:
            raise ValueError("El modelo inicial debe tener 10–12 vértices y 14–20 arcos.")
        incidentes = {v for arco in arcos for v in (arco["origen"], arco["destino"])}
        if incidentes != set(vertices) or any(not a.get("activo", True) for a in arcos):
            raise ValueError("El modelo inicial debe tener todos sus arcos activos y ningún aislado.")
    return grafo

#!/usr/bin/env python3
"""
verificar_informe.py

Script de verificación matemática y reproducibilidad experimental para el Proyecto 1:
"Simulador interactivo de laberintos y rutas alternativas" (INFO1158 - Teoría de Grafos).

Funcionalidades:
1. Utiliza el cliente de pruebas integrado de Flask (`app.test_client()`) para analizar
   las 5 configuraciones de estudio sin necesidad de levantar un servidor HTTP externo.
2. Implementa un algoritmo independiente de enumeración exhaustiva de caminos simples
   (mediante DFS con retroceso / backtracking) para contrastar el espacio total de caminos.
3. Verifica los certificados matemáticos de optimalidad:
   - Coincidencia de la distancia mínima con la ruta calculada por BFS.
   - Disyunción de arcos en la familia de caminos independientes: E(P_i) ∩ E(P_j) = ∅.
   - Coincidencia cardinal: |caminos| == |corte| == maximo flujo.
   - Desconexión estricta de la salida t al remover los arcos del corte mínimo (G - C).
4. Exporta los resultados completos a `verificacion-resultados.json`.
"""

import json
import sys
from copy import deepcopy
from pathlib import Path

from app import app
from algoritmos import bfs


def enumerar_caminos_simples(grafo):
    """
    Genera todos los caminos dirigidos simples desde entrada hasta salida
    mediante DFS con retroceso (backtracking).
    """
    s = grafo["entrada"]
    t = grafo["salida"]
    adyacencia = {v: [] for v in grafo["vertices"]}
    for arco in grafo["arcos"]:
        if arco.get("activo", True):
            adyacencia[arco["origen"]].append(arco["destino"])

    caminos = []
    camino_actual = [s]
    visitados_en_camino = {s}

    def dfs(u):
        if u == t:
            caminos.append(list(camino_actual))
            return
        for v in adyacencia.get(u, []):
            if v not in visitados_en_camino:
                visitados_en_camino.add(v)
                camino_actual.append(v)
                dfs(v)
                camino_actual.pop()
                visitados_en_camino.remove(v)

    dfs(s)
    return caminos


def construir_casos():
    """Construye las 5 configuraciones analizadas en el informe técnico."""
    ruta_casos = Path(__file__).resolve().parent / "casos.json"
    with open(ruta_casos, encoding="utf-8") as f:
        casos_base = json.load(f)

    # 1. Caso original
    original = deepcopy(casos_base["original"])

    # 2. Modificación 1: Bloqueo D -> t
    bloqueo = deepcopy(original)
    for a in bloqueo["arcos"]:
        if a["origen"] == "D" and a["destino"] == "t":
            a["activo"] = False

    # 3. Modificación 2: Atajo C -> t
    atajo = deepcopy(original)
    atajo["arcos"].append({"origen": "C", "destino": "t", "activo": True})

    # 4. Caso manual independiente (6 vértices, 7 arcos)
    manual = deepcopy(casos_base["manual"])

    # 5. Red desconectada: Bloqueo D -> t e I -> t
    sin_conexion = deepcopy(original)
    for a in sin_conexion["arcos"]:
        if (a["origen"] == "D" and a["destino"] == "t") or (a["origen"] == "I" and a["destino"] == "t"):
            a["activo"] = False

    return [
        {
            "id": "original",
            "nombre": "Red original (11 vértices, 18 arcos)",
            "grafo": original,
            "distancia_esperada": 3,
            "maximo_esperado": 2,
            "caminos_simples_esperados": 14
        },
        {
            "id": "bloqueo",
            "nombre": "Bloqueo pasillo D -> t",
            "grafo": bloqueo,
            "distancia_esperada": 4,
            "maximo_esperado": 1,
            "caminos_simples_esperados": 10
        },
        {
            "id": "atajo",
            "nombre": "Atajo pasillo C -> t",
            "grafo": atajo,
            "distancia_esperada": 2,
            "maximo_esperado": 3,
            "caminos_simples_esperados": 15
        },
        {
            "id": "manual",
            "nombre": "Caso manual independiente (6 vértices, 7 arcos)",
            "grafo": manual,
            "distancia_esperada": 3,
            "maximo_esperado": 2,
            "caminos_simples_esperados": 3
        },
        {
            "id": "sin_conexion",
            "nombre": "Red desconectada (bloqueo D->t e I->t)",
            "grafo": sin_conexion,
            "distancia_esperada": None,
            "maximo_esperado": 0,
            "caminos_simples_esperados": 0
        }
    ]


def verificar_configuracion(cliente, caso):
    """Ejecuta la solicitud HTTP sobre el cliente de pruebas y valida los certificados."""
    grafo = caso["grafo"]
    respuesta = cliente.post("/analizar", json=grafo)
    assert respuesta.status_code == 200, f"Error HTTP {respuesta.status_code}: {respuesta.get_json()}"
    datos = respuesta.get_json()

    s, t = grafo["entrada"], grafo["salida"]
    arcos_activos = {
        (a["origen"], a["destino"])
        for a in grafo["arcos"] if a.get("activo", True)
    }

    # 1. Distancia y ruta mínima
    distancia = datos["distancia"]
    ruta = datos["ruta"]
    assert distancia == caso["distancia_esperada"], (
        f"[{caso['id']}] Distancia incorrecta: esperada {caso['distancia_esperada']}, obtenida {distancia}"
    )

    if distancia is None:
        assert ruta is None, f"[{caso['id']}] En red desconectada, ruta debe ser null"
    else:
        assert isinstance(ruta, list) and len(ruta) == distancia + 1
        assert ruta[0] == s and ruta[-1] == t
        arcos_ruta = list(zip(ruta, ruta[1:]))
        assert set(arcos_ruta).issubset(arcos_activos), f"[{caso['id']}] Ruta contiene arcos inactivos"

    # 2. Máximo de caminos disjuntos
    maximo = datos["maximo"]
    caminos = datos["caminos"]
    assert maximo == caso["maximo_esperado"], (
        f"[{caso['id']}] Máximo incorrecto: esperado {caso['maximo_esperado']}, obtenido {maximo}"
    )
    assert len(caminos) == maximo, (
        f"[{caso['id']}] La cantidad de caminos devueltos ({len(caminos)}) difiere de maximo ({maximo})"
    )

    arcos_usados_familia = set()
    for idx, cam in enumerate(caminos):
        assert cam[0] == s and cam[-1] == t, f"[{caso['id']}] Camino {idx} no conecta s con t"
        assert len(cam) == len(set(cam)), f"[{caso['id']}] Camino {idx} no es simple (contiene ciclos)"
        arcos_cam = set(zip(cam, cam[1:]))
        assert arcos_cam.issubset(arcos_activos), f"[{caso['id']}] Camino {idx} usa arcos no activos"
        assert arcos_cam.isdisjoint(arcos_usados_familia), (
            f"[{caso['id']}] Arcos compartidos entre caminos de la familia independiente: {arcos_cam & arcos_usados_familia}"
        )
        arcos_usados_familia.update(arcos_cam)

    # 3. Corte mínimo
    corte = [tuple(p) for p in datos["corte"]]
    assert len(corte) == maximo, (
        f"[{caso['id']}] Cardinalidad del corte ({len(corte)}) no coincide con el máximo de caminos ({maximo})"
    )
    assert set(corte).issubset(arcos_activos), f"[{caso['id']}] El corte incluye arcos inactivos"

    # 4. Desconexión estricta en G - C
    adyacencia_reducida = {v: [] for v in grafo["vertices"]}
    for u, v in arcos_activos - set(corte):
        adyacencia_reducida[u].append(v)
    alcanzables_reducidos, _ = bfs(adyacencia_reducida, s)
    assert t not in alcanzables_reducidos, (
        f"[{caso['id']}] El corte devuelto NO desconecta la salida t en G - C"
    )

    # 5. Enumeración exhaustiva independiente de caminos simples
    todos_caminos_simples = enumerar_caminos_simples(grafo)
    conteo_caminos = len(todos_caminos_simples)
    assert conteo_caminos == caso["caminos_simples_esperados"], (
        f"[{caso['id']}] Conteo de caminos simples difiere: esperado {caso['caminos_simples_esperados']}, obtenido {conteo_caminos}"
    )

    if distancia is not None:
        longitud_minima_enumerada = min(len(c) - 1 for c in todos_caminos_simples)
        assert longitud_minima_enumerada == distancia, (
            f"[{caso['id']}] La distancia BFS ({distancia}) no coincide con la longitud mínima encontrada por enumeración ({longitud_minima_enumerada})"
        )

    return {
        "id": caso["id"],
        "nombre": caso["nombre"],
        "distancia_minima": distancia,
        "ruta_minima": ruta,
        "maximo_caminos_disjuntos": maximo,
        "caminos_independientes": caminos,
        "corte_minimo": datos["corte"],
        "caminos_simples_totales": conteo_caminos,
        "arcos_activos": len(arcos_activos)
    }


def main():
    print("=" * 78)
    print(" VERIFICACIÓN MATEMÁTICA Y REPRODUCIBILIDAD (INFO1158 - PROYECTO 1)")
    print("=" * 78)
    print("Entorno: app.test_client() (ejecución sin servidor externo)")

    cliente = app.test_client()
    casos = construir_casos()
    resultados_totales = {}

    print("\n{:<15} {:<10} {:<10} {:<10} {:<12} {:<10}".format(
        "Caso", "Activos", "Caminos", "Distancia", "Disjuntos", "Corte Mín"
    ))
    print("-" * 78)

    for caso in casos:
        resultado = verificar_configuracion(cliente, caso)
        resultados_totales[caso["id"]] = resultado
        dist_str = str(resultado["distancia_minima"]) if resultado["distancia_minima"] is not None else "Sin ruta"
        print("{:<15} {:<10} {:<10} {:<10} {:<12} {:<10}".format(
            resultado["id"],
            resultado["arcos_activos"],
            resultado["caminos_simples_totales"],
            dist_str,
            resultado["maximo_caminos_disjuntos"],
            len(resultado["corte_minimo"])
        ))

    ruta_salida = Path(__file__).resolve().parent / "verificacion-resultados.json"
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(resultados_totales, f, indent=2, ensure_ascii=False)

    print("-" * 78)
    print("Todos los certificados matemáticos y enumeraciones fueron validados.")
    print(f"Resultados guardados exitosamente en: {ruta_salida.name}")
    print("=" * 78)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERROR EN VERIFICACIÓN: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)

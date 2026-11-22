"""Verifica el caso de cancelación y los certificados de flujo y corte."""

import unittest
from copy import deepcopy

from algoritmos import bfs, flujo_unitario, resolver
from modelo import cargar_caso


class PruebasFlujoUnitario(unittest.TestCase):
    def comprobar_certificado(self, grafo, resultado):
        activos = {
            (a["origen"], a["destino"])
            for a in grafo["arcos"] if a.get("activo", True)
        }
        entrada, salida = grafo["entrada"], grafo["salida"]
        usados = set()
        for camino in resultado["caminos"]:
            self.assertEqual((camino[0], camino[-1]), (entrada, salida))
            self.assertEqual(len(camino), len(set(camino)))
            arcos = set(zip(camino, camino[1:]))
            self.assertTrue(arcos <= activos)
            self.assertTrue(arcos.isdisjoint(usados))
            usados.update(arcos)

        corte = {tuple(a) for a in resultado["corte"]}
        self.assertTrue(corte <= activos)
        self.assertEqual(resultado["maximo"], len(resultado["caminos"]))
        self.assertEqual(resultado["maximo"], len(resultado["corte"]))
        self.assertEqual(len(corte), len(resultado["corte"]))
        restantes = {v: [] for v in grafo["vertices"]}
        for origen, destino in activos - corte:
            restantes[origen].append(destino)
        alcanzables, _ = bfs(restantes, entrada)
        self.assertNotIn(salida, alcanzables)

    def test_manual_cancela_el_primer_paso_por_a_c(self):
        grafo = cargar_caso("manual")
        resultado = resolver(grafo)
        self.assertEqual(resultado["ruta"], ["s", "a", "c", "t"])
        self.assertEqual(resultado["distancia"], 3)
        self.assertEqual(resultado["caminos"], [
            ["s", "a", "d", "t"], ["s", "b", "c", "t"],
        ])
        self.assertEqual(resultado["corte"], [["s", "a"], ["s", "b"]])
        adyacencia = {v: [] for v in grafo["vertices"]}
        for arco in grafo["arcos"]:
            adyacencia[arco["origen"]].append(arco["destino"])
        flujo, alcanzables = flujo_unitario(adyacencia, "s", "t")
        self.assertEqual(flujo["a", "c"], 0)
        self.assertEqual(alcanzables, {"s"})
        self.comprobar_certificado(grafo, resultado)

    def test_rutas_pueden_compartir_vertices(self):
        arcos = [("s", "a"), ("s", "b"), ("a", "x"), ("b", "x"),
                 ("x", "t"), ("x", "y"), ("y", "t")]
        grafo = {
            "vertices": ["s", "a", "b", "x", "y", "t"],
            "entrada": "s", "salida": "t",
            "arcos": [{"origen": u, "destino": v} for u, v in arcos],
        }
        resultado = resolver(grafo)
        self.assertEqual(resultado["maximo"], 2)
        self.assertTrue(all("x" in camino for camino in resultado["caminos"]))
        self.comprobar_certificado(grafo, resultado)

    def test_red_original_y_ediciones(self):
        original = cargar_caso()
        bloqueo = deepcopy(original)
        for arco in bloqueo["arcos"]:
            if (arco["origen"], arco["destino"]) == ("D", "t"):
                arco["activo"] = False
        adicion = deepcopy(original)
        adicion["arcos"].append({"origen": "C", "destino": "t", "activo": True})
        for grafo, distancia, maximo in [
            (original, 3, 2), (bloqueo, 4, 1), (adicion, 2, 3),
        ]:
            with self.subTest(distancia=distancia, maximo=maximo):
                copia = deepcopy(grafo)
                resultado = resolver(grafo)
                self.assertEqual(resultado["distancia"], distancia)
                self.assertEqual(resultado["maximo"], maximo)
                self.assertEqual(grafo, copia)
                self.comprobar_certificado(grafo, resultado)

    def test_sin_conexion_devuelve_certificado_vacio(self):
        grafo = cargar_caso()
        for arco in grafo["arcos"]:
            if arco["destino"] == grafo["salida"]:
                arco["activo"] = False
        resultado = resolver(grafo)
        self.assertEqual(resultado, {
            "ruta": None, "distancia": None, "caminos": [],
            "maximo": 0, "corte": [], "calculos_pendientes": [],
        })
        self.comprobar_certificado(grafo, resultado)

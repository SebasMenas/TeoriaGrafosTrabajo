"""Verificaciones del modelo, BFS y contrato HTTP del primer avance."""

import unittest
from copy import deepcopy

from algoritmos import bfs, reconstruir_camino, resolver
from app import app
from modelo import cargar_caso, validar_grafo


class PruebasDelAvance(unittest.TestCase):
    def setUp(self):
        self.grafo = cargar_caso()
        self.cliente = app.test_client()

    def test_modelo_inicial_y_certificado_de_dos_rutas(self):
        self.assertEqual(len(self.grafo["vertices"]), 11)
        self.assertEqual(len(self.grafo["arcos"]), 18)
        pares = {(a["origen"], a["destino"]) for a in self.grafo["arcos"]}
        incidentes = {v for par in pares for v in par}
        self.assertEqual(incidentes, set(self.grafo["vertices"]))
        rutas = [["s", "A", "D", "t"], ["s", "B", "F", "I", "t"]]
        usados = set()
        for ruta in rutas:
            arcos = set(zip(ruta, ruta[1:]))
            self.assertTrue(arcos <= pares)
            self.assertTrue(usados.isdisjoint(arcos))
            usados.update(arcos)

    def test_bfs_por_capas_y_reconstruccion(self):
        padres, distancias = bfs({"s": ["a", "t"], "a": ["b"], "b": ["t"], "t": []}, "s")
        self.assertEqual(distancias["t"], 1)
        self.assertEqual(reconstruir_camino(padres, "t"), ["s", "t"])

    def test_distancia_original(self):
        resultado = resolver(self.grafo)
        self.assertEqual(resultado["ruta"], ["s", "A", "D", "t"])
        self.assertEqual(resultado["distancia"], 3)
        self.assertIsNone(resultado["maximo"])
        self.assertEqual(resultado["calculos_pendientes"], ["rutas_disjuntas", "corte_minimo"])

    def test_bloqueo_restablecimiento_y_atajo(self):
        pasillo = next(a for a in self.grafo["arcos"] if (a["origen"], a["destino"]) == ("D", "t"))
        pasillo["activo"] = False
        self.assertEqual(resolver(self.grafo)["distancia"], 4)
        pasillo["activo"] = True
        self.assertEqual(resolver(self.grafo)["distancia"], 3)
        self.grafo["arcos"].append({"origen": "C", "destino": "t", "activo": True})
        self.assertEqual(resolver(self.grafo)["ruta"], ["s", "C", "t"])

    def test_sin_conexion(self):
        for arco in self.grafo["arcos"]:
            if arco["destino"] == "t":
                arco["activo"] = False
        respuesta = self.cliente.post("/analizar", json=self.grafo)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json, {
            "ruta": None, "distancia": None, "maximo": 0,
            "caminos": [], "corte": [], "calculos_pendientes": [],
        })

    def test_ciclo_y_aislado_permitidos_en_una_edicion(self):
        grafo = {
            "vertices": ["s", "a", "b", "t", "x"], "entrada": "s", "salida": "t",
            "arcos": [{"origen": u, "destino": v} for u, v in [("s", "a"), ("a", "b"), ("b", "s"), ("b", "t")]],
        }
        self.assertEqual(resolver(grafo)["distancia"], 3)

    def test_cambio_de_extremos(self):
        self.grafo["entrada"] = "t"
        self.grafo["salida"] = "s"
        self.assertIsNone(resolver(self.grafo)["ruta"])

    def test_no_modifica_los_datos(self):
        copia = deepcopy(self.grafo)
        resolver(self.grafo)
        self.assertEqual(self.grafo, copia)

    def test_altas_invalidas_y_reciprocos_de_bloqueados(self):
        arcos = [
            {"origen": "s", "destino": "s"},
            {"origen": "s", "destino": "A"},
            {"origen": "A", "destino": "s"},
            {"origen": "s", "destino": "inexistente"},
        ]
        self.grafo["arcos"][0]["activo"] = False
        for arco in arcos:
            with self.subTest(arco=arco):
                grafo = deepcopy(self.grafo)
                grafo["arcos"].append(arco)
                self.assertEqual(self.cliente.post("/analizar", json=grafo).status_code, 400)

    def test_tipos_invalidos_producen_error_400(self):
        for datos in [None, [], {}, {**self.grafo, "entrada": "s", "salida": "s"},
                      {**self.grafo, "vertices": ["s", "s"]},
                      {**self.grafo, "arcos": [{"origen": "s", "destino": "t", "activo": "false"}]}]:
            with self.subTest(datos=datos):
                respuesta = self.cliente.post("/analizar", json=datos)
                self.assertEqual(respuesta.status_code, 400)
                self.assertIn("error", respuesta.json)

    def test_http_json_malformado_y_tipo_incorrecto(self):
        for texto, tipo in [("{", "application/json"), ("hola", "text/plain")]:
            respuesta = self.cliente.post("/analizar", data=texto, content_type=tipo)
            self.assertEqual(respuesta.status_code, 400)
            self.assertIn("error", respuesta.json)

    def test_casos_y_pagina(self):
        self.assertEqual(self.cliente.get("/").status_code, 200)
        self.assertEqual(self.cliente.get("/casos/original").json, self.grafo)
        self.assertEqual(resolver(cargar_caso("manual"))["distancia"], 3)
        self.assertEqual(self.cliente.get("/casos/desconocido").status_code, 404)


if __name__ == "__main__":
    unittest.main()

"""Servidor Flask del primer avance. Ejecutar con python -m flask --app app run."""

from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import BadRequest, UnsupportedMediaType

from algoritmos import resolver
from modelo import cargar_caso

app = Flask(__name__)
app.json.ensure_ascii = False


@app.get("/")
def inicio():
    """Sirve la pantalla de comprobación del cálculo mínimo."""
    return render_template("index.html")


@app.get("/casos/<nombre>")
def obtener_caso(nombre):
    """Devuelve los datos del caso solicitado, o un error JSON 404."""
    try:
        return jsonify(cargar_caso(nombre))
    except KeyError:
        return jsonify(error="Ese caso no existe."), 404


@app.post("/analizar")
def analizar():
    """Recibe el grafo como JSON y devuelve el cálculo o un error JSON 400.

    No persiste las ediciones. Cada solicitud incluye el estado de la red.
    """
    try:
        grafo = request.get_json()
    except (BadRequest, UnsupportedMediaType):
        return jsonify(error="Envía JSON válido con Content-Type application/json."), 400
    try:
        return jsonify(resolver(grafo))
    except ValueError as error:
        return jsonify(error=str(error)), 400

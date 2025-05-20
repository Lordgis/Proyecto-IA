from flask import jsonify
from services.firebase_service import db

def listar_usuarios():
    usuarios = db.collection("usuarios").stream()
    lista = [u.to_dict() for u in usuarios]
    return jsonify(lista), 200

def listar_asistencias():
    registros = db.collection("registros_asistencia").order_by("fecha_hora", direction=db.Query.DESCENDING).stream()
    lista = [r.to_dict() for r in registros]
    return jsonify(lista), 200

def listar_alertas():
    alertas = db.collection("alertas").order_by("fecha_hora", direction=db.Query.DESCENDING).stream()
    lista = [a.to_dict() for a in alertas]
    return jsonify(lista), 200

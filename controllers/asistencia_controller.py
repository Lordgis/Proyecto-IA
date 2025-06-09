from flask import Blueprint, request, jsonify
from services.facial_recognition import procesar_asistencia
from firebase_admin import firestore

db = firestore.client()
asistencia_bp = Blueprint('asistencia', __name__)

@asistencia_bp.route('/procesar', methods=['POST'])
def procesar():
    data = request.json
    imagen_base64 = data.get('imagen_base64')
    if not imagen_base64:
        return jsonify({"error": "Falta imagen_base64"}), 400

    resultado = procesar_asistencia(imagen_base64)
    if resultado.get("resultado") == "Asistencia registrada":
        return jsonify(resultado), 200
    else:
        return jsonify(resultado), 400

@asistencia_bp.route('/listar', methods=['GET'])
def listar_asistencias():
    try:
        docs = db.collection('registros_asistencia').stream()
        asistencias = []

        for doc in docs:
            data = doc.to_dict()
            asistencia = {
                'id': doc.id,
                'nombre_usuario': data.get('nombre_usuario', 'Desconocido'),
                'fecha_hora': data.get('fecha_hora'),
                'estado': data.get('estado', 'desconocido'),
                'modo': data.get('modo', '')
            }
            asistencias.append(asistencia)

        return jsonify(asistencias), 200
    except Exception as e:
        return jsonify({'error': 'No se pudieron cargar las asistencias', 'detalle': str(e)}), 500

@asistencia_bp.route('/eliminar/<id>', methods=['DELETE'])
def eliminar_asistencia(id):
    try:
        db.collection('registros_asistencia').document(id).delete()
        return jsonify({'mensaje': 'Asistencia eliminada'}), 200
    except Exception as e:
        return jsonify({'error': 'No se pudo eliminar', 'detalle': str(e)}), 500

from flask import Blueprint, request, jsonify
from services.facial_recognition import procesar_asistencia
from firebase_admin import firestore
from datetime import datetime

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
        try:
            uid = resultado.get("uid")
            nombre_usuario = resultado.get("nombre_usuario", "Desconocido")

            if not uid:
                return jsonify({"error": "Falta UID del usuario"}), 400

            # Fecha actual (Y-m-d)
            fecha_actual = datetime.now().strftime('%Y-%m-%d')

            # Consultar asistencias del mismo UID hoy
            asistencias_ref = db.collection("registros_asistencia")
            query = asistencias_ref \
                .where("uid", "==", uid) \
                .where("estado", "==", "Presente") \
                .stream()

            for registro in query:
                data = registro.to_dict()
                fecha_registro = data.get("fecha_hora")
                if fecha_registro and fecha_registro.strftime('%Y-%m-%d') == fecha_actual:
                    return jsonify({"error": "El usuario ya registró asistencia hoy"}), 409

            # Registrar asistencia si no hay duplicado
            doc = {
                "nombre_usuario": nombre_usuario,
                "uid": uid,
                "fecha_hora": firestore.SERVER_TIMESTAMP,
                "estado": "Presente",
                "modo": "facial"
            }
            db.collection("registros_asistencia").add(doc)
            return jsonify(resultado), 200

        except Exception as e:
            return jsonify({"error": "Reconocido pero no se pudo guardar", "detalle": str(e)}), 500

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

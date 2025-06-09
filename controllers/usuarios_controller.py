# controllers/usuarios_controller.py

from flask import Blueprint, jsonify, request
from firebase_admin import firestore

db = firestore.client()

usuario_bp = Blueprint('usuario', __name__)

# Ruta para listar usuarios
@usuario_bp.route('/listar', methods=['GET'])
def listar_usuarios():
    try:
        usuarios_ref = db.collection('users')
        docs = usuarios_ref.stream()
        usuarios = []
        for doc in docs:
            data = doc.to_dict()
            usuario = {
                'id': doc.id,
                'nombre': data.get('nombre'),
                'correo': data.get('correo'),
                'rol': data.get('rol')
            }
            usuarios.append(usuario)
        return jsonify(usuarios), 200
    except Exception as e:
        print(f"Error al listar usuarios: {e}")
        return jsonify({'error': 'No se pudieron cargar los usuarios'}), 500


# Ruta para listar asistencias
@usuario_bp.route('/asistencias', methods=['GET'])
def listar_asistencias():
    try:
        asistencias_ref = db.collection('registros_asistencia')
        docs = asistencias_ref.stream()
        asistencias = []
        for doc in docs:
            data = doc.to_dict()
            asistencia = {
                'id': doc.id,
                'nombre_usuario': data.get('nombre_usuario', 'Desconocido'),
                'fecha_hora': data.get('fecha_hora'),
                'estado': data.get('estado', 'desconocido'),
                'modo': data.get('modo', 'desconocido'),
                'id_usuario': data.get('id_usuario')
            }
            asistencias.append(asistencia)
        return jsonify(asistencias), 200
    except Exception as e:
        print(f"Error al listar asistencias: {e}")
        return jsonify({'error': 'No se pudieron cargar las asistencias'}), 500


# Ruta para listar alertas (puedes modificar según tu colección y datos)
@usuario_bp.route('/alertas', methods=['GET'])
def listar_alertas():
    try:
        alertas_ref = db.collection('alertas')
        docs = alertas_ref.stream()
        alertas = []
        for doc in docs:
            data = doc.to_dict()
            alerta = {
                'id': doc.id,
                'mensaje': data.get('mensaje', ''),
                'tipo': data.get('tipo', ''),
                'fecha': data.get('fecha')
            }
            alertas.append(alerta)
        return jsonify(alertas), 200
    except Exception as e:
        print(f"Error al listar alertas: {e}")
        return jsonify({'error': 'No se pudieron cargar las alertas'}), 500

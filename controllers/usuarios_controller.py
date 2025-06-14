from flask import Blueprint, jsonify
from firebase_admin import firestore
from datetime import datetime
from collections import defaultdict

db = firestore.client()
usuario_bp = Blueprint('usuario', __name__)

def timestamp_to_iso(ts):
    try:
        return ts.isoformat() if ts else None
    except Exception:
        return None

# Ruta para listar usuarios
@usuario_bp.route('/listar', methods=['GET'])
def listar_usuarios():
    try:
        usuarios_ref = db.collection('usuarios')
        docs = usuarios_ref.stream()

        usuarios = []
        correos_vistos = set()

        for doc in docs:
            data = doc.to_dict()
            correo = data.get('correo')

            if not correo or correo in correos_vistos:
                continue

            correos_vistos.add(correo)

            usuarios.append({
                'id': doc.id,
                'nombre_completo': data.get('nombre_completo', 'Desconocido'),
                'correo': correo,
                'rol': data.get('rol', 'estudiante'),
                'fecha_registro': timestamp_to_iso(data.get('fecha_registro')),
                'estado': data.get('estado', 'activo'),
            })

        return jsonify(usuarios), 200

    except Exception as e:
        return jsonify({'error': 'No se pudieron cargar los usuarios', 'detalle': str(e)}), 500

# Ruta para listar asistencias
@usuario_bp.route('/asistencias', methods=['GET'])
def listar_asistencias():
    try:
        usuarios_ref = db.collection('usuarios')
        usuarios_docs = usuarios_ref.stream()
        usuarios = {}
        for doc in usuarios_docs:
            data = doc.to_dict()
            nombre = data.get('nombre_completo')
            if nombre:
                usuarios[nombre] = {
                    'id': doc.id,
                    'nombre_completo': nombre
                }

        asistencias_ref = db.collection('registros_asistencia')
        docs = asistencias_ref.stream()

        asistencias_por_dia = defaultdict(dict)

        for doc in docs:
            data = doc.to_dict()
            nombre = data.get('nombre_usuario')
            fecha = data.get('fecha_hora')

            if not nombre or not fecha:
                continue

            fecha_str = fecha.astimezone().strftime('%Y-%m-%d')

            asistencias_por_dia[fecha_str][nombre] = {
                'id': doc.id,
                'id_usuario': usuarios.get(nombre, {}).get('id'),
                'nombre_usuario': nombre,
                'fecha_Usuario': fecha.isoformat(),
                'estado_asistencia': data.get('estado', 'desconocido'),
                'modo_registro': data.get('modo', 'manual'),
                'observaciones': data.get('observaciones', '')
            }

        resultado_final = []
        for fecha, asistencias in asistencias_por_dia.items():
            for nombre, info in usuarios.items():
                if nombre in asistencias:
                    resultado_final.append(asistencias[nombre])
                else:
                    resultado_final.append({
                        'id': None,
                        'id_usuario': info['id'],
                        'nombre_usuario': nombre,
                        'fecha_Usuario': fecha,
                        'estado_asistencia': 'ausente',
                        'modo_registro': 'no registrado',
                        'observaciones': 'hora no registrada'
                    })

        return jsonify(resultado_final), 200

    except Exception as e:
        return jsonify({'error': 'No se pudieron cargar las asistencias', 'detalle': str(e)}), 500

# Ruta para listar alertas
@usuario_bp.route('/alertas', methods=['GET'])
def listar_alertas():
    try:
        alertas_ref = db.collection('alertas').order_by('fecha', direction=firestore.Query.DESCENDING)
        docs = alertas_ref.stream()

        alertas = []
        for doc in docs:
            data = doc.to_dict()
            mensaje = data.get('mensaje')
            fecha = data.get('fecha')

            if not mensaje or not fecha:
                continue

            alertas.append({
                'id': doc.id,
                'mensaje': mensaje,
                'tipo_alerta': data.get('tipo', 'informativa'),
                'fecha': timestamp_to_iso(fecha),
                'prioridad': data.get('prioridad', 'media')
            })

        return jsonify(alertas), 200

    except Exception as e:
        return jsonify({'error': 'No se pudieron cargar las alertas', 'detalle': str(e)}), 500

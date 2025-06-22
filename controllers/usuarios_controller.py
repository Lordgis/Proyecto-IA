from flask import Blueprint, jsonify
from firebase_admin import firestore
from datetime import datetime
from collections import defaultdict
from flask import Blueprint, jsonify, request


db = firestore.client()
usuario_bp = Blueprint('usuario', __name__)

def timestamp_to_iso(ts):
    try:
        return ts.isoformat() if ts else None
    except Exception:
        return None

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

# Ruta para editar usuario
@usuario_bp.route('/editar/<usuario_id>', methods=['PUT'])
def editar_usuario(usuario_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se enviaron datos para actualizar'}), 400

        usuario_ref = db.collection('usuarios').document(usuario_id)
        usuario_doc = usuario_ref.get()

        if not usuario_doc.exists:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        # Opcional: validar campos permitidos para actualizar
        campos_permitidos = {'nombre_completo', 'correo', 'rol', 'estado'}
        datos_actualizar = {k: v for k, v in data.items() if k in campos_permitidos}

        if not datos_actualizar:
            return jsonify({'error': 'No hay campos válidos para actualizar'}), 400

        usuario_ref.update(datos_actualizar)
        return jsonify({'mensaje': 'Usuario actualizado correctamente'}), 200

    except Exception as e:
        return jsonify({'error': 'Error al actualizar usuario', 'detalle': str(e)}), 500

# Ruta para eliminar usuario
@usuario_bp.route('/eliminar/<usuario_id>', methods=['DELETE'])
def eliminar_usuario(usuario_id):
    try:
        usuario_ref = db.collection('usuarios').document(usuario_id)
        usuario_doc = usuario_ref.get()

        if not usuario_doc.exists:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        usuario_ref.delete()
        return jsonify({'mensaje': 'Usuario eliminado correctamente'}), 200

    except Exception as e:
        return jsonify({'error': 'Error al eliminar usuario', 'detalle': str(e)}), 500


@usuario_bp.route('/dashboard/estadisticas', methods=['GET'])
def estadisticas_dashboard():
    try:
        usuarios_ref = db.collection('usuarios')
        usuarios_docs = list(usuarios_ref.stream())
        total_usuarios = len(usuarios_docs)

        asistencias_ref = db.collection('registros_asistencia')
        registros = list(asistencias_ref.stream())

        hoy = datetime.now().date()
        mes_actual = hoy.strftime('%Y-%m')

        # Calcular cuántos días tiene el mes actual
        if hoy.month == 12:
            siguiente_mes = datetime(hoy.year + 1, 1, 1)
        else:
            siguiente_mes = datetime(hoy.year, hoy.month + 1, 1)
        dias_en_mes = (siguiente_mes - datetime(hoy.year, hoy.month, 1)).days

        dias_mes = {str(d).zfill(2): 0 for d in range(1, dias_en_mes + 1)}
        asistencias_hoy = 0
        asistencias_mes = 0

        for doc in registros:
            data = doc.to_dict()
            fecha = data.get('fecha_hora')
            estado = data.get('estado', '').lower()

            if not fecha or estado != 'autorizado':
                continue

            fecha_local = fecha.astimezone()
            fecha_str = fecha_local.strftime('%Y-%m-%d')
            mes_str = fecha_local.strftime('%Y-%m')
            dia_str = fecha_local.strftime('%d')

            if mes_str == mes_actual:
                asistencias_mes += 1
                dias_mes[dia_str] += 1

            if fecha_local.date() == hoy:
                asistencias_hoy += 1

        # Calcular porcentaje real: asistencias registradas / posibles asistencias
        total_posibles_asistencias = total_usuarios * dias_en_mes
        porcentaje = int((asistencias_mes / total_posibles_asistencias) * 100) if total_posibles_asistencias > 0 else 0

        # Armar serie para el gráfico
        serie = [{"dia": dia, "asistencias": dias_mes[dia]} for dia in sorted(dias_mes)]

        return jsonify({
            "totalUsuarios": total_usuarios,
            "asistenciasHoy": asistencias_hoy,
            "asistenciasMes": asistencias_mes,
            "porcentajeAsistencia": porcentaje,
            "serie": serie
        }), 200

    except Exception as e:
        return jsonify({"error": "Error al calcular estadísticas", "detalle": str(e)}), 500

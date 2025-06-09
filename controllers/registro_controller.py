from flask import request, jsonify
from utils.imagen_utils import procesar_imagen
from services.firebase_service import db
from firebase_admin import firestore 


def registrar_usuario():
    try:
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        imagen = request.files.get('imagen')

        if not nombre or not correo or not imagen:
            return jsonify({'error': 'Faltan datos'}), 400

        encoding = procesar_imagen(imagen)
        if encoding is None:
            return jsonify({'error': 'No se detectó rostro'}), 400

        # Aquí guardamos el encoding como lista serializable (ej. lista de floats)
        encoding_serializable = encoding.tolist() if hasattr(encoding, 'tolist') else encoding

        usuario = {
            "nombre_completo": nombre,
            "correo": correo,
            "encoding_vector": encoding_serializable,
            "rol": "estudiante",
            "fecha_registro": firestore.SERVER_TIMESTAMP
        }

        # Comprobar si correo ya existe (evitar duplicados)
        usuarios_ref = db.collection("usuarios")
        query = usuarios_ref.where("correo", "==", correo).limit(1).get()
        if query:
            return jsonify({'error': 'El correo ya está registrado'}), 400

        usuarios_ref.add(usuario)
        return jsonify({'mensaje': 'Usuario registrado correctamente'}), 200

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({'error': 'Error interno del servidor', 'detalle': str(e)}), 500

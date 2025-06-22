from flask import request, jsonify
from utils.imagen_utils import procesar_imagen, comparar_rostros
from services.firebase_service import db
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from datetime import datetime

def verificar_rostro():
    imagen = request.files.get('imagen')
    if not imagen:
        return jsonify({"error": "No se recibió imagen"}), 400

    encoding_nuevo = procesar_imagen(imagen)
    if encoding_nuevo is None:
        return jsonify({"resultado": "No se detectó rostro"}), 400

    usuarios = db.collection("usuarios").stream()
    encodings = []
    nombres = []
    ids = []

    for doc in usuarios:
        data = doc.to_dict()
        if "encoding_vector" in data:
            encodings.append(data["encoding_vector"])
            nombres.append(data.get("nombre_completo", "Desconocido"))
            ids.append(doc.id)

    coincidencia = comparar_rostros(encoding_nuevo, encodings)

    if coincidencia is not None:
        nombre = nombres[coincidencia]
        uid = ids[coincidencia]
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        fecha_actual = now.strftime("%Y-%m-%d")

        # Verificar si ya hay asistencia para hoy
        registros = db.collection("registros_asistencia") \
            .where("id_usuario", "==", uid) \
            .where("estado", "==", "autorizado") \
            .stream()

        for reg in registros:
            data = reg.to_dict()
            fecha_registro = data.get("fecha_hora")
            if fecha_registro and fecha_registro.strftime('%Y-%m-%d') == fecha_actual:
                return jsonify({
                    "resultado": "ya esta registrado en la asistencia hoy",
                    "nombre_usuario": nombre,
                    "uid": uid,
                    "fecha_hora": fecha_registro.strftime("%Y-%m-%d %H:%M:%S")
                }), 409

        # Registrar asistencia
        db.collection("registros_asistencia").add({
            "id_usuario": uid,
            "nombre_usuario": nombre,
            "fecha_hora": SERVER_TIMESTAMP,
            "modo": "automático",
            "estado": "autorizado"
        })

        return jsonify({
            "resultado": "Asistencia registrada",
            "nombre_usuario": nombre,
            "uid": uid,
            "fecha_hora": now_str
        }), 200

    # Registrar alerta si no hay coincidencia
    db.collection("alertas").add({
        "fecha_hora": SERVER_TIMESTAMP,
        "motivo": "Rostro no identificado",
        "estado": "pendiente"
    })

    return jsonify({
        "resultado": "Rostro no reconocido"
    }), 200

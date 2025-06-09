from flask import request, jsonify
from utils.imagen_utils import procesar_imagen, comparar_rostros
from services.firebase_service import db
from google.cloud.firestore_v1 import SERVER_TIMESTAMP

def verificar_rostro():
    imagen = request.files.get('imagen')
    if not imagen:
        return jsonify({"error": "No se recibió imagen"}), 400

    encoding_nuevo = procesar_imagen(imagen)
    if encoding_nuevo is None:
        return jsonify({"error": "No se detectó rostro"}), 400

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
        db.collection("registros_asistencia").add({
            "id_usuario": ids[coincidencia],
            "nombre_usuario": nombres[coincidencia],
            "fecha_hora": SERVER_TIMESTAMP,
            "modo": "automático",
            "estado": "autorizado"
        })
        return jsonify({"mensaje": f"Asistencia registrada para {nombres[coincidencia]}"}), 200
    else:
        db.collection("alertas").add({
            "fecha_hora": SERVER_TIMESTAMP,
            "motivo": "Rostro no identificado",
            "estado": "pendiente"
        })
        return jsonify({"mensaje": "Rostro no identificado"}), 200

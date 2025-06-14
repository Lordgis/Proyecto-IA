import face_recognition
import numpy as np
from utils.imagen_utils import base64_a_imagen
from config import FACE_MATCH_THRESHOLD
from services.asistencia import guardar_asistencia, obtener_embeddings


def procesar_asistencia(imagen_base64):
    try:
        imagen = base64_a_imagen(imagen_base64)
        if imagen is None:
            return {"resultado": "Error al decodificar imagen"}

        rostros = face_recognition.face_encodings(imagen)
        if not rostros:
            return {"resultado": "No se detectó ningún rostro"}

        rostro_nuevo = rostros[0]
        base_datos = obtener_embeddings()

        for uid, datos in base_datos.items():
            emb_db = np.array(datos["embedding"])
            distancia = np.linalg.norm(emb_db - rostro_nuevo)

            if distancia < FACE_MATCH_THRESHOLD:
                guardar_asistencia(uid)
                return {
                    "resultado": "Asistencia registrada",
                    "uid": uid,
                    "distancia": round(float(distancia), 4),
                    "nombre_usuario": datos.get("nombre", "Desconocido")
                }

        return {"resultado": "Rostro no reconocido"}

    except Exception as e:
        return {"resultado": "Error interno", "detalle": str(e)}

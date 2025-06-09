import face_recognition
import numpy as np
from utils.imagen_utils import base64_a_imagen
from config import FACE_MATCH_THRESHOLD
from services.asistencia import guardar_asistencia, obtener_embeddings


def reconocer_usuario_por_imagen(imagen_base64):
    imagen = base64_a_imagen(imagen_base64)
    rostros = face_recognition.face_encodings(imagen)
    if not rostros:
        return None  # No se detectó rostro
    rostro_nuevo = rostros[0]
    # Simular obtener embeddings desde base de datos
    base_datos = obtener_embeddings()
    for uid, datos in base_datos.items():
        emb_db = np.array(datos["embedding"])
        distancia = np.linalg.norm(emb_db - rostro_nuevo)
        if distancia < FACE_MATCH_THRESHOLD:
            return uid
    return None
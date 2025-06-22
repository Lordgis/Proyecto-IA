import face_recognition
import numpy as np
from utils.imagen_utils import base64_a_imagen        # Convierte base64 a imagen OpenCV
from config import FACE_MATCH_THRESHOLD               # Umbral de similitud para reconocimiento facial
from services.asistencia import guardar_asistencia, obtener_embeddings  # Funciones para asistencia y datos

# Función principal que procesa una imagen y registra asistencia si se reconoce un rostro
def procesar_asistencia(imagen_base64):
    try:
        # Convierte la imagen base64 enviada desde el frontend en una imagen procesable
        imagen = base64_a_imagen(imagen_base64)
        if imagen is None:
            return {"resultado": "Error al decodificar imagen"}

        # Extrae los encodings (vectores de características) del rostro detectado en la imagen
        rostros = face_recognition.face_encodings(imagen)
        if not rostros:
            return {"resultado": "No se detectó ningún rostro"}

        # Toma solo el primer rostro detectado (si hay más, se ignoran en esta versión)
        rostro_nuevo = rostros[0]

        # Obtiene todos los encodings registrados desde la base de datos (Firestore, archivo, etc.)
        base_datos = obtener_embeddings()

        # Recorre cada usuario registrado para comparar su encoding con el nuevo
        for uid, datos in base_datos.items():
            emb_db = np.array(datos["embedding"])  # Encoding del rostro registrado
            distancia = np.linalg.norm(emb_db - rostro_nuevo)  # Calcula la distancia Euclideana entre encodings

            # Si la distancia es menor al umbral definido, se considera una coincidencia válida
            if distancia < FACE_MATCH_THRESHOLD:
                guardar_asistencia(uid)  # Registra la asistencia del usuario identificado
                return {
                    "resultado": "Asistencia registrada",
                    "uid": uid,
                    "distancia": round(float(distancia), 4),
                    "nombre_usuario": datos.get("nombre", "Desconocido")  # Nombre opcional
                }

        # Si ningún rostro coincide con los registrados
        return {"resultado": "Rostro no reconocido"}

    except Exception as e:
        # En caso de error inesperado, devuelve un mensaje informativo
        return {"resultado": "Error interno", "detalle": str(e)}

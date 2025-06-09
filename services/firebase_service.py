import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Simulación temporal (reemplazar con Firebase)
USUARIOS = {
    "abc123": {"nombre": "Juan", "embedding": [0.1] * 128}
}

def obtener_embeddings():
    return USUARIOS

def guardar_asistencia(uid):
    print(f"Asistencia registrada para {uid}")

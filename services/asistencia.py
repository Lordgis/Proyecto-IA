from firebase_admin import firestore
from datetime import datetime

db = firestore.client()

def guardar_asistencia(user_id, modo="automático", estado="autorizado", nombre_usuario=None):
    now = datetime.utcnow()
    registro = {
        "id_usuario": user_id,
        "fecha_hora": now,
        "modo": modo,
        "estado": estado,
    }
    if nombre_usuario:
        registro["nombre_usuario"] = nombre_usuario

    db.collection('registros_asistencia').add(registro)
    return True

def obtener_embeddings():
    docs = db.collection('usuarios').stream()
    base_datos = {}
    for doc in docs:
        data = doc.to_dict()
        if "embedding" in data:
            base_datos[doc.id] = {
                "embedding": data["embedding"],
                "nombre": data.get("nombre", "")
            }
    return base_datos

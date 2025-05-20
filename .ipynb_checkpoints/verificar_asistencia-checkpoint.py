import cv2
import face_recognition
import firebase_admin
from firebase_admin import credentials, firestore
import numpy as np
from datetime import datetime

# Inicializar Firebase
cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Cargar datos de Firestore
print("📥 Cargando usuarios registrados...")
usuarios_docs = db.collection("usuarios").stream()
encodings_registrados = []
nombres_usuarios = []
ids_usuarios = []

for doc in usuarios_docs:
    data = doc.to_dict()
    if "encoding_vector" in data:
        encodings_registrados.append(np.array(data["encoding_vector"]))
        nombres_usuarios.append(data["nombre_completo"])
        ids_usuarios.append(doc.id)

print(f"✅ {len(encodings_registrados)} usuarios cargados.")

# Captura desde webcam
cam = cv2.VideoCapture(0)
print("🎥 Apunta la cámara a tu rostro. Presiona 's' para verificar.")

verificado = False

while True:
    ret, frame = cam.read()
    if not ret:
        print("❌ Error con la cámara.")
        break

    cv2.imshow("Verificación Facial", frame)
    key = cv2.waitKey(1)

    if key == ord('s'):
        print("📸 Captura realizada. Verificando...")
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb_frame)

        if not faces:
            print("❌ No se detectó ningún rostro.")
            break

        encoding_nuevo = face_recognition.face_encodings(rgb_frame, faces)[0]

        # Comparar con los registros
        resultados = face_recognition.compare_faces(encodings_registrados, encoding_nuevo)
        distancias = face_recognition.face_distance(encodings_registrados, encoding_nuevo)

        if True in resultados:
            idx_match = np.argmin(distancias)
            nombre = nombres_usuarios[idx_match]
            id_usuario = ids_usuarios[idx_match]
            print(f"✅ Rostro verificado: {nombre}")

            # Registrar asistencia
            db.collection("registros_asistencia").add({
                "id_usuario": id_usuario,
                "nombre_usuario": nombre,
                "fecha_hora": firestore.SERVER_TIMESTAMP,
                "modo": "automático",
                "estado": "autorizado"
            })
            print("📝 Asistencia registrada.")
        else:
            print("🚫 Rostro no identificado.")
            db.collection("alertas").add({
                "fecha_hora": firestore.SERVER_TIMESTAMP,
                "motivo": "Rostro no identificado",
                "estado": "pendiente"
            })

        break

    elif key == ord('q'):
        print("🚪 Saliste del modo cámara.")
        break

cam.release()
cv2.destroyAllWindows()

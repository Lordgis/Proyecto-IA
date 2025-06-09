import face_recognition
import numpy as np
import tempfile

import base64
import cv2

def procesar_imagen(imagen_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp:
        imagen_file.save(temp.name)
        imagen = face_recognition.load_image_file(temp.name)
        face_locations = face_recognition.face_locations(imagen)
        if not face_locations:
            return None
        encoding = face_recognition.face_encodings(imagen, face_locations)[0]
        return encoding.tolist()

def comparar_rostros(nuevo, lista_registrados):
    distancias = face_recognition.face_distance([np.array(e) for e in lista_registrados], np.array(nuevo))
    if len(distancias) == 0:
        return None
    indice_mas_cercano = np.argmin(distancias)
    if distancias[indice_mas_cercano] < 0.45:
        return indice_mas_cercano
    return None


def base64_a_imagen(base64_string):
    img_data = base64.b64decode(base64_string)
    np_arr = np.frombuffer(img_data, np.uint8)
    imagen = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return imagen

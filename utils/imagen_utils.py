import face_recognition
import numpy as np
import tempfile

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

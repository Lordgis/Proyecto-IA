import os

# Configuración general
DEBUG = True

# Claves de Firebase (reemplazar con tus propias claves reales si corresponde)
FIREBASE_CONFIG = {
    "apiKey": os.getenv("FIREBASE_API_KEY", "your-api-key"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", "your-project.firebaseapp.com"),
    "databaseURL": os.getenv("FIREBASE_DB_URL", "https://your-project.firebaseio.com"),
    "storageBucket": os.getenv("FIREBASE_BUCKET", "your-project.appspot.com"),
    "serviceAccount": os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "path/to/serviceAccountKey.json")
}

# Parámetros de reconocimiento facial
FACE_MATCH_THRESHOLD = 0.6

class Usuario:
    def __init__(self, uid, nombre, correo, embedding, rol="estudiante"):
        self.uid = uid
        self.nombre = nombre
        self.correo = correo
        self.embedding = embedding
        self.rol = rol

from flask import Flask
from flask_cors import CORS

from controllers.registro_controller import registrar_usuario
from controllers.verificacion_controller import verificar_rostro
from controllers.usuarios_controller import listar_usuarios, listar_asistencias, listar_alertas

app = Flask(__name__)
CORS(app)

# Rutas
app.add_url_rule('/registrar', view_func=registrar_usuario, methods=['POST'])
app.add_url_rule('/verificar', view_func=verificar_rostro, methods=['POST'])
app.add_url_rule('/usuarios', view_func=listar_usuarios, methods=['GET'])
app.add_url_rule('/asistencias', view_func=listar_asistencias, methods=['GET'])
app.add_url_rule('/alertas', view_func=listar_alertas, methods=['GET'])

if __name__ == '__main__':
    app.run(debug=True, port=5000)

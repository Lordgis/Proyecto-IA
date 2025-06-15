from flask import Flask, send_from_directory
from flask_cors import CORS
import os

from controllers.registro_controller import registrar_usuario
from controllers.verificacion_controller import verificar_rostro
from controllers.usuarios_controller import usuario_bp, listar_usuarios, listar_asistencias, editar_usuario, eliminar_usuario, listar_alertas
from controllers.asistencia_controller import asistencia_bp, procesar

app = Flask(__name__)
CORS(app)

# Carpeta donde se subirán las imágenes
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static', 'Img')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Rutas para registro y verificación (fuera del blueprint)
app.add_url_rule('/registrar', view_func=registrar_usuario, methods=['POST'])
app.add_url_rule('/verificar', view_func=verificar_rostro, methods=['POST'])


# Registro de blueprints
app.register_blueprint(usuario_bp, url_prefix="/usuario")
app.register_blueprint(asistencia_bp, url_prefix="/asistencia")

# Rutas independientes para listar datos
app.add_url_rule('/usuarios', view_func=listar_usuarios, methods=['GET'])
app.add_url_rule('/asistencias', view_func=listar_asistencias, methods=['GET'])
app.add_url_rule('/alertas', view_func=listar_alertas, methods=['GET'])
app.add_url_rule('/editar_usuario', view_func=editar_usuario, methods=['GET'])
app.add_url_rule('/eliminar_usuario', view_func=eliminar_usuario, methods=['GET'])

@app.route('/Img/<filename>')
def obtener_imagen(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True, port=5000)

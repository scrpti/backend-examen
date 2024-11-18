import os

from dotenv import load_dotenv
from flask import Flask
from service import tareas_bp
from service import colaboradores_bp

load_dotenv()

app = Flask(__name__)

# Registrar los microservicios como Blueprints
app.register_blueprint(tareas_bp, url_prefix="/tareas")
app.register_blueprint(colaboradores_bp, url_prefix="/colaboradores")

@app.route("/")
def main_route():
    return f"<a href='http://127.0.0.1:{os.getenv('SERVICE_PORT_MAIN')}/tareas'>Ver tareas</a>"

# Ejecutar la aplicación Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("SERVICE_PORT_MAIN"))
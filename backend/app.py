from flask import Flask
from routes.estatisticas_router import estatisticas_bp
from routes.operadoras_router import operadoras_bp

app = Flask(__name__)
app.register_blueprint(operadoras_bp)
app.register_blueprint(estatisticas_bp)
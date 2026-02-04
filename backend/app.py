from flask import Flask
from flask_cors import CORS
from routes.estatisticas_router import estatisticas_bp
from routes.operadoras_router import operadoras_bp

app = Flask(__name__)
CORS(app)
app.register_blueprint(operadoras_bp)
app.register_blueprint(estatisticas_bp)

if __name__ == "__main__": app.run(debug=True)
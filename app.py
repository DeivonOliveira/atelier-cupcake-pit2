from flask import Flask
from controllers.routes import api
from models.database import init_db
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "atelier-cupcake-gourmet-secret-2026")
    
    # Inicializa e migra automaticamente o banco de dados sem perder conexões ou dados
    init_db()
    
    # Registra as rotas principais
    app.register_blueprint(api)
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)

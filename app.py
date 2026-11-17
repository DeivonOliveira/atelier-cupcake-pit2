import os
from flask import Flask
from models.database import init_db
from controllers.routes import api


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "atelier-cupcake-pit2-key")
    init_db()
    app.register_blueprint(api)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

import os

from flask import Flask
from dotenv import load_dotenv

from routes.student_routes import student_bp


load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv(
        "FLASK_SECRET_KEY",
        "dev-secret-key"
    )

    app.register_blueprint(student_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
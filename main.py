import os

from dotenv import load_dotenv
from flask import Flask, app
from flasgger import Swagger

from routes.student_routes import student_bp
from routes.auth_routes import auth_bp

load_dotenv()


def create_app():
    app = Flask(
        __name__,
        static_folder=None,
        template_folder=None
    )

    app.config["SECRET_KEY"] = os.getenv(
        "FLASK_SECRET_KEY",
        "dev-secret-key"
    )

    Swagger(
        app,
        config={
            "headers": [],
            "specs": [
                {
                    "endpoint": "apispec_1",
                    "route": "/api/swagger.json",
                    "rule_filter": lambda rule: (
                        rule.endpoint != "auth.oauth_callback"
                    ),
                    "model_filter": lambda tag: True
                }
            ],
            "swagger_ui": True,
            "specs_route": "/api/swagger/"
        },
        template={
            "info": {
                "title": "Student Management API",
                "description": "CRUD API for managing students",
                "version": "1.0.0"
            },
            "definitions": {
                "Student": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "example": 1},
                        "name": {"type": "string", "example": "Ali Khan"},
                        "email": {"type": "string", "example": "ali@example.com"},
                        "age": {"type": "integer", "example": 21, "nullable": True},
                        "course": {"type": "string", "example": "Computer Science", "nullable": True},
                        "created_at": {"type": "string", "format": "date-time"}
                    }
                },
                "StudentInput": {
                    "type": "object",
                    "required": ["name", "email"],
                    "properties": {
                        "name": {"type": "string", "example": "Ali Khan"},
                        "email": {"type": "string", "example": "ali@example.com"},
                        "age": {"type": "integer", "example": 21, "nullable": True},
                        "course": {"type": "string", "example": "Computer Science", "nullable": True}
                    }
                },
                "StudentPatch": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "example": "Ali Khan"},
                        "email": {"type": "string", "example": "ali@example.com"},
                        "age": {"type": "integer", "example": 21, "nullable": True},
                        "course": {"type": "string", "example": "Computer Science", "nullable": True}
                    }
                }
            },
            "securityDefinitions": {
                "bearerAuth": {
                    "type": "apiKey",
                    "name": "Authorization",
                    "in": "header",
                    "description": "Enter: Bearer <Supabase access token>"
                }
            }
        }
    )

    app.register_blueprint(student_bp)
    app.register_blueprint(auth_bp)

    @app.route("/")
    def home():
        return {
            "message": "Student Management API is running",
            "status": "success",
            "documentation": "/api/swagger/"
        }

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
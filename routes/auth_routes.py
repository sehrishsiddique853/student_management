from flask import Blueprint

from controllers.auth_controller import (
    register,
    login,
    current_user
)
from middleware.auth_middleware import require_auth


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


auth_bp.add_url_rule(
    "/register",
    endpoint="register",
    view_func=register,
    methods=["POST"]
)


auth_bp.add_url_rule(
    "/me",
    endpoint="me",
    view_func=require_auth(current_user),
    methods=["GET"]
)


auth_bp.add_url_rule(
    "/login",
    endpoint="login",
    view_func=login,
    methods=["POST"]
)
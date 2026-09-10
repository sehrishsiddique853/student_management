from flask import Blueprint

from controllers.auth_controller import (
    register,
    login,
    current_user,
    change_password,
    forgot_password,
    oauth_callback
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


auth_bp.add_url_rule(
    "/change-password",
    endpoint="change_password",
    view_func=require_auth(change_password),
    methods=["POST"]
)


auth_bp.add_url_rule(
    "/forgot-password",
    endpoint="forgot_password",
    view_func=forgot_password,
    methods=["POST"]
)


auth_bp.add_url_rule(
    "/oauth/callback",
    endpoint="oauth_callback",
    view_func=oauth_callback,
    methods=["GET"]
)

from flask import Blueprint

from controllers.auth_controller import (
    register,
    login,
    oauth_start,
    oauth_callback_get,
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
    "/oauth/<provider>",
    endpoint="oauth_start",
    view_func=oauth_start,
    methods=["GET"]
)


auth_bp.add_url_rule(
    "/oauth/callback",
    endpoint="oauth_callback",
    view_func=oauth_callback_get,
    methods=["GET"]
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
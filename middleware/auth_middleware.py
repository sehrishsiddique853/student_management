from functools import wraps

from flask import g, jsonify, request

from database import SUPABASE_KEY, SUPABASE_URL, supabase
from supabase import create_client


def require_auth(view_func):
	@wraps(view_func)
	def wrapped(*args, **kwargs):
		authorization = request.headers.get("Authorization", "")
		scheme, _, token = authorization.partition(" ")

		if scheme.lower() != "bearer" or not token.strip():
			return jsonify({
				"error": "Authorization header must use a Bearer token"
			}), 401

		try:
			user_response = supabase.auth.get_user(token.strip())
			if not user_response or not user_response.user:
				raise ValueError("Invalid access token")
			g.current_user = user_response.user
			database_client = create_client(SUPABASE_URL, SUPABASE_KEY)
			database_client.postgrest.auth(token.strip())
			g.database_client = database_client
		except Exception:
			return jsonify({"error": "Invalid or expired access token"}), 401

		return view_func(*args, **kwargs)

	return wrapped

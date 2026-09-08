import base64
import hashlib
import os
import secrets
from urllib.parse import urlencode

from flask import g, jsonify, redirect, request, session
from database import supabase


OAUTH_PROVIDERS = {"google", "github", "azure", "facebook", "apple"}


def oauth_start(provider):
    """
    Start OAuth login
    ---
    tags:
      - Authentication
    parameters:
      - in: path
        name: provider
        required: true
        type: string
        enum: [google, github, azure, facebook, apple]
      - in: query
        name: redirect_to
        required: false
        type: string
        description: OAuth callback URL. Omit this value to use OAUTH_REDIRECT_URL.
        example: https://studentmanagement-ivory.vercel.app/auth/oauth/callback
    responses:
      302:
        description: Redirect to the OAuth provider
      400:
        description: Unsupported provider
    """
    provider = provider.lower()
    if provider not in OAUTH_PROVIDERS:
        return jsonify({"error": "Unsupported OAuth provider"}), 400

    redirect_to = request.args.get("redirect_to") or os.getenv(
        "OAUTH_REDIRECT_URL",
        f"{request.host_url.rstrip('/')}/auth/oauth/callback"
    )
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode("ascii")
    params = urlencode({
        "provider": provider,
        "redirect_to": redirect_to,
        "code_challenge": challenge,
        "code_challenge_method": "S256"
    })

    session["oauth_code_verifier"] = verifier
    session["oauth_redirect_to"] = redirect_to
    authorization_url = (
      f"{os.environ['SUPABASE_URL'].rstrip('/')}/auth/v1/authorize?{params}"
    )
    return redirect(authorization_url)


def oauth_callback_get():
    """
    Complete browser OAuth callback
    ---
    tags:
      - Authentication
    parameters:
      - in: query
        name: code
        required: true
        type: string
      - in: query
        name: error
        required: false
        type: string
    responses:
      200:
        description: OAuth login successful
      400:
        description: Missing OAuth code
      401:
        description: OAuth code exchange failed
    """
    return _exchange_oauth_code(request.args)


def _exchange_oauth_code(data):
    code = data.get("code")
    verifier = data.get("code_verifier") or session.get("oauth_code_verifier")
    redirect_to = data.get("redirect_to") or session.get("oauth_redirect_to")

    if not code or not verifier:
        return jsonify({
            "error": "code and code_verifier are required"
        }), 400

    try:
        response = supabase.auth.exchange_code_for_session({
            "auth_code": code,
            "code_verifier": verifier,
            "redirect_to": redirect_to
        })
        session.pop("oauth_code_verifier", None)
        session.pop("oauth_redirect_to", None)
        return _session_response(response, "OAuth login successful")
    except Exception:
        return jsonify({"error": "OAuth code exchange failed"}), 401


def current_user():
    """
    Get the authenticated user
    ---
    tags:
      - Authentication
    security:
      - bearerAuth: []
    responses:
      200:
        description: Authenticated user
      401:
        description: Invalid or expired access token
    """
    user = g.current_user
    return jsonify({"user": _user_payload(user)})


def _user_payload(user):
    metadata = user.user_metadata or {}
    return {
        "id": str(user.id),
        "email": user.email,
        "name": metadata.get("name")
    }


def _session_response(response, message):
    if not response.user or not response.session:
        raise ValueError("Supabase returned no session")
    return jsonify({
        "message": message,
        "user": _user_payload(response.user),
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token
    })


def register():
    """
    Register a new user
    ---
    tags:
      - Authentication
    consumes:
      - application/json
    parameters:
      - in: body
        name: credentials
        required: true
        schema:
          type: object
          required:
            - name
            - email
            - password
          properties:
            name:
              type: string
              example: Sehrish Siddique
            email:
              type: string
              example: sehrish@example.com
            password:
              type: string
              example: StrongPassword123
    responses:
      201:
        description: User registered successfully
      400:
        description: Invalid request
      409:
        description: User already exists
      429:
        description: Supabase email rate limit exceeded
      500:
        description: Registration failed
    """

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object"
        }), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({
            "error": "Name, email and password are required"
        }), 400

    name = name.strip()
    email = email.strip().lower()

    if len(password) < 6:
        return jsonify({
            "error": "Password must contain at least 6 characters"
        }), 400

    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "name": name
                }
            }
        })

        user = response.user
        session = response.session

        result = {
            "message": "User registered successfully",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": name
            }
        }

        if session:
            result["access_token"] = session.access_token
            result["refresh_token"] = session.refresh_token

        return jsonify(result), 201

    except Exception as error:

        message = str(error)

        if "already registered" in message.lower():
            return jsonify({
                "error": "User already registered"
            }), 409

        # Convert Supabase's email rate-limit error into a clear API response.
        if "rate limit" in message.lower():
          return jsonify({
        "error": "Registration email rate limit exceeded. Try again later."
          }), 429

        return jsonify({
            "error": message
        }), 500


def login():
    """
    Login user
    ---
    tags:
      - Authentication
    consumes:
      - application/json
    parameters:
      - in: body
        name: credentials
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: sehrish@example.com
            password:
              type: string
              example: StrongPassword123
    responses:
      200:
        description: Login successful
      400:
        description: Email and password are required
      401:
        description: Invalid credentials
    """

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object"
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required"
        }), 400

    email = email.strip().lower()

    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        return jsonify({
            "message": "Login successful",
            "user": {
                "id": str(response.user.id),
                "email": response.user.email,
                "name": (
                    response.user.user_metadata.get("name")
                    if response.user.user_metadata
                    else None
                )
            },
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }), 200

    except Exception:
        return jsonify({
            "error": "Invalid email or password"
        }), 401
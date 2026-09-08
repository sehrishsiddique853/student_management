from flask import g, jsonify, request
from database import supabase


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
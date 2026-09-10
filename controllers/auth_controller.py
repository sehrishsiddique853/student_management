import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

import resend
from flask import current_app, g, jsonify, request
from resend.exceptions import ResendError

from database import SUPABASE_KEY, SUPABASE_URL, admin_supabase, supabase
from supabase import create_client


RESET_OTP_TABLE = "password_reset_otps"
RESET_OTP_MINUTES = 10


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


def change_password():
    """Change the password for the authenticated user.
    ---
    tags:
      - Authentication
    security:
      - bearerAuth: []
    consumes:
      - application/json
    parameters:
      - in: body
        name: credentials
        required: true
        schema:
          type: object
          required:
            - current_password
            - new_password
          properties:
            current_password:
              type: string
              format: password
              example: OldPassword123
            new_password:
              type: string
              format: password
              minLength: 6
              example: NewPassword123
    responses:
      200:
        description: Password changed successfully
      400:
        description: Invalid request or password policy violation
      401:
        description: Invalid current password or access token
    """
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
      return jsonify({"error": "Request body must be a JSON object"}), 400

    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if not current_password or not new_password:
        return jsonify({
            "error": "Current password and new password are required"
        }), 400

    if not isinstance(current_password, str) or not isinstance(new_password, str):
        return jsonify({
            "error": "Current password and new password must be strings"
        }), 400

    if len(new_password) < 6:
        return jsonify({
            "error": "Password must contain at least 6 characters"
        }), 400

    if current_password == new_password:
        return jsonify({
            "error": "New password must be different from current password"
        }), 400

    try:
        auth_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        auth_client.auth.sign_in_with_password({
            "email": g.current_user.email,
            "password": current_password
        })
        auth_client.auth.update_user({"password": new_password})
        return jsonify({"message": "Password changed successfully"}), 200
    except Exception:
        return jsonify({"error": "Current password is incorrect"}), 401


def _otp_hash(email, otp):
    secret = current_app.config["SECRET_KEY"].encode()
    value = f"{email}:{otp}".encode()
    return hmac.new(secret, value, hashlib.sha256).hexdigest()


def _find_auth_user(email):
    users = admin_supabase.auth.admin.list_users()
    users = getattr(users, "users", users) or []
    for user in users:
        if (user.email or "").lower() == email:
            return user
    return None


def _send_reset_otp(email, otp):
    resend.api_key = os.getenv("RESEND_API_KEY", "")
    sender = os.getenv("RESEND_FROM_EMAIL", "")
    if not resend.api_key or not sender:
        raise RuntimeError(
            "RESEND_API_KEY and RESEND_FROM_EMAIL must be configured"
        )

    resend.Emails.send({
      "from": sender,
      "to": [email],
      "subject": "Your password reset code",
      "text": (
        f"Your password reset code is {otp}. "
        f"It expires in {RESET_OTP_MINUTES} minutes."
      ),
      "html": (
        "<p>Your password reset code is:</p>"
        f"<p style='font-size:24px'><strong>{otp}</strong></p>"
        f"<p>This code expires in {RESET_OTP_MINUTES} minutes.</p>"
      )
    })


def _forgot_password_with_supabase_recovery(email, otp, new_password):
  return jsonify({
    "error": (
      "Password reset OTP is not configured. "
      "Set SUPABASE_SERVICE_ROLE_KEY and restart the Flask server."
    )
  }), 503


def forgot_password():
  """Send an OTP, or verify it and reset the user's password.
  ---
  tags:
    - Authentication
  consumes:
    - application/json
  parameters:
    - in: body
      name: password_reset
      required: true
      schema:
        type: object
        required:
          - email
        properties:
          email:
            type: string
            format: email
            example: user@example.com
          otp:
            type: string
            pattern: '^\\d{6}$'
            example: '123456'
          new_password:
            type: string
            format: password
            minLength: 6
            example: NewPassword123
      description: |-
        Send an OTP with only email. Verify the OTP and reset the password by
        sending email, otp, and new_password.
  responses:
    200:
      description: OTP sent or password reset successfully
    400:
      description: Invalid request, OTP, or expired OTP
    502:
      description: Password reset email could not be sent
  """
  data = request.get_json(silent=True)

  if not isinstance(data, dict):
    return jsonify({"error": "Request body must be a JSON object"}), 400

  email = data.get("email")
  otp = data.get("otp")
  new_password = data.get("new_password")

  if not isinstance(email, str) or not email.strip():
    return jsonify({"error": "Email is required"}), 400

  email = email.strip().lower()
  if not admin_supabase:
    return _forgot_password_with_supabase_recovery(email, otp, new_password)

  if not otp and not new_password:
    user = _find_auth_user(email)
    if not user:
      return jsonify({
        "message": "If an account exists, a reset code has been sent"
      }), 200

    code = str(secrets.randbelow(900000) + 100000)
    expires_at = datetime.now(timezone.utc) + timedelta(
      minutes=RESET_OTP_MINUTES
    )

    try:
      _send_reset_otp(email, code)
      admin_supabase.table(RESET_OTP_TABLE).delete().eq(
        "email", email
      ).execute()
      admin_supabase.table(RESET_OTP_TABLE).insert({
        "user_id": str(user.id),
        "email": email,
        "otp_hash": _otp_hash(email, code),
        "expires_at": expires_at.isoformat(),
        "used": False
      }).execute()
    except ResendError:
      return jsonify({"error": "Unable to send password reset email"}), 502
    except Exception as error:
      current_app.logger.exception("Password reset request failed")
      return jsonify({"error": str(error)}), 500

    return jsonify({
      "message": "If an account exists, a reset code has been sent"
    }), 200

  if not otp or not new_password:
    return jsonify({
      "error": "Email, otp and new_password are required to reset password"
    }), 400

  if not isinstance(otp, str) or not otp.isdigit() or len(otp) != 6:
    return jsonify({"error": "OTP must be a 6-digit code"}), 400

  if not isinstance(new_password, str) or len(new_password) < 6:
    return jsonify({
      "error": "Password must contain at least 6 characters"
    }), 400

  try:
    record_response = admin_supabase.table(RESET_OTP_TABLE).select(
      "*"
    ).eq("email", email).eq("used", False).order(
      "created_at", desc=True
    ).limit(1).execute()
    record = (record_response.data or [None])[0]

    if not record or datetime.fromisoformat(
      record["expires_at"].replace("Z", "+00:00")
    ) <= datetime.now(timezone.utc):
      return jsonify({"error": "OTP is invalid or expired"}), 400

    if not hmac.compare_digest(record["otp_hash"], _otp_hash(email, otp)):
      return jsonify({"error": "OTP is invalid or expired"}), 400

    admin_supabase.auth.admin.update_user_by_id(
      record["user_id"],
      {"password": new_password}
    )
    admin_supabase.table(RESET_OTP_TABLE).update({
      "used": True
    }).eq("id", record["id"]).execute()
    return jsonify({"message": "Password reset successfully"}), 200
  except Exception:
    current_app.logger.exception("Password reset verification failed")
    return jsonify({"error": "Unable to reset password"}), 500


def oauth_callback():
  error = request.args.get("error")
  error_description = request.args.get("error_description")

  if error:
    return (
      "<h1>Password reset link failed</h1>"
      f"<p>{error_description or error}</p>"
      "<p>Please request a new password reset email and open the latest link.</p>"
    ), 400

  return (
    "<h1>Password reset link opened</h1>"
    "<p>If this page was opened from a Supabase recovery email, copy the "
    "access_token and refresh_token from the browser URL after the # symbol. "
    "For a numeric OTP flow, configure SUPABASE_SERVICE_ROLE_KEY instead.</p>"
  ), 200

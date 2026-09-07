from flask import jsonify, request

from models.student_model import StudentModel


def list_students():
    """
        List all students
        ---
        tags:
            - Students
        responses:
            200:
                description: A list of students
                schema:
                    type: array
                    items:
                        $ref: '#/definitions/Student'
            500:
                description: Database error
    """
    try:
        return jsonify(StudentModel.get_all())
    except Exception as error:
        return jsonify({"error": str(error)}), 500


def create_student():
    """
        Create a student
        ---
        tags:
            - Students
        consumes:
            - application/json
        parameters:
            - in: body
              name: student
              required: true
              schema:
                $ref: '#/definitions/StudentInput'
        responses:
            201:
                description: Student created successfully
                schema:
                    $ref: '#/definitions/Student'
            400:
                description: Invalid request body
            409:
                description: Email already exists
            500:
                description: Database error
    """
    data, error = _student_data_from_request()
    if error:
        return jsonify({"error": error}), 400

    try:
        students = StudentModel.create(data)
        return jsonify(students[0] if students else data), 201
    except Exception as error:
        return _database_error(error)


def get_student(student_id):
    """
        Get a student
        ---
        tags:
            - Students
        parameters:
            - in: path
              name: student_id
              required: true
              type: integer
        responses:
            200:
                description: Student returned successfully
                schema:
                    $ref: '#/definitions/Student'
            404:
                description: Student not found
            500:
                description: Database error
    """
    student = StudentModel.get_by_id(student_id)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(student)


def update_student(student_id):
    """
        Update a student
        ---
        tags:
            - Students
        consumes:
            - application/json
        parameters:
            - in: path
              name: student_id
              required: true
              type: integer
            - in: body
              name: student
              required: true
              schema:
                $ref: '#/definitions/StudentInput'
        responses:
            200:
                description: Student updated successfully
                schema:
                    $ref: '#/definitions/Student'
            400:
                description: Invalid request body
            404:
                description: Student not found
            409:
                description: Email already exists
            500:
                description: Database error
    """
    student = StudentModel.get_by_id(student_id)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    data, error = _student_data_from_request(partial=True)
    if error:
        return jsonify({"error": error}), 400

    try:
        students = StudentModel.update(student_id, data)
        return jsonify(students[0] if students else {**student, **data})
    except Exception as error:
        return _database_error(error)


def delete_student(student_id):
    """
        Delete a student
        ---
        tags:
            - Students
        parameters:
            - in: path
              name: student_id
              required: true
              type: integer
        responses:
            204:
                description: Student deleted successfully
            404:
                description: Student not found
            500:
                description: Database error
    """
    try:
        if not StudentModel.get_by_id(student_id):
            return jsonify({"error": "Student not found"}), 404

    except Exception as error:
        return _database_error(error)

    try:
        StudentModel.delete(student_id)
        return "", 204
    except Exception as error:
        return _database_error(error)


def _student_data_from_request(partial=False):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object"

    allowed_fields = {"name", "email", "age", "course"}
    unknown_fields = set(data) - allowed_fields
    if unknown_fields:
        return None, f"Unknown fields: {', '.join(sorted(unknown_fields))}"

    if not partial and ("name" not in data or "email" not in data):
        return None, "Name and email are required"

    if "name" in data:
        if not isinstance(data["name"], str) or not data["name"].strip():
            return None, "Name is required"
        data["name"] = data["name"].strip()

    if "email" in data:
        if not isinstance(data["email"], str) or not data["email"].strip():
            return None, "Email is required"
        data["email"] = data["email"].strip()

    if "age" in data and data["age"] is not None:
        if isinstance(data["age"], bool) or not isinstance(data["age"], int):
            return None, "Age must be an integer or null"
        if data["age"] < 0:
            return None, "Age cannot be negative"

    if "course" in data and data["course"] is not None:
        if not isinstance(data["course"], str):
            return None, "Course must be a string or null"
        data["course"] = data["course"].strip()

    return data, None


def _database_error(error):
    message = str(error)
    status_code = 409 if "duplicate" in message.lower() or "unique" in message.lower() else 500
    return jsonify({"error": message}), status_code
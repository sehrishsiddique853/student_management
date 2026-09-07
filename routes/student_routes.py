from flask import Blueprint

from controllers.student_controller import (
    list_students,
    create_student,
    edit_student,
    delete_student
)


student_bp = Blueprint(
    "students",
    __name__
)


student_bp.add_url_rule(
    "/students",
    endpoint="list",
    view_func=list_students,
    methods=["GET"]
)


student_bp.add_url_rule(
    "/students",
    endpoint="create",
    view_func=create_student,
    methods=["POST"]
)


student_bp.add_url_rule(
    "/students/<int:student_id>",
    endpoint="edit",
    view_func=edit_student,
    methods=["GET", "PUT", "PATCH"]
)


student_bp.add_url_rule(
    "/students/<int:student_id>",
    endpoint="delete",
    view_func=delete_student,
    methods=["DELETE"]
)
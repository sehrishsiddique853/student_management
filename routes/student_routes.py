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
    "/",
    endpoint="index",
    view_func=list_students,
    methods=["GET"]
)


student_bp.add_url_rule(
    "/students/create",
    endpoint="create",
    view_func=create_student,
    methods=["GET", "POST"]
)


student_bp.add_url_rule(
    "/students/<int:student_id>/edit",
    endpoint="edit",
    view_func=edit_student,
    methods=["GET", "POST"]
)


student_bp.add_url_rule(
    "/students/<int:student_id>/delete",
    endpoint="delete",
    view_func=delete_student,
    methods=["POST"]
)
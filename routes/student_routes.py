from flask import Blueprint

from controllers.student_controller import (
    list_students,
    create_student,
    get_student,
    update_student,
    patch_student,
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
    endpoint="get",
    view_func=get_student,
    methods=["GET"]
)


student_bp.add_url_rule(
    "/students/<int:student_id>",
    endpoint="update",
    view_func=update_student,
    methods=["PUT"]
)


student_bp.add_url_rule(
    "/students/<int:student_id>",
    endpoint="patch",
    view_func=patch_student,
    methods=["PATCH"]
)


student_bp.add_url_rule(
    "/students/<int:student_id>",
    endpoint="delete",
    view_func=delete_student,
    methods=["DELETE"]
)
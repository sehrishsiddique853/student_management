from flask import render_template, request, redirect, url_for, flash

from models.student_model import StudentModel


def list_students():
    students = StudentModel.get_all()

    return render_template(
        "students/index.html",
        students=students
    )


def create_student():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        age = request.form.get("age", "").strip()
        course = request.form.get("course", "").strip()

        if not name:
            flash("Name is required.", "danger")
            return render_template(
                "students/form.html",
                mode="create"
            )

        if not email:
            flash("Email is required.", "danger")
            return render_template(
                "students/form.html",
                mode="create"
            )

        try:
            age = int(age) if age else None

            StudentModel.create({
                "name": name,
                "email": email,
                "age": age,
                "course": course
            })

            flash(
                "Student created successfully.",
                "success"
            )

            return redirect(
                url_for("students.index")
            )

        except ValueError:
            flash(
                "Age must be a valid number.",
                "danger"
            )

        except Exception as error:
            print(error)

            flash(
                f"Could not create student: {error}",
                "danger"
            )

    return render_template(
        "students/form.html",
        mode="create"
    )


def edit_student(student_id):
    student = StudentModel.get_by_id(student_id)

    if not student:
        flash("Student not found.", "danger")

        return redirect(
            url_for("students.index")
        )

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        age = request.form.get("age", "").strip()
        course = request.form.get("course", "").strip()

        if not name or not email:
            flash(
                "Name and email are required.",
                "danger"
            )

            return render_template(
                "students/form.html",
                mode="edit",
                student=student
            )

        try:
            age = int(age) if age else None

            StudentModel.update(
                student_id,
                {
                    "name": name,
                    "email": email,
                    "age": age,
                    "course": course
                }
            )

            flash(
                "Student updated successfully.",
                "success"
            )

            return redirect(
                url_for("students.index")
            )

        except ValueError:
            flash(
                "Age must be a valid number.",
                "danger"
            )

        except Exception as error:
            print(error)

            flash(
                "Could not update student.",
                "danger"
            )

    return render_template(
        "students/form.html",
        mode="edit",
        student=student
    )


def delete_student(student_id):
    student = StudentModel.get_by_id(student_id)

    if not student:
        flash(
            "Student not found.",
            "danger"
        )

        return redirect(
            url_for("students.index")
        )

    try:
        StudentModel.delete(student_id)

        flash(
            "Student deleted successfully.",
            "success"
        )

    except Exception as error:
        print(error)

        flash(
            "Could not delete student.",
            "danger"
        )

    return redirect(
        url_for("students.index")
    )
from database import get_database_client


class StudentModel:
    TABLE = "students"

    @classmethod
    def get_all(cls):
        response = (
            get_database_client().table(cls.TABLE)
            .select("*")
            .order("id", desc=False)
            .execute()
        )
        return response.data or []

    @classmethod
    def get_by_id(cls, student_id):
        response = (
            get_database_client().table(cls.TABLE)
            .select("*")
            .eq("id", student_id)
            .limit(1)
            .execute()
        )

        if response.data:
            return response.data[0]

        return None

    @classmethod
    def create(cls, data):
        response = (
            get_database_client().table(cls.TABLE)
            .insert(data)
            .execute()
        )
        return response.data

    @classmethod
    def update(cls, student_id, data):
        response = (
            get_database_client().table(cls.TABLE)
            .update(data)
            .eq("id", student_id)
            .execute()
        )
        return response.data

    @classmethod
    def delete(cls, student_id):
        response = (
            get_database_client().table(cls.TABLE)
            .delete()
            .eq("id", student_id)
            .execute()
        )
        return response.data
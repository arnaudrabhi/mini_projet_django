from django.contrib.auth.backends import ModelBackend
from .models import Teacher


class TeacherBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            teacher = Teacher.objects.get(email=username)
        except Teacher.DoesNotExist:
            return None

        if teacher.check_password(password):
            return teacher
        return None

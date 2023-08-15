from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.


class Teacher(AbstractUser):


class Equipment(models.Model):
    name = models.CharField(
        max_length=126,
        null=False,
        help_text="Nom de l'équipement",
    )


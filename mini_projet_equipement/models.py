from django.contrib.auth.models import AbstractUser
from django.db import models


class Equipment(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    location_room = models.CharField(max_length=10, default='001')
    owner = models.ForeignKey('Teacher', on_delete=models.SET_NULL, null=True)
    holder = models.ForeignKey('Teacher', on_delete=models.SET_NULL, related_name='held_equipment', null=True)
    accessories = models.ManyToManyField('Accessory', blank=True)

    def __str__(self):
        return self.name


# Create your models here.
class Teacher(AbstractUser):
    civility = models.CharField(max_length=10)
    equipment = models.ManyToManyField(Equipment, related_name='teachers', through='HolderHistory')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Purchase(models.Model):
    id = models.AutoField(primary_key=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    user = models.ForeignKey('Teacher', on_delete=models.SET_NULL, null=True)
    from_budget = models.CharField(max_length=255)
    purchase_date = models.DateField()


class HolderHistory(models.Model):
    id = models.AutoField(primary_key=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    old_holder = models.ForeignKey('Teacher', on_delete=models.SET_NULL, related_name='old_holder_history',
                                   null=True)
    new_holder = models.ForeignKey('Teacher', on_delete=models.SET_NULL, related_name='new_holder_history',
                                   null=True)
    are_accessories_present = models.BooleanField()
    comment = models.TextField()
    holding_change_date = models.DateField()
    change_reason = models.TextField()
    location = models.CharField(max_length=255)


class Accessory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    condition = models.CharField(max_length=255)
    comment = models.TextField()

    def __str__(self):
        return self.name

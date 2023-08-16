from django.contrib.auth.models import AbstractUser, Permission, Group
from django.db import models


class Equipment(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    location_room = models.CharField(max_length=10, default='001')
    owner = models.ForeignKey('Teacher', on_delete=models.SET_NULL, related_name='owned_equipment', null=True)
    holder = models.ForeignKey('Teacher', on_delete=models.SET_NULL, related_name='held_equipment', null=True)
    accessories = models.ManyToManyField('Accessory', blank=True, related_name='equipment_accessories')

    def __str__(self):
        return self.name


# Create your models here.
class Teacher(AbstractUser):
    civility = models.CharField(max_length=10)
    equipment = models.ManyToManyField(Equipment, related_name='teachers', through='HolderHistory', through_fields=('new_holder', 'equipment'))
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='teachers_user_permissions',
        help_text='Specific permissions for this teacher.',
    )
    groups = models.ManyToManyField(Group, verbose_name='groups', blank=True, related_name='teacher_groups')

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
    old_holder = models.ForeignKey(Teacher, on_delete=models.SET_NULL, related_name='old_holder_history', null=True)
    new_holder = models.ForeignKey(Teacher, on_delete=models.SET_NULL, related_name='new_holder_history', null=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)

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

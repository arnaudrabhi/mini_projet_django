from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser, Permission, Group, PermissionsMixin
from django.db import models

from mini_projet_equipement.enums import RoomChoices


class Equipment(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    location_room = models.CharField(max_length=10, default='001')
    owner = models.ForeignKey('Teacher', on_delete=models.SET_NULL, related_name='owned_equipment', null=True)
    holder = models.ForeignKey('Teacher', on_delete=models.SET_NULL, related_name='held_equipment', null=True)
    accessories = models.ManyToManyField('Accessory', blank=True, related_name='equipment_accessories')

    def __str__(self):
        return self.name

    def get_location_room_value(self):
        try:
            return RoomChoices[self.location_room].value
        except KeyError:
            return self.location_room


class TeacherManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        teacher = self.model(email=email, **extra_fields)
        teacher.set_password(password)
        teacher.save(using=self._db)
        return teacher

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class Teacher(AbstractBaseUser, PermissionsMixin):
    civility = models.CharField(max_length=10)
    equipment = models.ManyToManyField(Equipment, related_name='teachers', through='HolderHistory',
                                       through_fields=('new_holder', 'equipment'))
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='teachers_user_permissions',
        help_text='Specific permissions for this teacher.',
    )
    groups = models.ManyToManyField(Group, verbose_name='groups', blank=True, related_name='teacher_groups')

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = TeacherManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'civility']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Purchase(models.Model):
    id = models.AutoField(primary_key=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    user = models.ForeignKey('Teacher', on_delete=models.SET_NULL, null=True)
    from_budget = models.CharField(max_length=255)
    purchase_date = models.DateField(null=True)


class HolderHistory(models.Model):
    id = models.AutoField(primary_key=True)
    old_holder = models.ForeignKey(Teacher, on_delete=models.SET_NULL, related_name='old_holder_history', null=True)
    new_holder = models.ForeignKey(Teacher, on_delete=models.SET_NULL, related_name='new_holder_history', null=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)

    are_accessories_present = models.BooleanField()
    comment = models.TextField()
    holding_change_date = models.DateTimeField()
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

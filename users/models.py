import uuid
from secrets import randbelow

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.text import slugify


def generate_user_handle_base(name, email):
    value = slugify(name or email.split('@')[0]).replace('-', '')
    return value or 'user'


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150, blank=True)
    handle = models.CharField(max_length=180, unique=True, blank=True)
    profile_image_url = models.URLField(blank=True)
    show_handle_on_leaderboard = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.handle:
            self.handle = self.generate_unique_handle()

        super().save(*args, **kwargs)

    def generate_unique_handle(self):
        base_handle = generate_user_handle_base(self.name, self.email)

        while True:
            handle = f'{base_handle}{randbelow(9000) + 1000}'

            if not User.objects.filter(handle=handle).exclude(id=self.id).exists():
                return handle

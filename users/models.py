from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

# 1. FIRST, Create a Custom Manager that knows how to create users without usernames
class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin') # Automatically make superusers admins

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

# 2. NOW, define the CustomUser model
class CustomUser(AbstractUser):
    # Remove the username field and use email instead
    username = None
    email = models.EmailField(unique=True)

    # Add custom fields
    ROLE_CHOICES = (
        ('passenger', 'Passenger'),
        ('driver', 'Driver'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='passenger')

    # Set the email as the unique identifier for authentication
    USERNAME_FIELD = 'email'
    # Email & Password are required by default. Add any other required fields here.
    REQUIRED_FIELDS = [] 

    # Tell the model to use our Custom Manager
    objects = CustomUserManager()

    def __str__(self):
        return self.email
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    username = models.CharField(max_length=300)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=300)
    phone_no = models.CharField(max_length=20)

    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'email'
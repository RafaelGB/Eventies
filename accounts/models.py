from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True,default="")
    location = models.CharField(max_length=30, blank=True,default="")
    birth_date = models.DateField(null=True, blank=True)
    def __str__(self):
        return self.username







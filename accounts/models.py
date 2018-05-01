from django.db import models
from django.contrib.auth.models import AbstractUser

def get_image_filename(instance, filename):
    primaryKey = instance.pk
    return "Users/%s/%s" % (str(primaryKey), filename)

class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True,default="")
    location = models.CharField(max_length=30, blank=True,default="")
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(
            upload_to =get_image_filename,
            default = 'none/icon_user.png',
            )
    """
    ==========================================================
                    Servicios de la clase
    ==========================================================

    """
    def __str__(self):
        return self.username







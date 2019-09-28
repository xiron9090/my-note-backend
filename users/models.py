from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    avatar = models.ImageField(upload_to='avatar/', blank=True, null=True,)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    
    class Meta:
        db_table = 'profile'
        verbose_name = 'profile'
        verbose_name_plural = 'profile'

    def __str__(self):
        return self.user.username
    
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Pet(models.Model):
    api_pet_id = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    comments = models.TextField(max_length=300)

    def __str__(self):
        return f'Pet ID: {self.api_pet_id}'

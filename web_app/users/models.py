from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser


#change the primary key to have length 7
class User(AbstractUser):
    username = models.CharField(max_length=7, primary_key=True)

    def __str__(self):
        return self.username
    
    
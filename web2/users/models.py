from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser


# Create your models here.
# class MyUser(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     plate = models.CharField(max_length=10)

#     def __str__(self):
#         return f"{self.user.username} {self.plate}"


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         MyUser.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.myuser.save()

class User(AbstractUser):
    plate = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.username} {self.plate}"
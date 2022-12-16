from django.db import models


class Cellulare(models.Model): 
  marca = models.CharField(max_length=30)
  modello = models.CharField(max_length=20)
  imei = models.CharField(max_length=30)

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
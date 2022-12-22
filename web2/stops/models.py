from django.db import models

# Create your models here.

#create a class for the stops, with stop_id as primary key(auto increment), plate, start and optional end time
class Stop(models.Model):
    stop_id = models.AutoField(primary_key=True)
    plate = models.CharField(max_length=8)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(auto_now=True, null=True)

    #return the plate number when printing the object
    def __str__(self):
        return self.plate


from django.db import models
from thingsboard_api_tools import TbApi
from users.models import User
# Create your models here.

#create a class for the stops, with stop_id as primary key(auto increment), user as foreign key, start and optional end time
class Stop(models.Model):
    stop_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)

    #return the plate number when printing the object
    def __str__(self):
        return f"{self.plate} {self.start_time} {self.end_time}"

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    stop_id = models.ForeignKey(Stop, on_delete=models.CASCADE)
    payment_time = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.stop_id} {self.payment_time} {self.amount}"



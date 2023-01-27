from django.db import models
from django.db import models
from thingsboard_api_tools import TbApi
from users.models import User
# Create your models here.

#park_model with park_id as primary key(auto increment), name, address, latitude, longitude, hour_price, total_spaces
# class Park(models.Model):
#     park_id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=50)
#     address = models.CharField(max_length=50)
#     latitude = models.DecimalField(max_digits=10, decimal_places=8)
#     longitude = models.DecimalField(max_digits=11, decimal_places=8)
#     price = models.DecimalField(max_digits=5, decimal_places=2)
#     total_spaces = models.IntegerField()

#     #return the name when printing the object
#     def __str__(self):
#         return f"{self.name} {self.address} {self.latitude} {self.longitude} {self.hour_price} {self.total_spaces}"


#create a class for the stops, with stop_id as primary key(auto increment), user as foreign key, start and optional end time
class Stop(models.Model):
    stop_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)
    park = models.CharField(max_length=50)

    #return the plate number when printing the object
    def __str__(self):
        return f"{self.user} {self.start_time} {self.end_time} {self.park}"

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    payment_time = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.stop} {self.payment_time} {self.amount}"


class Statistic(models.Model):
    statistic_id = models.AutoField(primary_key=True)
    park = models.CharField(max_length=50)
    total_income = models.DecimalField(max_digits=5, decimal_places=2)
    total_stops = models.IntegerField()
    total_active_stops = models.IntegerField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.park} {self.total_income} {self.total_stops} {self.total_active_stops} {self.date}"

class Price(models.Model):
    price_id = models.AutoField(primary_key=True)
    park = models.CharField(max_length=50)
    start_time = models.TimeField()
    end_time = models.TimeField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField(null=True)
    #day is 0 for monday, 1 for tuesday, 2 for wednesday, 3 for thursday, 4 for friday, 5 for saturday, 6 for sunday
    day = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.park} {self.start_time} {self.end_time} {self.price} {self.date} {self.day}"
from django.db import models

# Create your models here.

#park_model with park_id as primary key(auto increment), name, address, latitude, longitude, hour_price, total_spaces
class Park(models.Model):
    park_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    total_spaces = models.IntegerField()

    #return the name when printing the object
    def __str__(self):
        return f"{self.name} {self.address} {self.latitude} {self.longitude} {self.hour_price} {self.total_spaces}"

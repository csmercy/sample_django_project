from django.db import models

# Create your models here.

class Weather(models.Model):
    temperature = models.FloatField(null=True)
    humidity = models.FloatField(null=True)
    windspeed = models.FloatField(null=True)
    updated_time = models.DateTimeField( null=True )
    zipcode = models.CharField(null = True, max_length=10)

from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import Field
from django.db.models.fields.related import ForeignKey
from django.utils import timezone



# Create your models here.

class Transactions(models.Model):
    cryptocurrency = models.CharField(max_length=4)
    transaction_type = models.CharField(max_length=4)
    units = models.FloatField()
    value = models.FloatField()
    timestamp = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return(f"{self.user} completed a {self.transaction_type} transaction for {self.units} {self.cryptocurrency}")

    class Meta:
        verbose_name_plural = "Transactions"
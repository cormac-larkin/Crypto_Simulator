from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import Field
from django.db.models.fields.related import ForeignKey
from django.utils import timezone




# This model was created for the purpose of extending the base 'User' model, allowing a user's cash balance to be recorded.
class ExtendUser(models.Model):
    link = models.OneToOneField(User, on_delete=models.CASCADE)
    cash = models.DecimalField(default=10000.00, decimal_places=2, max_digits=20)

    def __str__(self):
        return self.link.username


# Model for storing transaction data
class Transactions(models.Model):
    cryptocurrency = models.CharField(max_length=5)
    transaction_type = models.CharField(max_length=4)
    units = models.DecimalField(decimal_places=8, max_digits=100)
    value = models.DecimalField(decimal_places=8, max_digits=100)
    timestamp = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return(f"{self.user} completed a {self.transaction_type} transaction for {self.units} {self.cryptocurrency} (€{self.value})")

    class Meta:
        verbose_name_plural = "Transactions"


# Model for tracking User's holdings
class Holdings(models.Model):
    cryptocurrency = models.CharField(max_length=5)
    units = models.DecimalField(decimal_places=8, max_digits=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return(f"{self.user} owns {self.units} units of {self.cryptocurrency}")

    class Meta:
        verbose_name_plural = "Holdings"
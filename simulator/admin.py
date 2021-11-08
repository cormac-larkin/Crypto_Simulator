from django.contrib import admin

from simulator.models import ExtendUser, Transactions

# Register your models here.

admin.site.register(Transactions)
admin.site.register(ExtendUser)
from django.db import models

class Price(models.Model):
    start_time = models.DateTimeField()
    price = models.DecimalField(max_digits=6, decimal_places=4)

    # currency is always EUR

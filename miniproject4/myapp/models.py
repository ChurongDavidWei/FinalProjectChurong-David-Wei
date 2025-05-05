from django.db import models

class Holding(models.Model):
    ticker = models.CharField(max_length=10)
    shares = models.FloatField()
    purchase_price = models.FloatField()
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticker} - {self.shares} shares"

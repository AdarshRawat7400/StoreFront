from django.db import models
from apps.core.models import AbstractBaseModel
from apps.users.models import Users


# Create your models here.
class Transaction(AbstractBaseModel):
    order = models.OneToOneField('store.Order', on_delete=models.CASCADE)
    transaction_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)

    def __str__(self):
        return f"Transaction - {self.order}"
    


class Payment(AbstractBaseModel):
    stripe_charge_id = models.CharField(max_length=50)
    customer = models.ForeignKey(Users, on_delete=models.CASCADE)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username



class PaymentHistory(AbstractBaseModel):
    order = models.ForeignKey('store.Order', on_delete=models.CASCADE)
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Payment - {self.order}"



class Refund(models.Model):
    order = models.ForeignKey('store.Order', on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"

from datetime import timedelta

from django.db import models
from django.utils import timezone


class TimeStampMixin(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now=True)
    modified_at = models.DateTimeField(auto_now_add=True)


class Client(TimeStampMixin, models.Model):
    name = models.CharField(max_length=255, null=False)
    client_id = models.CharField(max_length=255, unique=True, null=False)
    client_secret = models.CharField(max_length=255, null=False)
    expiry_date = models.DateTimeField(default=None)
    auth_token = models.CharField(max_length=255, default='')

    def is_expired(self):
        if self.expiry_date and timezone.now() > self.expiry_date:
            return True
        else:
            return False

    def update_auth_token(self, auth_token):
        self.auth_token = auth_token
        self.expiry_date = self.expiry_date + timedelta(minutes=5)
        self.save()

    def __str__(self):
        return self.name


class ShipmentItem(TimeStampMixin, models.Model):
    orderItemId = models.CharField(max_length=255, null=False)
    orderId = models.CharField(max_length=255, null=False)
    orderDate = models.DateTimeField(auto_now=True)
    latestDeliveryDate = models.DateTimeField(auto_now=True)
    ean = models.CharField(max_length=255, null=False)
    title = models.CharField(max_length=255, null=False)
    quantity = models.IntegerField(null=False)
    offerPrice = models.IntegerField(null=False)
    offerCondition = models.CharField(max_length=255, null=False)
    fulfilmentMethod = models.CharField(max_length=255, null=False)

    def __str__(self):
        return 'Delivery By : {}'.format(self.latestDeliveryDate)


class Transport(TimeStampMixin, models.Model):
    transportId = models.IntegerField(unique=True, null=False, db_index=True)
    transporterCode = models.CharField(max_length=255, null=False)
    trackAndTrace = models.CharField(max_length=255, null=False)

    def __str__(self):
        return '{} {}'.format(self.transporterCode, self.trackAndTrace)


class Customer(TimeStampMixin, models.Model):
    salutationCode = models.CharField(max_length=255, null=False)
    zipCode = models.CharField(max_length=255, null=False)
    countryCode = models.CharField(max_length=255, null=False)

    def __str__(self):
        return '{} {} {}'.format(self.countryCode, self.zipCode, self.salutationCode)


class Shipment(TimeStampMixin, models.Model):
    shipmentId = models.IntegerField(unique=True, null=False, db_index=True)
    shipmentDate = models.DateTimeField(null=False)
    pickUpPoint = models.BooleanField(default=True)
    shipmentItems = models.ManyToManyField(ShipmentItem, related_name='items')
    transport = models.ForeignKey(Transport, on_delete=models.CASCADE)
    customerDetails = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return 'Shipment {}'.format(self.shipmentId)

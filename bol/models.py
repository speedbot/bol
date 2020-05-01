from django.db import models


class TimeStampMixin(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now=True)
    modified_at = models.DateTimeField(auto_now_add=True)


class Client(TimeStampMixin, models.Model):
    name = models.CharField(max_length=255, null=False)
    client_id = models.CharField(max_length=255, null=False)
    client_secret = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.name
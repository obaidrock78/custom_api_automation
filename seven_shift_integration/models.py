from django.db import models
from django.utils import timezone


class CronJobRecord(models.Model):
    status = models.CharField(max_length=20, default="started")
    created_at = models.DateTimeField(default=timezone.now())

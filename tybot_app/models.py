from django.conf import settings
from django.db import models
from django.utils import timezone

# Create your models here.
class Change(models.Model):
    workflow = models.CharField(max_length=360)
    timestamp = models.DateTimeField(default=timezone.now)
    marketo_id = models.PositiveIntegerField()
    changed_field = models.CharField(max_length=360)
    old_value = models.CharField(max_length=360, blank=True, null=True)
    new_value = models.CharField(max_length=360, blank=True, null=True)

    def publish(self):
        self.timestamp = timezone.now()
        self.save()
    
    def __str__(self):
        return self.workflow + " " + str(self.timestamp)
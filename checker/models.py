from django.db import models
from django.utils import timezone

class WebsiteCheck(models.Model):
    url = models.URLField(max_length=255)
    status = models.CharField(max_length=10)  # 'up' or 'down'
    response_time = models.FloatField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    checked_at = models.DateTimeField(default=timezone.now)
    error_message = models.TextField(blank=True)
    content = models.TextField(blank=True)  # Store website content
    content_preview = models.CharField(max_length=200, blank=True)  # Short preview

    class Meta:
        ordering = ['-checked_at']

    def __str__(self):
        return f"{self.url} - {self.status} ({self.checked_at})"
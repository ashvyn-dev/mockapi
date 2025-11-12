from django.db import models


class RequestLog(models.Model):
    """Logs all requests made to mock endpoints"""

    endpoint = models.ForeignKey(
        "domains.MockEndpoint",  # Use string reference instead of direct import
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="request_logs",
    )

    # Request Details
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=1000)
    query_params = models.JSONField(default=dict, blank=True)
    request_headers = models.JSONField(default=dict, blank=True)
    request_body = models.TextField(blank=True)

    # Response Details
    response_status = models.IntegerField()
    response_headers = models.JSONField(default=dict, blank=True)
    response_body = models.TextField(blank=True)

    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    response_time_ms = models.IntegerField(
        default=0, help_text="Response time in milliseconds"
    )

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Request Log"
        verbose_name_plural = "Request Logs"
        indexes = [
            models.Index(fields=["-timestamp"]),
            models.Index(fields=["endpoint", "-timestamp"]),
        ]

    def __str__(self):
        return f"{self.method} {self.path} - {self.response_status} ({self.timestamp})"

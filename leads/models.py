import uuid

from django.db import models


class SearchJob(models.Model):
    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_DONE = "done"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_RUNNING, "Running"),
        (STATUS_DONE, "Done"),
        (STATUS_FAILED, "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.topic} ({self.status})"

    @property
    def valid_lead_count(self):
        return self.leads.filter(is_valid_email=True).count()

    @property
    def total_lead_count(self):
        return self.leads.count()


class Lead(models.Model):
    job = models.ForeignKey(SearchJob, related_name="leads", on_delete=models.CASCADE)
    source_url = models.URLField(max_length=500)
    company_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    is_valid_email = models.BooleanField(default=False)
    validation_note = models.CharField(max_length=255, blank=True)
    found_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_valid_email", "-found_at"]
        unique_together = ("job", "email", "source_url")

    def __str__(self):
        return f"{self.email or self.source_url} ({'valid' if self.is_valid_email else 'unverified'})"

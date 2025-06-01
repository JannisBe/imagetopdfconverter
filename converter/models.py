from django.db import models

class JPGUpload(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONVERTING = 'CONVERTING', 'Converting to PDF'
        SENDING = 'SENDING', 'Sending Email'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    email = models.EmailField(null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    jpeg_file = models.FileField(upload_to='uploads/jpg/')
    pdf_file = models.FileField(upload_to='uploads/pdf/', blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    error_message = models.TextField(blank=True, null=True)
    task_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.email} - {self.timestamp} ({self.status})"

    class Meta:
        ordering = ['-timestamp']

    def update_status(self, status, error_message=None):
        self.status = status
        if error_message:
            self.error_message = error_message
        self.save()

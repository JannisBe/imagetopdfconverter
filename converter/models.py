from django.db import models
from PIL import Image
from django.core.files.base import ContentFile
import io
import os

class ImageUpload(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONVERTING = 'CONVERTING', 'Converting to PDF'
        SENDING = 'SENDING', 'Sending Email'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    email = models.EmailField(null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    jpeg_file = models.FileField(upload_to='uploads/jpg/')
    _pdf_file = models.FileField(upload_to='uploads/pdf/', blank=True, null=True)
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

    @property
    def pdf_file(self):
        """Property that automatically generates PDF if it doesn't exist"""
        if self._pdf_file:
            if not self.error_message and self.status != self.Status.COMPLETED:
                self.status = self.Status.COMPLETED
                self.save()
            return self._pdf_file

        if not self._pdf_file and self.jpeg_file:
            try:
                # Open the image
                image = Image.open(self.jpeg_file)
                
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Create PDF in memory
                pdf_buffer = io.BytesIO()
                image.save(pdf_buffer, format='PDF', resolution=100.0)
                
                # Save PDF to model
                pdf_filename = os.path.splitext(os.path.basename(self.jpeg_file.name))[0] + '.pdf'
                self._pdf_file.save(pdf_filename, ContentFile(pdf_buffer.getvalue()), save=True)
                
                # Update status to COMPLETED if PDF is successfully created
                self.status = self.Status.COMPLETED
                self.save()
                
            except Exception as e:
                self.error_message = f"Error converting image to PDF: {str(e)}"
                self.status = self.Status.FAILED
                self.save()
                return None
        elif not self._pdf_file:
            return None
        
        return self._pdf_file

    def send_pdf_email(self):
        """Send the PDF file via email."""
        if not self.pdf_file:
            return False
        try:
            # Logic to send email with PDF attachment
            # This is a placeholder for the actual email sending logic
            return True
        except Exception as e:
            self.error_message = f"Error sending email: {str(e)}"
            self.save()
            return False

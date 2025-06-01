from PIL import Image
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.conf import settings
import io
import os

class JPGToPDFConverter:
    @staticmethod
    def convert_to_pdf(jpg_upload):
        """Convert JPG to PDF and store it in the model"""
        try:
            # Open the image
            image = Image.open(jpg_upload.jpeg_file)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Create PDF in memory
            pdf_buffer = io.BytesIO()
            image.save(pdf_buffer, format='PDF', resolution=100.0)
            
            # Save PDF to model
            pdf_filename = os.path.splitext(os.path.basename(jpg_upload.jpeg_file.name))[0] + '.pdf'
            jpg_upload.pdf_file.save(pdf_filename, ContentFile(pdf_buffer.getvalue()), save=True)
            
            return True
        except Exception as e:
            print(f"Error converting JPG to PDF: {str(e)}")
            return False

    @staticmethod
    def send_pdf_email(jpg_upload):
        """Send the PDF file via email"""
        try:
            subject = 'Your converted PDF file'
            message = 'Please find attached your converted PDF file.'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [jpg_upload.email]

            email = EmailMessage(
                subject,
                message,
                from_email,
                recipient_list
            )

            # Attach the PDF
            pdf_filename = os.path.basename(jpg_upload.pdf_file.name)
            email.attach_file(jpg_upload.pdf_file.path)
            
            email.send()
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False 
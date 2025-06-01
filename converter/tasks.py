from celery import shared_task
from .services import JPGToPDFConverter
from .models import JPGUpload
import logging
import time
from django.utils import timezone
from datetime import timedelta
from celery.schedules import crontab
from celery import Celery
import os

logger = logging.getLogger(__name__)

PENDING_TIMEOUT_SECONDS = 10
FILE_CLEANUP_MINUTES = 5

@shared_task
def cleanup_old_files():
    """Clean up JPG and PDF files that are older than FILE_CLEANUP_MINUTES minutes."""
    cleanup_threshold = timezone.now() - timedelta(minutes=FILE_CLEANUP_MINUTES)
    old_uploads = JPGUpload.objects.filter(timestamp__lt=cleanup_threshold)
    
    for upload in old_uploads:
        try:
            # Delete JPG file
            if upload.jpeg_file and os.path.exists(upload.jpeg_file.path):
                os.remove(upload.jpeg_file.path)
                upload.jpeg_file = None
            
            # Delete PDF file
            if upload.pdf_file and os.path.exists(upload.pdf_file.path):
                os.remove(upload.pdf_file.path)
                upload.pdf_file = None
            
            upload.save()
            logger.info(f"Cleaned up files for upload {upload.id}")
            
        except Exception as e:
            logger.error(f"Error cleaning up files for upload {upload.id}: {str(e)}")

@shared_task
def cleanup_stuck_uploads():
    """Clean up any stuck pending uploads that are older than the timeout."""
    timeout_threshold = timezone.now() - timedelta(seconds=PENDING_TIMEOUT_SECONDS)
    stuck_uploads = JPGUpload.objects.filter(
        status=JPGUpload.Status.PENDING,
        timestamp__lt=timeout_threshold
    )
    
    for upload in stuck_uploads:
        error_msg = f'Upload timed out after {PENDING_TIMEOUT_SECONDS} seconds'
        logger.error(f"Upload {upload.id}: {error_msg}")
        upload.update_status(JPGUpload.Status.FAILED, error_msg)

@shared_task(bind=True)
def process_jpg_upload(self, upload_id):
    """Process a JPG upload by converting it to PDF and sending via email."""
    try:
        jpg_upload = JPGUpload.objects.get(id=upload_id)
        jpg_upload.task_id = self.request.id
        jpg_upload.save()

        # Check if the upload has been pending for too long
        time_since_upload = timezone.now() - jpg_upload.timestamp
        if time_since_upload > timedelta(seconds=PENDING_TIMEOUT_SECONDS):
            error_msg = f'Upload timed out after {PENDING_TIMEOUT_SECONDS} seconds'
            logger.error(f"Upload {upload_id}: {error_msg}")
            jpg_upload.update_status(JPGUpload.Status.FAILED, error_msg)
            return {'status': 'error', 'message': error_msg}
        
        # Add initial delay to show PENDING status
        time.sleep(2)
        
        converter = JPGToPDFConverter()
        
        # Convert to PDF
        jpg_upload.update_status(JPGUpload.Status.CONVERTING)
        time.sleep(3)  # Show converting status for 3 seconds
        
        if not converter.convert_to_pdf(jpg_upload):
            error_msg = 'Failed to convert JPG to PDF'
            logger.error(f"Upload {upload_id}: {error_msg}")
            jpg_upload.update_status(JPGUpload.Status.FAILED, error_msg)
            return {'status': 'error', 'message': error_msg}
            
        # Send email
        jpg_upload.update_status(JPGUpload.Status.SENDING)
        time.sleep(2)  # Show sending status for 2 seconds
        
        if not converter.send_pdf_email(jpg_upload):
            error_msg = 'Failed to send email'
            logger.error(f"Upload {upload_id}: {error_msg}")
            jpg_upload.update_status(JPGUpload.Status.FAILED, error_msg)
            return {'status': 'error', 'message': error_msg}
        
        jpg_upload.update_status(JPGUpload.Status.COMPLETED)
        return {'status': 'success', 'message': 'File processed and sent successfully'}
        
    except JPGUpload.DoesNotExist:
        error_msg = 'Upload not found'
        logger.error(f"Upload {upload_id}: {error_msg}")
        return {'status': 'error', 'message': error_msg}
        
    except Exception as e:
        error_msg = str(e)
        logger.exception(f"Upload {upload_id}: Unexpected error during processing")
        try:
            jpg_upload.update_status(JPGUpload.Status.FAILED, error_msg)
        except:
            pass
        return {'status': 'error', 'message': error_msg} 
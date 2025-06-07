from celery import shared_task
from .models import ImageUpload
import logging
import time
from django.utils import timezone
from datetime import timedelta
from celery.schedules import crontab
from celery import Celery
import os
from django.conf import settings

logger = logging.getLogger(__name__)

@shared_task
def cleanup_old_files():
    """Clean up JPG and PDF files that are older than FILE_CLEANUP_MINUTES minutes."""
    cleanup_threshold = timezone.now() - timedelta(minutes=settings.FILE_CLEANUP_MINUTES)
    old_uploads = ImageUpload.objects.filter(timestamp__lt=cleanup_threshold)

    logger.info(f"Cleaning up old files: {old_uploads.count()} uploads found")
    
    for upload in old_uploads:
        try:
            # Delete JPG file
            if upload.jpeg_file and os.path.exists(upload.jpeg_file.path):
                os.remove(upload.jpeg_file.path)
                upload.jpeg_file = None
            
            # Delete PDF file
            if upload._pdf_file and os.path.exists(upload._pdf_file.path):
                os.remove(upload._pdf_file.path)
                upload._pdf_file = None
            
            upload.save()
            logger.info(f"Cleaned up files for upload {upload.id}")
            
        except Exception as e:
            logger.error(f"Error cleaning up files for upload {upload.id}: {str(e)}")

@shared_task
def cleanup_stuck_uploads():
    """Clean up any stuck pending uploads that are older than the timeout."""
    timeout_threshold = timezone.now() - timedelta(seconds=settings.PENDING_TIMEOUT_SECONDS)
    stuck_uploads = ImageUpload.objects.filter(
        status=ImageUpload.Status.PENDING,
        timestamp__lt=timeout_threshold
    )
    
    for upload in stuck_uploads:
        error_msg = f'Upload timed out after {settings.PENDING_TIMEOUT_SECONDS} seconds'
        logger.error(f"Upload {upload.id}: {error_msg}")
        upload.update_status(ImageUpload.Status.FAILED, error_msg)

@shared_task(bind=True)
def process_image_upload(self, upload_id):
    """Process an image upload by converting it to PDF and sending via email."""
    try:
        image_upload = ImageUpload.objects.get(id=upload_id)
        image_upload.task_id = self.request.id
        image_upload.save()

        # Check if the upload has been pending for too long
        time_since_upload = timezone.now() - image_upload.timestamp
        if time_since_upload > timedelta(seconds=settings.PENDING_TIMEOUT_SECONDS):
            error_msg = f'Upload timed out after {settings.PENDING_TIMEOUT_SECONDS} seconds'
            logger.error(f"Upload {upload_id}: {error_msg}")
            image_upload.update_status(ImageUpload.Status.FAILED, error_msg)
            return {'status': 'error', 'message': error_msg}
        
        # Add initial delay to show PENDING status
        time.sleep(2)
        
        # Convert to PDF
        image_upload.update_status(ImageUpload.Status.CONVERTING)
        time.sleep(3)  # Show converting status for 3 seconds
        
        # Access pdf_file property which will trigger conversion if needed
        if not image_upload.pdf_file:
            error_msg = 'Failed to convert image to PDF'
            logger.error(f"Upload {upload_id}: {error_msg}")
            image_upload.update_status(ImageUpload.Status.FAILED, error_msg)
            return {'status': 'error', 'message': error_msg}
            
        # Send email
        image_upload.update_status(ImageUpload.Status.SENDING)
        time.sleep(2)  # Show sending status for 2 seconds
        
        if not image_upload.send_pdf_email():
            error_msg = 'Failed to send email'
            logger.error(f"Upload {upload_id}: {error_msg}")
            image_upload.update_status(ImageUpload.Status.FAILED, error_msg)
            return {'status': 'error', 'message': error_msg}
        
        image_upload.update_status(ImageUpload.Status.COMPLETED)
        return {'status': 'success', 'message': 'File processed and sent successfully'}
        
    except ImageUpload.DoesNotExist:
        error_msg = 'Upload not found'
        logger.error(f"Upload {upload_id}: {error_msg}")
        return {'status': 'error', 'message': error_msg}
        
    except Exception as e:
        error_msg = str(e)
        logger.exception(f"Upload {upload_id}: Unexpected error during processing")
        try:
            image_upload.update_status(ImageUpload.Status.FAILED, error_msg)
        except:
            pass
        return {'status': 'error', 'message': error_msg} 
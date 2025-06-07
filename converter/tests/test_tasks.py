from django.test import TestCase, override_settings
from unittest.mock import patch, PropertyMock
from celery import Task
from ..models import ImageUpload
from ..tasks import process_image_upload, cleanup_old_files, cleanup_stuck_uploads
from .test_utils import TestFileManager
from faker import Faker
import os
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    CELERY_BROKER_URL='memory://',
    CELERY_RESULT_BACKEND='cache',
    CELERY_CACHE_BACKEND='memory',
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
)
class TaskTests(TestCase):
    def setUp(self):
        self.fake = Faker()
        # Create a test image
        self.test_file = TestFileManager.create_test_image(
            format='JPEG',
            mode='RGB',
            size=(100, 100),
            color='red'
        )
        
        self.upload = ImageUpload.objects.create(
            email=self.fake.email(),
            jpeg_file=self.test_file
        )

    def tearDown(self):
        # Clean up uploaded files
        if self.upload.jpeg_file:
            if os.path.exists(self.upload.jpeg_file.path):
                os.remove(self.upload.jpeg_file.path)
        if self.upload._pdf_file:
            if os.path.exists(self.upload._pdf_file.path):
                os.remove(self.upload._pdf_file.path)

    @patch('time.sleep', return_value=None)
    def test_successful_processing(self, mock_sleep):
        """Test successful processing of an upload"""
        result = process_image_upload(self.upload.id)
        self.upload.refresh_from_db()
        self.assertEqual(result['status'], 'success')
        self.assertEqual(self.upload.status, ImageUpload.Status.COMPLETED)

    @patch('time.sleep', return_value=None)
    @patch('converter.models.ImageUpload.pdf_file', new_callable=PropertyMock, return_value=None)
    def test_conversion_failure(self, mock_pdf_file, mock_sleep):
        """Test handling of conversion failure"""
        self.upload.error_message = 'Failed to convert image to PDF'
        self.upload.save()
        result = process_image_upload(self.upload.id)
        self.upload.refresh_from_db()
        self.assertEqual(result['status'], 'error')
        self.assertEqual(self.upload.status, ImageUpload.Status.FAILED)
        self.assertIsNotNone(self.upload.error_message)

    @patch('time.sleep', return_value=None)
    def test_nonexistent_upload(self, mock_sleep):
        """Test handling of non-existent upload ID"""
        result = process_image_upload(99999)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['message'], 'Upload not found')

    def test_cleanup_old_files(self):
        """Test cleanup of old files"""
        # Create an old upload
        old_file = TestFileManager.create_test_image(
            format='JPEG',
            mode='RGB',
            size=(100, 100),
            color='blue'
        )
        old_upload = ImageUpload.objects.create(
            email=self.fake.email(),
            jpeg_file=old_file
        )
        old_upload.timestamp = timezone.now() - timedelta(minutes=settings.FILE_CLEANUP_MINUTES + 1)
        old_upload.save()
        cleanup_old_files()
        self.assertFalse(os.path.exists(old_upload.jpeg_file.path))
        if old_upload._pdf_file:
            self.assertFalse(os.path.exists(old_upload._pdf_file.path))

    def test_cleanup_stuck_uploads(self):
        """Test cleanup of stuck uploads"""
        stuck_file = TestFileManager.create_test_image(
            format='JPEG',
            mode='RGB',
            size=(100, 100),
            color='green'
        )
        stuck_upload = ImageUpload.objects.create(
            email=self.fake.email(),
            jpeg_file=stuck_file
        )
        stuck_upload.timestamp = timezone.now() - timedelta(seconds=settings.PENDING_TIMEOUT_SECONDS + 1)
        stuck_upload.save()
        cleanup_stuck_uploads()
        stuck_upload.refresh_from_db()
        self.assertEqual(stuck_upload.status, ImageUpload.Status.FAILED)
        self.assertIsNotNone(stuck_upload.error_message) 
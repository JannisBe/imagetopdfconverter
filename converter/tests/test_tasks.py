from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
from celery import Task
from ..models import JPGUpload
from ..tasks import process_jpg_upload
from faker import Faker

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
        self.test_file = SimpleUploadedFile(
            "test.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        self.upload = JPGUpload.objects.create(
            email=self.fake.email(),
            jpeg_file=self.test_file
        )

    @patch('converter.services.JPGToPDFConverter.convert_to_pdf')
    @patch('converter.services.JPGToPDFConverter.send_pdf_email')
    def test_successful_processing(self, mock_send_email, mock_convert):
        """Test successful processing of an upload"""
        mock_convert.return_value = True
        mock_send_email.return_value = True
        
        # Mock the task request
        mock_task = MagicMock()
        mock_task.request.id = 'test-task-id'
        
        with patch('converter.tasks.process_jpg_upload', mock_task):
            result = process_jpg_upload(self.upload.id)
        
        self.upload.refresh_from_db()
        self.assertEqual(result['status'], 'success')
        self.assertEqual(self.upload.status, JPGUpload.Status.COMPLETED)
        
        mock_convert.assert_called_once()
        mock_send_email.assert_called_once()

    @patch('converter.services.JPGToPDFConverter.convert_to_pdf')
    def test_conversion_failure(self, mock_convert):
        """Test handling of conversion failure"""
        mock_convert.return_value = False
        
        # Mock the task request
        mock_task = MagicMock()
        mock_task.request.id = 'test-task-id'
        
        with patch('converter.tasks.process_jpg_upload', mock_task):
            result = process_jpg_upload(self.upload.id)
        
        self.upload.refresh_from_db()
        self.assertEqual(result['status'], 'error')
        self.assertEqual(self.upload.status, JPGUpload.Status.FAILED)
        self.assertIsNotNone(self.upload.error_message)

    @patch('converter.services.JPGToPDFConverter.convert_to_pdf')
    @patch('converter.services.JPGToPDFConverter.send_pdf_email')
    def test_email_failure(self, mock_send_email, mock_convert):
        """Test handling of email sending failure"""
        mock_convert.return_value = True
        mock_send_email.return_value = False
        
        # Mock the task request
        mock_task = MagicMock()
        mock_task.request.id = 'test-task-id'
        
        with patch('converter.tasks.process_jpg_upload', mock_task):
            result = process_jpg_upload(self.upload.id)
        
        self.upload.refresh_from_db()
        self.assertEqual(result['status'], 'error')
        self.assertEqual(self.upload.status, JPGUpload.Status.FAILED)
        self.assertIsNotNone(self.upload.error_message)

    def test_nonexistent_upload(self):
        """Test handling of non-existent upload ID"""
        # Mock the task request
        mock_task = MagicMock()
        mock_task.request.id = 'test-task-id'
        
        with patch('converter.tasks.process_jpg_upload', mock_task):
            result = process_jpg_upload(99999)
        
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['message'], 'Upload not found') 
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from ..models import JPGUpload
from faker import Faker

class JPGUploadModelTest(TestCase):
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

    def tearDown(self):
        # Clean up uploaded files
        if self.upload.jpeg_file:
            if os.path.exists(self.upload.jpeg_file.path):
                os.remove(self.upload.jpeg_file.path)
        if self.upload.pdf_file:
            if os.path.exists(self.upload.pdf_file.path):
                os.remove(self.upload.pdf_file.path)

    def test_upload_creation(self):
        """Test upload creation with default values"""
        self.assertEqual(self.upload.status, JPGUpload.Status.PENDING)
        self.assertIsNone(self.upload.error_message)
        self.assertIsNone(self.upload.task_id)
        self.assertNotEqual(self.upload.email, "")

    def test_status_update(self):
        """Test status update functionality"""
        self.upload.update_status(JPGUpload.Status.CONVERTING)
        self.assertEqual(self.upload.status, JPGUpload.Status.CONVERTING)
        
        self.upload.update_status(JPGUpload.Status.FAILED, "Test error")
        self.assertEqual(self.upload.status, JPGUpload.Status.FAILED)
        self.assertEqual(self.upload.error_message, "Test error")

    def test_string_representation(self):
        """Test the string representation of the model"""
        expected = f"{self.upload.email} - {self.upload.timestamp} ({self.upload.status})"
        self.assertEqual(str(self.upload), expected)

    def test_file_paths(self):
        """Test file path generation"""
        self.assertTrue(self.upload.jpeg_file.name.startswith('uploads/jpg/'))
        self.assertTrue(self.upload.jpeg_file.name.endswith('.jpg'))
        
        # PDF file should be None initially
        self.assertFalse(self.upload.pdf_file) 
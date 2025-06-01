from django.test import TestCase
from converter.serializers import JPGUploadSerializer
from .test_utils import TestFileManager
from faker import Faker

class JPGUploadSerializerTest(TestCase):
    def setUp(self):
        self.fake = Faker()
        self.temp_file_path = TestFileManager.create_temp_jpg()
        
        self.valid_data = {
            'email': self.fake.email(),
            'jpeg_file': TestFileManager.create_upload_file(self.temp_file_path)
        }
        
        self.invalid_email_data = {
            'email': 'invalid-email',
            'jpeg_file': TestFileManager.create_upload_file(self.temp_file_path)
        }

    def tearDown(self):
        TestFileManager.cleanup_file(self.temp_file_path)

    def test_valid_serializer(self):
        """Test that a valid email and JPEG file are accepted"""
        serializer = JPGUploadSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        
    def test_invalid_email(self):
        """Test that an invalid email format is rejected"""
        serializer = JPGUploadSerializer(data=self.invalid_email_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_missing_fields(self):
        """Test that both required fields are enforced"""
        invalid_data = {}
        serializer = JPGUploadSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        self.assertIn('jpeg_file', serializer.errors) 
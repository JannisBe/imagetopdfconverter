from django.test import TestCase
from converter.serializers import ImageUploadSerializer
from .test_utils import TestFileManager
from faker import Faker
from django.core.files.uploadedfile import SimpleUploadedFile

class ImageUploadSerializerTest(TestCase):
    def setUp(self):
        self.fake = Faker()
        # Create a test image
        self.test_file = TestFileManager.create_test_image(
            format='JPEG',
            mode='RGB',
            size=(100, 100),
            color='red'
        )
        
        self.valid_data = {
            'email': self.fake.email(),
            'jpeg_file': self.test_file
        }
        
        self.invalid_email_data = {
            'email': 'not-an-email',
            'jpeg_file': self.test_file
        }

    def test_valid_data(self):
        """Test serializer with valid data"""
        serializer = ImageUploadSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_email(self):
        """Test serializer with invalid email"""
        serializer = ImageUploadSerializer(data=self.invalid_email_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_missing_required_fields(self):
        """Test serializer with missing required fields"""
        invalid_data = {'email': 'test@example.com'}  # Missing jpeg_file
        serializer = ImageUploadSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('jpeg_file', serializer.errors)

    def test_invalid_file_type(self):
        """Test serializer with invalid file type"""
        # Create a text file
        invalid_file = SimpleUploadedFile(
            "test.txt",
            b"not an image",
            content_type="text/plain"
        )
        
        invalid_data = {
            'email': self.fake.email(),
            'jpeg_file': invalid_file
        }
        serializer = ImageUploadSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('jpeg_file', serializer.errors)

    def test_file_size_limit(self):
        """Test serializer with file exceeding size limit"""
        # Create a large image
        large_file = TestFileManager.create_test_image(
            format='PNG',
            mode='RGB',
            size=(1000, 1000),
            color='black'
        )

        large_data = {
            'email': self.fake.email(),
            'jpeg_file': large_file
        }
        serializer = ImageUploadSerializer(data=large_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('jpeg_file', serializer.errors) 
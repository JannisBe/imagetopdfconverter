from django.test import TestCase
from converter.serializers import ImageUploadSerializer
from .test_utils import TestFileManager
from faker import Faker
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework.exceptions import ValidationError
from ..models import ImageUpload
from ..serializers import ImageUploadSerializer

class ImageUploadSerializerTest(APITestCase):
    def setUp(self):
        self.fake = Faker()
        self.serializer = ImageUploadSerializer()
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
            format='TIFF',
            mode='RGB',
            size=(10000, 10000),
            color='black'
        )

        large_data = {
            'email': self.fake.email(),
            'jpeg_file': large_file
        }
        serializer = ImageUploadSerializer(data=large_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('jpeg_file', serializer.errors)

    def test_validate_image_file_types(self):
        """Test validation of different image file types using subtests."""
        file_types = [
            ('test.jpg', b'fake image data', 'image/jpeg'),
            ('test.jpeg', b'fake image data', 'image/jpeg'),
            ('test.png', b'fake image data', 'image/png'),
            ('test.gif', b'fake image data', 'image/gif'),
            ('test.bmp', b'fake image data', 'image/bmp'),
            ('test.txt', b'not an image', 'text/plain'),
        ]

        for filename, content, content_type in file_types:
            with self.subTest(filename=filename):
                file = SimpleUploadedFile(filename, content, content_type=content_type)
                if filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                    self.assertEqual(self.serializer.validate_jpeg_file(file), file)
                else:
                    with self.assertRaises(ValidationError):
                        self.serializer.validate_jpeg_file(file) 
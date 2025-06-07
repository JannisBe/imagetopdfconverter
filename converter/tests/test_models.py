from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.base import ContentFile
from PIL import Image
import io
import os
from ..models import ImageUpload
from faker import Faker
from .test_utils import TestFileManager

class ImageUploadModelTest(TestCase):
    def setUp(self):
        self.fake = Faker()
        # Create a test RGB image
        self.test_file = TestFileManager.create_test_image(
            format='JPEG',
            mode='RGB',
            size=(100, 100),
            color='red'
        )
        
        # Create test instance
        self.upload = ImageUpload.objects.create(
            email="test@example.com",
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

    def test_upload_creation(self):
        """Test upload creation with default values"""
        self.assertEqual(self.upload.status, ImageUpload.Status.PENDING)
        self.assertIsNone(self.upload.error_message)
        self.assertIsNone(self.upload.task_id)
        self.assertNotEqual(self.upload.email, "")

    def test_status_update(self):
        """Test status update functionality"""
        self.upload.update_status(ImageUpload.Status.CONVERTING)
        self.assertEqual(self.upload.status, ImageUpload.Status.CONVERTING)
        
        self.upload.update_status(ImageUpload.Status.FAILED, "Test error")
        self.assertEqual(self.upload.status, ImageUpload.Status.FAILED)
        self.assertEqual(self.upload.error_message, "Test error")

    def test_string_representation(self):
        """Test the string representation of the model"""
        expected = f"{self.upload.email} - {self.upload.timestamp} ({self.upload.status})"
        self.assertEqual(str(self.upload), expected)

    def test_file_paths(self):
        """Test file path generation"""
        self.assertTrue(self.upload.jpeg_file.name.startswith('uploads/jpg/'))
        self.assertTrue(self.upload.jpeg_file.name.endswith('.jpg'))

    def test_pdf_file_property_creates_pdf(self):
        """Test that accessing pdf_file property creates PDF if it doesn't exist"""
        # Access pdf_file property
        pdf_file = self.upload.pdf_file
        
        # Check PDF was created
        self.assertIsNotNone(pdf_file)
        self.assertTrue(os.path.exists(pdf_file.path))
        self.assertTrue(pdf_file.name.endswith('.pdf'))

    def test_pdf_file_property_returns_existing_pdf(self):
        """Test that pdf_file property returns existing PDF without recreating"""
        # Create initial PDF
        initial_pdf = self.upload.pdf_file
        initial_path = initial_pdf.path
        
        # Access pdf_file property again
        second_pdf = self.upload.pdf_file
        
        # Check it's the same file
        self.assertEqual(initial_path, second_pdf.path)

    def test_pdf_file_property_with_invalid_image(self):
        """Test pdf_file property with invalid image file"""
        # Create invalid image file
        invalid_file = SimpleUploadedFile(
            "invalid.jpg",
            b"not an image",
            content_type="image/jpeg"
        )
        
        # Create upload with invalid image
        invalid_upload = ImageUpload.objects.create(
            email="test@example.com",
            jpeg_file=invalid_file
        )
        
        # Try to access pdf_file property
        pdf_file = invalid_upload.pdf_file
        
        # Check PDF creation failed
        self.assertIsNone(pdf_file)
        self.assertEqual(invalid_upload.status, ImageUpload.Status.FAILED)
        self.assertIsNotNone(invalid_upload.error_message)

    def test_pdf_file_property_with_png_image(self):
        """Test pdf_file property with PNG image"""
        # Create PNG image
        png_file = TestFileManager.create_test_image(
            format='PNG',
            mode='RGB',
            size=(100, 100),
            color='blue'
        )
        png_upload = ImageUpload.objects.create(
            email="test@example.com",
            jpeg_file=png_file
        )
        # Access pdf_file property
        pdf_file = png_upload.pdf_file
        # Check PDF was created successfully
        self.assertIsNotNone(pdf_file)
        self.assertTrue(os.path.exists(pdf_file.path))
        # Clean up
        if png_upload.jpeg_file and os.path.exists(png_upload.jpeg_file.path):
            os.remove(png_upload.jpeg_file.path)
        if png_upload._pdf_file and os.path.exists(png_upload._pdf_file.path):
            os.remove(png_upload._pdf_file.path)

    def test_pdf_file_property_with_gif_image(self):
        """Test pdf_file property with GIF image"""
        # Create GIF image
        gif_file = TestFileManager.create_test_image(
            format='GIF',
            mode='RGB',
            size=(100, 100),
            color='green'
        )
        gif_upload = ImageUpload.objects.create(
            email="test@example.com",
            jpeg_file=gif_file
        )
        # Access pdf_file property
        pdf_file = gif_upload.pdf_file
        # Check PDF was created successfully
        self.assertIsNotNone(pdf_file)
        self.assertTrue(os.path.exists(pdf_file.path))
        # Clean up
        if gif_upload.jpeg_file and os.path.exists(gif_upload.jpeg_file.path):
            os.remove(gif_upload.jpeg_file.path)
        if gif_upload._pdf_file and os.path.exists(gif_upload._pdf_file.path):
            os.remove(gif_upload._pdf_file.path)

    def test_pdf_file_property_with_bmp_image(self):
        """Test pdf_file property with BMP image"""
        # Create BMP image
        bmp_file = TestFileManager.create_test_image(
            format='BMP',
            mode='RGB',
            size=(100, 100),
            color='yellow'
        )
        bmp_upload = ImageUpload.objects.create(
            email="test@example.com",
            jpeg_file=bmp_file
        )
        # Access pdf_file property
        pdf_file = bmp_upload.pdf_file
        # Check PDF was created successfully
        self.assertIsNotNone(pdf_file)
        self.assertTrue(os.path.exists(pdf_file.path))
        # Clean up
        if bmp_upload.jpeg_file and os.path.exists(bmp_upload.jpeg_file.path):
            os.remove(bmp_upload.jpeg_file.path)
        if bmp_upload._pdf_file and os.path.exists(bmp_upload._pdf_file.path):
            os.remove(bmp_upload._pdf_file.path)

    def test_pdf_file_property_with_grayscale_image(self):
        """Test pdf_file property with grayscale image"""
        # Create grayscale image
        gray_file = TestFileManager.create_test_image(
            format='JPEG',
            mode='L',
            size=(100, 100),
            color=128
        )
        gray_upload = ImageUpload.objects.create(
            email="test@example.com",
            jpeg_file=gray_file
        )
        # Access pdf_file property
        pdf_file = gray_upload.pdf_file
        # Check PDF was created successfully
        self.assertIsNotNone(pdf_file)
        self.assertTrue(os.path.exists(pdf_file.path))
        # Clean up
        if gray_upload.jpeg_file and os.path.exists(gray_upload.jpeg_file.path):
            os.remove(gray_upload.jpeg_file.path)
        if gray_upload._pdf_file and os.path.exists(gray_upload._pdf_file.path):
            os.remove(gray_upload._pdf_file.path)

    def test_pdf_file_property_with_transparent_png(self):
        """Test pdf_file property with transparent PNG image"""
        # Create transparent PNG image
        rgba_file = TestFileManager.create_test_image(
            format='PNG',
            mode='RGBA',
            size=(100, 100),
            color=(255, 0, 0, 128)
        )
        rgba_upload = ImageUpload.objects.create(
            email="test@example.com",
            jpeg_file=rgba_file
        )
        # Access pdf_file property
        pdf_file = rgba_upload.pdf_file
        # Check PDF was created successfully
        self.assertIsNotNone(pdf_file)
        self.assertTrue(os.path.exists(pdf_file.path))
        # Clean up
        if rgba_upload.jpeg_file and os.path.exists(rgba_upload.jpeg_file.path):
            os.remove(rgba_upload.jpeg_file.path)
        if rgba_upload._pdf_file and os.path.exists(rgba_upload._pdf_file.path):
            os.remove(rgba_upload._pdf_file.path)

    def test_pdf_file_property_with_large_image(self):
        """Test pdf_file property with a large image"""
        # Create large image
        large_file = TestFileManager.create_test_image(
            format='JPEG',
            mode='RGB',
            size=(4000, 4000),
            color='blue'
        )
        large_upload = ImageUpload.objects.create(
            email="test@example.com",
            jpeg_file=large_file
        )
        # Access pdf_file property
        pdf_file = large_upload.pdf_file
        # Check PDF was created successfully
        self.assertIsNotNone(pdf_file)
        self.assertTrue(os.path.exists(pdf_file.path))
        # Clean up
        if large_upload.jpeg_file and os.path.exists(large_upload.jpeg_file.path):
            os.remove(large_upload.jpeg_file.path)
        if large_upload._pdf_file and os.path.exists(large_upload._pdf_file.path):
            os.remove(large_upload._pdf_file.path)

    def test_pdf_file_property_preserves_filename(self):
        """Test that PDF filename is derived from original image filename"""
        # Access pdf_file property
        pdf_file = self.upload.pdf_file
        
        # Check filename
        expected_name = os.path.splitext(self.upload.jpeg_file.name)[0] + '.pdf'
        expected_name = expected_name.replace('uploads/jpg/', 'uploads/pdf/')
        self.assertEqual(pdf_file.name, expected_name)

    def test_pdf_file_property_updates_status(self):
        """Test that PDF creation updates status correctly"""
        # Check initial status
        self.assertEqual(self.upload.status, ImageUpload.Status.PENDING)
        
        # Access pdf_file property
        self.upload.pdf_file
        
        # Check status was updated
        self.assertEqual(self.upload.status, ImageUpload.Status.COMPLETED) 
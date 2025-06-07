from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from converter.models import ImageUpload
from .test_utils import TestFileManager
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from unittest.mock import patch, MagicMock
from faker import Faker

class ImageUploadViewTest(APITestCase):
    def setUp(self):
        self.fake = Faker()
        # Create a test image
        self.test_file = TestFileManager.create_test_image(
            format='JPEG',
            mode='RGB',
            size=(100, 100),
            color='red'
        )
        
        self.upload_url = reverse('converter:upload')
        self.valid_payload = {
            'email': self.fake.email(),
            'jpeg_file': self.test_file
        }

    def tearDown(self):
        # Clean up any uploaded files
        for image_upload in ImageUpload.objects.all():
            if image_upload.jpeg_file and os.path.exists(image_upload.jpeg_file.path):
                os.unlink(image_upload.jpeg_file.path)
            if image_upload._pdf_file and os.path.exists(image_upload._pdf_file.path):
                os.unlink(image_upload._pdf_file.path)

    @patch('converter.tasks.process_image_upload.delay')
    def test_successful_upload(self, mock_delay):
        """Test a successful file upload with valid data"""
        # Mock the Celery task
        mock_task = MagicMock()
        mock_task.id = 'test-task-id'
        mock_delay.return_value = mock_task

        response = self.client.post(self.upload_url, self.valid_payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        
        upload = ImageUpload.objects.first()
        self.assertEqual(upload.status, ImageUpload.Status.PENDING)
        self.assertEqual(upload.email, self.valid_payload['email'])
        self.assertEqual(upload.task_id, 'test-task-id')

        mock_delay.assert_called_once_with(upload.id)

    def test_missing_file_upload(self):
        """Test rejection when JPEG file is missing"""
        payload = {'email': self.fake.email()}
        response = self.client.post(self.upload_url, payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_email_upload(self):
        """Test rejection when email is missing"""
        payload = {'jpeg_file': self.test_file}
        response = self.client.post(self.upload_url, payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_email_upload(self):
        """Test rejection of invalid email format"""
        payload = {
            'email': 'invalid-email',
            'jpeg_file': self.test_file
        }
        response = self.client.post(self.upload_url, payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_file_type(self):
        """Test rejection of non-JPG file"""
        # Create a text file
        invalid_file = SimpleUploadedFile(
            "test.txt",
            b"not an image",
            content_type="text/plain"
        )
        
        payload = {
            'email': self.fake.email(),
            'jpeg_file': invalid_file
        }
        response = self.client.post(self.upload_url, payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('converter.tasks.process_image_upload.delay')
    def test_status_endpoint(self, mock_delay):
        """Test the status endpoint functionality"""
        # Mock the Celery task
        mock_task = MagicMock()
        mock_task.id = 'test-task-id'
        mock_delay.return_value = mock_task

        # Create an upload first
        response = self.client.post(self.upload_url, self.valid_payload, format='multipart')
        upload_id = response.data['id']
        
        # Test status endpoint
        status_url = reverse('converter:status', args=[upload_id])
        response = self.client.get(status_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('data', response.data)

    def test_status_nonexistent_upload(self):
        """Test status endpoint with non-existent upload ID"""
        status_url = reverse('converter:status', args=[99999])
        response = self.client.get(status_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 
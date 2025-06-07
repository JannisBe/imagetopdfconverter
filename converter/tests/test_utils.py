import tempfile
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

class TestFileManager:
    @staticmethod
    def create_temp_jpg(suffix='.jpg', content=b'fake jpeg content'):
        """Create a temporary JPG file with specified suffix and content.
        
        Args:
            suffix (str): File suffix (default: '.jpg')
            content (bytes): File content (default: b'fake jpeg content')
            
        Returns:
            str: Path to the created temporary file
        """
        temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        temp_file.write(content)
        temp_file.close()
        return temp_file.name

    @staticmethod
    def create_test_image(format='JPEG', mode='RGB', size=(100, 100), color='red'):
        """Create a test image with specified parameters.
        
        Args:
            format (str): Image format (JPEG, PNG, GIF, BMP)
            mode (str): Image mode (RGB, RGBA, L)
            size (tuple): Image dimensions (width, height)
            color: Color for the image (can be name, RGB tuple, or grayscale value)
            
        Returns:
            SimpleUploadedFile: The uploaded file
        """
        # Create image
        image = Image.new(mode=mode, size=size, color=color)
        
        # Save to buffer
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        buffer.seek(0)
        
        # Create SimpleUploadedFile
        content_type = f'image/{format.lower()}'
        if format == 'JPEG':
            content_type = 'image/jpeg'
            
        suffix = f'.{format.lower()}'
        if format == 'JPEG':
            suffix = '.jpg'
            
        return SimpleUploadedFile(
            name=f'test{suffix}',
            content=buffer.getvalue(),
            content_type=content_type
        )

    @staticmethod
    def create_upload_file(file_path):
        """Create a SimpleUploadedFile from a file path.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            SimpleUploadedFile: The uploaded file
        """
        return SimpleUploadedFile(
            name='test.jpg',
            content=open(file_path, 'rb').read(),
            content_type='image/jpeg'
        )

    @staticmethod
    def cleanup_file(file_path):
        """Remove a file if it exists.
        
        Args:
            file_path (str): Path to the file to remove
        """
        if os.path.exists(file_path):
            os.unlink(file_path) 
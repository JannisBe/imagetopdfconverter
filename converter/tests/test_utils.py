import tempfile
import os
from django.core.files.uploadedfile import SimpleUploadedFile

class TestFileManager:
    @staticmethod
    def create_temp_jpg():
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        temp_file.write(b'fake jpeg content')
        temp_file.close()
        return temp_file.name

    @staticmethod
    def create_upload_file(file_path):
        return SimpleUploadedFile(
            name='test.jpg',
            content=open(file_path, 'rb').read(),
            content_type='image/jpeg'
        )

    @staticmethod
    def cleanup_file(file_path):
        if os.path.exists(file_path):
            os.unlink(file_path) 
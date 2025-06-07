from rest_framework import serializers
from .models import ImageUpload
from PIL import Image

class ImageUploadSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    error_message = serializers.CharField(read_only=True)
    task_id = serializers.CharField(read_only=True)

    class Meta:
        model = ImageUpload
        fields = ['id', 'email', 'jpeg_file', 'timestamp', 'status', 'error_message', 'task_id']
        read_only_fields = ['id', 'timestamp', 'status', 'error_message', 'task_id']

    def validate_jpeg_file(self, value):
        exts = Image.registered_extensions()
        supported_extensions = {ex for ex, f in exts.items() if f in Image.OPEN}
        if not value.name.lower().endswith(tuple(supported_extensions)):
            raise serializers.ValidationError(f"Only image files with supported formats are allowed: {', '.join(supported_extensions)}.")
        if value.size > 10 * 1024 * 1024:  # 10MB limit
            raise serializers.ValidationError("File size cannot exceed 10MB.")
        return value

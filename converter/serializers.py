from rest_framework import serializers
from .models import JPGUpload

class JPGUploadSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    error_message = serializers.CharField(read_only=True)
    task_id = serializers.CharField(read_only=True)

    class Meta:
        model = JPGUpload
        fields = ['id', 'email', 'jpeg_file', 'timestamp', 'status', 'error_message', 'task_id']
        read_only_fields = ['id', 'timestamp', 'status', 'error_message', 'task_id']

    def validate_jpeg_file(self, value):
        if not value.name.lower().endswith(('.jpg', '.jpeg')):
            raise serializers.ValidationError("Only JPG/JPEG files are allowed.")
        if value.size > 10 * 1024 * 1024:  # 10MB limit
            raise serializers.ValidationError("File size cannot exceed 10MB.")
        return value

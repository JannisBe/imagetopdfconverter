from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.http import Http404
from .models import ImageUpload
from .serializers import ImageUploadSerializer
from .tasks import process_image_upload
from kombu.exceptions import OperationalError
import logging

logger = logging.getLogger(__name__)

# Create your views here.

class ImageUploadView(generics.CreateAPIView):
    queryset = ImageUpload.objects.all()
    serializer_class = ImageUploadSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        try:
            # Save the upload
            image_upload = serializer.save()
            
            # Start async processing
            task = process_image_upload.delay(image_upload.id)
            image_upload.task_id = task.id
            image_upload.save()
            
        except OperationalError as e:
            logger.error("Failed to connect to message broker: %s", str(e))
            image_upload.update_status(ImageUpload.Status.FAILED, "Failed to start processing task")
            raise ValidationError("Service temporarily unavailable. Please try again later.")
        except Exception as e:
            logger.exception("Failed to process upload")
            if image_upload:
                image_upload.update_status(ImageUpload.Status.FAILED, str(e))
            raise ValidationError(str(e))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Create the upload instance
            image_upload = serializer.save()
            
            # Start the processing task
            task = process_image_upload.delay(image_upload.id)
            image_upload.task_id = task.id
            image_upload.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # If anything goes wrong, update status and return error
            image_upload.update_status(ImageUpload.Status.FAILED, "Failed to start processing task")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ImageUploadStatusView(generics.RetrieveAPIView):
    queryset = ImageUpload.objects.all()
    serializer_class = ImageUploadSerializer
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                'status': instance.status,
                'error_message': instance.error_message,
                'data': serializer.data
            })
        except Http404:
            return Response({
                'message': 'Upload not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("Failed to retrieve upload status")
            return Response({
                'message': 'Failed to retrieve status',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

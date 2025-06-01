from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.http import Http404
from .models import JPGUpload
from .serializers import JPGUploadSerializer
from .tasks import process_jpg_upload
from kombu.exceptions import OperationalError
import logging

logger = logging.getLogger(__name__)

# Create your views here.

class JPGUploadView(generics.CreateAPIView):
    queryset = JPGUpload.objects.all()
    serializer_class = JPGUploadSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        try:
            # Save the upload
            jpg_upload = serializer.save()
            
            # Start async processing
            task = process_jpg_upload.delay(jpg_upload.id)
            jpg_upload.task_id = task.id
            jpg_upload.save()
            
        except OperationalError as e:
            logger.error("Failed to connect to message broker: %s", str(e))
            jpg_upload.update_status(JPGUpload.Status.FAILED, "Failed to start processing task")
            raise ValidationError("Service temporarily unavailable. Please try again later.")
        except Exception as e:
            logger.exception("Failed to process upload")
            if jpg_upload:
                jpg_upload.update_status(JPGUpload.Status.FAILED, str(e))
            raise ValidationError(str(e))

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            return Response({
                'message': 'File uploaded successfully. You will receive the PDF via email shortly.',
                'data': serializer.data
            }, status=status.HTTP_202_ACCEPTED)
            
        except ValidationError as e:
            return Response({
                'message': str(e),
                'errors': e.detail if hasattr(e, 'detail') else None
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Unexpected error during upload")
            return Response({
                'message': 'An unexpected error occurred',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class JPGUploadStatusView(generics.RetrieveAPIView):
    queryset = JPGUpload.objects.all()
    serializer_class = JPGUploadSerializer
    
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

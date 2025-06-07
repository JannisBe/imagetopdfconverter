from django.urls import path
from .views import ImageUploadView, ImageUploadStatusView

app_name = 'converter'

urlpatterns = [
    path('upload/', ImageUploadView.as_view(), name='upload'),
    path('status/<int:pk>/', ImageUploadStatusView.as_view(), name='status'),
] 
from django.urls import path
from .views import JPGUploadView, JPGUploadStatusView

app_name = 'converter'

urlpatterns = [
    path('upload/', JPGUploadView.as_view(), name='upload'),
    path('status/<int:pk>/', JPGUploadStatusView.as_view(), name='status'),
] 
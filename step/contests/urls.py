from django.urls import path

from .views import ArchiveView

urlpatterns = [
    path('api/archive/', ArchiveView.as_view(), name='archive')
]

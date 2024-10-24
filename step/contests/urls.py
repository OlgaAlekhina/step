from django.urls import path

from .views import ArchiveView

urlpatterns = [
    path('api/step/contests/archieve/', ArchiveView.as_view(), name='archive')
]

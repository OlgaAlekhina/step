from django.urls import path

from .views import ArchiveView, ContestDetailsView

urlpatterns = [
    path('api/step/contests/archieve/', ArchiveView.as_view(), name='archive'),
    path('api/step/contests/<uuid:contest_id>/', ContestDetailsView.as_view(), name='contest_details'),
]

from django.urls import path

from .views import ArchiveView, ContestDetailsView, ContestsView

urlpatterns = [
    path('api/step/contests/archieve/', ArchiveView.as_view(), name='archive'),
    path('api/contests/<uuid:contest_id>/', ContestDetailsView.as_view(), name='contest_details'),
    path('api/contests/<uuid:process_id>/', ContestsView.as_view(), name='contests'),
]

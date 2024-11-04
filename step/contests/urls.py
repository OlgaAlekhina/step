from django.urls import path

from .views import ArchiveView, ContestDetailsView, ContestsView

urlpatterns = [
    path('api/step/contests/archieve/', ArchiveView.as_view(), name='archive'),
    path('api/step/contests/<uuid:contest_id>/', ContestDetailsView.as_view(), name='contest_details'),
    path('api/contests/filter/', ContestsView.as_view(), name='contests_filter'),
]

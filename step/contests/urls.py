from django.urls import path

from .views import (
    ArchiveContestsView, ContestDetailsView, ActiveContestsView, UserTasksView
)

urlpatterns = [
    path('api/contests/<uuid:contest_id>/', ContestDetailsView.as_view(), name='contest_details'),
    path('api/contests/archive/', ArchiveContestsView.as_view(), name='contest_archive'),
    path('api/contests/active/', ActiveContestsView.as_view(), name='contest_active'),
    path('api/contests/user_tasks/', UserTasksView.as_view(), name='task_active'),
]

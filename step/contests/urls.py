from django.urls import path

from .views import (
    ArchiveContestsView, ContestDetailsView, ActiveContestsView, UserTasksView, QuitContestView, UserHistoryView
)

urlpatterns = [
    path('contests/<uuid:contest_id>/', ContestDetailsView.as_view(), name='contest_details'),
    path('contests/active/', ActiveContestsView.as_view(), name='contest_active'),
    path('contests/archive/', ArchiveContestsView.as_view(), name='contest_archive'),
    path('contests/user/my/tasks/', UserTasksView.as_view(), name='my_task'),
    path('contests/user/my/history/', UserHistoryView.as_view(), name='my_history'),
    path('contests/user/my/task/<uuid:task_id>/', QuitContestView.as_view(), name='quit_contest'),
]

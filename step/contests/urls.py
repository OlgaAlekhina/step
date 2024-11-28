from django.urls import path

from .views import (
    ArchiveContestsView, ContestDetailsView, ActiveContestsView, UserTasksView, QuitContestView, UserHistoryView
)

urlpatterns = [
    path('api/contests/<uuid:contest_id>/', ContestDetailsView.as_view(), name='contest_details'),
    path('api/contests/archive/', ArchiveContestsView.as_view(), name='contest_archive'),
    path('api/contests/active/', ActiveContestsView.as_view(), name='contest_active'),
    path('api/contests/user_tasks/', UserTasksView.as_view(), name='task_active'),
    path('api/contests/<uuid:contest_id>/quit_contest/', QuitContestView.as_view(), name='quit_contest'),
    path('api/contests/history_participation/', UserHistoryView.as_view(), name='history_participation'),

]

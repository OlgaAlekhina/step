from django.urls import path

from .views import *

urlpatterns = [
    path('api/contests/', ContestsView.as_view(), name='Contests'),
    path('api/solutions/', SolutionsView.as_view(), name='solutions')
]

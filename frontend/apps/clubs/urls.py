"""URL configuration for clubs app."""

from django.urls import path
from . import views

app_name = 'clubs'

urlpatterns = [
    path('', views.club_list, name='list'),
    path('<int:club_id>/', views.club_detail, name='detail'),
    path('my-clubs/', views.my_clubs, name='my_clubs'),
]


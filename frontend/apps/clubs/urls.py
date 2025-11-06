"""URL configuration for clubs app."""

from django.urls import path
from . import views

app_name = 'clubs'

urlpatterns = [
    path('', views.club_list, name='list'),
    path('create/', views.create_club, name='create'),
    path('my-clubs/', views.my_clubs, name='my_clubs'),
    path('<int:club_id>/', views.club_detail, name='detail'),
    path('<int:club_id>/join/', views.join_club, name='join'),
    path('<int:club_id>/leave/', views.leave_club, name='leave'),
    path('<int:club_id>/edit/', views.edit_club, name='edit'),
]


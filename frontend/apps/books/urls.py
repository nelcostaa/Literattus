"""URL configuration for books app."""

from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.book_list, name='list'),
    path('<int:book_id>/', views.book_detail, name='detail'),
    path('search/', views.book_search, name='search'),
]


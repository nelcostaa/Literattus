"""URL configuration for books app."""

from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.book_catalog, name='catalog'),
    path('list/', views.book_list, name='list'),  # Legacy redirect
    path('search/', views.book_search, name='search'),
    path('add/<str:google_book_id>/', views.add_book, name='add'),
    path('<str:book_id>/', views.book_detail, name='detail'),
]


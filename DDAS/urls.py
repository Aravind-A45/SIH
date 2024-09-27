from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    #credentials
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("", views.signup, name="signup"),
    path("home/", views.home, name="home"),

    path('upload_file', views.upload_file, name='upload_file'),
    path('download/<str:file_id>/', views.download_file, name='download_file'),
    path('files/', views.list_files, name='list_files'), 
]
from django.contrib import admin
from django.urls import path
from expense import views

urlpatterns = [
    path('', views.index),
    path('api/user-face-match/', views.FaceCheckAPI.as_view()),
    path('admin/', admin.site.urls),
]

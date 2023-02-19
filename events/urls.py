from django.urls import path

from . import views

urlpatterns = [
    path('readqr/', views.read_qr, name='readqr'),
]

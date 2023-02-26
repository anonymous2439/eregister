from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_user, name='register_user'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('events/', views.event_home, name='event_home'),
    path('event/details/<int:event_id>/', views.event_details, name='event_details'),
    path('event/manage/', views.event_manage, name='event_manage'),
    path('event/create/', views.event_create, name='event_create'),
    path('event/edit/<int:event_id>/', views.event_edit, name='event_edit'),
    path('event/participate/<int:event_id>/', views.event_participate, name='event_participate'),
]

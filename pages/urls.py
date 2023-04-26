from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('organizer/manage/', views.organizer_manage, name='organizer_manage'),
    path('participant/manage/', views.participant_manage, name='participant_manage'),
    path('organizer/register/', views.register_organizer, name='register_organizer'),
    path('participant/register/', views.register_participant, name='register_participant'),
    path('user/edit/<int:user_id>/', views.user_edit, name='user_edit'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('events/', views.event_home, name='event_home'),
    path('event/details/<int:event_id>/', views.event_details, name='event_details'),
    path('event/manage/', views.event_manage, name='event_manage'),
    path('event/create/', views.event_create, name='event_create'),
    path('event/edit/<int:event_id>/', views.event_edit, name='event_edit'),
    path('event/participate/<int:event_id>/', views.event_participate, name='event_participate'),
    path('exportcsv/<int:event_id>/', views.generate_csv, name='generate_csv'),
    path('sendsurvey/<int:event_id>/', views.send_survey, name='send_survey'),
]

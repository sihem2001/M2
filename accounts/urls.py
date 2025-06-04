from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.CustomRegistrationView.as_view(), name='register'),
    path('logout/', views.custom_logout, name='logout'),
    path('preferences-setup/', views.preferences_setup, name='preferences_setup'),
    path('preferences-edit/', views.preferences_edit, name='preferences_edit'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('process-id-card/', views.process_id_card, name='process_id_card'),
]
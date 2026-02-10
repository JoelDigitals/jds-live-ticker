from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),  # optional eigene logout function
    path('register/', views.register, name='register'),
    path('register/sso/', views.sso_connect, name='sso_connect'),
    path('register/callback/', views.sso_callback, name='sso_callback'),
    path('sso/login/', views.sso_login, name='sso_login'),
]

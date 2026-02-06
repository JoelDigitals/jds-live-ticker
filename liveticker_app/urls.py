from django.urls import path
from . import views

urlpatterns = [
    path('', views.liveticker_list, name='liveticker_list'),
    path('create/', views.liveticker_create, name='liveticker_create'),
    path('<int:pk>/', views.liveticker_detail, name='liveticker_detail'),
    path('<int:pk>/embed/', views.liveticker_embed, name='liveticker_embed'),
]

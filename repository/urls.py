from django.urls import path
from . import views
from . import auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_dataset, name='upload_dataset'),
    path('preview/<uuid:dataset_id>/', views.dataset_preview, name='dataset_preview'),
    path('search/', views.search_datasets, name='search_datasets'),
    path('download/<uuid:dataset_id>/', views.download_dataset, name='download_dataset'),
    path('register/', auth_views.register, name='register'),
    path('login/', auth_views.user_login, name='login'),
    path('logout/', auth_views.user_logout, name='logout'),
]
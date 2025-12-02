from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_dataset, name='upload_dataset'),
    path('preview/<uuid:dataset_id>/', views.dataset_preview, name='dataset_preview'),
    path('search/', views.search_datasets, name='search_datasets'),
]
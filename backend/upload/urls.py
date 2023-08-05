from django.urls import path
from . import views

app_name = 'authentication'
urlpatterns = [
    path('', views.UploadView.as_view(), name='upload_dataset'),
    path('status/', views.StatusView.as_view(), name='get_status'),
    path('download/', views.DownloadView.as_view(), name='download_project'),
    path('remove/', views.RemoveView.as_view(), name='remove_project')
]

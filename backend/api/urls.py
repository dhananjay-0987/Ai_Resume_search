from django.urls import path
from api import views

urlpatterns = [
    path('upload-resume/', views.ResumeUploadView.as_view(), name='upload-resume'),
    path('search-candidates/', views.SearchCandidatesView.as_view(), name='search-candidates'),
] 
from django.urls import path

from .views import anno, AnnoDetailView, comments

urlpatterns = [
    path ('anno/<int:pk>/comments/', comments), 
    path('anno/', anno),
    path('anno/<int:pk>/', AnnoDetailView.as_view()), 
]

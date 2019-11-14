from django.urls import path, include

from .views import URLAPIView, RetrieveSecretAPIView, FileAPIView, StatisticsAPIView


urlpatterns = [
    path("auth/", include("djoser.urls.authtoken")),
    path("secure/url/", URLAPIView.as_view()),
    path("secure/file/<str:filename>/", FileAPIView.as_view()),
    path("secret/", RetrieveSecretAPIView.as_view()),
    path("statistics/", StatisticsAPIView.as_view()),
]

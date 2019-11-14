from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import (
    UploadFileView,
    UploadUrlView,
    ChooseView,
    SuccessPage,
    HomePageView,
    FileSecretView,
    UrlSecretView,
)

urlpatterns = [
    path("", HomePageView.as_view()),
    path("upload/", login_required(ChooseView.as_view())),
    path("success/", login_required(SuccessPage.as_view())),
    path("upload/file", login_required(UploadFileView.as_view()), name="upload-file"),
    path("upload/url", login_required(UploadUrlView.as_view()), name="upload-url"),
    path("secret/f/<pk>", FileSecretView.as_view(), name="retrieve-file"),
    path("secret/u/<pk>", UrlSecretView.as_view(), name="retrieve-url"),
]

import os
import logging

from django.views.generic import CreateView, TemplateView, DetailView
from django.views.generic.edit import FormMixin
from django.shortcuts import render, HttpResponseRedirect
from django.http import FileResponse
from rest_framework import status

from .models import File, URL
from .utils import password_generator
from .forms import PasswordForm


logger = logging.getLogger(__name__)


class HomePageView(TemplateView):
    template_name = "safesend/home.html"


class ChooseView(TemplateView):
    template_name = "safesend/choose_upload_content.html"


class SuccessPage(TemplateView):
    template_name = "safesend/success.html"


class UploadViewBase(CreateView):
    template_name = "safesend/upload_file.html"
    success_url = "/success"

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        logger.info("Successfully send an object to share. Generating password.")
        if self.object:
            generated_password = password_generator()
            self.object.password = generated_password
            self.object.user = request.user
            self.object.save()

            secret_url = (
                f'{request.META["HTTP_ORIGIN"]}/secret/'
                f"{self.object.type}/{self.object.uuid}"
            )
            logger.info(
                f"Successfully created {self.object}. "
                f"Will be available under link: {secret_url}"
            )
            return render(
                request,
                "safesend/success.html",
                {"password": generated_password, "access_url": secret_url},
            )

        return response


class UploadFileView(UploadViewBase):
    model = File
    fields = ["file"]


class UploadUrlView(UploadViewBase):
    model = URL
    fields = ["url"]


class SecretView(DetailView):
    template_name = "safesend/secret_url_handler.html"


class SecretBaseView(FormMixin, DetailView):
    template_name = "safesend/secret_url_handler.html"
    form_class = PasswordForm
    ERROR_MESSAGE = None

    def _get_file_response(self):
        response = FileResponse(open(self.object.file.path, "rb"))
        response["Content-Type"] = "application/octet-stream"
        response["Content-Disposition"] = f"attachment;filename={self.object.filename}"
        response["Content-Length"] = os.path.getsize(self.object.file.path)

        return response

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["error_message"] = self.ERROR_MESSAGE
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_expired:
            logger.info(f"{self.object} is expired.")
            self.ERROR_MESSAGE = "URL has been expired!."
            response = super().get(self, request, *args, **kwargs)
            response.status_code = status.HTTP_404_NOT_FOUND
            return response

        form = self.get_form()
        if form.is_valid():
            password = form.cleaned_data["password"]
            logger.info(f"Checking password...")
            if self.object.check_password(password):
                self.object.visit_counter += 1
                self.object.save(hash_password=False)

                logger.info(f"Successfully get an access to {self.object}")
                return (
                    self._get_file_response()
                    if isinstance(self.object, File)
                    else HttpResponseRedirect(self.object.url)
                )
            self.ERROR_MESSAGE = "Wrong password."
            logger.info(f"Wrong password provided for {self.object}")

        return super().get(self, request, *args, **kwargs)


class FileSecretView(SecretBaseView):
    model = File

    def get_success_url(self):
        return self.object.file.url


class UrlSecretView(SecretBaseView):
    model = URL

    def get_success_url(self):
        return self.object.url

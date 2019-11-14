import logging
import base64
from collections import defaultdict
import os
from urllib.parse import urlparse

from django.shortcuts import get_object_or_404
from django.db.models import functions, Count

from rest_framework import generics
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser

from .serializers import URLSerializer, SecretSharedSerializer
from safesend.models import URL, File
from safesend.utils import password_generator

logger = logging.getLogger(__name__)
OBJECT_TYPES = {"u": URL, "f": File}


class URLAPIView(generics.CreateAPIView):
    queryset = URL.objects.all()
    serializer_class = URLSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)
        password = password_generator()
        instance = serializer.save(password=password, user=request.user)

        secret_url = f"{request.scheme}://{request.get_host()}/secret/u/{instance.uuid}"
        logger.info(
            f"URL `{instance.url}` uploaded by {request.user}. "
            f"Generated secret link: `{secret_url}`"
        )
        return Response(
            {"secret_url": secret_url, "password": password},
            status=status.HTTP_201_CREATED,
        )


class FileAPIView(APIView):
    model = File
    parser_classes = (FileUploadParser,)

    def put(self, request, filename, format=None):
        file_obj = request.FILES["file"]
        password = password_generator()
        file_instance = self.model.objects.create(
            file=file_obj, password=password, user=request.user
        )
        secret_url = (
            f"{request.scheme}://{request.get_host()}/secret/f/{file_instance.uuid}"
        )

        logger.info(
            f"File `{file_instance.file.path}` uploaded by {request.user}. "
            f"Generated secret link: `{secret_url}`"
        )
        return Response(
            {"secret_url": secret_url, "password": password},
            status=status.HTTP_201_CREATED,
        )


class RetrieveSecretAPIView(APIView):
    serializer_class = SecretSharedSerializer
    authentication_classes = []
    permission_classes = []

    def get_secret_object_data(self, url):
        parsed_url = urlparse(url)
        object_type, uuid = parsed_url.path.split("/")[-2:]

        return OBJECT_TYPES[object_type], uuid

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        url = serializer.validated_data["url"]
        password = serializer.validated_data["password"]

        logger.info(f"Trying to receive data from secret url: `{url}`")
        try:
            object, uuid = self.get_secret_object_data(url)
        except (KeyError, ValueError):
            logger.warning(f"Wrong URL provided: {url}")
            return Response("Wrong url", status=status.HTTP_400_BAD_REQUEST)

        instance = get_object_or_404(object, pk=uuid)

        logger.info(f"Checking if password match..")
        if not instance.check_password(password):
            logger.info(f"Wrong password provided for {instance}")
            return Response("Incorrect password.", status=status.HTTP_403_FORBIDDEN)

        instance.visit_counter += 1
        instance.save(hash_password=False)

        logger.info(f"Successfully retrieved an instance with uuid: {uuid}")
        if isinstance(instance, URL):
            return Response({"url": instance.url}, status=status.HTTP_302_FOUND)

        file = open(instance.file.path, "rb")
        encoded_file = base64.b64encode(file.read())
        filename = os.path.basename(instance.file.path)
        return Response(
            {"content": encoded_file, "name": filename}, status.HTTP_302_FOUND
        )


class StatisticsAPIView(APIView):
    def get_unique_visits_per_date(self, model):
        return (
            model.objects.filter(visit_counter__gte=1)
            .annotate(created=functions.TruncDate("created_at"))
            .values("created")
            .annotate(counter=Count("*"))
            .order_by("created")
        )

    def set_number_of_items_per_day(self, statistics, model, field_name):
        for result in self.get_unique_visits_per_date(model):
            statistics[str(result["created"])][field_name] = result["counter"]

    def get(self, request, *args, **kwargs):
        logger.info(f"User: `{request.user}` requested for statistics. ")
        statistics = defaultdict(lambda: {"files": 0, "urls": 0})
        self.set_number_of_items_per_day(statistics, File, "files")
        self.set_number_of_items_per_day(statistics, URL, "urls")

        return Response(statistics, status=status.HTTP_200_OK)

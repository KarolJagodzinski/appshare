from rest_framework import serializers

from safesend.models import File, URL


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ("file",)


class URLSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=False)

    class Meta:
        model = URL
        fields = ("url", "password")


class SecretSharedSerializer(serializers.Serializer):
    url = serializers.URLField()
    password = serializers.CharField()

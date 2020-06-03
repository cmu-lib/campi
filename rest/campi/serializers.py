from rest_framework import serializers
from django.contrib.auth.models import User


class CurrentUserSerializer(serializers.Serializer):
    # model = User
    # fields = ["id", "first_name", "last_name", "username", "email"]
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()

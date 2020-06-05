from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from campi import serializers


class GetSerializerClassMixin(object):
    def get_queryset(self):
        try:
            return self.queryset_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_queryset()

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()


class CurrentUserView(APIView):
    def get(self, request, format=None):
        current_user = request.user
        serialized_user = serializers.UserSerializer(
            current_user, context={"request": request}
        )
        return Response(serialized_user.data, status=status.HTTP_200_OK)

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

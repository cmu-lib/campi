from rest_framework import serializers
import collection.models
from rest_framework_recursive.fields import RecursiveField


class CollectionListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = collection.models.Collection
        fields = ["id", "url", "label"]


class CollectionParentSerializer(serializers.HyperlinkedModelSerializer):
    parent_directory = RecursiveField()

    class Meta:
        model = collection.models.Collection
        fields = ["id", "url", "label", "parent_directory"]


class CollectionDetailSerializer(serializers.HyperlinkedModelSerializer):
    parent_directory = CollectionParentSerializer()
    child_directories = CollectionListSerializer(many=True)

    class Meta:
        model = collection_models.Collection
        fields = ["id", "url", "label", "parent_directory", "child_directories"]

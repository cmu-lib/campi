from rest_framework import serializers
from collection import models as collection_models
from photograph import models as photograph_models
from rest_framework_recursive.fields import RecursiveField


class CollectionListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = collection_models.Collection
        fields = ["id", "url", "label"]


class CollectionParentSerializer(serializers.HyperlinkedModelSerializer):
    parent_collection = RecursiveField()

    class Meta:
        model = collection_models.Collection
        fields = ["id", "url", "label", "parent_collection"]


class CollectionDetailSerializer(serializers.HyperlinkedModelSerializer):
    parent_collection = CollectionParentSerializer()
    child_collections = CollectionListSerializer(many=True)

    class Meta:
        model = collection_models.Collection
        fields = ["id", "url", "label", "parent_collection", "child_collections"]

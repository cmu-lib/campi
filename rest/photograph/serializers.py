from rest_framework import serializers
from photograph import models
import collection.serializers
import tagging.models
import campi.serializers


class PFlatTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = tagging.models.Tag
        fields = ["id", "label"]


class PhotographTagSerializer(serializers.ModelSerializer):
    user_last_modified = campi.serializers.UserSerializer()
    tag = PFlatTagSerializer()

    class Meta:
        model = tagging.models.PhotographTag
        fields = ["id", "tag", "user_last_modified", "last_updated"]


class TaggingDecisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = tagging.models.TaggingDecision
        fields = ["id", "task", "is_applicable", "created_on", "user_created"]


class FaceAnnotationFlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FaceAnnotation
        fields = [
            "id",
            "detection_confidence",
            "joy_likelihood",
            "sorrow_likelihood",
            "anger_likelihood",
            "surprise_likelihood",
            "under_exposed_likelihood",
            "blurred_likelihood",
            "headwear_likelihood",
            "x",
            "y",
            "width",
            "height",
        ]


class ObjectAnnotationLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ObjectAnnotationLabel
        fields = ["id", "label"]


class ObjectAnnotationFlatSerializer(serializers.ModelSerializer):
    label = ObjectAnnotationLabelSerializer()

    class Meta:
        model = models.ObjectAnnotation
        fields = ["id", "label", "score", "x", "y", "width", "height"]


class PhotoLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PhotoLabel
        fields = ["id", "label"]


class PhotoLabelAnnotationSerializer(serializers.ModelSerializer):
    label = PhotoLabelSerializer()

    class Meta:
        model = models.PhotoLabelAnnotation
        fields = ["id", "label", "score"]


class PhotographDetailSerializer(serializers.ModelSerializer):
    directory = collection.serializers.DirectoryDetailSerializer()
    job = collection.serializers.JobDetailSerializer()
    photograph_tags = PhotographTagSerializer(many=True)
    decisions = TaggingDecisionSerializer(many=True)
    faceannotation = FaceAnnotationFlatSerializer(many=True)
    objectannotation = ObjectAnnotationFlatSerializer(many=True)
    label_annotations = PhotoLabelAnnotationSerializer(many=True)

    class Meta:
        model = models.Photograph
        fields = [
            "id",
            "url",
            "label",
            "image",
            "filename",
            "height",
            "width",
            "date_taken_early",
            "date_taken_late",
            "digitized_date",
            "directory",
            "job",
            "job_sequence",
            "photograph_tags",
            "decisions",
            "faceannotation",
            "objectannotation",
            "label_annotations",
        ]


class PhotographListSerializer(serializers.ModelSerializer):
    directory = collection.serializers.DirectoryListSerializer()
    job = collection.serializers.JobListSerializer()
    photograph_tags = PhotographTagSerializer(many=True)
    decisions = TaggingDecisionSerializer(many=True)
    label_annotations = PhotoLabelAnnotationSerializer(many=True)

    class Meta:
        model = models.Photograph
        fields = [
            "id",
            "url",
            "label",
            "image",
            "filename",
            "height",
            "width",
            "date_taken_early",
            "date_taken_late",
            "digitized_date",
            "directory",
            "job",
            "job_sequence",
            "photograph_tags",
            "decisions",
            "label_annotations",
        ]


class PhotographDistanceListSerializer(PhotographListSerializer):
    distance = serializers.FloatField(read_only=True)

    class Meta:
        model = models.Photograph
        fields = [
            "id",
            "url",
            "label",
            "image",
            "filename",
            "height",
            "width",
            "date_taken_early",
            "date_taken_late",
            "digitized_date",
            "directory",
            "job",
            "job_sequence",
            "photograph_tags",
            "decisions",
            "distance",
        ]


class FaceAnnotationSerializer(serializers.ModelSerializer):
    thumbnail = serializers.URLField(read_only=True)
    photograph = PhotographListSerializer(read_only=True)

    class Meta:
        model = models.FaceAnnotation
        fields = [
            "id",
            "photograph",
            "detection_confidence",
            "joy_likelihood",
            "sorrow_likelihood",
            "anger_likelihood",
            "surprise_likelihood",
            "under_exposed_likelihood",
            "blurred_likelihood",
            "headwear_likelihood",
            "x",
            "y",
            "width",
            "height",
            "thumbnail",
        ]


class ObjectAnnotationSerializer(serializers.ModelSerializer):
    thumbnail = serializers.URLField(read_only=True)
    photograph = PhotographListSerializer(read_only=True)
    label = serializers.SlugRelatedField(slug_field="label", read_only=True)

    class Meta:
        model = models.ObjectAnnotation
        fields = [
            "id",
            "photograph",
            "label",
            "score",
            "x",
            "y",
            "width",
            "height",
            "thumbnail",
        ]


class ObjectAnnotationLabelSerializer(serializers.ModelSerializer):
    n_annotations = serializers.IntegerField(read_only=True)
    n_images = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.ObjectAnnotationLabel
        fields = ["id", "label", "n_annotations", "n_images"]


class PhotoLabelSerializer(serializers.ModelSerializer):
    n_images = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.PhotoLabel
        fields = ["id", "label", "n_images"]

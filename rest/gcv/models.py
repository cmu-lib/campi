from django.db import models
from django.conf import settings
from picklefield.fields import PickledObjectField
import photograph.models
from campi.models import dateCreatedModel
from collections import namedtuple


class GCVResponse(dateCreatedModel):
    photograph = models.OneToOneField(
        photograph.models.Photograph,
        on_delete=models.CASCADE,
        related_name="gcv_response",
        help_text="Source photograph for this response",
    )
    annotations = PickledObjectField(null=True)

    def calc_transform_ratio(self):
        if self.photograph.height >= self.photograph.width:
            return self.photograph.height / settings.GOOGLE_SIZE
        else:
            return self.photograph.width / settings.GOOGLE_SIZE

    def extract_faces(self):
        image_ratio = self.calc_transform_ratio()

        face_objects = []

        for face in self.annotations.face_annotations:
            original_x_min = face.bounding_poly.vertices[0].x
            original_x_max = face.bounding_poly.vertices[1].x
            original_y_min = face.bounding_poly.vertices[0].y
            original_y_max = face.bounding_poly.vertices[2].y

            original_width = original_x_max - original_x_min
            original_height = original_y_max - original_y_min

            transformed_x = round(original_x_min * image_ratio)
            transformed_y = round(original_y_min * image_ratio)
            transformed_width = round(original_width * image_ratio)
            transformed_height = round(original_height * image_ratio)

            face_objects.append(
                photograph.models.FaceAnnotation(
                    photograph=self.photograph,
                    x=transformed_x,
                    y=transformed_y,
                    width=transformed_width,
                    height=transformed_height,
                    detection_confidence=face.detection_confidence,
                    joy_likelihood=face.joy_likelihood,
                    sorrow_likelihood=face.sorrow_likelihood,
                    anger_likelihood=face.anger_likelihood,
                    surprise_likelihood=face.surprise_likelihood,
                    under_exposed_likelihood=face.under_exposed_likelihood,
                    blurred_likelihood=face.blurred_likelihood,
                    headwear_likelihood=face.headwear_likelihood,
                )
            )
        photograph.models.FaceAnnotation.objects.bulk_create(face_objects)

    def extract_objects(self):

        located_objects = []
        for obj in self.annotations.localized_object_annotations:
            x_min = round(
                obj.bounding_poly.normalized_vertices[0].x * self.photograph.width
            )
            x_max = round(
                obj.bounding_poly.normalized_vertices[1].x * self.photograph.width
            )
            y_min = round(
                obj.bounding_poly.normalized_vertices[0].y * self.photograph.height
            )
            y_max = round(
                obj.bounding_poly.normalized_vertices[2].y * self.photograph.height
            )

            width = x_max - x_min
            height = y_max - y_min

            label_obj = photograph.models.ObjectAnnotationLabel.objects.get_or_create(
                label=obj.name
            )[0]
            located_objects.append(
                photograph.models.ObjectAnnotation(
                    photograph=self.photograph,
                    x=x_min,
                    y=y_min,
                    width=width,
                    height=height,
                    label=label_obj,
                    score=obj.score,
                )
            )
        photograph.models.ObjectAnnotation.objects.bulk_create(located_objects)

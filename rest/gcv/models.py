from django.db import models
from django.conf import settings
from picklefield.fields import PickledObjectField
import photograph.models
from campi.models import dateCreatedModel


class GCVResponse(dateCreatedModel):
    photograph = models.OneToOneField(
        photograph.models.Photograph,
        on_delete=models.CASCADE,
        related_name="gcv_response",
        help_text="Source photograph for this response",
    )
    annotations = PickledObjectField(null=True)

    def calc_transform_ratio(self):
        long_side = (
            self.photograph.height
            if self.photograph.height >= self.photograph.width
            else self.photograph.width
        )

        return long_side / settings.GOOGLE_SIZE

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
                )
            )
        photograph.models.FaceAnnotation.objects.bulk_create(face_objects)

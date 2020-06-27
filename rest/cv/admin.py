from django.contrib import admin
from cv.models import PyTorchModel


class PyTorchModelAdmin(admin.ModelAdmin):
    fields = ["label", "description"]


admin.site.register(PyTorchModel, PyTorchModelAdmin)

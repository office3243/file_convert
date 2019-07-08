from django.db import models
from django.core.validators import FileExtensionValidator
import uuid

ALLOWED_FILE_TYPES = ("png", "jpg", "jpeg", "pdf", "ppt", "pptx", "xls", "xlsx", "doc", "docx")
FILE_TYPE_CHOICES = (('jpg', 'JPG'), ('png', 'PNG'), ('pdf', 'PDF'), ('txt', 'TXT'))
INPUT_FILES_PATH = "files/input_files"
CONVERTED_FILES_PATH = "files/converted_files"


class File(models.Model):

    input_file = models.FileField(upload_to=INPUT_FILES_PATH,
                                  validators=[FileExtensionValidator(allowed_extensions=ALLOWED_FILE_TYPES), ])
    converted_file = models.FileField(upload_to=CONVERTED_FILES_PATH,
                                      validators=[FileExtensionValidator(allowed_extensions=ALLOWED_FILE_TYPES), ],
                                      blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    has_error = models.BooleanField(default=False)
    file_type = models.CharField(max_length=3, choices=FILE_TYPE_CHOICES, blank=True)

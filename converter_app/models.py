from django.db import models
from django.core.validators import FileExtensionValidator
import uuid
from django.conf import settings
import datetime
from django.db.models.signals import post_save, pre_delete, post_delete
import uuid
from django.urls import reverse_lazy
from django.core.validators import FileExtensionValidator
from . import converters
import os
from PyPDF2 import PdfFileReader


ALLOWED_FILE_TYPES = ("png", "jpg", "jpeg", "pdf", "txt", "ppt", "pptx", "xls", "xlsx", "doc", "docx")
FILE_TYPE_CHOICES = (('jpg', 'JPG'), ('png', 'PNG'), ('pdf', 'PDF'), ('txt', 'TXT'), ('ppt', 'PPT'), ('pptx', 'PPTX'),
                     ('doc', 'DOC'), ('docx', 'DOCX'), ('XLS', 'XLS'), ('xlsx', 'XLSX'))
INPUT_FILES_PATH = "files/input_files"
CONVERTED_FILES_PATH = "files/converted_files"
MEDIA_PATH = settings.MEDIA_ROOT
SITE_DOMAIN = "http://127.0.0.1:8000/"
SITE_DOMAIN_NAKED = "http://127.0.0.1:8000"


class File(models.Model):

    input_file = models.FileField(upload_to=INPUT_FILES_PATH,
                                  validators=[FileExtensionValidator(allowed_extensions=ALLOWED_FILE_TYPES), ])
    converted_file = models.FileField(upload_to=CONVERTED_FILES_PATH,
                                      validators=[FileExtensionValidator(allowed_extensions=ALLOWED_FILE_TYPES), ],
                                      blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    has_error = models.BooleanField(default=False)
    input_file_type = models.CharField(max_length=4, choices=FILE_TYPE_CHOICES)
    converted_file_type = models.CharField(max_length=4, choices=FILE_TYPE_CHOICES, blank=True)

    pages = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_pure_name(self):
        return self.input_file.name[(self.input_file.name.rfind("/") + 1): self.input_file.name.rfind(".")]

    @property
    def get_pdf_path(self):
        return CONVERTED_FILES_PATH + self.get_pure_name + ".pdf"

    @property
    def get_jpg_path_temp(self):
        return MEDIA_PATH + INPUT_FILES_PATH + self.get_pure_name + '.jpg'

    @property
    def get_pdf_path_raw(self):
        return MEDIA_PATH + self.get_pdf_path

    @property
    def convert_input_file(self):
        if self.input_file_type == "pdf":
            return converters.pdf_converter(self)
        elif self.input_file_type == "png":
            return converters.png_converter(self)
        elif self.input_file_type == "jpg":
            return converters.jpg_converter(self)
        else:
            pass

    @property
    def get_file_url(self):
        return SITE_DOMAIN_NAKED + self.converted_file.url

    @property
    def count_pdf_pages(self):
        pdf = PdfFileReader(open(self.converted_file.path, 'rb'))
        return pdf.getNumPages()

    def assign_pages(self):
        pages = self.count_pdf_pages
        if self.pages != pages:
            self.pages = pages
            self.save()

    def save(self, *args, **kwargs):

        if not self.converted_file:
            converted = self.convert_input_file
            if not converted:
                self.has_error = True
                super().save()
            else:
                super().save()

        if self.converted_file and not self.pages:
            self.assign_pages()
            super().save()

from django.core.files.storage import get_storage_class
from django.conf import settings


def get_media_storage():
    storage_class = get_storage_class(settings.DEFAULT_FILE_STORAGE)
    return storage_class()

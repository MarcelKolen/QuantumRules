from django.db import models
from django.utils import timezone


class BaseModuleModel(models.Model):
    """
    This model is the base model the game requires to properly deal with modules.
    This needs to be inherited in the base/core data object in a module
    """
    # Mandatory fields!
    ID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    has_hint = models.BooleanField(default=False)
    hint_content = models.TextField(null=True, blank=True)
    video_link = models.CharField(max_length=300, null=True, blank=True)

    publicationDate = models.DateTimeField(auto_now_add=True)
    lastChangedDate = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

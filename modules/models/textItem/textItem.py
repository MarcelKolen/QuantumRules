from django.db import models
from django.utils import timezone

class TextItem(models.Model):
    """
    Mandatory fields!
    """
    ID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    has_hint = models.BooleanField(default=False)
    hint_content = models.TextField(null=True, blank=True)
    video_link = models.CharField(max_length=300, null=True, blank=True)

    publicationDate = models.DateTimeField(auto_now_add=True)
    lastChangedDate = models.DateTimeField(auto_now=True)

    """
    Custom Fields
    """
    content = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'introduction text'
        verbose_name_plural = 'introduction texts'

    def __str__(self):
        return self.name
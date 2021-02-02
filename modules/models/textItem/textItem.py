from django.db import models
from django.utils import timezone

from modules.models.baseModel import BaseModuleModel


class TextItem(BaseModuleModel):
    """
    Base fields, required by the game engine/interface, are included in the BaseModuleModel.
    This base model can be inherited from and build upon in order to create custom data
    structures for modules. Note that this inheritance is required in the base/core database model of a module!
    """

    # Custom Fields
    content = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'introduction text'
        verbose_name_plural = 'introduction texts'

    def __str__(self):
        return self.name

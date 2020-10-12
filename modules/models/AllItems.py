from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from modules.module_manager import *


class AllModuleItems(models.Model):
    type = models.CharField(
        max_length=2,
        choices=ItemTypes.ITEM_TYPE_CHOICES,
        default=ItemTypes.TEXT_ITEM,
    )

    fkID = models.IntegerField()

    def module_item_content(self):
        try:
            module = select_module(self.type, True)

            if module is False:
                return False
            else:
                return module[1].objects.get(ID=self.fkID)
        except ObjectDoesNotExist:
            return False

    def module_item_handlers(self, admin=False):
        module = select_module(self.type, False, admin)

        if module is False:
            return False
        else:
            return module[1]

    class Meta:
        verbose_name = 'All Module Items'
        verbose_name_plural = 'All Module Items'

    def __str__(self):
        model = self.module_item_content()

        if model is False:
            return 'Module Item' + str(self.id)
        else:
            return model.name

    def type_str(self):
        for key, val in ItemTypes.ITEM_TYPE_CHOICES:
            if self.type == key:
                return val
        return None

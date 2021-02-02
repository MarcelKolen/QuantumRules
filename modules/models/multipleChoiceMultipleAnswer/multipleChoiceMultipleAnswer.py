from django.db import models
from django.utils import timezone

from modules.models.baseModel import BaseModuleModel


class MultipleChoiceMultipleAnswer(BaseModuleModel):
    """
    Base fields, required by the game engine/interface, are included in the BaseModuleModel.
    This base model can be inherited from and build upon in order to create custom data
    structures for modules. Note that this inheritance is required in the base/core database model of a module!
    """

    # Custom Fields
    content = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'MultipleChoice Multiple Answer question'
        verbose_name_plural = 'MultipleChoice Multiple Answer questions'

    def __str__(self):
        return self.name

    def related_choices_content(self):
        return MultipleChoiceMultipleAnswerChoices.objects.filter(related_question=self)


class MultipleChoiceMultipleAnswerChoices(models.Model):
    ID = models.AutoField(primary_key=True)
    related_question = models.ForeignKey(MultipleChoiceMultipleAnswer, null=False, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)

    content = models.TextField(null=True, blank=True)
    correct_answer = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']
        verbose_name = 'MultipleChoice Multiple Answer answer'
        verbose_name_plural = 'MultipleChoice Multiple Answer answers'

    def __str__(self):
        if self.related_question is not None:
            return self.related_question.name + ': Keuze (' + str(self.ID) + ')'
        else:
            return 'Keuze (' + str(self.ID) + ')'

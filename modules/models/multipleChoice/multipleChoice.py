from django.db import models
from django.utils import timezone


class MultipleChoice(models.Model):
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
        verbose_name = 'MultipleChoice question'
        verbose_name_plural = 'MultipleChoice questions'

    def __str__(self):
        return self.name

    def related_choices_content(self):
        return MultipleChoiceChoices.objects.filter(related_question=self)


class MultipleChoiceChoices(models.Model):
    ID = models.AutoField(primary_key=True)
    related_question = models.ForeignKey(MultipleChoice, null=False, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)

    content = models.TextField(null=True, blank=True)
    correct_answer = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']
        verbose_name = 'MultipleChoice answer'
        verbose_name_plural = 'MultipleChoice answers'

    def __str__(self):
        if self.related_question is not None:
            return self.related_question.name + ': Keuze (' + str(self.ID) + ')'
        else:
            return 'Keuze (' + str(self.ID) + ')'

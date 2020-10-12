from django.contrib import admin

from .models import \
    AllModuleItems, \
    TextItem, \
    MultipleChoice, MultipleChoiceChoices, \
    MultipleChoiceMultipleAnswer, MultipleChoiceMultipleAnswerChoices

admin.site.register(TextItem)
admin.site.register(MultipleChoice)
admin.site.register(MultipleChoiceChoices)
admin.site.register(MultipleChoiceMultipleAnswer)
admin.site.register(MultipleChoiceMultipleAnswerChoices)


admin.site.register(AllModuleItems)

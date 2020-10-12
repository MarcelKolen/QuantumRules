from django import forms

from modules.models import TextItem

class TextItemForm(forms.ModelForm):
    class Meta:
        model   = TextItem
        fields  = (
            'name',
            'content',
            'video_link',
            'has_hint',
            'hint_content',
        )

        labels = {
            'name':         'Text Item Naam',
            'content':      'Content',
            'has_hint':     'Heeft deze vraag een hint?',
            'hint_content': 'Hint content',

        }

        help_texts = {
            'content':      'Zowel markdown als LaTeX math zijn ondersteund!',
            'hint_content': 'Zowel markdown als LaTeX math zijn ondersteund!',
            'video_link': 'Gebruik een embedded video link!',
        }
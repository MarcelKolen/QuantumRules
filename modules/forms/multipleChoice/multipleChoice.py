from django import forms

from modules.models import MultipleChoice, MultipleChoiceChoices


class MultipleChoiceForm(forms.ModelForm):
    class Meta:
        model   = MultipleChoice
        fields  = (
            'name',
            'content',
            'video_link',
            'has_hint',
            'hint_content',
        )

        labels = {
            'name':         'Multiplechoice Naam',
            'content':      'Content',
            'has_hint':     'Heeft deze vraag een hint?',
            'hint_content': 'Hint content',

        }

        help_texts = {
            'content':      'Zowel markdown als LaTeX math zijn ondersteund!',
            'hint_content': 'Zowel markdown als LaTeX math zijn ondersteund!',
            'video_link':   'Gebruik een embedded video link!',
        }


class MultipleChoiceChoicesForm(forms.ModelForm):
    class Meta:
        model   = MultipleChoiceChoices
        fields  = (
            'order',
            'content',
            'correct_answer',
        )

        labels = {
            'order':            'Antwoord order',
            'content':          'Antwoord content',
            'correct_answer':   'Juiste antwoord',
        }

        help_texts = {
            'content': 'Zowel markdown als LaTeX math zijn ondersteund!',
        }

        widgets = {
            'content': forms.TextInput(),
        }

from django import forms

from modules.models import QuantumTicTacToe


class QuantumTicTacToeForm(forms.ModelForm):
    class Meta:
        model = QuantumTicTacToe
        fields = (
            'name',
            'content',
            'video_link',
            'has_hint',
            'hint_content',
            'turn',
        )

        labels = {
            'name': 'Quantum Tic Tac Toe Naam',
            'content': 'Content',
            'has_hint': 'Heeft deze vraag een hint?',
            'hint_content': 'Hint content',
            'turn': 'Begint O?'

        }

        help_texts = {
            'content': 'Zowel markdown als LaTeX math zijn ondersteund!',
            'hint_content': 'Zowel markdown als LaTeX math zijn ondersteund!',
            'video_link': 'Gebruik een embedded video link!',
            'turn': 'Ja: O begint. Nee: X begint.',
        }

        widgets = {
            'turn': forms.NullBooleanSelect(),
        }

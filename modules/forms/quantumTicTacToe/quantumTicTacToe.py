from django import forms

from modules.models import QuantumTicTacToe


class QuantumTicTacToeForm(forms.ModelForm):
    class Meta:
        model = QuantumTicTacToe
        fields = (
            'name',
            'video_link',
            'has_hint',
            'hint_content',
        )

        labels = {
            'name': 'Quantum Tic Tac Toe Naam',
            'has_hint': 'Heeft deze vraag een hint?',
            'hint_content': 'Hint content',
        }

        help_texts = {
            'hint_content': 'Zowel markdown als LaTeX math zijn ondersteund!',
            'video_link': 'Gebruik een embedded video link!',
        }

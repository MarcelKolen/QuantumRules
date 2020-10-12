from django import forms

from game.models import Game, Category, GameItemLink
from modules.module_manager import ItemTypes


class AnnouncementForm(forms.Form):
    title = forms.CharField(
        label='Titel',
        max_length=100,
        widget=forms.TextInput(
            attrs={'placeholder': 'Standaard is: \"Aankondiging!\"'}
        ),
        required=False
    )
    message = forms.CharField(
        label='Bericht',
        help_text='Zowel markdown als LaTeX math zijn ondersteund!',
        widget=forms.Textarea
    )


class GameForm(forms.ModelForm):
    class Meta:
        model   = Game
        fields  = '__all__'
        exclude = (
            'ID',
            'published',
            'publicationDate',
            'lastChangedDate',
        )

        labels = {
            'gameName':             'Spelnaam',
            'accessThroughTag':     'Speltoegang via tag',
            'accessTag':            'Speltag',
            'noDateNorTime':        'Spel is niet tijd/datum afhankelijk',
            'startDateTime':        'Startmoment van het spel',
            'endDateTime':          'Sluitingsmoment van het spel',
            'open':                 'Spel openstellen',
            'generalText':          'Algemene beschrijving',
        }

        help_texts = {
            'startDateTime':        'Format is: jjjj-mm-dd uu:mm:ss',
            'endDateTime':          'Format is: jjjj-mm-dd uu:mm:ss',
            'generalText':          'Zowel markdown als LaTeX math zijn ondersteund!',
        }

        widgets = {
            'startDateTime':    forms.DateTimeInput(attrs={'placeholder': 'jjjj-mm-dd uu:mm:ss'}),
            'endDateTime':      forms.DateTimeInput(attrs={'placeholder': 'jjjj-mm-dd uu:mm:ss'}),
        }

    def disableFields(self):
        # self.fields['gameName'].disabled = True
        self.fields['accessThroughTag'].disabled = True
        self.fields['accessTag'].disabled = True
        # self.fields['generalText'].disabled = True


class CatergoryFormAdd(forms.ModelForm):
    class Meta:
        model   = Category
        fields  = ('categoryName',)

        labels  = {'categoryName':     'Categorie naam'}

    def disableFields(self):
        self.fields['categoryName'].disabled = True


class CatergoryFormEdit(forms.ModelForm):
    class Meta:
        model   = Category
        fields  = '__all__'
        exclude = (
            'obtainedCategoryScore',
            'maxCategoryScore',
            'game',
            'firstItem',
        )

        labels = {
            'chained':          'Sequentieel verloop',
        }

        help_texts = {
            'chained':      'Als spelelementen sequentieel moeten velopen, dus na elkaar, moet deze optie gebruikt worden',
        }

    def disableFields(self):
        self.fields['categoryName'].disabled = True
        self.fields['chained'].disabled = True


class GameItemLinkFormEdit(forms.ModelForm):
    class Meta:
        model   = GameItemLink
        fields  = (
            'itemOrder',
            'hidden',
            'gameItemContinueByGM',
            # 'gameItemMaxTime',
            'maxScore',
            'faultPenalty',
            'maxNumAttempts',
        )

        labels = {
            'itemOrder':            'Item volgorde',
            'hidden':               'Verborgen',
            'gameItemContinueByGM': 'Game item moet wachten op input van gamemaster',
            # 'gameItemMaxTime':      'Maximum duurtijd van een game item',
            'maxScore':             'Aantal punten van game item',
            'faultPenalty':         'Punten aftrek na fout antwoord',
            'maxNumAttempts':       'Maximum aantal foute antwoorden mogelijk',
        }

        help_texts = {
            'nextItem':             'Next item hoeft alleen ingesteld te worden als "sequentieel" aangevinkt is',
            'hidden':               'Een verborgen item komt niet in de lijst van onderdelen te staan op de game "homescreen" maar zal wel bezocht worden. Let op! Dit werkt alleen in een sequentiele categorie',
        }

        widgets = {
            'gameItemLinkName': forms.TextInput(attrs={'readonly': 'readonly'}),
            # 'gameItemMaxTime':  forms.TimeInput(attrs={'type': 'time'}),
        }

    def disableFields(self):
        self.fields['gameItemContinueByGM'].disabled = True
        # self.fields['gameItemMaxTime'].disabled = True
        self.fields['maxScore'].disabled = True
        self.fields['faultPenalty'].disabled = True
        self.fields['maxNumAttempts'].disabled = True

    def disableItemOrder(self):
        self.fields['itemOrder'].disabled = True

    def setItemOrderMax(self, maxOrder):
        self.fields['itemOrder'].widget = forms.NumberInput(attrs={'min': '0', 'max': maxOrder - 1})


class Prime_Add_Item_Form(forms.Form):
    item_type = forms.ChoiceField(choices=ItemTypes.ITEM_TYPE_CHOICES)

    class Meta:
        labels = {
            'item_type':    'Item type'
        }

    def disableFields(self):
        self.fields['item_type'].disabled = True


class GameMasterForm_Game(forms.ModelForm):
    class Meta:
        model   = Game
        fields  = (
            'startDateTime',
            'endDateTime',
            'open',
        )

        labels = {
            'startDateTime':        'Startmoment van het spel',
            'endDateTime':          'Sluitingsmoment van het spel',
            'open':                 'Spel openstellen',
        }

        help_texts = {
            'startDateTime':        'Format is: jjjj-mm-dd uu:mm:ss',
            'endDateTime':          'Format is: jjjj-mm-dd uu:mm:ss',
        }

        widgets = {
            'startDateTime':    forms.DateTimeInput(attrs={'placeholder': 'jjjj-mm-dd uu:mm:ss'}),
            'endDateTime':      forms.DateTimeInput(attrs={'placeholder': 'jjjj-mm-dd uu:mm:ss'}),
        }
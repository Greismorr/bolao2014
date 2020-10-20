from django import forms
from .models import Bet
from .models import Game
from .models import Account
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate

class BetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(BetForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Bet
        fields = ('goals_team_one', 'goals_team_two', 'game_name',)
        labels = {'goals_team_one': 'Gols do Primeiro Time', 'goals_team_two': 'Gols do Segundo Time',}

    # Checa se o usuário já fez uma aposta para aquele jogo
    def clean_game_name(self):
        game_name = self.cleaned_data.get('game_name')
        bettor = self.request.user
        self.check_credits(bettor)

        try:
            match = Bet.objects.get(game_name=game_name, bettor=bettor)
        except Bet.DoesNotExist:
            return game_name
        raise forms.ValidationError('Já foi feita uma aposta para esse usuário')

    def check_credits(self, bettor):
        if bettor.credits < 5:
            raise forms.ValidationError('Créditos Insuficientes')


class registration_form(UserCreationForm):
    username = forms.CharField(max_length=30, help_text='Insira um nome de usuário válido.')

    class Meta:
        model = Account
        fields = ('username', 'firstname', 'lastname', 'password1', 'password2',)

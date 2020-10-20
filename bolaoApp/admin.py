from django.contrib import admin
from .models import Account
from .models import Game
from .models import Bet
from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = ('username', 'firstname', 'lastname')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Account
        fields = ('username', 'password', 'firstname', 'lastname', 'credits', 'is_active', 'is_admin')

    def clean_password(self):
        # Retorna o valor inicial independente da input do usuário.
        return self.initial["password"]      


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # Os campos de usuário a serem mostrados.
    list_display = ('username', 'firstname', 'lastname', 'is_admin', 'credits', 'money_won')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('firstname', 'lastname', 'credits', 'is_active', 'money_won',)}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    
    # Esses atributos serão usados para criar novos usuários.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'firstname', 'lastname', 'password1', 'password2', 'credits'),
        }),
    )
    search_fields = ('username',)
    ordering = ('username',)
    filter_horizontal = ()
   

class GameAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'round', 'winner', 'game_ended')
    ordering = ('last_day',)


class BetAdmin(admin.ModelAdmin):
    list_display = ('game_name', 'bettor', 'goals_team_one', 'goals_team_two',)
    ordering = ('game_name',)


admin.site.register(Account, UserAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Bet, BetAdmin)
admin.site.unregister(Group)

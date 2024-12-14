from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'profile_image', 'email']


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Введите действующий email.")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

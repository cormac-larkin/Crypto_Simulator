from django import forms
from django.contrib.auth.models import User

class SignUpForm(forms.ModelForm):
    confirmation = forms.TextInput()

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        help_texts = {
            "username": ""
        }
        
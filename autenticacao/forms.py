from django import forms
from django.contrib.auth.forms import AuthenticationForm
from vencimento.models import Casa  # Importando Casa do outro app

class CustomLoginForm(AuthenticationForm):
    casa = forms.ModelChoiceField(queryset=Casa.objects.none(), required=True)

    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields['casa'].queryset = Casa.objects.all()
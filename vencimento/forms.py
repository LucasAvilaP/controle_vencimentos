from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from .models import Lote, Casa

class LoteForm(forms.ModelForm):
    casa = forms.ModelChoiceField(queryset=Casa.objects.all(), required=True, label="Casa")

    class Meta:
        model = Lote
        fields = ['produto', 'identificacao', 'quantidade', 'categoria', 'data_chegada', 'data_validade', 'casa']
        widgets = {
            'identificacao': forms.TextInput(attrs={'placeholder': 'Digite a identificação do lote'}),
            'data_chegada': forms.DateInput(attrs={'type': 'date'}),
            'data_validade': forms.DateInput(attrs={'type': 'date'}),
            'quantidade': forms.NumberInput(attrs={'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super(LoteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('produto'),
            Field('identificacao'),
            Field('quantidade'),
            Field('categoria'),
            Field('data_chegada'),
            Field('data_validade'),
            Field('casa'),  # Adicione o campo casa aqui para que ele seja renderizado pelo crispy forms
            Submit('submit', 'Adicionar Lote', css_class='btn-primary')
        )


class SaidaProdutoForm(forms.Form):
    lote_id = forms.IntegerField(widget=forms.HiddenInput())
    quantidade_a_retirar = forms.IntegerField(label='Quantidade a retirar', min_value=1, help_text='Informe a quantidade de produtos a ser retirada do estoque.')

    def clean(self):
        cleaned_data = super().clean()
        lote_id = cleaned_data.get('lote_id')
        quantidade_a_retirar = cleaned_data.get('quantidade_a_retirar')
        lote = Lote.objects.get(pk=lote_id)
        
        if quantidade_a_retirar > lote.quantidade:
            raise forms.ValidationError("A quantidade a retirar excede o estoque disponível.")
        
        return cleaned_data

    def save(self):
        lote_id = self.cleaned_data.get('lote_id')
        quantidade_a_retirar = self.cleaned_data.get('quantidade_a_retirar')
        lote = Lote.objects.get(pk=lote_id)
        lote.quantidade -= quantidade_a_retirar
        lote.save()
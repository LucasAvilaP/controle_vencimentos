from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from .models import Lote, Casa, Produto, HistoricoLog
import logging
from django.db import transaction





class LoteForm(forms.ModelForm):
    casa_destinada = forms.ModelChoiceField(queryset=Casa.objects.all(), required=True, label="Casa Destinada")
    produto = forms.ModelChoiceField(
        queryset=Produto.objects.all().order_by('nome'),
        widget=forms.Select(attrs={'class': 'select2', 'style': 'width: 100%'}),
        label="Produto"
    )

    class Meta:
        model = Lote
        fields = ['produto', 'identificacao', 'quantidade', 'categoria', 'data_chegada', 'data_validade', 'casa_destinada']
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
            Field('casa_destinada'),
            Submit('submit', 'Adicionar Lote', css_class='btn-primary')
        )

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        instance.casa = Casa.objects.get(nome="Estoque Central")
        if commit:
            instance.save()
            # Criar log após salvar o lote
            HistoricoLog.objects.create(
                usuario=user,
                lote=instance,
                casa=instance.casa,
                acao='AD',
                descricao=f'Adicionado novo lote de {instance.quantidade} unidades do produto {instance.produto.nome} com validade até {instance.data_validade.strftime("%d/%m/%Y")} na casa {instance.casa.nome}.'
            )
        return instance



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


class TransferenciaLoteForm(forms.Form):
    lote = forms.ModelChoiceField(
        queryset=Lote.objects.filter(casa__nome="Estoque Central").order_by('identificacao'),
        label="Lote",
        widget=forms.Select(attrs={'class': 'select2', 'style': 'width: 100%'})
    )
    quantidade = forms.IntegerField(min_value=1)
    casa_destino = forms.ModelChoiceField(queryset=Casa.objects.exclude(nome="Estoque Central"))

    def clean(self):
        cleaned_data = super().clean()
        lote = cleaned_data.get('lote')
        quantidade = cleaned_data.get('quantidade')

        if lote and quantidade > lote.quantidade:
            raise forms.ValidationError("A quantidade a transferir excede o estoque disponível.")

        return cleaned_data

    def save(self, commit=True):
        lote_original = self.cleaned_data.get('lote')
        quantidade = self.cleaned_data.get('quantidade')
        casa_destino = self.cleaned_data.get('casa_destino')

        if lote_original.quantidade >= quantidade:
            with transaction.atomic():
                # Reduz a quantidade no lote de origem
                lote_original.quantidade -= quantidade
                lote_original.save(update_fields=['quantidade'])

                # Atualiza ou cria um novo lote na casa de destino
                novo_lote, created = Lote.objects.update_or_create(
                    produto=lote_original.produto,
                    categoria=lote_original.categoria,
                    identificacao=lote_original.identificacao,
                    casa=casa_destino,
                    casa_destinada=casa_destino,
                    defaults={
                        'data_chegada': lote_original.data_chegada,
                        'data_validade': lote_original.data_validade,
                        'quantidade': 0,  # Começar com 0 para ajustar após verificação de 'created'
                        'notificacao_enviada': False
                    }
                )
                if not created:
                    novo_lote.quantidade += quantidade  # Se o lote já existir, atualiza a quantidade
                else:
                    novo_lote.quantidade = quantidade  # Se for um novo lote, define a quantidade inicial
                novo_lote.save()

                # Retornar o novo lote, o lote original e a quantidade transferida
                return novo_lote, lote_original, quantidade
        return None


class DevolucaoForm(forms.Form):
    lote = forms.ModelChoiceField(
        queryset=Lote.objects.none(),  # Iniciar com uma queryset vazia
        widget=forms.Select(attrs={'class': 'select2', 'style': 'width: 100%'}),
        label="Lote"
    )
    quantidade = forms.IntegerField(min_value=1, label="Quantidade a Devolver")

    def __init__(self, *args, **kwargs):
        casa = kwargs.pop('casa', None)  # Receber a casa como argumento
        super(DevolucaoForm, self).__init__(*args, **kwargs)
        if casa:
            self.fields['lote'].queryset = Lote.objects.filter(casa=casa)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('lote'),
            Field('quantidade'),
            Submit('submit', 'Devolver', css_class='btn-primary')
        )

    def clean_quantidade(self):
        quantidade = self.cleaned_data['quantidade']
        lote = self.cleaned_data.get('lote')
        return quantidade
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from .models import Lote, Categoria, ConfiguracaoGlobal
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta
from django.db.models import Count
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from openpyxl.styles import Font, Color, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
import requests
from requests import request
from .forms import LoteForm, Lote
from django.contrib import messages
from django.core.mail import send_mail
import json

@login_required
def lista_lotes(request):
    hoje = timezone.now().date()
    query = request.GET.get('q')
    chegada_de = request.GET.get('chegada_de')
    chegada_ate = request.GET.get('chegada_ate')
    validade_de = request.GET.get('validade_de')
    validade_ate = request.GET.get('validade_ate')
    categoria_id = request.GET.get('categoria')
    status = request.GET.get('status')
    configuracao = ConfiguracaoGlobal.objects.first()
    dias_para_vencimento_proximo = configuracao.dias_para_vencimento_proximo if configuracao else 30
    dias_para_urgencia = 30

    lotes = Lote.objects.all()

    # Incluir a lógica para tratar a saída de produtos
    if request.method == 'POST':
        lote_id = request.POST.get('lote_id')
        lote = get_object_or_404(Lote, pk=lote_id)
        quantidade_a_retirar = int(request.POST.get('quantidade_a_retirar'))
        if lote.quantidade >= quantidade_a_retirar:
            lote.quantidade -= quantidade_a_retirar
            lote.save()
            messages.success(request, f"Saida de {quantidade_a_retirar} unidades registrada para o lote {lote.identificacao}.")
        else:
            messages.error(request, "Quantidade a retirar excede o estoque disponível.")
        return redirect('lista_lotes')

    if query:
        lotes = lotes.filter(Q(produto__nome__icontains=query) | Q(identificacao__icontains=query))

    if chegada_de:
        lotes = lotes.filter(data_chegada__gte=chegada_de)
    if chegada_ate:
        lotes = lotes.filter(data_chegada__lte=chegada_ate)

    if validade_de:
        lotes = lotes.filter(data_validade__gte=validade_de)
    if validade_ate:
        lotes = lotes.filter(data_validade__lte=validade_ate)
    if categoria_id:
        lotes = lotes.filter(categoria__id=categoria_id)
    
    # filtro por status
    if status == 'valido':
        lotes = lotes.filter(data_validade__gt=hoje + timedelta(days=dias_para_vencimento_proximo))
    elif status == 'proximo':
        lotes = lotes.filter(data_validade__gt=hoje + timedelta(days=dias_para_urgencia), data_validade__lte=hoje + timedelta(days=dias_para_vencimento_proximo))
    elif status == 'urgente':
        lotes = lotes.filter(data_validade__gt=hoje, data_validade__lte=hoje + timedelta(days=dias_para_urgencia))
    elif status == 'vencido':
        lotes = lotes.filter(data_validade__lte=hoje)

    # Refinar as condições de status para evitar sobreposições
    status_counts = {
        'Valido': lotes.filter(data_validade__gt=hoje + timedelta(days=dias_para_vencimento_proximo)).count(),
        'Urgente': lotes.filter(data_validade__gt=hoje, data_validade__lte=hoje + timedelta(days=dias_para_urgencia)).count(),
        'Proximo do Vencimento': lotes.filter(data_validade__gt=hoje + timedelta(days=dias_para_urgencia), data_validade__lte=hoje + timedelta(days=dias_para_vencimento_proximo)).count(),
        'Vencido': lotes.filter(data_validade__lte=hoje).count(),
    }

    categorias = Categoria.objects.all()
    categoria_data = list(categorias.annotate(total=Count('lotes')).values_list('nome', 'total'))

    return render(request, 'vencimento/lista_lotes.html', {
        'lotes': lotes,
        'categorias': categorias,
        'categoria_data': categoria_data,
        'status_data': [(key, value) for key, value in status_counts.items()]
    })



@login_required
def lotes_vencidos(request):
    lotes = Lote.objects.filter(data_validade__lt=timezone.now().date())
    return render(request, 'vencimento/lista_lotes.html', {'lotes': lotes})


@login_required
def adicionar_lote(request):
    if request.method == 'POST':
        form = LoteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lote adicionado com sucesso!')
            return redirect('lista_lotes')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = LoteForm()
    return render(request, 'vencimento/adicionar_lote.html', {'form': form})


@require_POST
@csrf_exempt
def deletar_lote(request):
    try:
        data = json.loads(request.body)
        lote_id = data.get('lote_id')
        if lote_id:
            lote = Lote.objects.get(id=lote_id)
            lote.delete()
            return JsonResponse({'success': True})
    except Lote.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Lote não encontrado'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dados inválidos'}, status=400)
    return JsonResponse({'success': False, 'error': 'ID do lote não fornecido'}, status=400)



@login_required
def exportar_lotes_excel(request):
    lotes = Lote.objects.all().values(
        'produto__nome', 'categoria__nome', 'identificacao',
        'quantidade', 'data_chegada', 'data_validade'
    )
    df = pd.DataFrame(lotes)
    df.columns = ['Produto', 'Categoria', 'Identificação', 'Quantidade', 'Data de Chegada', 'Data de Validade']

    # Transformar todos os dados da coluna 'Identificação' para maiúsculas
    df['Identificação'] = df['Identificação'].str.upper()

    # Garantir que as colunas de data sejam tratadas como data
    df['Data de Chegada'] = pd.to_datetime(df['Data de Chegada'])
    df['Data de Validade'] = pd.to_datetime(df['Data de Validade'])

    nome_arquivo = "lista_de_lotes.xlsx"
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename={nome_arquivo}'

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Lotes')
        workbook = writer.book
        worksheet = writer.sheets['Lotes']

        # Formatação de cabeçalho
        header_font = Font(bold=True, color='FFFFFF')
        fill = PatternFill("solid", fgColor="4F81BD")
        for col_num, col in enumerate(df.columns, 1):
            cell = worksheet.cell(row=1, column=col_num)
            cell.font = header_font
            cell.fill = fill

        # Ajustar a largura das colunas
        for col in df.columns:
            max_length = max(df[col].astype(str).map(len).max(), len(col))
            worksheet.column_dimensions[get_column_letter(df.columns.get_loc(col) + 1)].width = max_length

        # Formatação de células de data
        date_format = 'dd/mm/yyyy'
        for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row, min_col=5, max_col=6):
            for cell in row:
                cell.number_format = date_format

    return response
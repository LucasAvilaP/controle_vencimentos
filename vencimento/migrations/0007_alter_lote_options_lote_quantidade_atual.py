# Generated by Django 5.0 on 2024-05-09 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vencimento', '0006_lote_quantidade'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lote',
            options={'verbose_name': 'Lote', 'verbose_name_plural': 'Lotes'},
        ),
        migrations.AddField(
            model_name='lote',
            name='quantidade_atual',
            field=models.PositiveIntegerField(default=0, verbose_name='Quantidade Atual'),
        ),
    ]

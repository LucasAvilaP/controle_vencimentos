# Generated by Django 5.0 on 2024-06-05 17:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vencimento', '0014_casa_email_contato'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicolog',
            name='casa',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='vencimento.casa', verbose_name='Casa Relacionada'),
        ),
    ]
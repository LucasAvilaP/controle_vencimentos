# Generated by Django 5.0.6 on 2024-06-04 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vencimento', '0013_historicolog'),
    ]

    operations = [
        migrations.AddField(
            model_name='casa',
            name='email_contato',
            field=models.EmailField(max_length=254, null=True),
        ),
    ]
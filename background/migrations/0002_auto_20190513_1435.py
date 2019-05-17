# Generated by Django 2.1.5 on 2019-05-13 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('background', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cryptocurrencies',
            name='id',
        ),
        migrations.AlterField(
            model_name='cryptocurrencies',
            name='name',
            field=models.CharField(db_index=True, max_length=20, primary_key=True, serialize=False, unique=True),
        ),
    ]
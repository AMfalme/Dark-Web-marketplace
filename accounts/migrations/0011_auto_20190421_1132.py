# Generated by Django 2.1.5 on 2019-04-21 11:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_user_bip39'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='bip39',
            new_name='code_bip39',
        ),
    ]

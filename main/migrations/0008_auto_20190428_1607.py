# Generated by Django 2.1.5 on 2019-04-28 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_remove_message_reply'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='receiver_removed',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='message',
            name='sender_removed',
            field=models.BooleanField(default=True),
        ),
    ]

# Generated by Django 2.1.7 on 2019-04-10 04:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20190409_1635'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='reply',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='message',
            name='content',
            field=models.TextField(default=''),
        ),
    ]

# Generated by Django 3.2.6 on 2022-01-28 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0004_messageroom_last_message_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messageroom',
            name='last_message_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

# Generated by Django 3.2.6 on 2022-01-15 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customlecture', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customlecture',
            name='memo',
            field=models.CharField(max_length=200, null=True),
        ),
    ]

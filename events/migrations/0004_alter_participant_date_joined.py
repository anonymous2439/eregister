# Generated by Django 4.1.7 on 2023-02-17 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_participant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='date_joined',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
# Generated by Django 4.1.7 on 2023-05-14 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_alter_participant_scan_out'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='scan_out',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

# Generated by Django 4.2.19 on 2025-02-28 03:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('llmserver', '0008_userrecord_introduce_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userrecord',
            name='code_status',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='userrecord',
            name='introduce_status',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='userrecord',
            name='pdf_status',
            field=models.IntegerField(default=0),
        ),
    ]

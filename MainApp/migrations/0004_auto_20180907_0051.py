# Generated by Django 2.1 on 2018-09-06 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0003_auto_20180907_0035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailinfo',
            name='Author',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='emailinfojournal',
            name='Author',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]

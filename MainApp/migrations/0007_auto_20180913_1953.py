# Generated by Django 2.1 on 2018-09-13 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0006_auto_20180907_0934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailinfo',
            name='Author',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='emailinfo',
            name='title',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='emailinfojournal',
            name='Author',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='emailinfojournal',
            name='title',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]

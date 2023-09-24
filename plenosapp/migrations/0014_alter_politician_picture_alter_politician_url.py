# Generated by Django 4.0 on 2023-09-16 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plenosapp', '0013_remove_vote_politician_vote_job'),
    ]

    operations = [
        migrations.AlterField(
            model_name='politician',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to='politicians/', verbose_name='Foto cuadrada'),
        ),
        migrations.AlterField(
            model_name='politician',
            name='url',
            field=models.URLField(blank=True, null=True),
        ),
    ]

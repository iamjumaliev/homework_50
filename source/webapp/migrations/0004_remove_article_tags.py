# Generated by Django 2.2 on 2019-10-17 14:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0003_article_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='tags',
        ),
    ]

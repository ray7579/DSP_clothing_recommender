# Generated by Django 4.2 on 2023-03-23 18:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clothes', '0002_comment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='content',
            new_name='comment',
        ),
    ]

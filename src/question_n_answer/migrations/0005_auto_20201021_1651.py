# Generated by Django 3.1.1 on 2020-10-21 16:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('question_n_answer', '0004_auto_20201021_1458'),
    ]

    operations = [
        migrations.RenameField(
            model_name='file',
            old_name='created_data',
            new_name='created_date',
        ),
    ]

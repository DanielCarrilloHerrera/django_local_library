# Generated by Django 3.1.2 on 2021-05-16 04:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_auto_20210515_2255'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='book',
            options={'ordering': ['title', 'author'], 'permissions': (('can_manage_books', 'Can manage books'),)},
        ),
    ]

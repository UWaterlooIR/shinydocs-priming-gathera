# Generated by Django 3.0.5 on 2020-10-10 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_ccnewsrecord'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ccnewsrecord',
            name='record_id',
            field=models.CharField(max_length=50),
        ),
    ]

# Generated by Django 3.1.3 on 2021-01-10 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monstertracker', '0007_drop_grossincomeperkill'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monster',
            name='dropList',
            field=models.ManyToManyField(to='monstertracker.Drop'),
        ),
    ]

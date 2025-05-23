# Generated by Django 5.1.1 on 2025-05-23 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SearchHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(db_index=True, max_length=40)),
                ('city', models.CharField(db_index=True, max_length=100)),
                ('count', models.PositiveIntegerField(default=1)),
            ],
            options={
                'unique_together': {('session_key', 'city')},
            },
        ),
    ]

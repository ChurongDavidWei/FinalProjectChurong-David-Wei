# Generated by Django 5.2 on 2025-05-04 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Holding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticker', models.CharField(max_length=10)),
                ('shares', models.FloatField()),
                ('purchase_price', models.FloatField()),
                ('added_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]

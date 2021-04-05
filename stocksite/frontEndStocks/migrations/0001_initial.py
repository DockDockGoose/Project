# Generated by Django 3.0.5 on 2021-03-02 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FrontEndStock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stockSymbol', models.CharField(max_length=50)),
                ('price', models.FloatField(default=0.0)),
                ('quoteServerTime', models.BigIntegerField(default=0)),
            ],
        ),
    ]
# Generated by Django 5.0.3 on 2024-08-27 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="username",
            field=models.CharField(max_length=100, null=True),
        ),
    ]

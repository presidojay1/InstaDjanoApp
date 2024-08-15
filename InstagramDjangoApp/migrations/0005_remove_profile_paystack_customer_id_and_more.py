# Generated by Django 5.0.7 on 2024-08-14 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('InstagramDjangoApp', '0004_rename_stripe_customer_id_profile_paystack_customer_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='paystack_customer_id',
        ),
        migrations.AddField(
            model_name='profile',
            name='stripe_customer_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]

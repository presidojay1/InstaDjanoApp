# Generated by Django 5.0.7 on 2024-08-09 13:10

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('InstagramDjangoApp', '0002_remove_profile_number_of_ig_accounts_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='instagramaccount',
            name='access_token',
        ),
        migrations.RemoveField(
            model_name='instagramaccount',
            name='account_type',
        ),
        migrations.RemoveField(
            model_name='instagramaccount',
            name='media_count',
        ),
        migrations.RemoveField(
            model_name='instagramaccount',
            name='profile_picture_url',
        ),
        migrations.RemoveField(
            model_name='instagramaccount',
            name='user_id',
        ),
        migrations.AddField(
            model_name='instagramaccount',
            name='password',
            field=models.CharField(default=django.utils.timezone.now, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='number_of_ig_accounts',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='stripe_customer_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='subscription_end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='subscription_plan',
            field=models.CharField(blank=True, choices=[('basic', 'Basic'), ('medium', 'Medium'), ('premium', 'Premium')], max_length=50, null=True),
        ),
        migrations.CreateModel(
            name='PaymentHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('description', models.CharField(max_length=255)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_history', to='InstagramDjangoApp.profile')),
            ],
        ),
    ]

# Generated by Django 5.0.7 on 2024-08-07 23:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('InstagramDjangoApp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='number_of_ig_accounts',
        ),
        migrations.CreateModel(
            name='InstagramAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255)),
                ('access_token', models.CharField(max_length=255)),
                ('user_id', models.CharField(max_length=255)),
                ('profile_picture_url', models.URLField(blank=True, null=True)),
                ('account_type', models.CharField(blank=True, max_length=255, null=True)),
                ('media_count', models.IntegerField(default=0)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='instagram_accounts', to='InstagramDjangoApp.profile')),
            ],
        ),
    ]

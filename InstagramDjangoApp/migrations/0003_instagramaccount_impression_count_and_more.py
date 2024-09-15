# Generated by Django 5.0.6 on 2024-09-15 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("InstagramDjangoApp", "0002_instagramaccount_followers_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="instagramaccount",
            name="impression_count",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="instagramaccount",
            name="media_comment_count",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="instagramaccount",
            name="media_impression_count",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="instagramaccount",
            name="media_like_count",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="instagramaccount",
            name="media_reach_count",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="instagramaccount",
            name="media_save_count",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="instagramaccount",
            name="media_share_count",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="instagramaccount",
            name="profile_views",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="instagramaccount",
            name="reach_count",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="instagramaccount",
            name="website_clicks",
            field=models.IntegerField(default=0),
        ),
    ]

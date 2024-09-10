# Generated by Django 5.0.3 on 2024-08-27 09:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("age", models.IntegerField(blank=True, null=True)),
                ("has_confirmed_otp", models.BooleanField(default=False)),
                ("number_of_ig_accounts", models.PositiveIntegerField(default=0)),
                ("height", models.FloatField(blank=True, null=True)),
                (
                    "stripe_customer_id",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "subscription_plan",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("basic", "Basic"),
                            ("medium", "Medium"),
                            ("premium", "Premium"),
                            ("unsubscribed", "Unsubscribed"),
                        ],
                        default="unsubscribed",
                        max_length=50,
                        null=True,
                    ),
                ),
                ("subscription_end_date", models.DateField(blank=True, null=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PaymentHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("description", models.CharField(max_length=255)),
                ("reference", models.CharField(max_length=255)),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payment_history",
                        to="InstagramDjangoApp.profile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="InstagramAccount",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("username", models.CharField(max_length=255)),
                ("encrypted_password", models.BinaryField()),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="instagram_accounts",
                        to="InstagramDjangoApp.profile",
                    ),
                ),
            ],
        ),
    ]

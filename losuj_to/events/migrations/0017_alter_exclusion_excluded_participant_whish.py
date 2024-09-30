# Generated by Django 5.0 on 2024-08-16 21:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0016_alter_event_confirmed_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="exclusion",
            name="excluded_participant",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="exclusion_as_excluded_participant",
                to="events.participant",
            ),
        ),
        migrations.CreateModel(
            name="Whish",
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
                (
                    "description",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="events.event"
                    ),
                ),
                (
                    "participant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="events.participant",
                    ),
                ),
            ],
        ),
    ]
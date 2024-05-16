# Generated by Django 5.0 on 2024-04-25 21:53

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0014_emailtask_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="confirmed_date",
            field=models.DateField(blank=True, default=datetime.date.today, null=True),
        ),
    ]

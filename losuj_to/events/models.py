from datetime import date

from django.db import IntegrityError, models
from users.models import CustomUser


# Create your models here.
class Event(models.Model):
    class Currency(models.TextChoices):
        USD = "USD", "US Dollars"
        EUR = "EUR", "Euro"
        PLN = "PLN", "Polish zloty"
        GBP = "GBP", "British Pound"

    event_name = models.CharField(max_length=255)
    event_date = models.DateField(default=date.today)
    draw_date = models.DateTimeField(default=date.today, null=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    price_limit = models.IntegerField(null=True)
    price_currency = models.CharField(max_length=3, choices=Currency.choices)
    active = models.BooleanField(default=True)
    ancestor = models.ForeignKey(
        "self", blank=True, null=True, on_delete=models.CASCADE
    )
    confirmed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.event_name


class Draw(models.Model):
    draw_date = models.DateTimeField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    draw_taken = models.BooleanField()


class Participant(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        unique_together = [("event", "name"), ("event", "user")]

    def __str__(self):
        return f"participant {self.name}"


class Exclusion(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name="exlusion_as_participant"
    )
    excluded_participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name="exlusion_as_excluded_participant",
    )

    def save(self, *args, **kwargs):
        if self.participant == self.excluded_participant:
            raise IntegrityError(
                "Participand and exluded participant cannot be the same"
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.participant} excludes {self.excluded_participant} in {self.event}"
        )

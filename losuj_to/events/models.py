import uuid
from datetime import date

from django.core.signing import Signer
from django.db import IntegrityError, models
from users.models import CustomUser


class Event(models.Model):
    class Currency(models.TextChoices):
        USD = "USD", "US Dollars"
        EUR = "EUR", "Euro"
        PLN = "PLN", "Polish zloty"
        GBP = "GBP", "British Pound"

    event_name = models.CharField(max_length=255)
    event_location = models.CharField(max_length=255, null=True)
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
    confirmed_date = models.DateField(default=None, null=True, blank=True)
    token = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self) -> str:
        return self.event_name

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        signer = Signer()
        token = signer.sign(self.id)
        token = token[4:]
        self.token = token
        super().save()


class Participant(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        unique_together = [("event", "name"), ("event", "user")]

    def __str__(self):
        return f"{self.name}"


class Draw(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name="draw_participant"
    )
    drawn_participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name="draw_as_drawn_participant",
    )
    collected = models.BooleanField(default=False, null=False)

    def save(self, *args, **kwargs):
        if self.participant == self.drawn_participant:
            raise IntegrityError("Participant and drawn participant cannot be the same")
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Drawing result for event {self.event} and participant {self.participant} ({self.participant.user}), result: {self.drawn_participant} ({self.drawn_participant.user})"


class Exclusion(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name="exlusion_as_participant"
    )
    excluded_participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name="exclusion_as_excluded_participant",
    )

    def save(self, *args, **kwargs):
        if self.participant == self.excluded_participant:
            raise IntegrityError(
                "Participant and excluded participant cannot be the same"
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.participant} excludes {self.excluded_participant} in {self.event}"
        )


class EmailTask(models.Model):
    class Status(models.TextChoices):
        OK = "OK", "US Dollars"
        NOK = "NOK", "Not send"
        PEN = "PEN", "Pending"

    task_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    email = models.EmailField()
    status = models.CharField(max_length=3, choices=Status.choices, null=True)

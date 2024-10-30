from typing import Any

from django.db import models


class CustomEventManager(models.Manager):
    def create(self, **kwargs: Any) -> Any:
        return super().create(**kwargs)

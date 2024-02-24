from typing import Any

from django.db import models


class CustomEventManager(models.Manager):
    def create(self, **kwargs: Any) -> Any:
        # event = self.model(**kwargs)
        # print("-------custom manager start--------------------------------------")
        # print(event.__dict__)
        # event_id = event.id
        # owner_id = event.owner_id
        # value = f"{event_id}"
        # signer = Signer()
        # token = signer.sign(value)
        # print(token)
        # print("-------custom manager stop---------------------------------------")
        return super().create(**kwargs)

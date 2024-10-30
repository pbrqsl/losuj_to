from typing import Any

from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Updates default site to custom value"

    def handle(self, *args: Any, **options: Any):
        from django.contrib.sites.models import Site

        site = Site.objects.get_current()
        site.domain = "127.0.0.1:8000"
        site.name = "127.0.0.1:8000"
        site.save(update_fields=("domain", "name"))

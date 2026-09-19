import time

from django.core.management.base import BaseCommand

from news_api.scheduler import start


class Command(BaseCommand):
    help = "Run Cyberbrief background scheduler"

    def handle(self, *args, **options):
        scheduler = start()

        try:
            while scheduler.running:
                time.sleep(60)
        except KeyboardInterrupt:
            scheduler.shutdown(wait=False)

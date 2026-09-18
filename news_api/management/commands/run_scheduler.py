import time

from django.core.management.base import BaseCommand

from news_api.scheduler import scheduled_ingest, start


class Command(BaseCommand):
    help = "Run Cyberbrief background scheduler"

    def handle(self, *args, **options):
        scheduled_ingest()
        start()

        self.stdout.write(self.style.SUCCESS("Cyberbrief scheduler started."))

        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            pass

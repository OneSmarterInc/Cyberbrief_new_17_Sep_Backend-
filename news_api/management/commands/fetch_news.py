from django.core.management.base import BaseCommand
from news_api.services import fetch_and_store_news, generate_pending_content

class Command(BaseCommand):
    help = "Fetch RSS news and generate AI summaries"

    def handle(self, *args, **options):
        new_count = fetch_and_store_news()
        processed_count = generate_pending_content(limit=5)
        self.stdout.write(
            self.style.SUCCESS(
                f"Fetched {new_count} new articles and processed {processed_count} with AI"
            )
        )

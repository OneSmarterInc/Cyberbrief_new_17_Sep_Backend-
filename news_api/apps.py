from django.apps import AppConfig
import os

class NewsApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news_api'

    def ready(self):
        # == 'true' ensures the scheduler runs in the newly reloaded worker process!
        if os.environ.get('RUN_MAIN') == 'true':
            from . import scheduler
            scheduler.start()
            print("Background Email Scheduler Started!")
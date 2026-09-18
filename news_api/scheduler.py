from apscheduler.schedulers.background import BackgroundScheduler
import datetime

last_sent_date = None

def scheduled_ingest():
    from .services import fetch_and_store_news
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Checking for new stories...")
    fetch_and_store_news()

def check_and_send_emails():
    global last_sent_date
    from .models import SMTPConfig
    from .views import process_mass_blast

    config = SMTPConfig.objects.first()
    if not config or not config.daily_send_time:
        return

    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M")
    current_date = now.strftime("%Y-%m-%d")

    if current_time == config.daily_send_time and last_sent_date != current_date:
        process_mass_blast()
        last_sent_date = current_date

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_ingest, 'interval', minutes=5, max_instances=1)
    scheduler.add_job(check_and_send_emails, 'cron', minute='*', max_instances=1)
    scheduler.start()

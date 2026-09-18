from apscheduler.schedulers.background import BackgroundScheduler
import datetime

last_sent_date = None

def scheduled_ingest():
    from .services import fetch_and_store_news
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Checking for new stories...")
    fetch_and_store_news()

# NOTE: scheduled_reset has been removed to prevent wiping your database every hour. 
# Your articles will now safely persist for 30 days via the automated purge in services.py.

def check_and_send_emails():
    global last_sent_date
    from .models import SMTPConfig
    from .views import process_mass_blast

    config = SMTPConfig.objects.first()
    if not config or not config.daily_send_time: return

    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M")
    current_date = now.strftime("%Y-%m-%d")

    if current_time == config.daily_send_time and last_sent_date != current_date:
        process_mass_blast()
        last_sent_date = current_date

def start():
    scheduler = BackgroundScheduler()
    # max_instances=1 guarantees the jobs will never overlap and crash
    scheduler.add_job(scheduled_ingest, 'interval', minutes=10, max_instances=1)
    
    # Hourly reset job removed here!
    
    scheduler.add_job(check_and_send_emails, 'cron', minute='*', max_instances=1)
    scheduler.start()

from apscheduler.schedulers.background import BackgroundScheduler
import datetime

last_sent_date = None

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
    
    # NOTE: The AI ingest function (scheduled_ingest) has been permanently removed 
    # from the Django BackgroundScheduler to prevent Gunicorn OOM crashes on EC2.
    # AI fetching must now be triggered via Linux crontab calling the management command.
    
    # Only the lightweight email checker remains in the background thread.
    scheduler.add_job(check_and_send_emails, 'cron', minute=5, max_instances=1)
    scheduler.start()

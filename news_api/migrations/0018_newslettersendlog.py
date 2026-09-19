from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_api', '0017_socialmediaconfig_linkedin_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsletterSendLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('send_date', models.DateField(unique=True)),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]

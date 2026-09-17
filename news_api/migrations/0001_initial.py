from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Article",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("guid", models.CharField(max_length=500, unique=True)),
                ("source", models.CharField(max_length=150)),
                ("category", models.CharField(max_length=50)),
                ("title", models.TextField()),
                ("ai_headline", models.TextField(blank=True)),
                ("summary", models.TextField(blank=True)),
                ("link", models.URLField(blank=True, max_length=1000)),
                ("published", models.CharField(blank=True, max_length=200)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]

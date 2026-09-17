from django.db import models
from django.db import models
from django.contrib.auth.models import User


class AdminTwoFactor(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="two_factor"
    )
    secret = models.CharField(max_length=64)
    is_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"2FA - {self.user.username}"

class Article(models.Model):
    guid = models.CharField(max_length=500, unique=True)
    source = models.CharField(max_length=150)
    category = models.CharField(max_length=50)
    title = models.TextField()
    ai_headline = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    link = models.URLField(max_length=1000, blank=True)
    published = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.ai_headline or self.title

class ArticleQuery(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="queries")
    query_text = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Query for {self.article.id}"

class SMTPConfig(models.Model):
    name = models.CharField(max_length=150, blank=True)
    email = models.CharField(max_length=150)
    reply_to = models.CharField(max_length=150, blank=True)
    
    host = models.CharField(max_length=200)
    port = models.IntegerField(default=587)
    username = models.CharField(max_length=200, blank=True)
    password = models.CharField(max_length=200)
    
    PROTOCOL_CHOICES = [
        ('TLS', 'TLS'),
        ('SSL', 'SSL'),
        ('NONE', 'None'),
    ]
    security_protocol = models.CharField(max_length=10, choices=PROTOCOL_CHOICES, default='TLS')
    
    # NEW: Daily scheduled time
    daily_send_time = models.CharField(max_length=5, default="08:00") 
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SMTP: {self.host}"


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    emails_received = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True) # <--- ADD THIS LINE

    class Meta:
        ordering = ["-subscribed_at"]

    def __str__(self):
        return self.email

class Admin2FA(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name="admin_2fa")
    totp_secret = models.CharField(max_length=64, blank=True)
    is_enabled = models.BooleanField(default=False)

    def __str__(self):
        return f"2FA for {self.user.username}"

class RSSFeed(models.Model):
    name = models.CharField(max_length=150)
    url = models.URLField(max_length=500, unique=True)
    category = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.category})"
    
class SocialMediaConfig(models.Model):
    twitter = models.URLField(max_length=500, blank=True)
    youtube = models.URLField(max_length=500, blank=True)
    email = models.CharField(max_length=500, blank=True)
    insta = models.URLField(max_length=500, blank=True)
    facebook = models.URLField(max_length=500, blank=True)
    linkedin = models.URLField(max_length=500, blank=True) # <-- ADD THIS FIELD

    def __str__(self):
        return "Social Media Links"
    
class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image_data = models.TextField(blank=True, null=True)
    publish_option = models.CharField(max_length=50, default="now")
    scheduled_for = models.DateTimeField(blank=True, null=True)  # <--- NEW FIELD
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    url = models.URLField(max_length=500)  # Purchase Link
    image_data = models.TextField(blank=True, null=True)  # Base64 image storage
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
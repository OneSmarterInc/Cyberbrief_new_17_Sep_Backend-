from django.contrib import admin
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("source", "category", "ai_headline", "created_at")
    list_filter = ("source", "category")
    search_fields = ("title", "ai_headline", "summary")

from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health, name='health'),
    path('news/', views.news, name='news'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    
    # Updated to match the React frontend fetch URLs
    path('setup-2fa/', views.setup_2fa, name='setup_2fa'),
    path('verify-2fa/', views.verify_2fa, name='verify_2fa'),
    
    # Added the missing logout endpoint
    path('logout/', views.logout, name='logout'),
    
    path('news/<int:article_id>/toggle/', views.toggle_article, name='toggle_article'),
    path('news/<int:article_id>/query/', views.submit_query, name='submit_query'),
    path('admin/queries/', views.get_queries, name='get_queries'),
    path('admin/queries/<int:query_id>/toggle/', views.toggle_query_status, name='toggle_query_status'),
    path('admin/subscribers/', views.manage_subscribers, name='manage_subscribers'),
    path('admin/subscribers/<int:sub_id>/toggle/', views.toggle_subscriber, name='toggle_subscriber'),
    path('admin/subscribers/<int:sub_id>/delete/', views.delete_subscriber, name='delete_subscriber'),
    path('admin/smtp/', views.manage_smtp, name='manage_smtp'),
    path('admin/smtp/test/', views.send_test_email, name='send_test_email'),
    path('admin/smtp/blast/', views.send_daily_blast, name='send_daily_blast'),
    path('subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('unsubscribe/', views.unsubscribe_email, name='unsubscribe_email'),
    path('audio/', views.generate_audio, name='generate_audio'),
    path('admin/feeds/', views.manage_rss_feeds, name='manage_rss_feeds'),
    path('admin/feeds/<int:feed_id>/', views.modify_rss_feed, name='modify_rss_feed'),
    path("social/", views.get_social_links, name="get_social_links"),
    path("admin/social/", views.admin_social_links, name="admin_social_links"),
    
    # --- UPDATED BLOG URLS ---
    path("blogs/", views.get_blogs, name="get_blogs"),
    path("admin/blogs/", views.admin_manage_blogs, name="admin_manage_blogs"),
    path("admin/blogs/<int:blog_id>/", views.admin_modify_blog, name="admin_modify_blog"),
    path('books/', views.get_books, name='get_books'), # Public facing books
    path('admin/books/', views.admin_manage_books, name='admin_manage_books'), # Admin GET/POST
    path('admin/books/<int:book_id>/', views.admin_modify_book, name='admin_modify_book'), 
    path("rss-feeds/", views.get_active_rss_feeds, name="get_active_rss_feeds"),# Admin PUT/DELETE
]
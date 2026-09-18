import os
import hashlib
import re
import html
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import feedparser
from django.db import close_old_connections
from django.utils import timezone
from django.conf import settings

from .models import Article, RSSFeed

# --- STRICT CYBERSECURITY KEYWORD FILTER ---
CYBER_KEYWORDS = [
    "cybersecurity", "cyber-security", "infosec", "malware", "ransomware", 
    "vulnerability", "exploit", "cve", "zero-day", "hacker", "hackers", 
    "breach", "data leak", "data breach", "phishing", "cyberattack", 
    "cyber attack", "ddos", "trojan", "spyware", "backdoor", "patch", 
    "security flaw", "security update", "secops", "threat actor", "apt", 
    "malicious", "credential", "stolen data", "security incident", "encryption",
    "authentication", "firewall", "botnet", "cisco", "microsoft patch", "apple security"
]

def is_cybersecurity_related(title, summary):
    text = f"{title} {summary}".lower()
    return any(keyword in text for keyword in CYBER_KEYWORDS)

def clean_text(value):
    if not value:
        return ""
    text = html.unescape(value)
    text = re.sub(r'&#[a-zA-Z0-9;]+', "'", text) 
    text = text.replace("&#xd", "").replace("&#xD", "")
    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub(r"<[^>]+>", " ", text)
    return " ".join(text.split())

def strip_ai_artifacts(text):
    if not text:
        return ""
    
    text = re.sub(r'^(here is|summary:|assistant:|sure).*?:', '', text, flags=re.IGNORECASE)
    text = re.sub(r"(?:i'm|i am|i have|i've)\s+(?:excited to share|planned|announced|noted).*?(?:\.|:)", "", text, flags=re.IGNORECASE)
    text = re.sub(r'```[a-zA-Z]*', '', text) 
    text = text.replace('`', '') 
    text = re.sub(r'[\u4e00-\u9fff\u3000-\u30ff]', '', text)
    text = re.sub(r'\([^)]*\)', '', text)                    
    text = re.sub(r'\[.*?\]', '', text)                      
    text = re.sub(r'[\(\)\[\]\{\}\|\<\>\~_#\*\\/]', ' ', text)
    text = re.sub(r'\s*[,;:\-\.]\s*[,;:\-\.]+', '.', text)    
    text = re.sub(r'\s{2,}', ' ', text)                      
    return text.strip()

def detect_category(title, summary, default_category=None):
    return "Cybersecurity"

def make_guid(source, link, title):
    return hashlib.sha256(f"{source}|{link}|{title}".encode("utf-8")).hexdigest()

def reset_article_database():
    deleted_count, _ = Article.objects.all().delete()
    print(f"Database Reset: Removed {deleted_count} old articles.")
    return deleted_count

def get_active_feeds():
    feeds = RSSFeed.objects.filter(is_active=True)
    if not feeds.exists():
        return [
            {"name": "The Hacker News", "url": "[https://feeds.feedburner.com/TheHackersNews](https://feeds.feedburner.com/TheHackersNews)", "category": "Cybersecurity"},
            {"name": "BleepingComputer", "url": "[https://www.bleepingcomputer.com/feed/](https://www.bleepingcomputer.com/feed/)", "category": "Cybersecurity"},
            {"name": "Krebs on Security", "url": "[https://krebsonsecurity.com/feed/](https://krebsonsecurity.com/feed/)", "category": "Cybersecurity"},
            {"name": "Dark Reading", "url": "[https://www.darkreading.com/rss.xml](https://www.darkreading.com/rss.xml)", "category": "Cybersecurity"},
        ]
    return [{"name": f.name, "url": f.url, "category": "Cybersecurity"} for f in feeds]

def fetch_feed_data(feed_info):
    items = []
    try:
        # Upgraded headers to bypass basic Cloudflare/AWS bot blocks
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        response = requests.get(feed_info["url"], timeout=10, headers=headers)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        for item in feed.entries[:6]: 
            items.append({"feed_info": feed_info, "item": item})
    except Exception as e:
        # Prints out the 403 Forbidden or Timeout if AWS IP is blocked
        print(f"RSS Fetch Error [{feed_info['name']}]: {e}")
    return items

def fetch_and_store_news():
    close_old_connections()
    
    thirty_days_ago = timezone.now() - timedelta(days=30)
    expired_count, _ = Article.objects.filter(created_at__lt=thirty_days_ago).delete()
    if expired_count > 0:
        print(f"Database Cleanup: Purged {expired_count} stories older than 30 days.")

    current_rss_feeds = get_active_feeds()
    raw_items = []

    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = [executor.submit(fetch_feed_data, feed) for feed in current_rss_feeds]
        for future in as_completed(futures):
            raw_items.extend(future.result())

    new_found = 0
    filtered_out = 0

    for data in raw_items:
        feed_info = data["feed_info"]
        item = data["item"]
        title = clean_text(item.get("title"))
        raw_summary = clean_text(item.get("summary") or item.get("description") or "")
        link = item.get("link", "")

        if not title:
            continue

        if not is_cybersecurity_related(title, raw_summary):
            filtered_out += 1
            continue

        category = detect_category(title, raw_summary, default_category=feed_info.get("category"))
        guid = make_guid(feed_info["name"], link, title)

        if not Article.objects.filter(guid=guid).exists():
            Article.objects.create(
                guid=guid,
                source=feed_info["name"],
                category=category,
                title=title,
                ai_headline="",  
                summary=raw_summary,
                link=link,
                published=clean_text(item.get("published") or item.get("updated") or ""),
            )
            new_found += 1
            print(f"--> NEW CYBER STORY [{feed_info['name']}]: {title[:40]}...")

    print(f"Live Scan Complete: Checked {len(raw_items)} articles. Skipped {filtered_out} non-cyber articles. Added {new_found} new.")

    # PHASE 2: Qwen2.5 Chat-Template Summarization Pipeline
    pending_articles = Article.objects.filter(ai_headline="")
    
    if pending_articles.exists():
        print(f"AI Model Processing {pending_articles.count()} unsummarized cybersecurity articles with Qwen2.5...")
        
        # MODEL LOADED LOCALLY TO PREVENT GUNICORN OOM CRASHES
        print("Loading AI Model into memory...")
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            # Resolves the absolute path dynamically so cron doesn't fail
            MODEL_PATH = os.path.join(settings.BASE_DIR, "ai_model")
            
            tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
            model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)
        except Exception as e:
            print(f"Failed to load AI model from {MODEL_PATH}. Error: {e}")
            return

        for art in pending_articles:
            cleaned_title = clean_text(art.title)
            cleaned_raw_summary = clean_text(art.summary)
            
            if len(cleaned_raw_summary.split()) < 10:
                content_to_use = f"A cybersecurity report and technical advisory focusing on: {cleaned_title}."
            else:
                content_to_use = cleaned_raw_summary

            messages = [
                {
                    "role": "system", 
                    "content": (
                        "You are a strict, zero-hallucination cybersecurity news editor. "
                        "Summarize the provided text accurately and objectively in plain English (80-120 words). "
                        "CRITICAL RULES:\n"
                        "1. Use ONLY facts explicitly stated in the source text. Do not extrapolate.\n"
                        "2. NEVER add historical comparisons, corporate boilerplate (e.g., 'commitment to security'), or unverified impacts.\n"
                        "3. If details are sparse, keep the summary brief and factual based solely on the title and provided snippet.\n"
                        "4. Do not repeat the title."
                    )
                },
                {"role": "user", "content": f"Title: {cleaned_title}\n\nContent: {content_to_use}"}
            ]
            
            try:
                text_input = tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
                
                inputs = tokenizer([text_input], return_tensors="pt").to(model.device)
                
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=220,    
                    min_new_tokens=100,    
                    temperature=0.3,
                    do_sample=True,
                    top_p=0.9,
                    repetition_penalty=1.15 
                )
                
                generated_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
                raw_summary = tokenizer.decode(generated_tokens, skip_special_tokens=True)
                final_summary = strip_ai_artifacts(raw_summary)
                
            except Exception as exc:
                print(f"AI Error on '{art.title[:20]}': {exc}")
                continue

            if final_summary:
                if final_summary.lower().startswith(cleaned_title.lower()):
                    final_summary = final_summary[len(cleaned_title):].strip()
                
                final_summary = re.sub(r'^[^a-zA-Z0-9]+', '', final_summary).strip()
                
                if len(final_summary) > 0:
                    final_summary = final_summary[0].upper() + final_summary[1:]
                
                if not final_summary.endswith((".", "!", "?")):
                    last_punctuation = max(final_summary.rfind("."), final_summary.rfind("!"), final_summary.rfind("?"))
                    if last_punctuation > len(final_summary) * 0.5:
                        final_summary = final_summary[:last_punctuation+1]
                    else:
                        final_summary += "."

            if len(final_summary.split()) < 15:
                final_summary = f"Comprehensive cybersecurity coverage regarding {cleaned_title}. Read the complete analysis via the original source link provided below."

            art.ai_headline = art.title[:500]
            art.summary = final_summary[:2000]
            art.save(update_fields=["ai_headline", "summary"])
            print(f"--> AI Summary Ready: {art.title[:30]}...")

    close_old_connections()

def get_stored_news():
    return Article.objects.all().order_by("-id")

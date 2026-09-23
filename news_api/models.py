import re
from django.db import models
from django.contrib.auth.models import User

# --- 8 Specialized Cybersecurity Keyword Groups ---
PROFESSOR_KEYWORD_MAP = {
    1: [  # Security Operations (SOC)
        "siem", "soar", "soc", "security operations center", "secops", "xdr", "edr", 
        "ndr", "mdr", "security incident response", "incident response", 
        "incident investigation", "digital forensics", "forensics", "threat detection", 
        "intrusion detection", "intrusion prevention", "ids", "ips"
    ],
    2: [  # Vulnerability & Application Security
        "vulnerability", "vulnerabilities", "exploit", "exploitation", "zero-day", "0-day", 
        "zero day", "security flaw", "security flaws", "cve", "cvss", "kev", 
        "known exploited vulnerability", "security patch", "patching", "patch management", 
        "security update", "firmware vulnerability", "critical vulnerability", 
        "remote code execution", "rce", "privilege escalation", "local privilege escalation", 
        "lpe", "command injection", "code injection", "sql injection", "sqli", "xss", 
        "cross-site scripting", "csrf", "ssrf", "xxe", "path traversal", "directory traversal", 
        "buffer overflow", "memory corruption", "authentication bypass", "sandbox escape", 
        "security bypass", "application security", "appsec", "software security", 
        "secure coding", "devsecops", "code security", "source code vulnerability", 
        "dependency vulnerability", "browser security", "chrome vulnerability", 
        "firefox vulnerability", "edge vulnerability", "safari vulnerability", 
        "mobile vulnerability", "bug bounty", "responsible disclosure", "security advisory"
    ],
    3: [  # Threat Intelligence & Research
        "threat actor", "threat actors", "attack group", "adversary", "adversaries", 
        "apt", "advanced persistent threat", "nation-state attack", "state-sponsored", 
        "state sponsored", "threat intelligence", "cyber threat intelligence", "cti", 
        "ioc", "indicators of compromise", "ttp", "ttps", "threat hunting", "threat report", 
        "security report", "threat research", "security researcher", "security researchers", 
        "ethical hacker", "dark web", "darkweb", "dark web marketplace", "underground forum", 
        "crowdstrike", "sentinelone", "mandiant"
    ],
    4: [  # Malware & Ransomware Security
        "malware", "ransomware", "spyware", "adware", "trojan", "rootkit", "worm", 
        "backdoor", "keylogger", "botnet", "cryptojacking", "wiper", "stealer", 
        "infostealer", "loader", "dropper", "mobile malware", "ransomware group", 
        "ransomware gang", "ransomware attack", "ransomware campaign", "extortion", 
        "double extortion", "malware analysis", "reverse engineering malware", 
        "sophos security", "eset security", "trend micro"
    ],
    5: [  # REPLACED: AI & Machine Learning Cybersecurity
        "artificial intelligence", "ai security", "machine learning", "llm vulnerability", 
        "prompt injection", "large language model", "chatgpt security", "deepfake", 
        "generative ai", "genai security", "data poisoning", "model inversion", 
        "adversarial ai", "ai threat", "automated attack", "ai-powered attack", 
        "neural network security"
    ],
    6: [  # REPLACED: Financial Cybersecurity & FinTech
        "fintech security", "bank breach", "financial fraud", "cryptocurrency hack", 
        "crypto theft", "defi exploit", "blockchain security", "smart contract vulnerability", 
        "swift network", "payment security", "atm skimming", "wire fraud", 
        "digital wallet breach", "crypto exchange attack", "financial cybercrime"
    ],
    7: [  # Cloud & Supply Chain Security
        "cloud security", "cloud cybersecurity", "aws security", "azure security", 
        "google cloud security", "cloud vulnerability", "cloud breach", "cloud attack", 
        "container security", "docker security", "kubernetes security", "k8s security", 
        "serverless security", "saas security", "api security", "api vulnerability", 
        "api attack", "software supply chain", "software supply-chain attack", 
        "supply chain attack", "supply-chain security", "open source security", 
        "third-party risk", "dependency confusion", "typosquatting"
    ],
    8: [  # REPLACED: Core Security & Cyber-Physical Defense
        "cyber warfare", "national security", "cyber-physical", "infrastructure attack", 
        "homeland security", "cisa", "cyber defense", "state-sponsored attack", 
        "iot security", "physical breach", "critical infrastructure", "ot security", 
        "scada security", "industrial cybersecurity", "grid attack", "cyber espionage"
    ]
}

def determine_professor_by_content(text):
    """Scans text against keyword mapping and returns the professor ID with the most matches."""
    if not text:
        return 1
    
    clean_text = text.lower()
    scores = {prof_id: 0 for prof_id in PROFESSOR_KEYWORD_MAP.keys()}

    for prof_id, keywords in PROFESSOR_KEYWORD_MAP.items():
        for kw in keywords:
            pattern = r'\b' + re.escape(kw) + r'\b'
            matches = len(re.findall(pattern, clean_text))
            if matches > 0:
                scores[prof_id] += matches

    best_prof = max(scores, key=scores.get)
    return best_prof if scores[best_prof] > 0 else 1

# Dummy function restored to satisfy old migration dependency lookups
def get_random_professor():
    return 1


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
    
    professor_id = models.IntegerField(default=get_random_professor)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        # Dynamically evaluate keywords across the article text to assign the correct desk
        combined_text = f"{self.title} {self.ai_headline} {self.summary} {self.category}"
        self.professor_id = determine_professor_by_content(combined_text)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.ai_headline or self.title


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
    daily_send_time = models.CharField(max_length=5, default="08:00") 
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SMTP: {self.host}"


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    emails_received = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

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


class NewsletterSendLog(models.Model):
    send_date = models.DateField(unique=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.send_date)


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
    linkedin = models.URLField(max_length=500, blank=True)

    def __str__(self):
        return "Social Media Links"
    

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image_data = models.TextField(blank=True, null=True)
    publish_option = models.CharField(max_length=50, default="now")
    scheduled_for = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    url = models.URLField(max_length=500)
    image_data = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class VolunteerApplication(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    position = models.CharField(max_length=255)
    preferred_desk = models.CharField(max_length=255, blank=True)
    pitch = models.TextField()
    portfolio_url = models.URLField(max_length=500, blank=True)
    resume_data = models.TextField(blank=True, null=True)
    samples_data = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]  # Fixed error from '-random'

    def __str__(self):
        return f"{self.full_name} - {self.position}"


class OpenPosition(models.Model):
    title = models.CharField(max_length=255)
    seats = models.IntegerField(default=1)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

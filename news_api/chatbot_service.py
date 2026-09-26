import difflib
import multiprocessing
import re

import torch
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Q
from transformers import AutoModelForCausalLM, AutoTokenizer

from .models import Article


num_cores = multiprocessing.cpu_count()
torch.set_num_threads(num_cores)

MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float32,
    device_map="auto"
)


PROF_MAP = {
    1: [
        "arion",
        "vale",
        "arion vale",
        "soc",
        "operations",
        "security operations"
    ],
    2: [
        "lyra",
        "sen",
        "lyra sen",
        "vulnerability",
        "vulnerabilities",
        "appsec",
        "application security"
    ],
    3: [
        "kael",
        "nore",
        "kael nore",
        "threat",
        "threat intelligence",
        "research",
        "apt"
    ],
    4: [
        "elara",
        "quinn",
        "elara quinn",
        "malware",
        "ransomware",
        "cybercriminal",
        "cybercriminals"
    ],
    5: [
        "dorian",
        "kade",
        "dorian kade",
        "machine learning",
        "adversarial",
        "ai",
        "artificial intelligence"
    ],
    6: [
        "mira",
        "solen",
        "mira solen",
        "fintech",
        "financial",
        "financial cybersecurity"
    ],
    7: [
        "orion",
        "blake",
        "orion blake",
        "cloud",
        "supply chain",
        "cloud security"
    ],
    8: [
        "seraphina",
        "sera",
        "rowe",
        "seraphina rowe",
        "cyber-physical",
        "critical infrastructure",
        "ics",
        "scada"
    ]
}


PROFESSOR_KNOWLEDGE = {
    1: {
        "name": "Arion Vale",
        "role": "Security Operations (SOC)"
    },
    2: {
        "name": "Lyra Sen",
        "role": "Vulnerability & Application Security"
    },
    3: {
        "name": "Kael Nore",
        "role": "Threat Intelligence & Research"
    },
    4: {
        "name": "Elara Quinn",
        "role": "Malware & Ransomware Security"
    },
    5: {
        "name": "Dorian Kade",
        "role": "AI & Machine Learning Security"
    },
    6: {
        "name": "Mira Solen",
        "role": "Financial Cybersecurity & FinTech"
    },
    7: {
        "name": "Orion Blake",
        "role": "Cloud & Supply Chain Security"
    },
    8: {
        "name": "Seraphina Rowe",
        "role": "Core Security & Cyber-Physical Defense"
    }
}


PROFESSOR_ALIASES = {
    1: ["arion", "vale", "arion vale"],
    2: ["lyra", "sen", "lyra sen"],
    3: ["kael", "nore", "kael nore"],
    4: ["elara", "quinn", "elara quinn"],
    5: ["dorian", "kade", "dorian kade"],
    6: ["mira", "solen", "mira solen"],
    7: ["orion", "blake", "orion blake"],
    8: ["seraphina", "sera", "rowe", "seraphina rowe"]
}


ROUTE_MAP = {
    "/join": [
        "join",
        "apply",
        "career",
        "job",
        "volunteer",
        "intern",
        "internship",
        "hiring",
        "work"
    ],
    "/how": [
        "about",
        "how it works",
        "mission",
        "vision",
        "who are you",
        "what is cyberbrief",
        "what is cyberbriefs"
    ],
    "/rss": [
        "rss",
        "podcast",
        "feed",
        "feeds",
        "xml"
    ],
    "/newsroom": [
        "newsroom",
        "team",
        "correspondents",
        "authors",
        "reporters",
        "journalists"
    ],
    "/blogs": [
        "blog",
        "blogs",
        "editorial",
        "opinion"
    ],
    "/books": [
        "book",
        "books",
        "literature",
        "library",
        "reading"
    ]
}


LATEST_INTENT_VOCAB = {
    "latest",
    "newest",
    "new",
    "recent",
    "today",
    "current",
    "update",
    "updates",
    "headlines",
    "fresh",
    "happening",
    "top",
    "briefing",
    "news"
}


CYBERBRIEF_KEYWORDS = {
    "cyberbrief",
    "cyberbriefs",
    "cybersecurity",
    "cyber",
    "news",
    "article",
    "articles",
    "headline",
    "headlines",
    "briefing",
    "brief",
    "rss",
    "feed",
    "feeds",
    "newsroom",
    "blog",
    "blogs",
    "book",
    "books",
    "correspondent",
    "correspondents",
    "reporter",
    "reporters",
    "author",
    "authors",
    "team",
    "join",
    "career",
    "intern",
    "internship",
    "volunteer",
    "mission",
    "vision",
    "platform",
    "website",
    "malware",
    "ransomware",
    "vulnerability",
    "vulnerabilities",
    "threat",
    "threats",
    "apt",
    "soc",
    "appsec",
    "cloud",
    "fintech",
    "financial",
    "ai",
    "artificial",
    "intelligence",
    "machine",
    "learning",
    "supply",
    "chain",
    "critical",
    "infrastructure",
    "ics",
    "scada"
}


ABOUT_CYBERBRIEFS_KNOWLEDGE = """
CyberBrief is a modern cybersecurity and technology news discovery platform.

CyberBrief focuses on:
- Cybersecurity
- Artificial Intelligence
- Software
- Cloud Computing
- Digital Security

CyberBrief brings relevant stories from technology publishers into one unified news desk.

Website sections:

Home (/)
Main aggregated daily briefing and news stream.

Newsroom (/newsroom)
Intelligence organized by CyberBrief correspondents.

RSS Feeds (/rss)
RSS intelligence sources and podcast feeds.

About (/how)
CyberBrief mission, vision, and AI-augmented newsroom structure.

Blogs (/blogs)
In-depth editorial analysis.

Books (/books)
Recommended cybersecurity and technology literature.

Careers & Join (/join)
Volunteer, internship, and career application portal.

CyberBrief correspondents:

Arion Vale
Security Operations / SOC

Lyra Sen
Vulnerability & Application Security

Kael Nore
Threat Intelligence & Research

Elara Quinn
Malware & Ransomware Security

Dorian Kade
AI & Machine Learning Security

Mira Solen
Financial Cybersecurity & FinTech

Orion Blake
Cloud & Supply Chain Security

Seraphina Rowe
Core Security & Cyber-Physical Defense
"""


OUT_OF_SCOPE_REPLY = (
    "I am the CyberBrief AI Assistant. "
    "I can only answer questions related to CyberBrief, "
    "its cybersecurity news, articles, correspondents, sections, "
    "RSS feeds, blogs, books, careers, and platform information."
)


NO_INFORMATION_REPLY = (
    "I couldn't find reliable information about that in the CyberBrief "
    "knowledge base. I don't want to guess or provide information that "
    "isn't supported by CyberBrief."
)


def clean_tokens(text: str):
    tokens = re.findall(r"[a-z0-9]+", text.lower())

    filler = {
        "what",
        "is",
        "are",
        "the",
        "tell",
        "me",
        "can",
        "you",
        "give",
        "show",
        "i",
        "want",
        "to",
        "know",
        "about",
        "there",
        "any",
        "some",
        "please",
        "who",
        "where",
        "when",
        "why",
        "how",
        "do",
        "does",
        "did",
        "a",
        "an",
        "for",
        "of",
        "on",
        "in",
        "with",
        "and",
        "or",
        "my",
        "your"
    }

    meaningful = [
        token for token in tokens
        if token not in filler
    ]

    return tokens, meaningful


def fuzzy_match_token(
    token: str,
    vocabulary: set,
    cutoff: float = 0.80
) -> bool:
    if token in vocabulary:
        return True

    if len(token) <= 2:
        return False

    matches = difflib.get_close_matches(
        token,
        vocabulary,
        n=1,
        cutoff=cutoff
    )

    return bool(matches)


def contains_phrase(text: str, phrases) -> bool:
    text_lower = text.lower()

    for phrase in phrases:
        if phrase.lower() in text_lower:
            return True

    return False


def detect_cyberbrief_intent(user_query: str) -> bool:
    raw_tokens, meaningful_tokens = clean_tokens(user_query)
    query_lower = user_query.lower()

    if "cyberbrief" in query_lower:
        return True

    if "cyberbriefs" in query_lower:
        return True

    for aliases in PROFESSOR_ALIASES.values():
        for alias in aliases:
            if alias in query_lower:
                return True

    if contains_phrase(
        query_lower,
        [
            "your website",
            "your platform",
            "your news",
            "your articles",
            "your newsroom",
            "your rss",
            "your blogs",
            "your books",
            "your correspondents",
            "your team"
        ]
    ):
        return True

    for token in meaningful_tokens:
        if fuzzy_match_token(
            token,
            CYBERBRIEF_KEYWORDS,
            0.82
        ):
            return True

    for triggers in ROUTE_MAP.values():
        for trigger in triggers:
            if trigger in query_lower:
                return True

    return False


def detect_latest_news_intent(raw_tokens: list) -> bool:
    return any(
        fuzzy_match_token(
            token,
            LATEST_INTENT_VOCAB,
            0.80
        )
        for token in raw_tokens
    )


def detect_professors(meaningful_tokens):
    matched_profs = []

    for pid, names in PROF_MAP.items():
        for token in meaningful_tokens:
            if len(token) <= 3:
                if token in names:
                    matched_profs.append(pid)
                    break
            else:
                if difflib.get_close_matches(
                    token,
                    names,
                    n=1,
                    cutoff=0.80
                ):
                    matched_profs.append(pid)
                    break

    return list(set(matched_profs))


def detect_routes(meaningful_tokens):
    matched_routes = []

    for route, triggers in ROUTE_MAP.items():
        for token in meaningful_tokens:
            if len(token) <= 3:
                if token in triggers:
                    matched_routes.append(route)
                    break
            else:
                if difflib.get_close_matches(
                    token,
                    triggers,
                    n=1,
                    cutoff=0.80
                ):
                    matched_routes.append(route)
                    break

    return list(set(matched_routes))


def build_article_context(articles):
    context_blocks = []

    for article in articles:
        title = article.title or ""
        category = article.category or ""
        summary = article.summary or ""

        short_summary = summary[:500]

        if len(summary) > 500:
            short_summary += "..."

        block = (
            f"Article ID: {article.id}\n"
            f"Title: {title}\n"
            f"Category: {category}\n"
            f"Summary: {short_summary}"
        )

        context_blocks.append(block)

    return "\n\n---\n\n".join(context_blocks)


def search_cyberbrief_context(
    user_query: str,
    limit: int = 5
):
    raw_tokens, meaningful_tokens = clean_tokens(user_query)

    matched_profs = detect_professors(
        meaningful_tokens
    )

    direct_agent_ids = []

    for pid, aliases in PROFESSOR_ALIASES.items():
        for alias in aliases:
            if re.search(
                rf"\b{re.escape(alias)}\b",
                user_query.lower()
            ):
                direct_agent_ids.append(pid)
                break

    matched_profs = list(
        set(matched_profs + direct_agent_ids)
    )

    matched_routes = detect_routes(
        meaningful_tokens
    )

    if not detect_cyberbrief_intent(user_query):
        return (
            "",
            [],
            matched_profs,
            matched_routes,
            False
        )

    if direct_agent_ids:
        agent_blocks = []

        for pid in sorted(set(direct_agent_ids)):
            agent = PROFESSOR_KNOWLEDGE.get(pid)

            if agent:
                agent_blocks.append(
                    f"Agent Name: {agent['name']}\n"
                    f"Role: {agent['role']}"
                )

        if agent_blocks:
            agent_question = any(
                word in user_query.lower().split()
                for word in [
                    "who",
                    "name",
                    "role",
                    "what",
                    "which",
                    "about"
                ]
            )

            if agent_question:
                return (
                    "\n---\n".join(agent_blocks),
                    [],
                    matched_profs,
                    matched_routes,
                    True
                )

    query_lower = user_query.lower()

    platform_question = (
        "cyberbrief" in query_lower
        or "cyberbriefs" in query_lower
        or bool(matched_routes)
        or bool(matched_profs)
        or contains_phrase(
            query_lower,
            [
                "who are you",
                "what is this",
                "how it works",
                "about cyberbrief",
                "about cyberbriefs",
                "your platform",
                "your website"
            ]
        )
    )

    if platform_question:
        has_article_search_terms = any(
            token in {
                "article",
                "articles",
                "news",
                "headline",
                "headlines",
                "malware",
                "ransomware",
                "vulnerability",
                "vulnerabilities",
                "threat",
                "threats",
                "apt",
                "soc",
                "cloud",
                "fintech",
                "financial",
                "ai",
                "artificial",
                "intelligence"
            }
            for token in meaningful_tokens
        )

        if not has_article_search_terms:
            return (
                ABOUT_CYBERBRIEFS_KNOWLEDGE.strip(),
                [],
                matched_profs,
                matched_routes,
                True
            )

    if detect_latest_news_intent(raw_tokens):
        latest_articles = list(
            Article.objects
            .filter(is_active=True)
            .order_by("-published")[:limit]
        )

        if latest_articles:
            context = build_article_context(
                latest_articles
            )

            return (
                context,
                latest_articles,
                matched_profs,
                matched_routes,
                True
            )

    matching_articles = []

    if meaningful_tokens:
        search_terms = " ".join(
            meaningful_tokens
        )

        vector = (
            SearchVector("title", weight="A")
            + SearchVector("summary", weight="B")
        )

        query = SearchQuery(search_terms)

        matches = list(
            Article.objects
            .annotate(
                rank=SearchRank(vector, query)
            )
            .filter(
                rank__gt=0.001,
                is_active=True
            )
            .order_by("-rank")[:limit]
        )

        matching_articles = matches

    if not matching_articles and meaningful_tokens:
        q_filter = Q()

        for token in meaningful_tokens:
            if len(token) < 3:
                continue

            q_filter |= (
                Q(title__icontains=token)
                | Q(summary__icontains=token)
                | Q(category__icontains=token)
            )

        if q_filter:
            matching_articles = list(
                Article.objects
                .filter(
                    q_filter,
                    is_active=True
                )
                .order_by("-published")[:limit]
            )

    if not matching_articles:
        if platform_question:
            return (
                ABOUT_CYBERBRIEFS_KNOWLEDGE.strip(),
                [],
                matched_profs,
                matched_routes,
                True
            )

        return (
            "",
            [],
            matched_profs,
            matched_routes,
            True
        )

    context = build_article_context(
        matching_articles
    )

    return (
        context,
        matching_articles,
        matched_profs,
        matched_routes,
        True
    )


def generate_chatbot_reply(
    user_message: str
) -> str:
    user_message = (
        user_message or ""
    ).strip()

    if not user_message:
        return OUT_OF_SCOPE_REPLY

    (
        context,
        articles,
        matched_profs,
        matched_routes,
        is_cyberbrief_query
    ) = search_cyberbrief_context(
        user_message
    )

    if not is_cyberbrief_query:
        return OUT_OF_SCOPE_REPLY

    if not context:
        return NO_INFORMATION_REPLY

    system_prompt = f"""
You are the official CyberBrief AI Assistant.

Your ONLY job is to answer questions about CyberBrief.

CyberBrief includes:
- Cybersecurity news
- Cybersecurity articles
- AI and machine learning security
- Vulnerabilities
- Threat intelligence
- Malware and ransomware
- SOC and security operations
- Financial cybersecurity
- Cloud security
- Supply chain security
- Cyber-physical security
- CyberBrief correspondents
- CyberBrief newsroom
- CyberBrief RSS feeds
- CyberBrief blogs
- CyberBrief books
- CyberBrief careers and internships
- CyberBrief website sections
- CyberBrief mission and platform information

STRICT RULES:

1. Use ONLY the information contained in the Context.

2. NEVER use your own pretrained knowledge to answer.

3. NEVER invent facts.

4. NEVER guess.

5. NEVER create statistics, dates, names, vulnerabilities, companies, events, or explanations that are not present in Context.

6. If the answer is not supported by Context, say:
"I couldn't find reliable information about that in the CyberBrief knowledge base. I don't want to guess or provide information that isn't supported by CyberBrief."

7. If the user asks something unrelated to CyberBrief, say:
"I am the CyberBrief AI Assistant. I can only answer questions related to CyberBrief, its cybersecurity news, articles, correspondents, sections, RSS feeds, blogs, books, careers, and platform information."

8. Keep answers concise and directly answer the question.

9. If the Context contains an article summary, summarize only that information.

10. Do not add external cybersecurity knowledge.

11. Do not pretend to know information that is absent from Context.

12. Do not answer general questions just because they contain a cybersecurity word.

Context:
{context}
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    prompt_text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    model_inputs = tokenizer(
        [prompt_text],
        return_tensors="pt"
    ).to(device)

    with torch.no_grad():
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=180,
            do_sample=False,
            use_cache=True,
            repetition_penalty=1.05
        )

    response_tokens = [
        output_ids[len(input_ids):]
        for input_ids, output_ids in zip(
            model_inputs.input_ids,
            generated_ids
        )
    ]

    reply_text = tokenizer.batch_decode(
        response_tokens,
        skip_special_tokens=True
    )[0].strip()

    if not reply_text:
        reply_text = NO_INFORMATION_REPLY

    hallucination_phrases = [
        "as an ai",
        "i think",
        "i believe",
        "probably",
        "it is likely",
        "might be",
        "could be",
        "according to my knowledge",
        "generally speaking",
        "in general"
    ]

    reply_lower = reply_text.lower()

    if any(
        phrase in reply_lower
        for phrase in hallucination_phrases
    ):
        reply_text = NO_INFORMATION_REPLY

    if articles:
        article_tags = " ".join(
            f"[ARTICLE:{article.id}]"
            for article in articles
        )

        reply_text += " " + article_tags

    if matched_profs:
        prof_tags = " ".join(
            f"[PROF:{pid}]"
            for pid in sorted(set(matched_profs))
        )

        reply_text += " " + prof_tags

    if matched_routes:
        route_tags = " ".join(
            f"[ROUTE:{route}]"
            for route in sorted(set(matched_routes))
        )

        reply_text += " " + route_tags

    return reply_text

import os
import re
import urllib.request
import urllib.error
import json
from models.schema import PortfolioRequest

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = (
    "You are an expert portfolio writer and web developer. "
    "Generate a stunning, professional, fully self-contained HTML portfolio page. "
    "Use only inline CSS and JS. Google Fonts via @import in <style> is allowed. "
    "Include: sticky navbar, hero section, about, experience timeline, "
    "projects cards, skills, education, contact section, footer. "
    "Make it visually impressive, responsive, and deployment-ready. "
    "Return ONLY raw HTML starting with <!DOCTYPE html> — "
    "no markdown, no code fences, no explanation whatsoever."
)


def build_prompt(data: PortfolioRequest) -> str:
    style_desc = {
        "modern": (
            "Modern & sleek: dark hero (#0f0f0f), bold white typography, "
            "gold accent (#d4a853), card-based sections with subtle borders"
        ),
        "minimal": (
            "Ultra-minimal: white background, generous whitespace, "
            "clean serif typography (Playfair Display), muted grays, thin accents"
        ),
        "creative": (
            "Bold & creative: vibrant purple-to-teal gradient hero, "
            "expressive typography, bright accents, asymmetric layouts, animations"
        ),
    }.get(data.style or "modern", "Modern & professional")

    links = ""
    if data.linkedin:
        links += f"\n- LinkedIn: {data.linkedin}"
    if data.github:
        links += f"\n- GitHub: {data.github}"
    if data.website:
        links += f"\n- Website: {data.website}"

    return f"""Generate a complete HTML portfolio page for the following person:

Name: {data.name}
Title: {data.title}
Email: {data.email}
Phone: {data.phone or 'Not provided'}
Location: {data.location or 'Not provided'}
Summary: {data.summary or 'A passionate professional dedicated to excellence.'}

Education:
{data.education}

Skills:
{data.skills}

Projects:
{data.projects}

Experience:
{data.experience}

Links:{links or ' None'}

Design Style: {style_desc}

Requirements:
- Google Fonts via @import (choose fonts that match the style)
- Fully responsive, mobile-first
- Sticky navbar with name/initials logo and smooth scroll
- Hero section with name, title, and a tagline
- Animated skill tags or progress bars
- Project cards with hover effects
- Experience timeline layout
- Contact section with clickable email
- Footer with copyright year
- Vanilla JS only — no frameworks
- Everything inline in one HTML file
- Start output with <!DOCTYPE html> and nothing else before it"""


def clean_html(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    idx = text.lower().find("<!doctype")
    if idx > 0:
        text = text[idx:]
    return text


def generate_portfolio(data: PortfolioRequest) -> str:
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is not set. "
            "Get a FREE key at https://console.groq.com — "
            "sign up, go to API Keys, create one, then add it to your .env file."
        )

    prompt = build_prompt(data)

    payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 8192,
    }).encode("utf-8")

    req = urllib.request.Request(
        GROQ_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "User-Agent": "Mozilla/5.0",  # ✅ FIX 1
        },
        method="POST",
    )

    try:
        # ✅ FIX 2: Retry mechanism
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    body = json.loads(resp.read().decode("utf-8"))
                    break
            except urllib.error.HTTPError as e:
                if e.code == 403 and attempt < 2:
                    continue
                error_body = e.read().decode("utf-8")
                try:
                    msg = json.loads(error_body).get("error", {}).get("message", error_body)
                except Exception:
                    msg = error_body
                raise RuntimeError(f"Groq API error {e.code}: {msg}")

    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error connecting to Groq: {e.reason}")

    try:
        text = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise RuntimeError(f"Unexpected Groq response: {body}")

    return clean_html(text)
#!/usr/bin/env python3
"""
Recon Lead — Scanner Completo de Leads, Contatos e Diagnóstico de Dores do Cliente.
Compatível com Antigravity, Claude Code e OpenAI Codex.
Não requer dependências externas (utiliza biblioteca padrão do Python 3).

Capacidades:
1. Varredura técnica de performance, TTFB, viewport mobile e CMS/tecnologias.
2. Extração multicanal de contatos: Telefones, WhatsApp, Emails e Redes Sociais
   (Instagram, LinkedIn, Facebook, Google Maps/Business, YouTube, TikTok).
3. Diagnóstico aprofundado da DOR DO CLIENTE (Customer Pain) em PT, EN e ES,
   identificando gargalos de conversão, velocidade, agregadores genéricos e atrito de contato.

Uso:
    python3 recon_lead.py --url https://exemplo.com
    python3 recon_lead.py --url https://linktr.ee/clinicaexemplo --format json
"""

import sys
import os
import argparse
import json
import time
import re
import urllib.request
import urllib.error
import ssl

USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"

# Patterns to filter out dummy or asset emails
IGNORED_EMAIL_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif', '.css', '.js', '.woff', '.woff2', '.ttf')
IGNORED_EMAIL_DOMAINS = ('example.com', 'domain.com', 'email.com', 'sentry.io', 'wixpress.com', 'schema.org', 'w3.org')

def clean_phone_str(raw: str) -> str:
    cleaned = re.sub(r'[^\d+]', '', raw.strip())
    if len(cleaned) < 8 or len(cleaned) > 20:
        return ""
    return cleaned

def classify_entity_type(name: str) -> str:
    """
    Identifies whether the lead is an individual specialist/professional ('person')
    or an organization/clinic/business ('company').
    """
    if not name:
        return "company"
    lower = name.lower()
    
    # Direct honorific / specialist checks
    if re.search(r'\b(?:dr|dra|doutor|doutora|doctor|adv|advogado|advogada|attorney|lawyer|arq|arquiteto|arquiteta|architect|nutri|nutricionista|psico|psicologo|psicologa|personal|coach)\b\.?', lower):
        return "person"
        
    company_keywords = {
        'clinica', 'clínica', 'clinic', 'consultorio', 'consultório', 'escritorio', 'escritório',
        'instituto', 'institute', 'estudio', 'estúdio', 'studio', 'advocacia', 'odontologia', 'odonto',
        'dental', 'dentistry', 'estetica', 'estética', 'aesthetic', 'aesthetics', 'medspa', 'spa',
        'center', 'centro', 'hospital', 'group', 'grupo', 'solucoes', 'soluções', 'solutions',
        'servicos', 'serviços', 'services', 'agency', 'agência', 'boutique', 'limpieza', 'limpeza',
        'limpiex', 'cleaning', 'imoveis', 'imóveis', 'imobiliaria', 'imobiliária', 'realty', 'brokerage',
        'construtora', 'engenharia', 'digital', 'lab', 'laboratorio', 'laboratório', 'associados',
        'associates', 'partners', 'store', 'loja', 'oficial', 'official', 'academy', 'academia',
        'restaurante', 'hotel', 'resort', 'consultoria', 'consulting', 'beauty', 'beleza',
        'saude', 'saúde', 'health', 'care', 'softwares', 'tech'
    }
    
    words = [w for w in re.split(r'[\s\-_\.,&/]+', lower) if w]
    if any(k in words or any(k in w for w in words) for k in company_keywords):
        return "company"
        
    # If 1 or 2 capitalized words without corporate markers, typically a personal name / brand
    if 1 <= len(words) <= 2:
        return "person"
        
    return "company"

def humanize_handle(handle: str) -> tuple:
    """
    Transforms a raw handle or social ID (e.g. @dr_robertosilva, @clinica_sorriso_sp)
    into a clean, human business/person name and classifies its entity type.
    Returns (clean_name, entity_type).
    """
    if not handle:
        return ("Lead Alvo", "company")
        
    clean = handle.lstrip('@').strip().strip('/')
    if "instagram.com/" in clean:
        clean = clean.split("instagram.com/")[-1].split("/")[0].split("?")[0]
        
    lower_raw = clean.lower()
    
    known_replacements = {
        'innova.dentalcare': ('Innova Dental Care', 'company'),
        'dentistbrausa': ('Dentist Brazilian USA', 'company'),
        'dr.raqbruno': ('Dra. Raquel Bruno', 'person'),
        'dentalcosmeticmiami': ('Dental Cosmetic Miami', 'company'),
        'rosa.cleaningservicesfl': ('Rosa Cleaning Services', 'company'),
        'marialimahousecleaning': ('Maria Lima House Cleaning', 'company'),
        'patyscleaningfl': ("Paty's Cleaning Services", 'company'),
        'pavlenko_home_cleaning': ('Pavlenko Home Cleaning', 'company'),
        'mrs.apcleaning': ('Mrs. AP Cleaning', 'company'),
        'artem_consultoria': ('Artem Consultoria', 'company'),
        'consultoriaparaguai': ('Consultoria Paraguai', 'company'),
        'atuarparaguai': ('Atuar Intercâmbio Paraguai', 'company'),
        'rhemaclinicpy': ('Rhema Clinic', 'company'),
        'estheticpalacepy': ('Esthetic Palace', 'company'),
        'dra.milenerezendep': ('Dra. Milene Rezende', 'person'),
        'dra.amandaoliveirac': ('Dra. Amanda Oliveira', 'person'),
        'odontocarecde': ('Odonto Care CDE', 'company'),
        'marrone_medicinanoparaguai': ('Marrone Medicina no Paraguai', 'company'),
        'moreira.py': ('Moreira Odontología Digital', 'company'),
        'master_limpiezacde': ('Master Limpieza CDE', 'company'),
        'impecablepy': ('Impecable Limpieza', 'company'),
        'limpiexpy': ('Limpiex Paraguay', 'company'),
    }
    if lower_raw in known_replacements:
        return known_replacements[lower_raw]
        
    is_person = False
    prefix = ""
    lower = clean.lower()
    
    # Handle professional honorific prefixes
    if lower.startswith(('dr_', 'dr.')):
        is_person = True
        prefix = "Dr. "
        clean = clean[3:]
    elif lower.startswith(('dra_', 'dra.')):
        is_person = True
        prefix = "Dra. "
        clean = clean[4:]
    elif lower.startswith(('doutor_', 'doutor.')):
        is_person = True
        prefix = "Dr. "
        clean = clean[7:]
    elif lower.startswith(('doutora_', 'doutora.')):
        is_person = True
        prefix = "Dra. "
        clean = clean[8:]
    elif lower.startswith(('adv_', 'adv.')):
        is_person = True
        prefix = "Adv. "
        clean = clean[4:]
    elif lower.startswith(('arq_', 'arq.')):
        is_person = True
        prefix = "Arq. "
        clean = clean[4:]
    elif lower.startswith(('nutri_', 'nutri.')):
        is_person = True
        prefix = "Nutri "
        clean = clean[6:]
        
    # Strip common noise suffixes: _sp, _rj, _oficial, _brasil, _py, _cde, etc.
    noise_patterns = [
        r'[_\.](?:sp|rj|mg|df|pr|sc|rs|ba|pe|ce|go|am|py|cde|fl|usa|br|brasil|oficial|official|assessoria|consultoria|adv|odonto|dermato|med)$'
    ]
    for np in noise_patterns:
        clean = re.sub(np, '', clean, flags=re.IGNORECASE)

    # Clean concatenated words
    compound_words = [
        ('cleaningservices', ' Cleaning Services'),
        ('housecleaning', ' House Cleaning'),
        ('dentalcare', ' Dental Care'),
        ('dentalcosmetic', ' Dental Cosmetic'),
        ('medicinanoparaguai', ' Medicina no Paraguai'),
        ('rhemaclinic', ' Rhema Clinic'),
        ('estheticpalace', ' Esthetic Palace'),
        ('odontocare', ' Odonto Care'),
        ('patyscleaning', " Paty's Cleaning"),
        ('dentistbra', ' Dentist Brazilian')
    ]
    for comp, repl in compound_words:
        clean = re.sub(comp, repl, clean, flags=re.IGNORECASE)
        
    parts = re.split(r'[_\.\-\s]+', clean)
    words = [p.capitalize() for p in parts if p]
    
    clean_name = (prefix + " ".join(words)).strip()
    entity_type = "person" if is_person else classify_entity_type(clean_name)
    return (clean_name or "Lead Alvo", entity_type)

def extract_clean_entity_name(html: str, title: str, og_site_name: str, og_title: str, final_url: str = "") -> tuple:
    """
    Extracts the genuine official business name or professional's name from HTML meta tags,
    filtering out generic platform names, website boilerplate, and SEO slogans.
    Returns (clean_name, entity_type).
    """
    # 1. Prefer og:site_name if concise and not a platform name
    if og_site_name and len(og_site_name) <= 45:
        lower_site = og_site_name.lower()
        if not any(g in lower_site for g in ['instagram', 'linktree', 'beacons', 'bento', 'wordpress', 'wix', 'squarespace']):
            site_clean = re.sub(r'\s*(?:\||-|—|•)\s*.*$', '', og_site_name).strip()
            if len(site_clean) >= 3:
                return (site_clean, classify_entity_type(site_clean))

    # 2. Check for Doctor/Specialist honorific patterns in Title or og:title
    for text in [og_title, title]:
        if not text:
            continue
        doc_match = re.search(r'\b(Dr[a]?\.?\s+[A-ZÀ-Ú][a-zà-ú]+(?:\s+[A-ZÀ-Ú][a-zà-ú]+){1,3})', text)
        if doc_match:
            doc_name = doc_match.group(1).strip()
            if not doc_name.startswith(("Dr.", "Dra.")):
                doc_name = doc_name.replace("Dr ", "Dr. ").replace("Dra ", "Dra. ")
            return (doc_name, "person")

    # 3. Check JSON-LD structured data for name / legalName
    if html and '<script type="application/ld+json">' in html:
        json_matches = re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
        for jm in json_matches:
            try:
                name_match = re.search(r'["\'](?:name|legalName)["\']\s*:\s*["\']([^"\'\\]{3,45})["\']', jm)
                if name_match:
                    cand_j = name_match.group(1).strip()
                    if not any(p in cand_j.lower() for p in ['http', 'www.', '.com', 'home', 'início']):
                        return (cand_j, classify_entity_type(cand_j))
            except Exception:
                pass

    # 4. Split title on standard branding delimiters (| - — • : ·)
    for text in [og_title, title]:
        if not text:
            continue
        parts = re.split(r'\s+[\|\-—•:·]\s+', text)
        for p in parts:
            p_clean = p.strip()
            lower_p = p_clean.lower()
            if 3 <= len(p_clean) <= 45 and not any(k in lower_p for k in ['home', 'início', 'inicio', 'bem-vindo', 'welcome', 'oficial', 'fotos e vídeos', 'página inicial', 'agendamento', 'whatsapp', 'linktr.ee', 'instagram']):
                return (p_clean, classify_entity_type(p_clean))

    # 5. Fallback from domain name
    if final_url:
        domain = final_url.split("://")[-1].split("/")[0].replace("www.", "")
        root_name = domain.split(".")[0]
        if root_name and root_name not in ['linktr', 'beacons', 'bento', 'instagram']:
            clean_domain = root_name.capitalize()
            return (clean_domain, classify_entity_type(clean_domain))

    return ("", "company")

def get_greeting_name(lead_name: str, entity_type: str) -> str:
    """
    Returns the most natural conversational name for greetings (e.g. 'Dr. Marcelo', 'Mariana', 'Clínica Lumina').
    """
    lead_name = (lead_name or "").strip()
    if entity_type == "company":
        return lead_name
    doc_match = re.match(r'^(Dr[a]?\.?|Adv\.?|Arq\.?|Nutri\.?)\s+([A-ZÀ-Ú][a-zà-ú]+)', lead_name, re.I)
    if doc_match:
        prefix = doc_match.group(1).capitalize()
        if not prefix.endswith('.'):
            prefix += '.'
        return f"{prefix} {doc_match.group(2).capitalize()}"
    parts = lead_name.split()
    if parts:
        return parts[0].capitalize()
    return lead_name

def extract_contacts_from_html(html: str, base_url: str = "") -> dict:
    contacts = {
        "emails": [],
        "phones": [],
        "whatsapp": [],
        "social": {
            "instagram": None,
            "linkedin": None,
            "facebook": None,
            "google_maps": None,
            "youtube": None,
            "tiktok": None
        }
    }

    # 1. Emails: mailto links first
    mailto_matches = re.findall(r'mailto:([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', html, re.IGNORECASE)
    for m in mailto_matches:
        em = m.strip().lower()
        if not any(em.endswith(ext) for ext in IGNORED_EMAIL_EXTENSIONS) and not any(dom in em for dom in IGNORED_EMAIL_DOMAINS):
            if em not in contacts["emails"]:
                contacts["emails"].append(em)

    # Emails: general text regex
    text_emails = re.findall(r'\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b', html)
    for em in text_emails:
        em_clean = em.strip().lower().rstrip('.')
        if not any(em_clean.endswith(ext) for ext in IGNORED_EMAIL_EXTENSIONS) and not any(dom in em_clean for dom in IGNORED_EMAIL_DOMAINS):
            if em_clean not in contacts["emails"]:
                contacts["emails"].append(em_clean)

    # 2. Phones: tel: links
    tel_matches = re.findall(r'href=["\']tel:([^"\'\s>]+)["\']', html, re.IGNORECASE)
    for t in tel_matches:
        phone_c = clean_phone_str(t)
        if phone_c and phone_c not in contacts["phones"]:
            contacts["phones"].append(phone_c)

    # 3. WhatsApp: wa.me and api.whatsapp.com
    wa_matches = re.findall(r'href=["\'](?:https?://)?(?:wa\.me/|api\.whatsapp\.com/send\?phone=)([^"\'\s&?#]+)', html, re.IGNORECASE)
    for w in wa_matches:
        wa_c = clean_phone_str(w)
        if wa_c:
            wa_link = f"https://wa.me/{wa_c.lstrip('+')}"
            if wa_link not in contacts["whatsapp"]:
                contacts["whatsapp"].append(wa_link)
            if wa_c not in contacts["phones"]:
                contacts["phones"].append(wa_c)

    # 4. Social Links
    # Instagram
    ig_matches = re.findall(r'https?://(?:www\.)?instagram\.com/([a-zA-Z0-9_\.]{2,30})/?', html, re.IGNORECASE)
    for ig in ig_matches:
        if ig.lower() not in ["p", "reel", "reels", "explore", "stories", "about", "legal", "terms", "privacy", "developer"]:
            contacts["social"]["instagram"] = f"https://www.instagram.com/{ig}/"
            break

    # LinkedIn
    li_matches = re.findall(r'https?://(?:www\.)?linkedin\.com/(?:in|company)/([a-zA-Z0-9_\-\.%]+)/?', html, re.IGNORECASE)
    if li_matches:
        contacts["social"]["linkedin"] = f"https://www.linkedin.com/company/{li_matches[0]}/" if "company/" in html else f"https://www.linkedin.com/in/{li_matches[0]}/"

    # Facebook
    fb_matches = re.findall(r'https?://(?:www\.)?(?:facebook\.com|fb\.com)/([a-zA-Z0-9_\-\.%]+)/?', html, re.IGNORECASE)
    for fb in fb_matches:
        if fb.lower() not in ["sharer", "share", "policies", "terms", "privacy", "tr", "watch"]:
            contacts["social"]["facebook"] = f"https://www.facebook.com/{fb}/"
            break

    # Google Maps / Google Business
    gmaps_match = re.search(r'https?://(?:www\.)?(?:google\.com/maps|maps\.app\.goo\.gl|search\.google\.com/local)[^\s"\'<>]+', html, re.IGNORECASE)
    if gmaps_match:
        contacts["social"]["google_maps"] = gmaps_match.group(0).rstrip(".,;")

    # YouTube
    yt_match = re.search(r'https?://(?:www\.)?(?:youtube\.com/(?:@[a-zA-Z0-9_\-\.]+|channel/[a-zA-Z0-9_\-\.]+)|youtu\.be/[a-zA-Z0-9_\-\.]+)', html, re.IGNORECASE)
    if yt_match:
        contacts["social"]["youtube"] = yt_match.group(0)

    # TikTok
    tt_match = re.search(r'https?://(?:www\.)?tiktok\.com/@([a-zA-Z0-9_\-\.]+)', html, re.IGNORECASE)
    if tt_match:
        contacts["social"]["tiktok"] = f"https://www.tiktok.com/@{tt_match.group(1)}"

    return contacts

def diagnose_customer_pain(recon: dict) -> dict:
    """
    Identifies the Lead's Core Pain (A DOR DO CLIENTE) across technical, mobile,
    conversion, and authority dimensions. Formulates clean hook phrases in PT, EN, and ES.
    """
    cms = recon.get("detected_cms", [])
    latency = recon.get("response_time_ms")
    has_viewport = recon.get("has_viewport", True)
    tools = recon.get("detected_tools", [])
    contacts = recon.get("contacts", {})
    has_wa = bool(contacts.get("whatsapp")) or "WhatsApp Direct" in tools
    has_calendar = any(b in tools for b in ["Acuity Scheduling", "Booksy", "Fresha", "Calendly"])

    friction_points = []
    category = "Conversão Mobile"
    core_pain_pt = ""
    core_pain_en = ""
    core_pain_es = ""
    recommended_solution = ""

    # Priority 1: Linktree / Generic Bio Aggregators (High drop-off)
    if any(c in cms for c in ["Linktree", "Beacons", "Bento"]):
        category = "Fuga por Agregador de Links"
        friction_points.append("Uso de agregador genérico (Linktree/Beacons) na bio: muitas opções espalhadas fazem o cliente desistir.")
        core_pain_pt = "o link da bio tem muitas opções espalhadas e as pessoas acabam ficando confusas antes de mandar mensagem"
        core_pain_en = "the bio link has too many buttons and people get confused before reaching out"
        core_pain_es = "el enlace de la bio tiene demasiados botones y la gente se pierde antes de mandar mensaje"
        recommended_solution = "Página rápida e direta para o WhatsApp, com catálogo simples e contato em 1 toque."

    # Priority 2: Critical Latency / Mobile Slowness (> 2s TTFB)
    elif latency and latency > 1800:
        category = "Lentidão no Celular"
        friction_points.append(f"Site lento no celular: demora para abrir e faz pessoas desistirem antes do contato.")
        core_pain_pt = "o site demora um pouco para abrir no celular e as pessoas acabam desistindo antes de ver seus serviços"
        core_pain_en = "the website takes a bit long to load on phones and people give up before seeing your services"
        core_pain_es = "el sitio tarda en abrir en el celular y muchas personas desisten antes de ver sus servicios"
        recommended_solution = "Otimização para o site abrir na hora no celular, evitando que você perca clientes."

    # Priority 3: Missing Mobile Viewport
    elif not has_viewport:
        category = "Experiência Mobile Quebrada"
        friction_points.append("Página sem ajuste para celular: o texto e as imagens ficam desconfigurados na tela do smartphone.")
        core_pain_pt = "a página fica desconfigurada na tela do celular e é difícil de navegar pelo smartphone"
        core_pain_en = "the page doesn't fit phone screens properly, making it hard to read and navigate"
        core_pain_es = "la página se ve desconfigurada en el celular y cuesta navegar desde el teléfono"
        recommended_solution = "Adaptação visual completa para o celular, facilitando a navegação em qualquer smartphone."

    # Priority 4: Cold Calendar Booking Friction
    elif has_calendar and not has_wa:
        category = "Atrito no Agendamento"
        friction_points.append("Direcionamento direto para calendário: pede data e hora antes da pessoa ver fotos e diferenciais.")
        core_pain_pt = "mandar a pessoa direto para um calendário sem antes mostrar seus trabalhos faz muita gente desistir antes de agendar"
        core_pain_en = "sending people straight to a calendar before showing your work causes many to leave"
        core_pain_es = "enviar a la persona directo a un calendario sin mostrar primero sus trabajos hace que muchos desistan"
        recommended_solution = "Página simples apresentando seus melhores trabalhos e botão direto para tirar dúvidas no WhatsApp."

    # Priority 5: Missing Direct 1-Tap Conversion Channel
    elif not has_wa and not contacts.get("phones"):
        category = "Dificuldade de Contato Imediato"
        friction_points.append("Falta de botão direto para WhatsApp: o visitante precisa procurar como falar com a equipe.")
        core_pain_pt = "quem acessa o site pelo celular tem dificuldade de achar um botão rápido para falar no WhatsApp"
        core_pain_en = "visitors on phones can't easily find a direct button to chat on WhatsApp"
        core_pain_es = "quien entra desde el celular no encuentra fácil un botón rápido para hablar a su WhatsApp"
        recommended_solution = "Colocação de botão direto e visível para o WhatsApp da equipe em todo o site."

    # Priority 6: Standard / Generic Functional Layout (Authority Gap)
    else:
        category = "Autoridade & Apresentação Visual"
        friction_points.append("Visual básico: a página atual não transmite toda a qualidade do serviço presencial.")
        core_pain_pt = "o visual da página não valoriza todo o padrão de qualidade e cuidado que vocês entregam na prática"
        core_pain_en = "the current page doesn't reflect the high quality of work you actually deliver"
        core_pain_es = "el diseño actual no luce todo el nivel de calidad que ustedes ofrecen en persona"
        recommended_solution = "Modernização do visual da página para valorizar o padrão e a qualidade dos seus serviços."

    return {
        "category": category,
        "core_pain_pt": core_pain_pt,
        "core_pain_en": core_pain_en,
        "core_pain_es": core_pain_es,
        "friction_points": friction_points,
        "recommended_solution": recommended_solution
    }

def analyze_url(url: str, timeout: int = 10) -> dict:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    result = {
        "url": url,
        "final_url": url,
        "status_code": None,
        "response_time_ms": None,
        "is_https": url.startswith("https://"),
        "has_viewport": False,
        "title": None,
        "og_title": None,
        "og_site_name": None,
        "detected_name": None,
        "entity_type": "company",
        "description": None,
        "detected_cms": [],
        "detected_tools": [],
        "contacts": {
            "emails": [],
            "phones": [],
            "whatsapp": [],
            "social": {}
        },
        "friction_points": [],
        "pain": {},
        "recommended_angle": "",
        "success": False,
        "error": None
    }

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
    )

    start_time = time.time()
    html = ""
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
            elapsed_ms = int((time.time() - start_time) * 1000)
            result["response_time_ms"] = elapsed_ms
            result["status_code"] = response.getcode()
            result["final_url"] = response.geturl()

            raw_bytes = response.read(500000) # Read first 500KB
            try:
                html = raw_bytes.decode('utf-8', errors='ignore')
            except Exception:
                html = raw_bytes.decode('latin-1', errors='ignore')

            result["success"] = True
    except urllib.error.HTTPError as e:
        result["status_code"] = e.code
        result["error"] = f"HTTP Error {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        result["error"] = f"Connection Error: {e.reason}"
    except Exception as e:
        result["error"] = f"Unexpected Error: {str(e)}"

    if html:
        # Meta Title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        if title_match:
            result["title"] = re.sub(r'\s+', ' ', title_match.group(1)).strip()

        # og:title
        og_t_match = re.search(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
        if not og_t_match:
            og_t_match = re.search(r'<meta[^>]*content=["\'](.*?)["\'][^>]*property=["\']og:title["\']', html, re.IGNORECASE)
        if og_t_match:
            result["og_title"] = re.sub(r'\s+', ' ', og_t_match.group(1)).strip()

        # og:site_name
        og_s_match = re.search(r'<meta[^>]*property=["\']og:site_name["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
        if not og_s_match:
            og_s_match = re.search(r'<meta[^>]*content=["\'](.*?)["\'][^>]*property=["\']og:site_name["\']', html, re.IGNORECASE)
        if og_s_match:
            result["og_site_name"] = re.sub(r'\s+', ' ', og_s_match.group(1)).strip()

        # Extract genuine Entity Name (Pessoa / Especialista ou Empresa)
        entity_name, entity_type = extract_clean_entity_name(
            html=html,
            title=result["title"] or "",
            og_site_name=result["og_site_name"] or "",
            og_title=result["og_title"] or "",
            final_url=result["final_url"]
        )
        result["detected_name"] = entity_name
        result["entity_type"] = entity_type

        # Meta Description
        desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
        if not desc_match:
            desc_match = re.search(r'<meta[^>]*content=["\'](.*?)["\'][^>]*name=["\']description["\']', html, re.IGNORECASE)
        if desc_match:
            result["description"] = re.sub(r'\s+', ' ', desc_match.group(1)).strip()

        # Viewport Check (Mobile Friendly)
        if re.search(r'<meta[^>]*name=["\']viewport["\']', html, re.IGNORECASE):
            result["has_viewport"] = True
        else:
            result["friction_points"].append("Página sem tag viewport mobile: layout pode quebrar em smartphones.")

        # CMS & Builder Fingerprinting
        cms_signatures = {
            "WordPress": [r'/wp-content/', r'/wp-includes/', r'wp-json'],
            "Elementor (WP)": [r'elementor-', r'/plugins/elementor/'],
            "Divi (WP)": [r'et_pb_', r'/themes/Divi/'],
            "Webflow": [r'data-wf-page', r'webflow\.js'],
            "Wix": [r'wix\.com', r'static\.wixstatic\.com'],
            "Squarespace": [r'squarespace\.com', r'sqs-'],
            "Shopify": [r'cdn\.shopify\.com', r'Shopify\.theme'],
            "Carrd": [r'carrd\.co'],
            "Linktree": [r'linktr\.ee', r'linktree'],
            "Beacons": [r'beacons\.ai', r'beacons\.page'],
            "Bento": [r'bento\.me']
        }

        for cms_name, patterns in cms_signatures.items():
            if any(re.search(pat, html, re.IGNORECASE) for pat in patterns) or any(re.search(pat, result["final_url"], re.IGNORECASE) for pat in patterns):
                result["detected_cms"].append(cms_name)

        # Booking & Contact Tools Fingerprinting
        tool_signatures = {
            "Acuity Scheduling": [r'acuityscheduling\.com', r'as\.me'],
            "Booksy": [r'booksy\.com'],
            "Fresha": [r'fresha\.com'],
            "Calendly": [r'calendly\.com'],
            "WhatsApp Direct": [r'wa\.me/', r'api\.whatsapp\.com/send'],
            "Typeform": [r'typeform\.com'],
            "Google Forms": [r'docs\.google\.com/forms'],
            "Click-to-Call (tel:)": [r'href=["\']tel:']
        }

        for tool_name, patterns in tool_signatures.items():
            if any(re.search(pat, html, re.IGNORECASE) for pat in patterns):
                result["detected_tools"].append(tool_name)

        # Contact Extraction
        result["contacts"] = extract_contacts_from_html(html, result["final_url"])

    # Pain Diagnosis
    pain_data = diagnose_customer_pain(result)
    result["pain"] = pain_data
    result["friction_points"].extend(pain_data["friction_points"])
    result["recommended_angle"] = pain_data["recommended_solution"]

    return result

def format_markdown(data: dict) -> str:
    md = []
    md.append(f"# 🔍 Scanner Completo do Lead & Diagnóstico de Dores")
    md.append(f"**URL do Alvo:** `{data['url']}`  ")
    if data['final_url'] != data['url']:
        md.append(f"**Redireciona para:** `{data['final_url']}`  ")
    md.append(f"**Status HTTP:** `{data['status_code']}` | **Latência Inicial (TTFB):** `{data['response_time_ms']} ms`  \n")

    if data.get("detected_name"):
        type_label = "👤 Especialista / Pessoa Física" if data.get("entity_type") == "person" else "🏢 Empresa / Estabelecimento"
        md.append(f"**Empresa / Especialista Identificado:** `{data['detected_name']}` ({type_label})  ")
    if data.get("title"):
        md.append(f"**Título da Página:** {data['title']}  ")
    if data.get("og_site_name"):
        md.append(f"**Nome do Site (og:site_name):** {data['og_site_name']}  ")
    if data.get("description"):
        md.append(f"**Meta Descrição:** {data['description']}  ")
    md.append("")

    # Contact Info
    c = data.get("contacts", {})
    md.append("### 📞 Informações de Contato Encontradas")
    emails_str = ", ".join(c.get("emails", [])) if c.get("emails") else "Nenhum email público no HTML"
    phones_str = ", ".join(c.get("phones", [])) if c.get("phones") else "Nenhum telefone direto"
    wa_str = ", ".join(c.get("whatsapp", [])) if c.get("whatsapp") else "Sem botão direto WhatsApp"
    md.append(f"- **Emails:** `{emails_str}`")
    md.append(f"- **Telefones:** `{phones_str}`")
    md.append(f"- **WhatsApp:** `{wa_str}`")

    soc = c.get("social", {})
    soc_active = [f"[{k.title()}]({v})" for k, v in soc.items() if v]
    if soc_active:
        md.append(f"- **Redes Sociais & Perfis:** {' | '.join(soc_active)}")
    md.append("")

    # Stack
    md.append("### 🛠️ Tecnologias & Plataformas Identificadas")
    cms_str = ", ".join(data["detected_cms"]) if data["detected_cms"] else "Custom / Não identificado"
    tools_str = ", ".join(data["detected_tools"]) if data["detected_tools"] else "Nenhuma ferramenta externa de agendamento"
    md.append(f"- **CMS / Builder:** {cms_str}")
    md.append(f"- **Ferramentas de Conversão:** {tools_str}")
    md.append(f"- **Compatibilidade Mobile:** {'✅ Viewport Presente' if data['has_viewport'] else '⚠️ Viewport Ausente ou Quebrada'}")
    md.append("")

    # Customer Pain Section
    pain = data.get("pain", {})
    md.append("### ⚠️ A DOR DO CLIENTE (Customer Pain Diagnosed)")
    md.append(f"**Categoria do Gargalo:** `{pain.get('category', 'Geral')}`")
    md.append(f"> **Dor Central (PT):** *\"{pain.get('core_pain_pt')}\"*")
    md.append(f"> **Core Pain (EN):** *\"{pain.get('core_pain_en')}\"*")
    md.append(f"> **Dolor Principal (ES):** *\"{pain.get('core_pain_es')}\"*")
    md.append("")

    md.append("### 💡 Solução Recomendada (Serviços do Setup)")
    md.append(f"> {pain.get('recommended_solution')}")
    md.append("")
    md.append("---")
    md.append("💡 *O Hook da mensagem inicial deve ser aberto diretamente com esta DOR, conectando à solução do setup e finalizando com hook de pergunta provocativo para Call.*")
    return "\n".join(md)

def main():
    parser = argparse.ArgumentParser(description="Scanner completo de leads, contatos e diagnóstico da dor do cliente.")
    parser.add_argument("--url", "-u", required=True, help="URL do site ou link na bio a ser analisado.")
    parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown", help="Formato de saída (markdown ou json).")
    parser.add_argument("--timeout", "-t", type=int, default=10, help="Tempo limite de conexão em segundos.")
    args = parser.parse_args()

    data = analyze_url(args.url, timeout=args.timeout)

    if args.format == "json":
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(format_markdown(data))

if __name__ == "__main__":
    main()

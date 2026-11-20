#!/usr/bin/env python3
"""
Process List & Outreach Roadmap Generator — Lead Approach.
Parses a batch list of businesses/leads from files (PDF, TXT, Markdown, CSV, JSON) or direct input,
executes technical & commercial reconnaissance on each link, applies campaign profile memory,
and builds an actionable multi-day Outreach Roadmap with 4-block copy, follow-ups, and priority tiers.

Compatible with Antigravity, Claude Code, and OpenAI Codex.

Usage:
    python3 scripts/process_list.py --file leads.txt
    python3 scripts/process_list.py --file leads.pdf --pdf roadmap.pdf
    python3 scripts/process_list.py --file leads.csv --output roadmap.md
    python3 scripts/process_list.py --input "https://example1.com, @aesthetic_dr, https://example2.com"
"""

import sys
import os
import argparse
import json
import re
import csv
import subprocess
import datetime
import shutil

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)

from recon_lead import analyze_url, humanize_handle, classify_entity_type, extract_clean_entity_name, get_greeting_name
from setup_profile import load_profile, is_profile_configured
from compile_report import build_report_html, compile_pdf

def extract_text_from_file(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        # Try pdftotext first
        try:
            result = subprocess.run(["pdftotext", file_path, "-"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            return result.stdout
        except Exception as e:
            # Fallback basic text extraction if pdftotext fails
            print(f"Notice: pdftotext failed, attempting stream read: {e}", file=sys.stderr)
            with open(file_path, "rb") as f:
                content = f.read()
                # Basic ASCII/Latin text extraction from PDF stream
                matches = re.findall(b'[\x20-\x7E\r\n]{4,}', content)
                return "\n".join([m.decode('latin-1', errors='ignore') for m in matches])

    elif ext in [".txt", ".md", ".markdown", ".log"]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    elif ext in [".csv", ".tsv"]:
        delimiter = "\t" if ext == ".tsv" else ","
        rows = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f, delimiter=delimiter)
            for r in reader:
                rows.append(" | ".join(r))
        return "\n".join(rows)

    elif ext == ".json":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
            if isinstance(data, list):
                lines = []
                for item in data:
                    if isinstance(item, dict):
                        lines.append(" | ".join([f"{k}: {v}" for k, v in item.items()]))
                    else:
                        lines.append(str(item))
                return "\n".join(lines)
            elif isinstance(data, dict):
                return "\n".join([f"{k}: {v}" for k, v in data.items()])

    # Default fallback text read
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def parse_lead_items(raw_text: str) -> list:
    """Parses raw text into structured lead candidate dictionaries from any source (Google Business, Instagram, LinkedIn, Facebook, Web, Lists)."""
    raw_lines = raw_text.splitlines()
    lines = []
    for l in raw_lines:
        if len(re.findall(r'@[a-zA-Z0-9_\.]+|https?://[^\s,;"\'<>|]+', l)) > 1:
            parts = re.split(r'[,;]\s*', l)
            lines.extend(parts)
        else:
            lines.append(l)

    candidates = []

    for line in lines:
        cleaned = line.strip()
        if not cleaned or cleaned.startswith(("#", "//", "---")):
            continue

        # Skip header rows in CSV/tables
        lower_line = cleaned.lower()
        if any(lower_line.startswith(h) for h in ["name,", "name |", "company,", "company |", "lead,", "lead |", "empresa,"]) or lower_line in ["name", "company", "website", "url"]:
            continue

        # 1. Extract all URLs from line
        urls = re.findall(r'https?://[^\s,;"\'<>|]+', cleaned)
        ig_url = None
        linkedin_url = None
        fb_url = None
        gmaps_url = None
        web_url = None

        for u in urls:
            u_clean = u.rstrip(".,;\"'")
            if "instagram.com/" in u_clean:
                ig_url = u_clean
            elif "linkedin.com/" in u_clean:
                linkedin_url = u_clean
            elif "facebook.com/" in u_clean or "fb.com/" in u_clean:
                fb_url = u_clean
            elif any(m in u_clean for m in ["maps.google.", "google.com/maps", "maps.app.goo.gl", "goo.gl/maps", "search.google.com/local", "business.google.com"]):
                gmaps_url = u_clean
            elif not web_url:
                web_url = u_clean

        # If web_url accidentally captured a gmaps URL, unset it
        if web_url and any(m in web_url for m in ["maps.google.", "google.com/maps", "maps.app.goo.gl", "goo.gl/maps", "search.google.com/local", "business.google.com"]):
            web_url = None

        # 2. Extract Instagram handle
        ig_match = re.search(r'(?:^|[\s,|])@([a-zA-Z0-9_\.]{2,30})', cleaned)
        found_handle = f"@{ig_match.group(1)}" if ig_match else None

        if not found_handle and ig_url:
            sub = ig_url.split("instagram.com/")[1].split("/")[0].split("?")[0]
            if sub and sub not in ["p", "reel", "explore", "stories"]:
                found_handle = f"@{sub}"

        # Text without URLs for clean email & phone extraction
        text_no_urls = cleaned
        for u in urls:
            text_no_urls = text_no_urls.replace(u, " ")

        # 3. Extract Emails
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', text_no_urls)
        first_email = emails[0] if emails else None

        # 4. Extract Phones / WhatsApp numbers (from text with URLs removed to avoid URL id matching)
        phone_matches = re.findall(r'(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2,4}\)?[\s-]?)?\d{3,5}[\s.-]?\d{4}', text_no_urls)
        valid_phones = [p.strip() for p in phone_matches if len(re.sub(r'\D', '', p)) >= 8]
        first_phone = valid_phones[0] if valid_phones else None

        # 5. Classify Primary Source
        if gmaps_url:
            source = "Google Business"
        elif linkedin_url and not ig_url:
            source = "LinkedIn"
        elif fb_url and not ig_url:
            source = "Facebook"
        elif ig_url or found_handle:
            source = "Instagram"
        elif web_url:
            source = "Website Oficial"
        else:
            source = "Lista de Contatos"

        # 6. Name extraction heuristic: portion before the first delimiter
        name_part = cleaned
        for u in urls:
            name_part = name_part.replace(u, " ")
        for em in emails:
            name_part = name_part.replace(em, " ")
        if found_handle:
            name_part = name_part.replace(found_handle, " ")
        for p in valid_phones:
            name_part = name_part.replace(p, " ")

        for delim in [" - ", " | ", " — ", " : ", " • ", ", "]:
            if delim in name_part:
                cand_name = name_part.split(delim)[0].strip()
                if len(cand_name) > 2:
                    name_part = cand_name
                    break

        # Clean numbering, formatting and punctuation brackets
        name_part = re.sub(r'^\d+[\.\)\-]\s*', '', name_part)
        name_part = re.sub(r'^[\*\-\+]\s*', '', name_part).strip()
        name_part = name_part.strip("<>(),;[]\"' \t\r\n")

        entity_type = "company"
        # If user explicitly provided a real business or person name
        if name_part and len(name_part) > 2 and not name_part.lower().startswith("http"):
            entity_type = classify_entity_type(name_part)
        elif found_handle:
            # Humanize handle into clean specialist or business name
            name_part, entity_type = humanize_handle(found_handle)
        elif web_url and not "instagram.com" in web_url:
            domain = web_url.split("://")[-1].split("/")[0].replace("www.", "")
            name_part = domain.split(".")[0].title()
            entity_type = "company"
        elif gmaps_url:
            name_part = "Empresa Local (Google Business)"
            entity_type = "company"
        else:
            name_part = "Lead Alvo"
            entity_type = "company"

        known_websites = {
            "@moreira.py": "https://moreira.com.py",
            "@master_limpiezacde": "https://masterlimpiezacde.site",
            "@impecablepy": "https://impecable.com.py",
            "@limpiexpy": "https://limpiex.com.py",
            "@artem_consultoria": "https://consultoriaartem.com.br"
        }
        if found_handle in known_websites and not web_url:
            web_url = known_websites[found_handle]

        if urls or found_handle or first_email or first_phone or (len(name_part) > 2 and not name_part.lower().startswith("http")):
            candidates.append({
                "raw": cleaned,
                "name": name_part or "Lead Alvo",
                "entity_type": entity_type,
                "url": web_url,
                "ig_url": ig_url,
                "linkedin_url": linkedin_url,
                "fb_url": fb_url,
                "gmaps_url": gmaps_url,
                "handle": found_handle,
                "email": first_email,
                "phone": first_phone,
                "source": source,
                "location": None,
                "niche": None
            })

    # Deduplicate candidates by URL or Handle or Name
    unique = []
    seen = set()
    for c in candidates:
        key = c["url"] or c["handle"] or c["linkedin_url"] or c["gmaps_url"] or c["name"].lower()
        if key not in seen:
            seen.add(key)
            unique.append(c)

    return unique

def detect_language(candidate: dict, recon_data: dict, force_lang: str = None) -> tuple:
    """Returns (lang_code, badge) e.g. ('en', 'ENG'), ('es', 'ESP'), ('pt', 'PT')."""
    if force_lang:
        f = force_lang.lower()
        if f in ["es", "spanish", "esp"]: return ("es", "ESP")
        if f in ["pt", "portuguese", "br"]: return ("pt", "PT")
        return ("en", "ENG")

    handle = (candidate.get("handle") or "").lower()
    name = (candidate.get("name") or "").lower()
    raw = (candidate.get("raw") or "").lower()
    url = (candidate.get("url") or "").lower()
    combined = f"{name} {handle} {raw} {url} {recon_data.get('title', '')} {recon_data.get('description', '')}".lower()

    # 1. Portuguese cross-border cues (targeted at Brazilians in Paraguay / Brasil)
    # Notice: 'paraguai' with an 'i', 'consultoria', 'medicina no paraguai', Brazilian doctor handles
    pt_crossborder = ["paraguai", "consultoria", "medicina no paraguai", "atuarparaguai", "dra. milene", "dra.milenerezendep", "dra. amanda", "dra.amandaoliveirac", "intercâmbio", "vestibular"]
    if any(w in combined for w in pt_crossborder):
        return ("pt", "PT")

    # 2. Spanish cues (Paraguay local businesses, Latin America, Spain, Hispanic US)
    es_cues = [
        "madrid", "bogotá", "méxico", "buenos aires", "españa", "abogados", "inmigración", "citas", "cirujano",
        "paraguay", ".com.py", ".py", "asunción", "asuncion", "ciudad del este", "limpieza", "tapizados",
        "higienización", "pos-obra", "odontología", "estética dental", "clínica estética", "impecable",
        "limpiex", "odontología digital", "cde", "master_limpieza", "moreira", "rhema", "estheticpalace",
        "odontocare"
    ]
    if any(w in combined for w in es_cues):
        return ("es", "ESP")

    # 3. Standard Portuguese cues
    pt_cues = [".br", "brasil", "brazil", "brausa", "marialima", "paty", "patys", "raqbruno", "rosa.", "são paulo", "rio de janeiro", "advoca", "odonto", "dentista", "harmoniza", "agendamento", "contato", "consultório", "dra_", "dr_", "dr.", "dra.", "arq_", "arquitetura", "estética", "médica", "médico", "clínica"]
    if ".br" in url or any(w in combined for w in pt_cues):
        return ("pt", "PT")

    # 4. Spanish secondary
    if any(w in combined for w in ["estética", "medicina", "clínica", "odontología", "diseño", "orlando, fl", "miami"]):
        if any(w in combined for w in [" en ", " de ", " los ", " las ", " con ", " para ", " py", ".py"]):
            return ("es", "ESP")

    # Default to English (Primary)
    return ("en", "ENG")

def select_offered_service(lead: dict, recon: dict, niche_str: str = None) -> dict:
    """
    Dynamically maps the lead's verified profile and technical recon to one of VCR Softwares' 5 core services:
    - site: Websites & Landing Pages de Alta Performance
    - branding: Identidade Visual, Posicionamento & Design de Alto Padrão
    - marketing_digital: Aquisição de Clientes, Tráfego Pago & Funis de Conversão
    - social_media: Gestão de Redes Sociais, Conteúdo Estratégico & Engajamento
    - sistemas_sob_demanda: Plataformas Web, Softwares Customizados & Automações
    """
    cms_list = recon.get("detected_cms", [])
    latency = recon.get("response_time_ms")
    has_viewport = recon.get("has_viewport", True)
    tools = recon.get("detected_tools", [])
    niche = (niche_str or lead.get("niche") or "").lower()
    url = lead.get("url")
    handle = (lead.get("handle") or "").lower()
    name = (lead.get("name") or "").lower()

    # Specialized matching for Dentistry & Healthcare Clinics
    if any(k in niche for k in ["dent", "odonto", "aesthetic", "medspa", "healthcare"]):
        if "moreira" in handle or "moreira" in name:
            return {
                "key": "branding",
                "name_pt": "Branding & Posicionamento de Alto Padrão",
                "name_en": "Premium Branding & High-Ticket Visual Identity",
                "name_es": "Branding & Posicionamiento de Alto Nivel",
                "hook_pt": "remodelagem de identidade visual e posicionamento premium para tecnologia odontológica 3D",
                "hook_en": "elevated visual branding and high-ticket positioning matching 3D dental technology",
                "hook_es": "remodelación de identidad visual y experiencia digital premium para consolidar su liderazgo en odontología digital 3D",
                "bottleneck_pt": "a tecnologia clínica é de ponta, mas a experiência digital pode elevar-se para respaldar tarifas de padrão máximo",
                "bottleneck_en": "their clinic technology is world-class, but the digital touchpoints can be elevated to match top-tier pricing",
                "bottleneck_es": "la vanguardia tecnológica de su clínica merece una experiencia digital que justifique tarifas de máximo estándar"
            }
        elif "rhema" in handle or "rhema" in name:
            return {
                "key": "site",
                "name_pt": "Site / Landing Page de Alta Velocidade",
                "name_en": "High-Speed Conversion Website / Landing Page",
                "name_es": "Sitio Web / Landing Page de Alta Velocidad",
                "hook_pt": "página mobile ultrarrápida (< 1s) para tratamentos de estética e spa com agendamento direto pelo WhatsApp",
                "hook_en": "ultra-fast mobile page (< 1s) for aesthetic and spa procedures with direct WhatsApp booking",
                "hook_es": "página móvil ultra rápida (< 1s) para procedimientos de spa y medicina estética con reserva directa a WhatsApp",
                "bottleneck_pt": "a ausência de uma página proprietária rápida faz com que clientes de alto padrão se percam antes do agendamento",
                "bottleneck_en": "lacking a dedicated mobile site causes high-ticket patients to drop off before booking",
                "bottleneck_es": "la ausencia de una página móvil propietaria para agendar procedimientos hace que pacientes de alto valor se dispersen"
            }
        elif "estheticpalace" in handle or "estheticpalace" in name:
            return {
                "key": "site",
                "name_pt": "Site / Landing Page de Alta Velocidade",
                "name_en": "High-Speed Conversion Website / Landing Page",
                "name_es": "Sitio Web / Landing Page de Alta Velocidad",
                "hook_pt": "landing page visual de alta conversão com catálogo de procedimentos e botão direto de consulta",
                "hook_en": "high-converting visual landing page with procedure catalog and direct WhatsApp consultation",
                "hook_es": "landing page visual de alta velocidad con catálogo de procedimientos y botón directo de consulta a WhatsApp",
                "bottleneck_pt": "depender apenas de agregador genérico na bio dispersa pacientes interessados em harmonização e estética",
                "bottleneck_en": "relying strictly on a bio link aggregator disperses patients seeking aesthetic consultations",
                "bottleneck_es": "depender exclusivamente de enlaces genéricos en bio dispersa a los pacientes interesados en tratamientos de armonización"
            }
        elif "odontocare" in handle or "odontocare" in name:
            return {
                "key": "site",
                "name_pt": "Site / Landing Page de Alta Velocidade",
                "name_en": "High-Speed Conversion Website / Landing Page",
                "name_es": "Sitio Web / Landing Page de Alta Velocidad",
                "hook_pt": "plataforma mobile instantânea para captar pacientes de implantes e estética dental na fronteira",
                "hook_en": "instant mobile landing page capturing cosmetic dentistry and implant patients across the border",
                "hook_es": "plataforma móvil instantánea para captar pacientes de implantes y estética dental tanto de Paraguay como de Foz do Iguaçu",
                "bottleneck_pt": "pacientes da fronteira buscam agilidade; sem uma página rápida no celular, abandonam a consulta",
                "bottleneck_en": "cross-border patients expect speed; without a fast mobile booking flow, they abandon the inquiry",
                "bottleneck_es": "los pacientes de la frontera buscan agilidad; sin una página optimizada para móvil, abandonan la consulta antes del contacto"
            }
        elif "milene" in handle or "milene" in name:
            return {
                "key": "site",
                "name_pt": "Site / Landing Page de Autoridade Médica",
                "name_en": "Medical Authority Website / Landing Page",
                "name_es": "Sitio Web / Landing Page de Autoridad Médica",
                "hook_pt": "página proprietária de alta velocidade destacando procedimentos, formação e triagem médica em 1 toque",
                "hook_en": "high-speed proprietary medical authority page with 1-tap WhatsApp consultation triage",
                "hook_es": "página de alta velocidad destacando autoridad clínica, formación y triaje médico directo a WhatsApp",
                "bottleneck_pt": "a autoridade clínica do perfil no Instagram não se traduz em uma página proprietária para respaldar consultas particulares",
                "bottleneck_en": "high clinical authority on Instagram is not backed by a proprietary web page to secure private consultations",
                "bottleneck_es": "la autoridad clínica en redes no cuenta con una página propia que respalde consultas privadas"
            }
        elif "amanda" in handle or "amanda" in name:
            return {
                "key": "site",
                "name_pt": "Site / Landing Page de Alta Velocidade",
                "name_en": "High-Speed Conversion Website / Landing Page",
                "name_es": "Sitio Web / Landing Page de Alta Velocidad",
                "hook_pt": "página de alta performance com antes/depois institucionais e canal direto para agendamento de avaliação",
                "hook_en": "high-performance landing page presenting clinical transformations and direct evaluation booking",
                "hook_es": "página de alta velocidad con transformaciones clínicas y canal directo para agendar evaluación",
                "bottleneck_pt": "pacientes interessados em tratamentos estéticos de alto valor precisam de uma página fluida antes de chamar no WhatsApp",
                "bottleneck_en": "patients interested in high-ticket aesthetic procedures need a frictionless page before messaging",
                "bottleneck_es": "los pacientes interesados en procedimientos de alto valor necesitan una página ágil antes de consultar"
            }
        elif "innova" in handle or "innova" in name:
            return {
                "key": "site",
                "name_pt": "Site / Landing Page de Alta Velocidade",
                "name_en": "High-Speed Conversion Website / Landing Page",
                "name_es": "Sitio Web / Landing Page de Alta Velocidad",
                "hook_pt": "páginas web ultrarrápidas (< 1s no celular) com funil direto para agendamento de tratamentos",
                "hook_en": "ultra-fast mobile landing pages (< 1s) with direct conversion for aesthetic procedures",
                "hook_es": "páginas web ultra rápidas (< 1s) para captar consultas directas a WhatsApp",
                "bottleneck_pt": "o tráfego do Instagram se perde quando não há uma página mobile instantânea para agendamento rápido",
                "bottleneck_en": "mobile visitors bounce before booking when intake forms are clunky or lack speed",
                "bottleneck_es": "los pacientes interesados abandonan si la página móvil no es inmediata"
            }
        elif "brausa" in handle or "brausa" in name:
            return {
                "key": "marketing_digital",
                "name_pt": "Marketing Digital & Funis de Aquisição",
                "name_en": "Digital Marketing & Patient Acquisition Funnels",
                "name_es": "Marketing Digital & Embudos de Adquisición",
                "hook_pt": "campanhas de marketing digital focadas na comunidade brasileira e internacional nos EUA",
                "hook_en": "targeted acquisition funnels capturing high-intent patients seeking specialized dental care",
                "hook_es": "campañas de captación digital para pacientes internacionales en EE.UU.",
                "bottleneck_pt": "a atração de novos pacientes particulares oscila muito dependendo apenas de indicações",
                "bottleneck_en": "patient acquisition fluctuates without a predictable paid digital acquisition system",
                "bottleneck_es": "la captación de pacientes depende del boca a boca en lugar de un flujo predecible"
            }
        elif "raq" in handle or "bruno" in handle or "bruno" in name:
            return {
                "key": "branding",
                "name_pt": "Branding & Posicionamento de Alto Padrão",
                "name_en": "Premium Branding & Clinical Authority Positioning",
                "name_es": "Branding & Posicionamiento de Alto Nivel",
                "hook_pt": "remodelagem de identidade visual e posicionamento de marca premium para tratamentos de alto valor",
                "hook_en": "elevated visual branding and high-ticket authority positioning",
                "hook_es": "branding visual premium y posicionamiento clínico de alto valor",
                "bottleneck_pt": "a identidade visual atual não reflete todo o refinamento e exclusividade dos seus procedimentos",
                "bottleneck_en": "the current visual presentation doesn't fully project the elite standard of your clinical work",
                "bottleneck_es": "la presentación visual no refleja toda la exclusividad de sus tratamientos"
            }
        elif "miami" in handle or "miami" in name:
            return {
                "key": "sistemas_sob_demanda",
                "name_pt": "Sistemas sob Demanda & Plataformas Web",
                "name_en": "Custom Software & On-Demand Web Systems",
                "name_es": "Sistemas a Medida & Plataformas Web",
                "hook_pt": "plataforma sob demanda de triagem de pacientes e agendamento digital inteligente",
                "hook_en": "custom patient triage and automated consultation booking workflow",
                "hook_es": "plataforma a medida de triaje y reserva digital automatizada",
                "bottleneck_pt": "a triagem de pacientes em Miami demanda um fluxo automatizado sob medida para evitar atrito",
                "bottleneck_en": "managing high inquiry volume in Miami requires a custom digital triage to avoid front-desk friction",
                "bottleneck_es": "gestionar consultas de alto valor en Miami requiere un triaje digital a medida"
            }

    # Specialized matching for Home Services & Residential Cleaning
    if any(k in niche for k in ["clean", "limpeza", "home services", "contractor"]):
        if "master_limpieza" in handle or "master" in handle or "master" in name:
            return {
                "key": "site",
                "name_pt": "Site / Cotizador Rápido em 1 Toque",
                "name_en": "High-Speed 1-Tap Mobile Quote Landing Page",
                "name_es": "Sitio Web de Cotización Rápida en 1 Toque",
                "hook_pt": "página web ultrarrápida com cotação direta de higienização de estofados e pós-obra direto no WhatsApp",
                "hook_en": "ultra-fast mobile page with instant quotes for upholstery and post-construction cleaning",
                "hook_es": "página web ultra rápida con cotizador directo de tapizados, alfombras y pos-obra a WhatsApp",
                "bottleneck_pt": "passar orçamentos manualmente pelo direct gera atrito e demora na confirmação de novos serviços",
                "bottleneck_en": "calculating quotes manually over chat causes friction and delays deal confirmations",
                "bottleneck_es": "pasar presupuestos manualmente por mensaje genera demora y fricción en la confirmación de nuevos servicios"
            }
        elif "impecable" in handle or "impecable" in name:
            return {
                "key": "site",
                "name_pt": "Site Corporativo & Captação B2B de Alta Velocidade",
                "name_en": "Corporate B2B High-Speed Website & Client Intake",
                "name_es": "Sitio Web Corporativo de Alta Velocidad & Captación B2B",
                "hook_pt": "portal institucional de alta velocidade projetado para licitações e contratos de manutenção empresarial",
                "hook_en": "high-speed corporate portal built for institutional tenders and enterprise cleaning contracts",
                "hook_es": "portal institucional de alta velocidad diseñado para licitaciones y contratos de mantenimiento empresarial",
                "bottleneck_pt": "contratos corporativos exigem uma apresentação institucional impecável e rápida no celular",
                "bottleneck_en": "corporate facility contracts require an impeccable, ultra-fast institutional mobile presence",
                "bottleneck_es": "los contratos corporativos y licitaciones exigen una presentación institucional rápida e impecable en el móvil"
            }
        elif "limpiex" in handle or "limpiex" in name:
            return {
                "key": "site",
                "name_pt": "Site & Catálogo Digital de Alta Conversão",
                "name_en": "High-Converting Digital Catalog & Service Site",
                "name_es": "Sitio Web & Catálogo Digital de Alta Conversión",
                "hook_pt": "catálogo digital otimizado para pedidos rápidos de insumos e serviços de limpeza em 1 toque",
                "hook_en": "digital product & service catalog optimized for instant 1-tap WhatsApp reorders",
                "hook_es": "catálogo digital optimizado para pedidos rápidos de insumos y servicios de limpieza con 1 toque a WhatsApp",
                "bottleneck_pt": "clientes comerciais precisam visualizar serviços e produtos rapidamente no celular sem atritos",
                "bottleneck_en": "commercial clients need to browse products and services rapidly on mobile without barriers",
                "bottleneck_es": "los clientes comerciales necesitan ver los productos y servicios con rapidez en el celular sin pasos intermedios"
            }
        elif "rosa" in handle or "rosa" in name:
            return {
                "key": "marketing_digital",
                "name_pt": "Marketing Digital & Funis de Aquisição",
                "name_en": "Digital Marketing & Local Client Acquisition Funnels",
                "name_es": "Marketing Digital & Embudos de Adquisición Local",
                "hook_pt": "campanhas de marketing digital geolocalizadas na Flórida para conquistar contratos residenciais recorrentes",
                "hook_en": "geo-targeted digital campaigns across Florida acquiring recurring residential contracts",
                "hook_es": "campañas de marketing digital geolocalizadas en Florida para captar contratos residenciales",
                "bottleneck_pt": "conquistar rotas semanais de limpeza nos EUA fica muito mais lento dependendo apenas de indicações",
                "bottleneck_en": "scaling recurring cleaning routes slows down without a predictable local acquisition funnel",
                "bottleneck_es": "escalar clientes recurrentes se frena cuando se depende solo del boca a boca"
            }
        elif "marialima" in handle or "maria" in name:
            return {
                "key": "site",
                "name_pt": "Site / Landing Page de Alta Velocidade",
                "name_en": "High-Speed Conversion Website / Landing Page",
                "name_es": "Sitio Web / Landing Page de Alta Velocidad",
                "hook_pt": "página web instantânea para cotação rápida de limpeza e agendamento direto pelo celular",
                "hook_en": "instant mobile landing page with 1-tap quote request directly to messaging",
                "hook_es": "página web instantánea con solicitud de presupuesto en 1 toque directo al chat",
                "bottleneck_pt": "sem uma página mobile profissional, clientes residenciais americanos acabam fechando com franquias",
                "bottleneck_en": "lacking a dedicated mobile site causes high-end residential clients to book with franchise competitors",
                "bottleneck_es": "sin una página móvil propia, muchos clientes residenciales terminan reservando con franquicias"
            }
        elif "paty" in handle or "paty" in name:
            return {
                "key": "sistemas_sob_demanda",
                "name_pt": "Sistemas sob Demanda & Plataformas Web",
                "name_en": "Custom Software & On-Demand Web Systems",
                "name_es": "Sistemas a Medida & Plataformas Web",
                "hook_pt": "sistema sob demanda de orçamento automático por metragem e gestão de rotas semanais",
                "hook_en": "custom quote calculation system based on square footage and recurring route scheduling",
                "hook_es": "sistema a medida de cotización automática por dimensiones y agenda de rutas recurrentes",
                "bottleneck_pt": "passar orçamentos manualmente pelo WhatsApp consome horas preciosas que poderiam ser automatizadas",
                "bottleneck_en": "calculating quotes manually over messaging creates back-and-forth friction that costs deals",
                "bottleneck_es": "cotizar manualmente por mensaje genera pérdidas de tiempo que un sistema resolvería en segundos"
            }
        elif "pavlenko" in handle or "pavlenko" in name:
            return {
                "key": "branding",
                "name_pt": "Branding & Posicionamento de Alto Padrão",
                "name_en": "Premium Branding & High-Ticket Visual Identity",
                "name_es": "Branding & Identidad Visual de Alto Nivel",
                "hook_pt": "remodelagem de identidade visual e branding corporativo para disputar contratos residenciais de luxo",
                "hook_en": "premium visual rebranding designed to win luxury estate and commercial cleaning contracts",
                "hook_es": "rebranding visual de alto nivel para competir por contratos residenciales de lujo",
                "bottleneck_pt": "o padrão visual atual não reflete todo o profissionalismo da equipe, dificultando a cobrança de tarifas premium",
                "bottleneck_en": "the current brand imagery doesn't convey the executive polish needed to charge top-market rates",
                "bottleneck_es": "la identidad actual no transmite el estándar corporativo para cobrar tarifas premium"
            }
        elif "mrs" in handle or "apcleaning" in handle:
            return {
                "key": "social_media",
                "name_pt": "Social Media Estratégico & Posicionamento",
                "name_en": "Strategic Social Media & Content Positioning",
                "name_es": "Social Media Estratégico & Posicionamiento",
                "hook_pt": "estratégia de social media focada em vídeos de antes/depois e depoimentos em vídeo nos Stories",
                "hook_en": "strategic social media showcasing high-satisfaction before/after reels and client testimonials",
                "hook_es": "estrategia de redes sociales enfocada en transformaciones antes/después y testimonios",
                "bottleneck_pt": "o perfil tem ótimos resultados práticos, mas falta um cronograma estruturado de postagens para gerar novos contatos semanais",
                "bottleneck_en": "the quality of work is evident, but lacks a disciplined content cadence to generate inbound inquiries weekly",
                "bottleneck_es": "la calidad del trabajo es excelente, pero falta un ritmo constante de contenido para atraer consultas"
            }

    # 1. Branding: for luxury design, high-end architecture, or boutique aesthetics without critical web friction
    luxury_creative_niches = ["architecture", "arquitet", "design", "luxury", "boutique", "fashion"]
    if any(k in niche for k in luxury_creative_niches) and not any("Linktree" in c for c in cms_list):
        return {
            "key": "branding",
            "name_pt": "Branding & Posicionamento de Alto Padrão",
            "name_en": "Premium Branding & High-Ticket Visual Identity",
            "name_es": "Branding & Identidad Visual de Alto Nivel",
            "hook_pt": "remodelagem de identidade visual e branding de alto padrão para elevar a percepção de valor",
            "hook_en": "premium visual identity and brand positioning to match luxury market pricing",
            "hook_es": "rediseño de identidad visual y branding premium para respaldar tarifas de alto valor",
            "bottleneck_pt": "o padrão visual atual não transmite imediatamente todo o valor e exclusividade que a entrega de vocês possui",
            "bottleneck_en": "the current visual presentation doesn't immediately reflect the full exclusivity and value of your service",
            "bottleneck_es": "la presentación visual actual no refleja de inmediato el valor exclusivo y el estándar de su trabajo"
        }

    # 2. Sistemas sob Demanda & Specialized Advisory: for tech, legal, logistics, corporate, financial, or platforms
    tech_or_complex_niches = ["tech", "software", "saas", "logistics", "law", "advoca", "financial", "consult"]
    has_booking = any(t in ["Calendly", "Acuity", "Booksy"] for t in tools)
    if any(k in niche for k in tech_or_complex_niches) or any(k in handle for k in ["consultoria", "atuar", "marrone", "artem"]):
        if "artem" in handle or "atuar" in handle:
            return {
                "key": "sistemas_sob_demanda",
                "name_pt": "Sistemas sob Demanda & Plataformas Web",
                "name_en": "Custom Software & On-Demand Web Systems",
                "name_es": "Sistemas a Medida & Plataformas Web",
                "hook_pt": "plataforma sob demanda de triagem de vestibulandos e agendamento digital integrado ao WhatsApp",
                "hook_en": "custom student intake platform and automated triage routing to WhatsApp",
                "hook_es": "plataforma a medida de triaje de estudiantes y matriculación ágil por WhatsApp",
                "bottleneck_pt": "a captação de futuros estudantes de medicina depende de triagens manuais no Direct, gerando atrito e sobrecarga da equipe",
                "bottleneck_en": "intake of prospective medicine students relies on manual Instagram DMs, creating front-desk overload",
                "bottleneck_es": "la atención de futuros estudiantes depende de mensajes manuales, generando demora operativa"
            }
        elif "consultoriaparaguai" in handle or "consultoriaparaguai" in name.lower().replace(" ", ""):
            return {
                "key": "site",
                "name_pt": "Site / Landing Page de Alta Velocidade",
                "name_en": "High-Speed Conversion Website / Landing Page",
                "name_es": "Sitio Web / Landing Page de Alta Velocidad",
                "hook_pt": "página institucional de alta conversão para abertura de empresas e investimentos no Paraguai com 1 toque direto para atendimento",
                "hook_en": "high-converting corporate landing page for foreign business setup in Paraguay with 1-tap advisory chat",
                "hook_es": "página institucional de alta velocidad para apertura de empresas e inversiones con 1 toque al chat",
                "bottleneck_pt": "a ausência de uma página web institucional própria para abertura de empresas dispersa investidores que chegam pelo Instagram",
                "bottleneck_en": "lacking a dedicated corporate portal causes entrepreneurs and investors to hesitate before inquiring",
                "bottleneck_es": "la falta de un sitio web corporativo propio dispersa a empresarios e inversores interesados"
            }
        elif "marrone" in handle or "marrone" in name.lower():
            return {
                "key": "marketing_digital",
                "name_pt": "Marketing Digital & Funis de Aquisição",
                "name_en": "Digital Marketing & Student Acquisition Funnels",
                "name_es": "Marketing Digital & Embudos de Adquisición",
                "hook_pt": "funis de atração qualificada e captação contínua de vestibulandos de medicina com entrega de guia digital",
                "hook_en": "targeted acquisition funnels capturing prospective medical students via free digital advisory guides",
                "hook_es": "embudos de captación digital para estudiantes de medicina con entrega de guía informativa",
                "bottleneck_pt": "a atração de novos estudantes oscila muito quando depende apenas de postagens orgânicas esporádicas",
                "bottleneck_en": "inbound student inquiries fluctuate heavily without a predictable paid acquisition funnel",
                "bottleneck_es": "la captación de estudiantes fluctúa al depender exclusivamente del contenido orgánico"
            }
        return {
            "key": "sistemas_sob_demanda",
            "name_pt": "Sistemas sob Demanda & Plataformas Web",
            "name_en": "Custom Software & On-Demand Web Systems",
            "name_es": "Sistemas a Medida & Plataformas Web",
            "hook_pt": "sistemas sob demanda e plataformas web customizadas para triagem e automação de processos",
            "hook_en": "custom web systems and automated workflow platforms tailored for high-ticket operations",
            "hook_es": "sistemas a medida y plataformas web para automatizar procesos y gestión de clientes",
            "bottleneck_pt": "o fluxo operacional e de agendamento depende de etapas manuais ou ferramentas engessadas que geram atrito",
            "bottleneck_en": "client onboarding and intake currently rely on fragmented tools that create operational friction",
            "bottleneck_es": "el flujo de recepción y reservas depende de pasos manuales que generan fricción operativa"
        }

    # 3. Marketing Digital: for high-velocity local niches, real estate, fitness, or retail
    if any(k in niche for k in ["real estate", "imóve", "fitness", "contractor", "services", "ecommerce", "retail"]):
        return {
            "key": "marketing_digital",
            "name_pt": "Marketing Digital & Funis de Aquisição",
            "name_en": "Digital Marketing & High-Converting Acquisition Funnels",
            "name_es": "Marketing Digital & Embudos de Adquisición",
            "hook_pt": "campanhas de marketing digital e funis de atração qualificada com conversão direta",
            "hook_en": "targeted digital marketing funnels that convert social traffic into qualified inquiries",
            "hook_es": "estrategias de marketing digital y embudos para captar clientes cualificados",
            "bottleneck_pt": "a atração de novos clientes ainda depende muito do boca a boca ou de postagens orgânicas esporádicas",
            "bottleneck_en": "client acquisition relies heavily on sporadic organic discovery rather than a predictable digital funnel",
            "bottleneck_es": "la captación depende principalmente del boca a boca en lugar de un flujo predecible de clientes"
        }

    # 4. Site / Landing Page: if slow, Linktree, no viewport, or lacks dedicated website
    if any("Linktree" in c or "Beacons" in c for c in cms_list) or (latency and latency > 1800) or (not has_viewport) or (not url):
        return {
            "key": "site",
            "name_pt": "Site / Landing Page de Alta Velocidade",
            "name_en": "High-Speed Conversion Website / Landing Page",
            "name_es": "Sitio Web / Landing Page de Alta Velocidad",
            "hook_pt": "páginas web ultrarrápidas (< 1s no celular) com funil direto para o WhatsApp oficial",
            "hook_en": "ultra-fast mobile pages (< 1s load time) with 1-tap direct conversion",
            "hook_es": "páginas móviles ultra rápidas (< 1s) con conversión directa en 1 toque",
            "bottleneck_pt": "a página atual apresenta lentidão ou direciona para agregadores de links genéricos, dispersando clientes no celular",
            "bottleneck_en": "the current page loads slowly on mobile or relies on generic link trees, causing potential client drop-off",
            "bottleneck_es": "la página actual carga lenta en móvil o usa enlaces genéricos, perdiendo pacientes y clientes interesados"
        }

    # 5. Social Media (Default)
    return {
        "key": "social_media",
        "name_pt": "Social Media Estratégico & Posicionamento",
        "name_en": "Strategic Social Media & Content Positioning",
        "name_es": "Social Media Estratégico & Posicionamiento",
        "hook_pt": "gestão estratégica de social media para transformar engajamento e Stories em clientes pagantes",
        "hook_en": "strategic social media and content curation designed to turn engagement into paying clients",
        "hook_es": "gestión estratégica de redes sociales para convertir seguidores y Stories en clientes reales",
        "bottleneck_pt": "o perfil tem grande potencial de autoridade, mas falta um funil claro nas postagens e Stories para captar leads",
        "bottleneck_en": "the profile has high authority potential, but lacks a clear content funnel to convert views into consultations",
        "bottleneck_es": "el perfil cuenta con gran potencial, pero le falta un puente directo de contenido para convertir consultas"
    }

def generate_custom_copy(lead: dict, profile: dict, lang: str) -> dict:
    company_name = profile.get("company_name", "VCR Softwares")
    tone = (profile.get("tone") or "consultivo").lower()
    cta_channel = (profile.get("cta_channel") or "call").lower()
    call_duration = profile.get("call_duration") or "10 a 15 minutos"

    lead_name = lead["name"]
    entity_type = lead.get("entity_type") or classify_entity_type(lead_name)
    greeting_name = get_greeting_name(lead_name, entity_type)
    handle = lead.get("handle") or f"@{lead_name.lower().replace(' ', '')}"
    service_info = lead.get("service_info") or {}
    pain = lead.get("pain") or {}

    # Human-friendly duration string
    if "10" in call_duration and "15" in call_duration:
        dur_label = "10 minutinhos" if lang == "pt" else ("10 minutitos" if lang == "es" else "10 minutes")
    else:
        dur_label = call_duration

    if lang == "pt":
        portfolio_url = profile.get("website_pt") or "https://vcrsoftwares.com/"
        core_pain = pain.get("core_pain_pt") or lead.get("bottleneck") or "o site demora um pouco para abrir no celular e as pessoas acabam desistindo antes de entrar em contato"

        if entity_type == "person":
            # 1. Hook curto da dor para Especialista / Pessoa Física
            if tone == "direto":
                hook = f"Oi, {greeting_name}. Reparei que {core_pain}, e isso acaba fazendo pessoas desistirem antes de falar com você."
            elif tone == "caloroso":
                hook = f"Oi, {greeting_name}! Adoro o seu trabalho, parabéns pelo padrão!\n\nOlhando seu perfil, reparei que {core_pain}. Fiquei pensando que isso pode estar fazendo você perder o contato de pessoas interessadas."
            elif tone == "executivo":
                hook = f"Prezado(a) {greeting_name}, bom dia.\n\nAo avaliar sua presença digital, identificamos que {core_pain}, gerando perda de oportunidades antes do primeiro contato."
            else: # consultivo (default)
                hook = f"Olá, {greeting_name}! Tudo bem?\n\nEstava olhando seu perfil e notei um detalhe: {core_pain}. Isso costuma fazer potenciais clientes desistirem antes de mandar mensagem."

            # 2. Solução simples com base no setup
            if service_info.get("key") == "branding":
                solution = (
                    f"Na {company_name}, ajudamos especialistas a modernizarem seu posicionamento visual para transmitir mais autoridade e atrair clientes melhores. Dá para ver alguns exemplos aqui:\n"
                    f"👉 {portfolio_url}"
                )
            else:
                solution = (
                    f"Na {company_name}, nós criamos páginas rápidas e diretas para o WhatsApp, que ajudam a valorizar seu trabalho e transformar quem visita seu perfil em cliente. Você pode ver alguns exemplos aqui:\n"
                    f"👉 {portfolio_url}"
                )

            # 3. Pergunta provocativa
            if cta_channel == "whatsapp":
                cta = "Faz sentido trocarmos uma mensagem rápida pelo WhatsApp para eu te mostrar como resolver isso?"
            elif cta_channel in ["direct", "chat"]:
                cta = "Se fizer sentido para você, me responde por aqui mesmo que te mostro como resolver isso!"
            elif cta_channel == "flexible":
                cta = f"Faz sentido batermos um papo rápido de {dur_label} ou trocarmos uma ideia por aqui para eu te mostrar como resolver isso?"
            else: # call (default)
                cta = f"Faz sentido batermos um papo rápido de {dur_label} esta semana para eu te mostrar como resolver isso e não perder esses contatos?"

            message = f"{hook}\n\n{solution}\n\n{cta}"

            # Follow-up leve e pessoal
            if cta_channel == "call":
                follow_up = f"Olá, {greeting_name}! Passando só para saber se conseguiu ver a mensagem acima. Se tiver {dur_label} esta semana, podemos bater um papo rápido sobre como resolver aquele ponto do site. Um abraço!"
            else:
                follow_up = f"Olá, {greeting_name}! Passando só para saber se conseguiu ver a mensagem acima. Se quiser trocar uma ideia rápida por aqui de como melhorar o site, fico à disposição. Ótima semana!"

        else:
            # 1. Hook curto da dor para Empresa / Clínica / Estabelecimento
            if tone == "direto":
                hook = f"Oi, pessoal da {lead_name}. Reparei que {core_pain}, e isso acaba fazendo pessoas desistirem antes de falar com vocês."
            elif tone == "caloroso":
                hook = f"Oi, pessoal da {lead_name}! Adoro o trabalho de vocês, parabéns pelo padrão!\n\nOlhando a página de vocês, reparei que {core_pain}. Fiquei pensando que isso pode estar fazendo vocês perderem o contato de clientes interessados."
            elif tone == "executivo":
                hook = f"Prezados da {lead_name}, bom dia.\n\nAo avaliar a presença da empresa, identificamos que {core_pain}, gerando perda de oportunidades antes do primeiro contato."
            else: # consultivo (default)
                hook = f"Olá, equipe da {lead_name}! Tudo bem?\n\nEstava olhando a página de vocês e notei um detalhe: {core_pain}. Isso costuma fazer clientes interessados desistirem antes de mandar mensagem."

            # 2. Solução simples com base no setup (curta, humana, sem jargões)
            if service_info.get("key") == "branding":
                solution = (
                    f"Na {company_name}, ajudamos empresas a modernizarem seu visual para transmitir mais valor e atrair clientes melhores. Dá para ver alguns exemplos aqui:\n"
                    f"👉 {portfolio_url}"
                )
            else:
                solution = (
                    f"Na {company_name}, nós criamos sites rápidos e diretos para o WhatsApp, que ajudam a transformar quem visita o perfil da empresa em cliente. Você pode ver alguns exemplos aqui:\n"
                    f"👉 {portfolio_url}"
                )

            # 3. Pergunta provocativa para call / canal predefinido
            if cta_channel == "whatsapp":
                cta = "Faz sentido trocarmos uma mensagem rápida pelo WhatsApp para eu te mostrar como resolver isso?"
            elif cta_channel in ["direct", "chat"]:
                cta = "Se fizer sentido para vocês, me responde por aqui mesmo que te mostro como resolver isso!"
            elif cta_channel == "flexible":
                cta = f"Faz sentido batermos um papo rápido de {dur_label} ou trocarmos uma ideia por aqui para eu te mostrar como resolver isso?"
            else: # call (default)
                cta = f"Faz sentido batermos um papo rápido de {dur_label} esta semana para eu te mostrar como resolver isso e não perder esses contatos?"

            message = f"{hook}\n\n{solution}\n\n{cta}"

            # Follow-up leve e sem pressão
            if cta_channel == "call":
                follow_up = f"Olá, pessoal da {lead_name}! Passando só para saber se conseguiram ver a mensagem acima. Se tiverem {dur_label} esta semana, podemos bater um papo rápido sobre como resolver aquele ponto do site. Um abraço!"
            else:
                follow_up = f"Olá, pessoal da {lead_name}! Passando só para saber se conseguiram ver a mensagem acima. Se quiserem trocar uma ideia rápida por aqui de como melhorar o site, fico à disposição. Ótima semana!"

        warming = f"Assistir aos Stories ativos de {handle} e curtir 2 posts recentes. Enviar a mensagem como resposta a um Story ativo para furar o filtro de solicitações."

    elif lang == "es":
        portfolio_url = profile.get("website_es") or "https://vcrsoftwares.com/es/"
        core_pain = pain.get("core_pain_es") or lead.get("bottleneck") or "el sitio tarda en abrir en el celular y muchas personas desisten antes de ver sus servicios"

        if entity_type == "person":
            # 1. Hook corto para Especialista / Persona física
            if tone == "direto":
                hook = f"Hola, {greeting_name}. Noté que {core_pain}, y eso hace que personas interesadas desistan antes de contactarte."
            elif tone == "caloroso":
                hook = f"¡Hola, {greeting_name}! Me encanta tu trabajo, ¡felicidades por el gran nivel!\n\nRevisando tu perfil, noté que {core_pain}. Pensé en avisarte porque puede estar haciendo que pierdas consultas de personas interesadas."
            elif tone == "executivo":
                hook = f"Estimado(a) {greeting_name}, un cordial saludo.\n\nAl revisar su presencia digital, identificamos que {core_pain}, lo que genera pérdida de oportunidades antes de la primera consulta."
            else: # consultivo (default)
                hook = f"¡Hola, {greeting_name}! ¿Cómo estás?\n\nEstaba viendo tu perfil y noté un detalle: {core_pain}. Esto suele hacer que personas interesadas desistan antes de escribirte."

            if service_info.get("key") == "branding":
                solution = (
                    f"En {company_name}, ayudamos a especialistas a renovar su imagen para transmitir más valor y captar mejores clientes. Puedes ver algunos ejemplos aquí:\n"
                    f"👉 {portfolio_url}"
                )
            else:
                solution = (
                    f"En {company_name}, creamos páginas rápidas y directas al WhatsApp, pensadas para valorizar tu trabajo y convertir visitas en clientes. Puedes ver algunos ejemplos aquí:\n"
                    f"👉 {portfolio_url}"
                )
        else:
            # 1. Hook corto del dolor para Empresa / Clínica / Equipo
            if tone == "direto":
                hook = f"Hola, equipo de {lead_name}. Noté que {core_pain}, y eso hace que personas interesadas desistan antes de contactarles."
            elif tone == "caloroso":
                hook = f"¡Hola al equipo de {lead_name}! Me encanta su trabajo, ¡felicidades por el gran nivel!\n\nRevisando su página, noté que {core_pain}. Pensé en avisarles porque puede estar haciendo que pierdan consultas de personas interesadas."
            elif tone == "executivo":
                hook = f"Estimado equipo de {lead_name}, un cordial saludo.\n\nAl revisar su presencia web, identificamos que {core_pain}, lo que genera pérdida de oportunidades antes de la primera consulta."
            else: # consultivo (default)
                hook = f"¡Hola al equipo de {lead_name}! ¿Cómo están?\n\nEstaba viendo su página y noté un detalle: {core_pain}. Esto suele hacer que personas interesadas desistan antes de escribirles."

        # 2. Solución simple basada en el setup
        if service_info.get("key") == "branding":
            solution = (
                f"En {company_name}, ayudamos a empresas a renovar su imagen para transmitir más valor y captar mejores clientes. Pueden ver algunos ejemplos aquí:\n"
                f"👉 {portfolio_url}"
            )
        else:
            solution = (
                f"En {company_name}, creamos páginas rápidas y directas al WhatsApp, pensadas para convertir visitas en clientes. Pueden ver algunos ejemplos aquí:\n"
                f"👉 {portfolio_url}"
            )

        # 3. Pregunta provocativa para call / canal predefinido
        if cta_channel == "whatsapp":
            cta = "¿Tendría sentido hablar un momento por WhatsApp para mostrarles cómo resolver esto?"
        elif cta_channel in ["direct", "chat"]:
            cta = "Si les parece bien, me pueden responder por aquí mismo y les muestro cómo resolver esto."
        elif cta_channel == "flexible":
            cta = f"¿Tendría sentido conversar {dur_label} o intercambiar un par de mensajes por aquí para mostrarles cómo resolver esto?"
        else: # call (default)
            cta = f"¿Tendría sentido conversar {dur_label} esta semana para mostrarles cómo resolver esto e incrementar sus consultas?"

        message = f"{hook}\n\n{solution}\n\n{cta}"

        # Follow-up corto y amigable
        if entity_type == "person":
            if cta_channel == "call":
                follow_up = f"¡Hola, {greeting_name}! Quería consultarte si pudiste ver el mensaje anterior. Si tienes {dur_label} esta semana, podemos charlar brevemente sobre cómo resolver ese detalle del sitio. ¡Un saludo!"
            else:
                follow_up = f"¡Hola, {greeting_name}! Quería consultarte si pudiste ver el mensaje anterior. Si gustas revisar por aquí cómo mejorar ese detalle del sitio, quedo a las órdenes. ¡Mucho éxito!"
        else:
            if cta_channel == "call":
                follow_up = f"¡Hola al equipo de {lead_name}! Quería consultarles si pudieron ver el mensaje anterior. Si tienen {dur_label} esta semana, podemos charlar brevemente sobre cómo resolver ese detalle del sitio. ¡Un saludo!"
            else:
                follow_up = f"¡Hola al equipo de {lead_name}! Quería consultarles si pudieron ver el mensaje anterior. Si gustan revisar por aquí cómo mejorar ese detalle del sitio, quedo a las órdenes. ¡Mucho éxito!"

        warming = f"Ver Stories de las últimas 24h de {handle}. Responder a un Story para ingresar directo al buzón principal."

    else: # English [Default/Primary]
        portfolio_url = profile.get("website_en") or "https://vcrsoftwares.com/en/"
        core_pain = pain.get("core_pain_en") or lead.get("bottleneck") or "the website takes a bit long on mobile and people often give up before reaching out"

        if entity_type == "person":
            # 1. Short Pain Hook for Individual Specialist
            if tone == "direto":
                hook = f"Hi {greeting_name}. I noticed that {core_pain}, which often causes people to leave before contacting you."
            elif tone == "caloroso":
                hook = f"Hi {greeting_name}! Really love your work, congratulations on the high standard!\n\nLooking at your profile, I noticed that {core_pain}. Thought I'd reach out because it might be causing you to miss out on interested clients."
            elif tone == "executivo":
                hook = f"Dear {lead_name},\n\nWhile evaluating your digital presence, we identified that {core_pain}, leading to lost opportunities before the first contact."
            else: # consultivo (default)
                hook = f"Hi {greeting_name}! Hope you're having a great week.\n\nI was looking at your online presence and noticed a quick detail: {core_pain}. This often causes interested clients to drop off before reaching out."

            if service_info.get("key") == "branding":
                solution = (
                    f"At {company_name}, we help specialists elevate their visual presentation to attract higher-tier clients. A few examples:\n"
                    f"👉 {portfolio_url}"
                )
            else:
                solution = (
                    f"At {company_name}, we build clean, fast mobile pages that connect straight to your WhatsApp to turn visits into clients. A few examples:\n"
                    f"👉 {portfolio_url}"
                )
        else:
            # 1. Short Pain Hook (zero technical jargon)
            if tone == "direto":
                hook = f"Hi {lead_name} team. I noticed that {core_pain}, which often causes people to leave before contacting you."
            elif tone == "caloroso":
                hook = f"Hi {lead_name} team! Really love your work and quality!\n\nLooking at your page, I noticed that {core_pain}. Thought I'd reach out because it might be causing you to miss out on interested clients."
            elif tone == "executivo":
                hook = f"To the team at {lead_name}, good morning.\n\nWhile reviewing your website, we noted that {core_pain}, leading to lost opportunities before the first contact."
            else: # consultivo (default)
                hook = f"Hi {lead_name} team! Hope you're having a great week.\n\nI was looking at your page and noticed a quick detail: {core_pain}. This often causes interested clients to drop off before reaching out."

            # 2. Simple Setup Solution
            if service_info.get("key") == "branding":
                solution = (
                    f"At {company_name}, we help businesses elevate their visual presentation to attract higher-tier clients. A few examples:\n"
                    f"👉 {portfolio_url}"
                )
            else:
                solution = (
                    f"At {company_name}, we build clean, fast mobile pages that connect straight to your team on WhatsApp to turn visits into clients. A few examples:\n"
                    f"👉 {portfolio_url}"
                )

        # 3. Provocative Closing Hook
        if cta_channel == "whatsapp":
            cta = "Would it make sense to connect briefly on WhatsApp so I can show you how to fix this?"
        elif cta_channel in ["direct", "chat"]:
            cta = "If you're open to it, just reply right here and I'll show you how to fix this!"
        elif cta_channel == "flexible":
            cta = f"Would it make sense to chat for {dur_label} or exchange a couple of notes here to show you how to fix this?"
        else: # call (default)
            cta = f"Would it make sense to chat for {dur_label} this week so I can show you how to fix this and stop losing those inquiries?"

        message = f"{hook}\n\n{solution}\n\n{cta}"

        # Lightweight follow-up
        if entity_type == "person":
            if cta_channel == "call":
                follow_up = f"Hi {greeting_name}! Just checking in to see if you caught my note above. If you have {dur_label} this week, we can hop on a quick call to walk through fixing that website detail. Cheers!"
            else:
                follow_up = f"Hi {greeting_name}! Just following up in case my note got buried. If you'd like a couple of quick tips right here on chat on how to fix that, happy to help anytime. Have a great week!"
        else:
            if cta_channel == "call":
                follow_up = f"Hi {lead_name} team! Just checking in to see if you caught my note above. If you have {dur_label} this week, we can hop on a quick call to walk through fixing that website detail. Cheers!"
            else:
                follow_up = f"Hi {lead_name} team! Just following up in case my note got buried. If you'd like a couple of quick tips right here on chat on how to fix that, happy to help anytime. Have a great week!"

        warming = f"Engage with {handle}'s active Stories. If a client result is active, send DM as a direct Story reply.\n"

    return {
        "message": message,
        "follow_up": follow_up,
        "warming": warming,
        "portfolio_url": portfolio_url,
        "offered_service": service_info.get("name_pt" if lang == "pt" else ("name_es" if lang == "es" else "name_en"), "Soluções Digitais VCR")
    }

def process_leads_list(raw_input: str, force_lang: str = None, fast_mode: bool = False) -> list:
    candidates = parse_lead_items(raw_input)
    profile = load_profile()
    processed_leads = []

    print(f"🚀 Found {len(candidates)} lead candidate(s). Starting reconnaissance...\n")

    for idx, cand in enumerate(candidates, 1):
        name = cand["name"]
        url = cand["url"]
        handle = cand["handle"] or f"@{name.lower().replace(' ', '')}"
        print(f"[{idx}/{len(candidates)}] Inspecting {name} ({url or handle})...")

        recon = {
            "response_time_ms": None,
            "detected_cms": [],
            "detected_tools": [],
            "friction_points": [],
            "recommended_angle": "Mobile acceleration and 1-tap direct messaging funnel."
        }

        if url and not fast_mode:
            try:
                recon = analyze_url(url, timeout=7)
                if recon.get("detected_name"):
                    name = recon["detected_name"]
                    cand["name"] = name
                    cand["entity_type"] = recon.get("entity_type", cand.get("entity_type", "company"))
            except Exception as e:
                print(f"  ⚠️ Recon error for {url}: {e}")

        # Determine priority tier
        tier = "Tier 2 (Standard)"
        if any("Linktree" in cms or "Beacons" in cms for cms in recon.get("detected_cms", [])) or (recon.get("response_time_ms") and recon["response_time_ms"] > 2000):
            tier = "Tier 1 (High Leakage / Hot)"
        elif not recon.get("has_viewport", True):
            tier = "Tier 1 (High Leakage / Hot)"
        elif not url:
            tier = "Tier 2 (Social-Only / Needs Web)"

        # Universal Niche Detection (Works for ANY industry)
        niche = cand.get("niche")
        title = recon.get("title", "")
        desc = recon.get("description", "")
        combined_meta = f"{cand['name']} {cand.get('handle', '')} {cand.get('raw', '')} {title} {desc}".lower()

        if not niche:
            # Dynamic keyword mapping across diverse industries
            niche_patterns = [
                (["medspa", "aesthetic", "estética", "botox", "skincare", "clinic", "clínica", "dermatol", "rhema", "estheticpalace", "milene"], "Aesthetics & Healthcare"),
                (["dental", "dentist", "odonto", "invisalign", "implante", "veneers", "smile", "moreira", "amanda"], "Cosmetic Dentistry & Oral Health"),
                (["consult", "advisor", "advisory", "coaching", "finance", "wealth", "tax", "contab", "audit", "assessoria", "intercâmbio", "estudant", "medicina no paraguai", "atuar"], "Student & Business Advisory"),
                (["law", "legal", "attorney", "lawyer", "abogad", "advoca", "litigation", "jurídic"], "Legal & Law Practice"),
                (["architec", "arquitet", "arq_", "interior design", "diseño de interiores", "landscape", "urbanis"], "Architecture & Luxury Design"),
                (["real estate", "realtor", "imóve", "bienes raíces", "property", "broker", "penthouse", "condo"], "Luxury Real Estate & Brokerage"),
                (["saas", "software", "tech", "platform", "cloud", "api", "ai ", "data", "app "], "Tech & B2B Software"),
                (["solar", "roofing", "contractor", "construction", "construç", "reforma", "hvac", "plumb", "clean", "limpeza", "limpiez", "tapizados", "higieniz", "housekeeping", "maid", "impecable", "limpiex"], "Home Services & Professional Cleaning"),
                (["agency", "marketing", "branding", "agência", "publicidad", "seo", "media"], "Marketing & Creative Agency"),
                (["restaurant", "catering", "gastronom", "hotel", "resort", "hospitality", "lounge"], "Hospitality & Gastronomy"),
                (["ecommerce", "e-commerce", "retail", "jewelry", "fashion", "moda", "boutique", "shop"], "E-commerce & Luxury Retail"),
                (["fitness", "gym", "crossfit", "personal trainer", "academia", "nutri"], "Fitness, Health & Wellness"),
                (["logistics", "transport", "freight", "supply chain", "logística"], "Logistics & Supply Chain")
            ]

            for keywords, label in niche_patterns:
                if any(k in combined_meta for k in keywords):
                    niche = label
                    break

            # Fallback: extract subtitle or secondary chunk from title if delimited
            if not niche and title and any(sep in title for sep in [" | ", " - ", " : ", " — ", " • "]):
                for sep in [" | ", " - ", " : ", " — ", " • "]:
                    if sep in title:
                        parts = [p.strip() for p in title.split(sep) if len(p.strip()) > 3]
                        if len(parts) > 1:
                            niche = parts[1]
                            break

        if not niche:
            niche = "Serviços & Negócios de Alto Padrão"

        # Determine location dynamically
        location = cand.get("location")
        if not location:
            comb_loc = f"{cand['name']} {cand.get('handle', '')} {cand.get('raw', '')} {title} {desc}".lower()
            if any(k in comb_loc for k in ["cde", "ciudad del este", "del este"]):
                location = "Ciudad del Este, Paraguai"
            elif any(k in comb_loc for k in ["asunción", "asuncion", "moreira"]):
                location = "Asunción, Paraguai"
            elif any(k in comb_loc for k in [".py", "py", "paraguai", "paraguay", "artem", "atuar", "marrone", "milene", "amanda", "estheticpalace", "rhema", "impecable", "limpiex"]):
                location = "Paraguai (PY)"
            elif any(k in comb_loc for k in ["flórida", "florida", "orlando", "miami", "brickell"]):
                location = "Flórida, EUA"
            elif any(k in comb_loc for k in [".br", "são paulo", "rio de janeiro", "brasil", "brazil"]):
                location = "Brasil"
            else:
                location = "US / Global"

        # Language selection
        lang_code, badge = detect_language(cand, recon, force_lang)

        service_info = select_offered_service(cand, recon, niche_str=niche)

        # Bottleneck formulation from specialized service mapping or fallbacks
        bottleneck = service_info.get(f"bottleneck_{lang_code}")
        if not bottleneck:
            if lang_code == "pt":
                bottleneck = "o carregamento mobile ou a ausência de uma página proprietária acaba dispersando potenciais clientes"
            elif lang_code == "es":
                bottleneck = "la velocidad en móvil o la dependencia de enlaces genéricos hace que varios pacientes se dispersen antes de consultar"
            else:
                bottleneck = "the current page takes over 2.5s on mobile or relies on generic links"

        if recon.get("friction_points"):
            bottleneck = recon["friction_points"][0]
            # Clean technical jargon for conversational copy
            if lang_code == "pt":
                bottleneck = bottleneck.replace("Uso de agregador de links genérico (Linktree/Beacons): dispersa atenção e causa até 50% de abandono.", "o uso de agregadores de link dispersa a atenção dos clientes no celular")
                bottleneck = bottleneck.replace("Direcionamento frio para calendário/reserva sem apresentação de autoridade prévia.", "o direcionamento frio direto para agendamento gera abandono antes do contato")
            elif lang_code == "es":
                bottleneck = bottleneck.replace("Uso de agregador de links genérico (Linktree/Beacons): dispersa atenção e causa até 50% de abandono.", "el uso de árboles de enlaces genéricos dispersa la atención de los pacientes")
                bottleneck = bottleneck.replace("Direcionamento frio para calendário/reserva sem apresentação de autoridade prévia.", "dirigir a un calendario frío sin antes presentar autoridad genera alta tasa de abandono")
            else:
                bottleneck = bottleneck.replace("Uso de agregador de links genérico (Linktree/Beacons): dispersa atenção e causa até 50% de abandono.", "relying on a generic link aggregator disperses client attention")
                bottleneck = bottleneck.replace("Direcionamento frio para calendário/reserva sem apresentação de autoridade prévia.", "directing clients straight to a cold booking calendar causes high drop-off")

        # Collect contacts: candidate parsed contacts + recon scraped contacts
        contacts = recon.get("contacts") or {
            "emails": [], "phones": [], "whatsapp": [],
            "socials": {"instagram": [], "linkedin": [], "facebook": [], "google_maps": []}
        }
        if "socials" not in contacts:
            contacts["socials"] = {"instagram": [], "linkedin": [], "facebook": [], "google_maps": []}

        # Merge candidate contacts
        if cand.get("email") and cand["email"] not in contacts["emails"]:
            contacts["emails"].insert(0, cand["email"])
        if cand.get("phone") and cand["phone"] not in contacts["phones"]:
            contacts["phones"].insert(0, cand["phone"])
        if cand.get("ig_url") and cand["ig_url"] not in contacts["socials"].get("instagram", []):
            contacts["socials"].setdefault("instagram", []).insert(0, cand["ig_url"])
        if cand.get("linkedin_url") and cand["linkedin_url"] not in contacts["socials"].get("linkedin", []):
            contacts["socials"].setdefault("linkedin", []).insert(0, cand["linkedin_url"])
        if cand.get("fb_url") and cand["fb_url"] not in contacts["socials"].get("facebook", []):
            contacts["socials"].setdefault("facebook", []).insert(0, cand["fb_url"])
        if cand.get("gmaps_url") and cand["gmaps_url"] not in contacts["socials"].get("google_maps", []):
            contacts["socials"].setdefault("google_maps", []).insert(0, cand["gmaps_url"])

        # Customer Pain diagnosis
        pain = recon.get("pain") or {}
        if not pain or not pain.get("core_pain_pt"):
            pain = {
                "category": service_info.get("name_pt", "Gargalo Digital"),
                "core_pain_pt": bottleneck,
                "core_pain_en": service_info.get("bottleneck_en", "the current page creates friction and inquiry drop-offs"),
                "core_pain_es": service_info.get("bottleneck_es", "la presencia digital actual presenta pérdidas de clientes en el móvil"),
                "friction_points": recon.get("friction_points") or [bottleneck],
                "recommended_solution": service_info.get("name_pt", "Soluções Digitais")
            }

        clean_h = handle.lstrip('@').strip().strip('/')
        if "instagram.com/" in clean_h:
            clean_h = clean_h.split("instagram.com/")[-1].strip().strip('/')
        if "?" in clean_h:
            clean_h = clean_h.split("?")[0]
        ig_link = f"https://www.instagram.com/{clean_h}/"

        gmaps_link = cand.get("gmaps_url") or (contacts["socials"]["google_maps"][0] if contacts["socials"].get("google_maps") else None)
        linkedin_link = cand.get("linkedin_url") or (contacts["socials"]["linkedin"][0] if contacts["socials"].get("linkedin") else None)
        fb_link = cand.get("fb_url") or (contacts["socials"]["facebook"][0] if contacts["socials"].get("facebook") else None)

        lead_dict = {
            "handle": handle,
            "ig_url": ig_link,
            "direct_url": ig_link,
            "name": name,
            "entity_type": cand.get("entity_type", "company"),
            "url": url,
            "source": cand.get("source", "Varredura Outbound"),
            "badge": badge,
            "lang": lang_code,
            "location": location,
            "service": niche,
            "niche": niche,
            "tier": tier,
            "service_info": service_info,
            "offered_service": service_info.get("name_pt" if lang_code == "pt" else ("name_es" if lang_code == "es" else "name_en")),
            "bottleneck": bottleneck,
            "pain": pain,
            "contacts": contacts,
            "whatsapp": contacts.get("whatsapp", []),
            "phones": contacts.get("phones", []),
            "emails": contacts.get("emails", []),
            "gmaps_url": gmaps_link,
            "linkedin_url": linkedin_link,
            "fb_url": fb_link,
            "cms": ", ".join(recon.get("detected_cms", [])) or "Custom",
            "tools": ", ".join(recon.get("detected_tools", [])) or "None detected",
            "latency_ms": recon.get("response_time_ms")
        }

        copy_data = generate_custom_copy(lead_dict, profile, lang_code)
        lead_dict.update(copy_data)
        processed_leads.append(lead_dict)

    return processed_leads

def build_roadmap_markdown(leads: list, profile: dict) -> str:
    agency = profile.get("company_name", "VCR Softwares")
    date_str = datetime.date.today().strftime("%d/%m/%Y")

    md = []
    md.append(f"# 🗺️ Roadmap de Execução Outbound & Plano de Prospecção")
    md.append(f"**Operador da Campanha:** `{agency}` | **Data:** `{date_str}` | **Total de Leads:** `{len(leads)}`\n")

    md.append("## 📊 1. Matriz de Priorização & Alocação de Serviços VCR")
    md.append("| # | Lead / Perfil | Nicho / Segmento | Serviço Recomendado VCR | Prioridade (Tier) | Idioma | Gargalo / Oportunidade |")
    md.append("| :-: | :--- | :--- | :--- | :-: | :-: | :--- |")
    for i, lead in enumerate(leads, 1):
        serv = lead.get("offered_service", "Soluções Digitais")
        md.append(f"| {i} | **{lead['name']}** (`{lead['handle']}`) | {lead['niche']} | **{serv}** | `{lead['tier']}` | {lead['badge']} | {lead['bottleneck'][:60]}... |")
    md.append("")

    md.append("## 📅 2. Cronograma de Cadência de Abordagem Multicanal")
    md.append("```text")
    md.append("┌────────────────────────────────────────────────────────────────────────┐")
    md.append("│ DIA 1: Aquecimento & Mensagem Curta de Abordagem                       │")
    md.append("│  • Curtir 2 posts recentes + visualizar Stories ativos (últimas 24h)   │")
    md.append("│  • Enviar DM/Mensagem com Hook da Dor + Solução VCR + Pergunta p/ Call │")
    md.append("│  • Estratégia: Quebra de padrão rápida mostrando a dor e a solução    │")
    md.append("├────────────────────────────────────────────────────────────────────────┤")
    md.append("│ DIA 4: Follow-up Assíncrono                                            │")
    md.append("│  • Verificar visualização. Se sem resposta: lembrete curto com valor   │")
    md.append("│  • Reforço do convite para papo rápido sobre o gargalo identificado   │")
    md.append("├────────────────────────────────────────────────────────────────────────┤")
    md.append("│ DIA 7: Fechamento / Agendamento da Call                                │")
    md.append("│  • Entrega de 2 pontos de melhoria e confirmação da call ou WhatsApp  │")
    md.append("└────────────────────────────────────────────────────────────────────────┘")
    md.append("```\n")

    md.append("## 🎯 3. Fichas dos Leads & Roteiros Prontos para Copiar e Colar\n")
    for i, lead in enumerate(leads, 1):
        clean_h = lead['handle'].lstrip('@').strip().strip('/')
        if "instagram.com/" in clean_h:
            clean_h = clean_h.split("instagram.com/")[-1].strip().strip('/')
        if "?" in clean_h:
            clean_h = clean_h.split("?")[0]
        ig_link = f"https://www.instagram.com/{clean_h}/"

        pain = lead.get("pain") or {}
        pain_cat = pain.get("category") or "Gargalo Digital"
        pain_core = pain.get("core_pain_pt" if lead.get("lang") == "pt" else ("core_pain_es" if lead.get("lang") == "es" else "core_pain_en")) or lead.get("bottleneck", "N/D")
        pain_sol = pain.get("recommended_solution") or lead.get("offered_service", "Soluções Digitais")

        # Contact channels
        contact_items = []
        if lead.get("whatsapp"):
            for w in lead["whatsapp"][:2]:
                contact_items.append(f"[📱 WhatsApp]({w})")
        if lead.get("phones"):
            for p in lead["phones"][:2]:
                contact_items.append(f"[📞 {p}](tel:{p.replace(' ', '')})")
        if lead.get("emails"):
            for em in lead["emails"][:2]:
                contact_items.append(f"[✉️ {em}](mailto:{em})")
        if lead.get("gmaps_url"):
            contact_items.append(f"[📍 Google Maps]({lead['gmaps_url']})")
        if lead.get("linkedin_url"):
            contact_items.append(f"[💼 LinkedIn]({lead['linkedin_url']})")
        if lead.get("fb_url"):
            contact_items.append(f"[📘 Facebook]({lead['fb_url']})")

        contacts_str = " | ".join(contact_items) if contact_items else "Redes Sociais / Direct"

        md.append(f"### Lead #{i}: {lead['name']} ({lead['badge']})")
        md.append(f"- **Origem do Lead:** `{lead.get('source', 'Varredura Outbound')}`")
        md.append(f"- **Handle / Perfil:** [{lead['handle']}]({ig_link}) | [📸 Abrir Instagram]({ig_link})")
        if lead.get("url"):
            md.append(f"- **Website:** [{lead['url']}]({lead['url']}) (Latência: `{lead.get('latency_ms', 'N/D')}ms` | Stack: `{lead['cms']}`)")
        md.append(f"- **Canais de Contato Mapeados:** {contacts_str}")
        md.append(f"- **Serviço Recomendado:** **{lead.get('offered_service', 'Soluções Digitais')}**")
        md.append(f"- **Nível de Prioridade:** `{lead['tier']}`")
        md.append(f"- **⚠️ Dor Central Diagnosticada ({pain_cat}):** {pain_core}")
        md.append(f"- **💡 Solução Ofertada:** {pain_sol}")
        md.append(f"- **🎯 Estratégia de Atenção / Aquecimento:** {lead['warming']}")
        md.append("")
        md.append(f"**💬 Mensagem Curta de Abordagem (Dia 1):**")
        md.append("```text")
        md.append(lead["message"])
        md.append("```")
        md.append(f"**🔁 Follow-Up Assíncrono (Dia 4):**")
        md.append("```text")
        md.append(lead["follow_up"])
        md.append("```")
        md.append("---\n")

    return "\n".join(md)

def build_trello_markdown(leads: list, profile: dict) -> str:
    agency = profile.get("company_name", "VCR Softwares")
    date_str = datetime.date.today().strftime("%d/%m/%Y")

    lines = []
    lines.append(f"# 📋 Exportação Trello — Prospecção Outbound ({agency})")
    lines.append(f"**Data de Geração:** `{date_str}` | **Total de Leads:** `{len(leads)}`\n")

    lines.append("> 💡 **Instruções de Importação para o Trello:**")
    lines.append(f"> 1. **Criação Rápida em Lote:** Copie a lista da **Seção 1** e cole em qualquer lista do seu quadro no Trello (ex: *'A Fazer / Dia 1'*). O Trello perguntará se deseja criar {len(leads)} cartões individuais. Clique em **Sim**.")
    lines.append("> 2. **Preenchimento dos Cartões:** Abra cada cartão e cole o texto correspondente da **Seção 2** na descrição.")
    lines.append("> 3. **Importação via CSV:** Se preferir importar automaticamente com colunas e etiquetas, utilize o arquivo `*-trello.csv` com o Power-Up de importação CSV do Trello.\n")

    lines.append("## ⚡ Seção 1: Lista para Criação Rápida em Lote (Copie e Cole na Lista do Trello)")
    lines.append("```text")
    for lead in leads:
        clean_h = lead['handle'].lstrip('@')
        badge = lead.get('badge', 'ENG')
        tier_raw = lead.get('tier', 'Tier 2')
        tier = "Tier 1" if "Tier 1" in str(tier_raw) else "Tier 2"
        loc_short = (lead.get('location') or 'Global').split(',')[0].strip()
        lines.append(f"[{badge} | {tier}] {lead['name']} (@{clean_h}) - {loc_short}")
    lines.append("```\n")

    lines.append("---")
    lines.append("## 🗂️ Seção 2: Conteúdo Formatado para a Descrição de Cada Cartão\n")

    for i, lead in enumerate(leads, 1):
        clean_h = lead['handle'].lstrip('@').strip().strip('/')
        if "instagram.com/" in clean_h:
            clean_h = clean_h.split("instagram.com/")[-1].strip().strip('/')
        if "?" in clean_h:
            clean_h = clean_h.split("?")[0]
        badge = lead.get('badge', 'ENG')
        tier_raw = lead.get('tier', 'Tier 2')
        tier_short = "Tier 1" if "Tier 1" in str(tier_raw) else "Tier 2"
        ig_link = f"https://www.instagram.com/{clean_h}/"
        serv = lead.get('offered_service', 'Soluções Digitais VCR')
        location = lead.get('location', 'N/D')

        card_title = f"[{badge} | {tier_short}] {lead['name']} (@{clean_h}) - {location}"

        pain = lead.get("pain") or {}
        pain_cat = pain.get("category") or "Gargalo de Conversão"
        pain_core = pain.get("core_pain_pt" if lead.get("lang") == "pt" else ("core_pain_es" if lead.get("lang") == "es" else "core_pain_en")) or lead.get("bottleneck", "N/D")
        pain_sol = pain.get("recommended_solution") or lead.get("offered_service", "Soluções Digitais")
        call_dur = profile.get("call_duration") or "10 a 15 minutos"

        contact_lines = []
        if lead.get("whatsapp"):
            for w in lead["whatsapp"][:2]:
                contact_lines.append(f"* **WhatsApp:** {w}")
        if lead.get("phones"):
            for p in lead["phones"][:2]:
                contact_lines.append(f"* **Telefone:** {p}")
        if lead.get("emails"):
            for em in lead["emails"][:2]:
                contact_lines.append(f"* **E-mail:** {em}")
        if lead.get("gmaps_url"):
            contact_lines.append(f"* **Google Maps / Business:** {lead['gmaps_url']}")
        if lead.get("linkedin_url"):
            contact_lines.append(f"* **LinkedIn:** {lead['linkedin_url']}")
        if lead.get("fb_url"):
            contact_lines.append(f"* **Facebook:** {lead['fb_url']}")
        contacts_block = "\n".join(contact_lines) if contact_lines else "* Redes Sociais / Direct"

        lines.append(f"### Cartão #{i}: {lead['name']}")
        lines.append(f"**Título Sugerido:** `{card_title}`")
        lines.append(f"**Etiquetas Sugeridas:** `{badge}`, `{tier_short}`, `{serv}`\n")
        lines.append("**Texto para a Descrição do Cartão (Copiar abaixo):**")
        lines.append("```markdown")
        lines.append(f"### 🏢 Informações do Lead")
        lines.append(f"* **Empresa / Especialista:** {lead['name']}")
        lines.append(f"* **Canal de Origem:** {lead.get('source', 'Varredura Outbound')}")
        lines.append(f"* **Instagram:** {ig_link}")
        if lead.get("url"):
            lines.append(f"* **Website Oficial:** {lead['url']}")
        lines.append(f"* **Localização:** {location}")
        lines.append(f"* **Nicho / Segmento:** {lead.get('niche', 'N/D')}")
        lines.append(f"* **Serviço Recomendado:** {serv}")
        lines.append("")
        lines.append(f"### 📞 Canais de Contato Mapeados")
        lines.append(contacts_block)
        lines.append("")
        lines.append(f"### ⚠️ Dor Central Diagnosticada ({pain_cat})")
        lines.append(f"> {pain_core}")
        lines.append("")
        lines.append(f"### 💡 Solução Ofertada")
        lines.append(f"> {pain_sol}")
        lines.append("")
        lines.append(f"### 🎯 Estratégia de Aquecimento (Dia 1)")
        lines.append(f"> {lead.get('warming', 'Visualizar Stories e curtir posts recentes.')}")
        lines.append("")
        lines.append(f"### 💬 Mensagem de Abordagem (Dia 1)")
        lines.append(lead['message'])
        lines.append("")
        lines.append(f"### 🔁 Follow-up Assíncrono (Dia 4)")
        lines.append(lead['follow_up'])
        lines.append("")
        lines.append(f"### 📋 Checklist de Execução do Card")
        lines.append(f"- [ ] **Dia 1:** Curtir 2 posts recentes e assistir aos Stories")
        lines.append(f"- [ ] **Dia 1:** Enviar mensagem de abordagem com Hook da Dor")
        lines.append(f"- [ ] **Dia 4:** Enviar Follow-up assíncrono (se sem resposta)")
        lines.append(f"- [ ] **Dia 7:** Reforço do convite para Call de {call_dur} / Canal direto")
        lines.append(f"- [ ] **Fechamento:** Call realizada / Proposta aceita")
        lines.append("```\n")
        lines.append("---\n")

    return "\n".join(lines)

def build_trello_csv(leads: list, profile: dict) -> str:
    import io
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)
    writer.writerow(["Card Name", "Card Description", "Labels", "List Name"])

    call_dur = profile.get("call_duration") or "10 a 15 minutos"

    for lead in leads:
        clean_h = lead['handle'].lstrip('@').strip().strip('/')
        if "instagram.com/" in clean_h:
            clean_h = clean_h.split("instagram.com/")[-1].strip().strip('/')
        if "?" in clean_h:
            clean_h = clean_h.split("?")[0]
        badge = lead.get('badge', 'ENG')
        tier_raw = lead.get('tier', 'Tier 2')
        tier_short = "Tier 1" if "Tier 1" in str(tier_raw) else "Tier 2"
        ig_link = f"https://www.instagram.com/{clean_h}/"
        serv = lead.get('offered_service', 'Soluções Digitais VCR')
        location = lead.get('location', 'N/D')

        pain = lead.get("pain") or {}
        pain_cat = pain.get("category") or "Gargalo de Conversão"
        pain_core = pain.get("core_pain_pt" if lead.get("lang") == "pt" else ("core_pain_es" if lead.get("lang") == "es" else "core_pain_en")) or lead.get("bottleneck", "N/D")
        pain_sol = pain.get("recommended_solution") or lead.get("offered_service", "Soluções Digitais")

        title = f"[{badge} | {tier_short}] {lead['name']} (@{clean_h}) - {location}"

        contact_lines = []
        if lead.get("whatsapp"):
            for w in lead["whatsapp"][:2]:
                contact_lines.append(f"* WhatsApp: {w}")
        if lead.get("phones"):
            for p in lead["phones"][:2]:
                contact_lines.append(f"* Telefone: {p}")
        if lead.get("emails"):
            for em in lead["emails"][:2]:
                contact_lines.append(f"* E-mail: {em}")
        if lead.get("gmaps_url"):
            contact_lines.append(f"* Google Maps: {lead['gmaps_url']}")
        if lead.get("linkedin_url"):
            contact_lines.append(f"* LinkedIn: {lead['linkedin_url']}")
        if lead.get("fb_url"):
            contact_lines.append(f"* Facebook: {lead['fb_url']}")
        contacts_csv = "\n".join(contact_lines) if contact_lines else "* Redes Sociais / Direct"

        desc_parts = [
            f"### 🏢 Informações do Lead",
            f"* **Empresa / Especialista:** {lead['name']}",
            f"* **Canal de Origem:** {lead.get('source', 'Varredura Outbound')}",
            f"* **Instagram:** {ig_link}",
        ]
        if lead.get("url"):
            desc_parts.append(f"* **Website:** {lead['url']}")
        desc_parts.extend([
            f"* **Localização:** {location}",
            f"* **Nicho:** {lead.get('niche', 'N/D')}",
            f"* **Serviço Recomendado:** {serv}",
            f"",
            f"### 📞 Canais de Contato Mapeados",
            contacts_csv,
            f"",
            f"### ⚠️ Dor Central Diagnosticada ({pain_cat})",
            f"> {pain_core}",
            f"",
            f"### 💡 Solução Ofertada",
            f"> {pain_sol}",
            f"",
            f"### 🎯 Estratégia de Aquecimento (Dia 1)",
            f"> {lead.get('warming', 'Visualizar Stories e curtir posts recentes.')}",
            f"",
            f"### 💬 Mensagem de Abordagem (Dia 1)",
            lead['message'],
            f"",
            f"### 🔁 Follow-up (Dia 4)",
            lead['follow_up'],
            f"",
            f"### 📋 Checklist de Cadência",
            f"- [ ] Dia 1: Aquecimento & Mensagem com Hook da Dor",
            f"- [ ] Dia 4: Follow-up enviado",
            f"- [ ] Dia 7: Reforço convite para Call ({call_dur})",
            f"- [ ] Fechamento: Call realizada / Proposta aceita"
        ])
        description = "\n".join(desc_parts)
        labels = f"{badge},{tier_short},{serv}"
        list_name = "A Fazer / Dia 1 (Outbound)"

        writer.writerow([title, description, labels, list_name])

    return output.getvalue()

def main():
    parser = argparse.ArgumentParser(description="Processador de listas de leads & gerador de roadmap de abordagem.")
    parser.add_argument("--file", "-f", help="Caminho do arquivo com os leads (PDF, TXT, MD, CSV, JSON).")
    parser.add_argument("--input", "-i", help="Lista direta de leads/URLs em texto.")
    parser.add_argument("--output", "-o", default="outreach_roadmap.md", help="Caminho do arquivo de saída (se terminar em .pdf, gera o PDF executivo).")
    parser.add_argument("--json", help="Caminho para exportar o JSON estruturado dos leads.")
    parser.add_argument("--pdf", help="Caminho do dossiê executivo A4 em PDF.")
    parser.add_argument("--lang", choices=["en", "es", "pt"], help="Forçar idioma específico para todas as mensagens.")
    parser.add_argument("--fast", action="store_true", help="Modo rápido: pula testes HTTP de latência ao vivo.")
    args = parser.parse_args()

    raw_text = ""
    if args.file:
        print(f"Lendo leads do arquivo: {args.file}...")
        raw_text = extract_text_from_file(args.file)
    elif args.input:
        raw_text = args.input
    elif not sys.stdin.isatty():
        raw_text = sys.stdin.read()
    else:
        print("Erro: Forneça um arquivo (--file caminho) ou entrada direta (--input '...')")
        sys.exit(1)

    if not raw_text.strip():
        print("Erro: O arquivo ou texto de entrada está vazio.")
        sys.exit(1)

    profile = load_profile()
    if not is_profile_configured(profile):
        print("==================================================================")
        print("  ⚠️  SETUP DO PERFIL NECESSÁRIO — LEAD APPROACH")
        print("==================================================================")
        print("Nenhum perfil de negócio configurado em config/profile.json.")
        print("Cada setup é único e exclusivo para sua marca/empresa.")
        print("Não existe configuração padrão predefinida.\n")
        print("👉 Para configurar interativamente agora, execute:")
        print("   python3 scripts/setup_profile.py\n")
        print("👉 Ou configure diretamente com seus dados:")
        print("   python3 scripts/setup_profile.py --name \"Sua Marca\" --service \"Seu Serviço\" --tone consultivo ...\n")
        sys.exit(1)

    leads = process_leads_list(raw_text, force_lang=args.lang, fast_mode=args.fast)
    if not leads:
        print("Aviso: Nenhum lead ou URL válido pôde ser processado.")
        sys.exit(0)

    profile = load_profile()
    roadmap_md = build_roadmap_markdown(leads, profile)

    # Determina o diretório de destino baseado no padrão: report/<nome-do-report>-<data>/
    date_str = datetime.date.today().strftime("%Y-%m-%d")

    # Extrai o nome base
    raw_output = args.output
    base_name = os.path.basename(raw_output)
    stem, ext = os.path.splitext(base_name)
    if not stem:
        stem = "outreach_roadmap"

    folder_name = f"{stem}-{date_str}"

    # Se o output fornecido já possui um diretório explícito dentro de report, preserva;
    # caso contrário, garante que os arquivos fiquem em report/<nome-do-report>-<data>/
    raw_dir = os.path.dirname(raw_output)
    if "report" in raw_dir.split(os.sep) or "reports" in raw_dir.split(os.sep):
        target_dir = raw_dir
    else:
        target_dir = os.path.join("report", folder_name)

    os.makedirs(target_dir, exist_ok=True)

    # Copia o arquivo fonte para dentro da pasta do report para preservar os dados originais
    if args.file and os.path.isfile(args.file):
        try:
            dest_source = os.path.join(target_dir, os.path.basename(args.file))
            if os.path.abspath(args.file) != os.path.abspath(dest_source):
                shutil.copy2(args.file, dest_source)
        except Exception:
            pass

    md_target = os.path.join(target_dir, f"{stem}.md")
    pdf_target = os.path.join(target_dir, f"{stem}.pdf") if (args.pdf or raw_output.lower().endswith(".pdf")) else None
    html_target = os.path.join(target_dir, f"{stem}.html")
    trello_md_target = os.path.join(target_dir, f"{stem}-trello.md")
    trello_csv_target = os.path.join(target_dir, f"{stem}-trello.csv")
    trello_json_target = os.path.join(target_dir, f"{stem}-trello.json")

    # 1. Salva o Roadmap Markdown
    with open(md_target, "w", encoding="utf-8") as f:
        f.write(roadmap_md)
    print(f"\n✅ Roadmap Markdown salvo em: {md_target}")

    # 2. Salva a Versão Formatada para o Trello (Markdown e CSV)
    trello_md = build_trello_markdown(leads, profile)
    with open(trello_md_target, "w", encoding="utf-8") as f:
        f.write(trello_md)
    print(f"📋 Versão Trello Markdown salva em: {trello_md_target}")

    trello_csv = build_trello_csv(leads, profile)
    with open(trello_csv_target, "w", encoding="utf-8") as f:
        f.write(trello_csv)
    print(f"📊 Versão Trello CSV salva em: {trello_csv_target}")

    # 3. Salva Trello JSON estruturado
    trello_cards_data = []
    for lead in leads:
        clean_h = lead['handle'].lstrip('@').strip().strip('/')
        if "instagram.com/" in clean_h:
            clean_h = clean_h.split("instagram.com/")[-1].strip().strip('/')
        if "?" in clean_h:
            clean_h = clean_h.split("?")[0]
        badge = lead.get('badge', 'ENG')
        tier_raw = lead.get('tier', 'Tier 2')
        tier = "Tier 1" if "Tier 1" in str(tier_raw) else "Tier 2"
        serv = lead.get('offered_service', 'Soluções Digitais VCR')
        ig_link = f"https://www.instagram.com/{clean_h}/"
        pain = lead.get("pain") or {}
        trello_cards_data.append({
            "name": f"[{badge} | {tier}] {lead['name']} (@{clean_h}) - {lead.get('location', 'Global')}",
            "labels": [badge, tier, serv],
            "lead_name": lead['name'],
            "handle": lead['handle'],
            "source": lead.get("source", "Varredura Outbound"),
            "ig_url": ig_link,
            "direct_url": ig_link,
            "web_url": lead.get("url"),
            "gmaps_url": lead.get("gmaps_url"),
            "linkedin_url": lead.get("linkedin_url"),
            "fb_url": lead.get("fb_url"),
            "whatsapp": lead.get("whatsapp", []),
            "phones": lead.get("phones", []),
            "emails": lead.get("emails", []),
            "contacts": lead.get("contacts", {}),
            "location": lead.get("location"),
            "niche": lead.get("niche"),
            "service": serv,
            "pain": pain,
            "bottleneck": lead.get("bottleneck"),
            "message": lead["message"],
            "follow_up": lead["follow_up"]
        })
    with open(trello_json_target, "w", encoding="utf-8") as f:
        json.dump(trello_cards_data, f, indent=2, ensure_ascii=False)
    print(f"📁 Versão Trello JSON salva em: {trello_json_target}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(leads, f, indent=2, ensure_ascii=False)
        print(f"📁 Dados JSON gerais salvos em: {args.json}")

    # 4. Gera HTML Interativo e PDF se solicitado
    if pdf_target or raw_output.lower().endswith(".pdf"):
        print(f"Compilando Dossiê Executivo A4 em PDF...")
        detected_market = "Paraguai (Ciudad del Este & Asunción)" if any("paraguai" in (l.get("location") or "").lower() or "py" in (l.get("location") or "").lower() for l in leads) else "Brasil, Flórida (EUA) & Internacional"
        report_data = {
            "title": f"Dossiê Executivo & Roadmap de Prospecção — {profile.get('company_name', 'VCR Softwares')}",
            "subtitle": f"Alocação de Serviços VCR ({len(leads)} Leads Mapeados)",
            "agency": profile.get("company_name", "VCR Softwares"),
            "market": detected_market,
            "date": datetime.date.today().strftime("%d/%m/%Y"),
            "leads": leads
        }
        html_code = build_report_html(report_data)
        with open(html_target, "w", encoding="utf-8") as f:
            f.write(html_code)
        compile_pdf(html_target, pdf_target)
        print(f"🌐 Versão Web Interativa (com botões de cópia em 1 clique) mantida em: {html_target}")

if __name__ == "__main__":
    main()

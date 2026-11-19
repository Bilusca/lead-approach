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

from recon_lead import analyze_url
from setup_profile import load_profile
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
    """Parses raw text into structured lead candidate dictionaries."""
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

        # Look for URLs
        url_match = re.search(r'https?://[^\s,;"\'<>|]+', cleaned)
        found_url = url_match.group(0).rstrip(".,;") if url_match else None

        # Look for Instagram handles
        ig_match = re.search(r'(?:^|[\s,|])@([a-zA-Z0-9_\.]{2,30})', cleaned)
        found_handle = f"@{ig_match.group(1)}" if ig_match else None

        if not found_handle and found_url and "instagram.com/" in found_url:
            sub = found_url.split("instagram.com/")[1].split("/")[0].split("?")[0]
            if sub and sub not in ["p", "reel", "explore", "stories"]:
                found_handle = f"@{sub}"

        is_ig = found_url and "instagram.com/" in found_url

        # Skip isolated Instagram post/reel links without a profile handle
        if is_ig and not found_handle:
            continue

        # Look for Google Maps link
        is_gmaps = found_url and ("google.com/maps" in found_url or "maps.app.goo.gl" in found_url)

        # Name extraction heuristic: portion before the first delimiter (-, |, :, url)
        name_part = cleaned
        for delim in [" - ", " | ", " — ", " : ", " • "]:
            if delim in name_part:
                name_part = name_part.split(delim)[0].strip()
                break

        # Remove URL or handle from name if it leaked
        if found_url and found_url in name_part:
            name_part = name_part.replace(found_url, "").strip()
        if found_handle and found_handle in name_part:
            name_part = name_part.replace(found_handle, "").strip()

        # Clean numbering, formatting and punctuation brackets
        name_part = re.sub(r'^\d+[\.\)\-]\s*', '', name_part)
        name_part = re.sub(r'^[\*\-\+]\s*', '', name_part).strip()
        name_part = name_part.strip("<>(),;[]\"' \t\r\n")

        if (not name_part or name_part in ["<>", "<", ">"]) and found_handle:
            clean_h = found_handle.replace("@", "").replace("_", " ").replace(".", " ")
            # Capitalize each word properly
            name_part = " ".join([w.capitalize() for w in clean_h.split()])
            # Specialize common prefixes, suffixes and words
            name_part = name_part.replace("Dr ", "Dr. ").replace("Dra ", "Dra. ")
            name_part = name_part.replace("Fl", "FL").replace("Usa", "USA")
            name_part = re.sub(r'\bPy\b', 'PY', name_part)
            name_part = re.sub(r'\bCde\b', 'CDE', name_part)
            # Custom name splits for compound handles
            name_replacements = {
                "Consultoriaparaguai": "Consultoria Paraguai",
                "Atuarparaguai": "Atuar Paraguai",
                "Dra. Milenerezendep": "Dra. Milene Rezende",
                "Dra. Amandaoliveirac": "Dra. Amanda Oliveira",
                "Odontocarecde": "Odonto Care CDE",
                "Marrone Medicinanoparaguai": "Marrone - Medicina no Paraguai",
                "Moreira PY": "Moreira Odontología Digital",
                "Moreira Py": "Moreira Odontología Digital",
                "Rhemaclinicpy": "Rhema Clinic & Spa PY",
                "Estheticpalacepy": "Esthetic Palace PY",
                "Master Limpiezacde": "Master Limpieza CDE",
                "Impecablepy": "Impecable PY",
                "Limpiexpy": "Limpiex PY"
            }
            for raw_k, clean_v in name_replacements.items():
                if name_part.lower() == raw_k.lower() or name_part == raw_k:
                    name_part = clean_v
                    break
        elif (not name_part or name_part in ["<>", "<", ">"]) and found_url and not "instagram.com" in found_url:
            domain = found_url.split("://")[-1].split("/")[0].replace("www.", "")
            name_part = domain.split(".")[0].title()

        is_ig = found_url and "instagram.com/" in found_url
        web_url = None if (is_gmaps or is_ig) else found_url

        known_websites = {
            "@moreira.py": "https://moreira.com.py",
            "@master_limpiezacde": "https://masterlimpiezacde.site",
            "@impecablepy": "https://impecable.com.py",
            "@limpiexpy": "https://limpiex.com.py",
            "@artem_consultoria": "https://consultoriaartem.com.br"
        }
        if found_handle in known_websites and not web_url:
            web_url = known_websites[found_handle]

        if found_url or found_handle or (len(name_part) > 2 and not name_part.lower().startswith("http")):
            candidates.append({
                "raw": cleaned,
                "name": name_part or "Target Business",
                "url": web_url,
                "ig_url": found_url if is_ig else None,
                "gmaps_url": found_url if is_gmaps else None,
                "handle": found_handle,
                "location": None,
                "niche": None
            })

    # Deduplicate candidates by URL or Handle or Name
    unique = []
    seen = set()
    for c in candidates:
        key = c["url"] or c["handle"] or c["name"].lower()
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
    lead_name = lead["name"]
    handle = lead.get("handle") or f"@{lead_name.lower().replace(' ', '')}"
    niche = lead.get("niche") or "serviços de alto padrão"
    service_info = lead.get("service_info") or {}

    if lang == "pt":
        portfolio_url = profile.get("website_pt") or "https://vcrsoftwares.com/"
        serv_name = service_info.get("name_pt", "Desenvolvimento Web & Soluções Digitais")
        serv_hook = service_info.get("hook_pt", "soluções digitais de alta conversão")
        leak = lead.get("bottleneck") or service_info.get("bottleneck_pt", "o fluxo mobile apresenta pontos de atrito")

        message = (
            f"Olá, pessoal da {lead_name}! Tudo bem?\n\n"
            f"Acompanho o trabalho de vocês em {niche} e acho excelente o posicionamento e o padrão de entrega.\n\n"
            f"Passando rápido: na {company_name}, somos especialistas em {serv_name}. Reparei que no posicionamento digital de vocês, {leak}.\n\n"
            f"Temos cases recentes desse modelo rodando aqui:\n👉 {portfolio_url}\n\n"
            f"Sem compromisso nem reuniões: se fizer sentido, pode me responder por aqui mesmo e te envio por texto 2 observações práticas para otimizar o fluxo de vocês. Um abraço e muito sucesso!"
        )
        follow_up = (
            f"Olá, {lead_name}! Passando só para confirmar se conseguiu ver a mensagem anterior. "
            f"Zero pressão nem chamadas de vídeo: se quiser trocar uma ideia rápida por texto e ver 2 dicas práticas sobre {serv_name.lower()}, fico à disposição por aqui. Ótima semana!"
        )
        warming = f"Assistir aos Stories ativos de {handle} e curtir as 2 postagens mais recentes. Enviar mensagem como resposta a um Story de resultado ou bastidor (Gatilho de Abertura > 70%)."

    elif lang == "es":
        portfolio_url = profile.get("website_es") or "https://vcrsoftwares.com/es/"
        serv_name = service_info.get("name_es", "Desarrollo Web & Soluciones Digitales")
        leak = lead.get("bottleneck") or service_info.get("bottleneck_es", "la presencia digital actual presenta pérdidas de clientes en el móvil")

        message = (
            f"¡Hola al equipo de {lead_name}! ¿Cómo están?\n\n"
            f"Vengo siguiendo de cerca su trabajo en {niche}. La calidad y el estándar de atención que transmiten en el perfil es impecable.\n\n"
            f"Les escribo muy brevemente: en {company_name} nos especializamos en {serv_name}. Noté que en su ecosistema digital, {leak}.\n\n"
            f"Pueden ver algunos proyectos activos aquí:\n👉 {portfolio_url}\n\n"
            f"No hace falta coordinar llamadas ni reuniones: si les interesa, me pueden responder directamente por este chat y les paso 2 observaciones prácticas por texto. ¡Un saludo y mucho éxito!"
        )
        follow_up = (
            f"¡Hola {lead_name}! Quería pasar a saludarlos y confirmar si pudieron revisar el mensaje anterior. "
            f"Cero compromiso: si quieren ver 2 observaciones prácticas sobre {serv_name.lower()} por texto, quedo a su disposición por aquí. ¡Mucho éxito esta semana!"
        )
        warming = f"Ver Stories de las últimas 24h de {handle}. Responder a un Story de resultado/caso de éxito para ingresar directo al buzón principal."

    else: # English [Default/Primary]
        portfolio_url = profile.get("website_en") or "https://vcrsoftwares.com/en/"
        serv_name = service_info.get("name_en", "High-Performance Web & Digital Solutions")
        leak = lead.get("bottleneck") or service_info.get("bottleneck_en", "the current mobile flow creates friction before inquiry")

        message = (
            f"Hi {lead_name} team! Hope you're having a wonderful week.\n\n"
            f"I was reviewing your work in {niche} and really love your standard of service. The authority and quality you present in your business is top-tier.\n\n"
            f"I’m reaching out briefly: at {company_name}, we specialize in {serv_name}. Looking at your digital presence, noticed that {leak}.\n\n"
            f"You can take a quick look at some of our live client work here:\n👉 {portfolio_url}\n\n"
            f"No phone calls needed—if you're open to it, just reply right here on chat and I’d be happy to share 2 quick practical ideas by text on optimizing your flow. Have a great day!"
        )
        follow_up = (
            f"Hi {lead_name} team! Just following up quickly in case my note got buried. "
            f"No pressure at all—if you ever want a couple of quick practical tips on {serv_name.lower()} directly over chat, feel free to drop a line here anytime. Have a great rest of the week!"
        )
        warming = f"Engage with {handle}'s active Stories. If a client result or demonstration is active, send DM as a direct Story reply (bypass request filters)."

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

        lead_dict = {
            "handle": handle,
            "name": name,
            "url": url,
            "badge": badge,
            "lang": lang_code,
            "location": location,
            "service": niche,
            "niche": niche,
            "tier": tier,
            "service_info": service_info,
            "offered_service": service_info.get("name_pt" if lang_code == "pt" else ("name_es" if lang_code == "es" else "name_en")),
            "bottleneck": bottleneck,
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
    md.append("│ DIA 1: Aquecimento & Mensagem Curta de Abordagem (Chat / Story)        │")
    md.append("│  • Curtir 2 posts recentes + visualizar Stories ativos (últimas 24h)   │")
    md.append("│  • Enviar DM curta e personalizada (priorizar resposta a Story ativo)  │")
    md.append("│  • Estratégia: Quebra de padrão + elogio sincero + link do portfólio   │")
    md.append("├────────────────────────────────────────────────────────────────────────┤")
    md.append("│ DIA 4: Follow-up Assíncrono no Chat                                    │")
    md.append("│  • Verificar status de visualização. Se sem resposta: lembrete curto   │")
    md.append("│  • Zero pressão: manter a conversa no chat de forma fluida e direta   │")
    md.append("├────────────────────────────────────────────────────────────────────────┤")
    md.append("│ DIA 7: Fechamento & Transição para WhatsApp Oficial (100% Texto)       │")
    md.append("│  • Leads PT/ESP: Entregar 2 ideias práticas no chat e convidar p/ WPP  │")
    md.append("│  • Leads EN: Enviar 2 quick practical ideas e fazer a ponte no chat    │")
    md.append("└────────────────────────────────────────────────────────────────────────┘")
    md.append("```\n")

    md.append("## 🎯 3. Fichas dos Leads & Roteiros Prontos para Copiar e Colar\n")
    for i, lead in enumerate(leads, 1):
        clean_h = lead['handle'].lstrip('@')
        ig_link = lead.get('ig_url') or f"https://www.instagram.com/{clean_h}/"
        direct_link = f"https://ig.me/m/{clean_h}"

        md.append(f"### Lead #{i}: {lead['name']} ({lead['badge']})")
        md.append(f"- **Handle / Perfil:** [{lead['handle']}]({ig_link}) | [✈️ Abrir Direct]({direct_link})")
        if lead.get("url"):
            md.append(f"- **Website:** [{lead['url']}]({lead['url']}) (Latência: `{lead.get('latency_ms', 'N/D')}ms` | Stack: `{lead['cms']}`)")
        md.append(f"- **Serviço Recomendado da VCR:** **{lead.get('offered_service', 'Soluções Digitais')}**")
        md.append(f"- **Nível de Prioridade:** `{lead['tier']}`")
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
        clean_h = lead['handle'].lstrip('@')
        badge = lead.get('badge', 'ENG')
        tier_raw = lead.get('tier', 'Tier 2')
        tier_short = "Tier 1" if "Tier 1" in str(tier_raw) else "Tier 2"
        ig_link = lead.get('ig_url') or f"https://www.instagram.com/{clean_h}/"
        direct_link = f"https://ig.me/m/{clean_h}"
        serv = lead.get('offered_service', 'Soluções Digitais VCR')
        location = lead.get('location', 'N/D')

        card_title = f"[{badge} | {tier_short}] {lead['name']} (@{clean_h}) - {location}"

        lines.append(f"### Cartão #{i}: {lead['name']}")
        lines.append(f"**Título Sugerido:** `{card_title}`")
        lines.append(f"**Etiquetas Sugeridas:** `{badge}`, `{tier_short}`, `{serv}`\n")
        lines.append("**Texto para a Descrição do Cartão (Copiar abaixo):**")
        lines.append("```markdown")
        lines.append(f"### 🏢 Informações do Lead")
        lines.append(f"* **Empresa / Especialista:** {lead['name']}")
        lines.append(f"* **Perfil Instagram:** {ig_link}")
        lines.append(f"* **Bate-Papo no Direct:** {direct_link}")
        if lead.get("url"):
            lines.append(f"* **Website Oficial:** {lead['url']}")
        lines.append(f"* **Localização:** {location}")
        lines.append(f"* **Nicho / Segmento:** {lead.get('niche', 'N/D')}")
        lines.append(f"* **Serviço Recomendado VCR:** {serv}")
        lines.append("")
        lines.append(f"### 🔍 Gargalo Digital & Oportunidade")
        lines.append(f"> {lead.get('bottleneck', 'N/D')}")
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
        lines.append(f"- [ ] **Dia 1:** Enviar DM de Abordagem no Instagram")
        lines.append(f"- [ ] **Dia 4:** Enviar Follow-up Assíncrono (se sem resposta)")
        lines.append(f"- [ ] **Dia 7:** Entregar 2 ideias práticas no chat e enviar link WhatsApp")
        lines.append(f"- [ ] **Fechamento:** Proposta aceita / Transição WhatsApp concluída")
        lines.append("```\n")
        lines.append("---\n")

    return "\n".join(lines)

def build_trello_csv(leads: list, profile: dict) -> str:
    import io
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)
    writer.writerow(["Card Name", "Card Description", "Labels", "List Name"])

    for lead in leads:
        clean_h = lead['handle'].lstrip('@')
        badge = lead.get('badge', 'ENG')
        tier_raw = lead.get('tier', 'Tier 2')
        tier_short = "Tier 1" if "Tier 1" in str(tier_raw) else "Tier 2"
        ig_link = lead.get('ig_url') or f"https://www.instagram.com/{clean_h}/"
        direct_link = f"https://ig.me/m/{clean_h}"
        serv = lead.get('offered_service', 'Soluções Digitais VCR')
        location = lead.get('location', 'N/D')

        title = f"[{badge} | {tier_short}] {lead['name']} (@{clean_h}) - {location}"

        desc_parts = [
            f"### 🏢 Informações do Lead",
            f"* **Empresa / Especialista:** {lead['name']}",
            f"* **Instagram:** {ig_link}",
            f"* **Direct:** {direct_link}",
        ]
        if lead.get("url"):
            desc_parts.append(f"* **Website:** {lead['url']}")
        desc_parts.extend([
            f"* **Localização:** {location}",
            f"* **Nicho:** {lead.get('niche', 'N/D')}",
            f"* **Serviço VCR:** {serv}",
            f"",
            f"### 🔍 Gargalo Digital & Oportunidade",
            f"> {lead.get('bottleneck', 'N/D')}",
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
            f"- [ ] Dia 1: Aquecimento & DM enviada",
            f"- [ ] Dia 4: Follow-up enviado",
            f"- [ ] Dia 7: Fechamento / Transição WhatsApp"
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
        clean_h = lead['handle'].lstrip('@')
        badge = lead.get('badge', 'ENG')
        tier_raw = lead.get('tier', 'Tier 2')
        tier = "Tier 1" if "Tier 1" in str(tier_raw) else "Tier 2"
        serv = lead.get('offered_service', 'Soluções Digitais VCR')
        trello_cards_data.append({
            "name": f"[{badge} | {tier}] {lead['name']} (@{clean_h}) - {lead.get('location', 'Global')}",
            "labels": [badge, tier, serv],
            "lead_name": lead['name'],
            "handle": lead['handle'],
            "ig_url": lead.get('ig_url') or f"https://www.instagram.com/{clean_h}/",
            "direct_url": f"https://ig.me/m/{clean_h}",
            "web_url": lead.get("url"),
            "location": lead.get("location"),
            "niche": lead.get("niche"),
            "service": serv,
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

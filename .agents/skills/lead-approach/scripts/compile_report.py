#!/usr/bin/env python3
"""
Compilador Automático de Dossiês Executivos (HTML -> PDF).
Pega uma lista de leads com diagnósticos e abordagens e gera o PDF final com diagramação A4,
respeitando estritamente o MANUAL DA MARCA do usuário (cores, tipografia, logo, slogan)
definido no setup (config/profile.json).

Compatível com Antigravity, Claude Code e OpenAI Codex.

Uso:
    python3 compile_report.py --data leads.json --output relatorio.pdf
    python3 compile_report.py --sample --output exemplo.pdf
"""

import sys
import os
import argparse
import json
import datetime
from generate_pdf import compile_pdf
from setup_profile import load_profile, derive_brand_tints

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(CURRENT_DIR, "..", "templates", "report-template.html")

SAMPLE_DATA = {
    "title": "Dossiê Executivo — Prospecção Ativa & Diagnósticos Digitais",
    "subtitle": "Estratégia de Abordagens 'No-Call' para Serviços de Alto Padrão",
    "agency": "VCR Softwares",
    "market": "Flórida, EUA & Brasil",
    "date": datetime.date.today().strftime("%d/%m/%Y"),
    "leads": [
        {
            "handle": "@yohanna_aesthetic",
            "name": "Yohanna MedSpa & Beauty",
            "badge": "ESP",
            "location": "Orlando, FL (Oak Ridge Rd)",
            "service": "K-Beauty, Protocolos Glass Skin & Injetáveis",
            "bottleneck": "Usa Linktree genérico com 8 botões; alta perda de pacientes no celular.",
            "strategy": "Página proprietária ultrarrápida com botão direto para WhatsApp oficial.",
            "message": "¡Hola Yohanna y equipo! ¿Cómo están?\n\nVengo siguiendo de cerca su trabajo en Orlando, en especial los resultados con K-Beauty y protocolos de Glass Skin. La autoridad clínica que transmiten en el perfil es impecable.\n\nLes escribo muy brevemente: nos especializamos en desarrollo web y páginas de captación de alto rendimiento para clínicas en EE.UU.\n\nSabemos que cuando una clínica ofrece procedimientos tan especializados, depender de links genéricos de reserva o páginas lentas en el móvil hace que muchos pacientes se pierdan antes de consultar. Diseñamos plataformas ultra rápidas preparadas para convertir visitas en consultas directas a su WhatsApp.\n\nPueden ver algunos proyectos que desarrollamos para el mercado de EE.UU. aquí:\n👉 https://vcrsoftwares.com/es/\n\nNo hace falta coordinar llamadas ni reuniones; si les interesa, me pueden responder directamente por este chat y les comparto por texto 2 observaciones prácticas para su clínica. ¡Un saludo y mucho éxito!",
            "follow_up": "¡Hola Yohanna! Quería pasar a saludarlos y confirmar si pudieron revisar el mensaje anterior. Cero compromiso: si quieren ver 2 observaciones prácticas sobre su presencia web por texto, quedo a su disposición por aquí. ¡Mucho éxito en la clínica!"
        },
        {
            "handle": "@fl_personalinjury_law",
            "name": "Vance & Partners Legal",
            "badge": "ENG",
            "location": "Miami, FL (Brickell Ave)",
            "service": "Personal Injury & Corporate Immigration",
            "bottleneck": "Formulário desktop antigo com 9 campos; tempo de resposta do site > 3.8s.",
            "strategy": "Página mobile-first com triagem confidencial em 1 toque.",
            "message": "Hi Team at Vance & Partners! Hope you're having a productive week.\n\nI've been following your firm’s updates regarding Florida personal injury claims. The authority and clarity you share here are top-notch.\n\nI’m reaching out briefly: we engineer ultra-fast digital intake pages and mobile experiences tailored for US law firms.\n\nWhen clients need legal assistance, 90%+ search from their phones under urgent conditions. Sluggish loading speeds and lengthy forms cause high drop-off rates before the initial intake happens. We build sleek pages loading under 1 second that route urgent inquiries directly to your staff.\n\nYou can check out our US digital work here:\n👉 https://vcrsoftwares.com/en/\n\nNo phone calls required—if you’re open to it, just reply here and I’ll send over 2 quick practical observations by text on streamlining your mobile client flow. Have a great day!",
            "follow_up": "Hi Team! Just following up quickly in case my note got buried. No pressure at all—if you ever want a couple of quick tips on your mobile intake flow, feel free to drop a line here anytime. Have a great week!"
        }
    ]
}

def render_lead_card(index: int, lead: dict) -> str:
    badge_class = f"badge-{lead.get('badge', 'esp').lower()}"
    badge_label = lead.get('badge', 'ESP').upper()

    html = f"""
    <div class="lead-card avoid-break">
      <div class="lead-header">
        <div class="lead-header-left">
          <div class="lead-num">{index}</div>
          <div>
            <div class="lead-handle">{lead.get('handle', '@lead')}</div>
            <div class="lead-subname">{lead.get('name', '')}</div>
          </div>
        </div>
        <span class="badge-pill {badge_class}">{badge_label}</span>
      </div>
      <div class="lead-body">
        <div class="lead-meta-row">
          <div class="meta-col">
            <strong>Localização</strong>
            <span>{lead.get('location', 'N/D')}</span>
          </div>
          <div class="meta-col">
            <strong>Serviço Âncora</strong>
            <span>{lead.get('service', 'N/D')}</span>
          </div>
          <div class="meta-col">
            <strong>Gargalo / Oportunidade</strong>
            <span>{lead.get('bottleneck', 'N/D')}</span>
          </div>
        </div>

        <div class="msg-label">
          💬 Mensagem de Abordagem Sugerida (DM / InBox)
        </div>
        <div class="msg-box">{lead.get('message', '').strip()}</div>

        <div class="follow-box">
          <strong>Follow-up (3 a 4 dias):</strong> {lead.get('follow_up', '').strip()}
        </div>
      </div>
    </div>
    """
    return html

def build_report_html(data: dict) -> str:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Template não encontrado em: {TEMPLATE_PATH}")

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    profile = load_profile()
    brand = profile.get("brand", {})

    agency = data.get("agency") or profile.get("company_name", "VCR Softwares")
    title = data.get("title") or f"Dossiê Executivo — {agency}"
    subtitle = data.get("subtitle") or f"Estratégia de Abordagem & Diagnóstico · {profile.get('primary_service', 'Serviços Digitais')}"
    market = data.get("market") or ", ".join(profile.get("target_niches", ["EUA & Brasil"])[:3])
    date_str = data.get("date") or datetime.date.today().strftime("%d/%m/%Y")
    leads = data.get("leads", [])

    # Brand Guidelines extraction
    brand_primary = brand.get("primary_color", "#8338ec")
    brand_secondary = brand.get("secondary_color", "#3a86ff")
    brand_dark = brand.get("dark_color", "#0f172a")
    brand_font = brand.get("font_family", "Plus Jakarta Sans")
    brand_tagline = brand.get("tagline") or profile.get("primary_service", "Soluções Digitais & Alta Performance")
    brand_tag = brand.get("tag_badge", "Inteligência Comercial Outbound")
    brand_disclaimer = brand.get("disclaimer", "Documento Confidencial · Uso Interno de Prospecção")

    # Dynamic tints derivation
    brand_light_bg = brand.get("light_bg")
    brand_light_border = brand.get("light_border")
    if not brand_light_bg or not brand_light_border:
        derived_bg, derived_bd = derive_brand_tints(brand_primary)
        brand_light_bg = brand_light_bg or derived_bg
        brand_light_border = brand_light_border or derived_bd

    # Brand Logo / Monogram generation
    logo_url = brand.get("logo_url", "").strip()
    if logo_url:
        logo_html = f'<img src="{logo_url}" alt="{agency}" class="brand-logo-img">'
    else:
        words = agency.split()
        initials = "".join([w[0].upper() for w in words[:3]]) if words else "AG"
        logo_html = f'<div class="brand-monogram">{initials}</div>'

    content_parts = []

    # Header section following Brand Manual
    content_parts.append(f"""
    <div class="header">
      <div class="header-left">
        {logo_html}
        <div>
          <span class="brand-tag">{brand_tag}</span>
          <h1 class="main-title">{title}</h1>
          <p class="main-subtitle">{subtitle}</p>
        </div>
      </div>
      <div class="header-meta">
        <div><strong>{agency}</strong></div>
        <div style="font-size: 8.5px; color: #64748b; margin-top: 1px;">{brand_tagline}</div>
        <div style="margin-top: 3px;"><strong>Data:</strong> {date_str}</div>
        <div><strong>Total de Leads:</strong> {len(leads)} perfis</div>
      </div>
    </div>
    """)

    # Methodology Section
    content_parts.append(f"""
    <div style="background: var(--brand-light-bg); border-left: 3.5px solid var(--brand-primary); padding: 8px 12px; border-radius: 4px; margin-bottom: 14px; font-size: 10px; color: var(--brand-dark);">
      <strong>Metodologia Aplicada:</strong> Abordagem em 4 blocos (Conexão + Diagnóstico + Prova Social + CTA No-Call). 100% orientada a texto (Direct/WhatsApp), sem exigência de chamadas síncronas de voz ou vídeo.
    </div>
    """)

    # Lead cards
    content_parts.append('<div class="section-title">Leads Mapeados & Roteiros de Abordagem</div>')
    for i, lead in enumerate(leads, 1):
        content_parts.append(render_lead_card(i, lead))

    # Page footer following Brand Manual
    content_parts.append(f"""
    <div class="page-footer">
      <span><strong>{agency}</strong> · {brand_tagline}</span>
      <span>{brand_disclaimer}</span>
    </div>
    """)

    full_content = "\n".join(content_parts)

    # Replace all template brand variables
    rendered = template.replace("{{ BRAND_PRIMARY }}", brand_primary) \
                       .replace("{{ BRAND_SECONDARY }}", brand_secondary) \
                       .replace("{{ BRAND_DARK }}", brand_dark) \
                       .replace("{{ BRAND_LIGHT_BG }}", brand_light_bg) \
                       .replace("{{ BRAND_LIGHT_BORDER }}", brand_light_border) \
                       .replace("{{ BRAND_FONT }}", brand_font) \
                       .replace("{{ TITLE }}", title) \
                       .replace("{{ CONTENT }}", full_content)

    return rendered

def main():
    parser = argparse.ArgumentParser(description="Compilador de Dossiê Executivo de Prospecção (JSON -> PDF) com Manual da Marca.")
    parser.add_argument("--data", "-d", help="Arquivo JSON contendo as informações dos leads.")
    parser.add_argument("--sample", action="store_true", help="Gera um relatório de exemplo para demonstração.")
    parser.add_argument("--output", "-o", default="relatorio_prospeccao.pdf", help="Caminho do arquivo PDF de saída.")
    parser.add_argument("--html-only", action="store_true", help="Salva apenas o arquivo HTML sem compilar PDF.")
    args = parser.parse_args()

    if args.sample:
        data = SAMPLE_DATA
    elif args.data:
        if not os.path.exists(args.data):
            print(f"Erro: Arquivo JSON não encontrado: {args.data}")
            sys.exit(1)
        with open(args.data, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        print("Erro: Forneça um arquivo de dados (--data caminho.json) ou use a flag --sample.")
        sys.exit(1)

    html_content = build_report_html(data)
    temp_html = os.path.splitext(args.output)[0] + ".html"

    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML estruturado com Manual da Marca gerado em: {temp_html}")

    if not args.html_only:
        compile_pdf(temp_html, args.output)
        if os.path.exists(temp_html) and not args.html_only:
            os.remove(temp_html)

if __name__ == "__main__":
    main()

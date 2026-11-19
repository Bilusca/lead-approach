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
import shutil
import re
import html as html_lib
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

def format_clickable_message(text: str) -> str:
    """Escapes HTML and converts URLs into clickable hyperlinks for PDF and Web."""
    if not text:
        return ""
    escaped = html_lib.escape(text.strip())
    def replace_url(m):
        u = m.group(0)
        return f'<a href="{u}" target="_blank" class="msg-inline-link">{u} ↗</a>'
    return re.sub(r'https?://[^\s,;"\'<>|]+', replace_url, escaped)

def render_lead_card(index: int, lead: dict) -> str:
    badge_class = f"badge-{lead.get('badge', 'esp').lower()}"
    badge_label = lead.get('badge', 'ESP').upper()
    offered_serv = lead.get('offered_service') or lead.get('service', 'N/D')

    handle = lead.get('handle', '@lead')
    clean_handle = handle.lstrip('@')
    name = lead.get('name', '')

    ig_url = lead.get('ig_url') or f"https://www.instagram.com/{clean_handle}/"
    direct_url = f"https://ig.me/m/{clean_handle}"

    web_url = lead.get('url')
    web_label = ""
    if web_url:
        web_label = web_url.replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/")

    raw_message = lead.get('message', '').strip()
    formatted_message = format_clickable_message(raw_message)

    raw_follow_up = lead.get('follow_up', '').strip()
    formatted_follow_up = format_clickable_message(raw_follow_up)

    header_web_html = f'<div style="margin-top:2px;"><a href="{web_url}" target="_blank" class="header-web-link">🌐 {web_label} ↗</a></div>' if web_url else ''
    meta_web_html = f'<a href="{web_url}" target="_blank" class="meta-link">{web_label} ↗</a>' if web_url else 'Redes Sociais / Direct'

    html = f"""
    <div class="lead-card avoid-break" id="lead-{index}">
      <div class="lead-header">
        <div class="lead-header-left">
          <div class="lead-num">{index}</div>
          <div>
            <div class="lead-title-row">
              <a href="{ig_url}" target="_blank" class="lead-handle-link" title="Acessar perfil no Instagram">
                {handle} <span class="ext-icon">↗</span>
              </a>
              <span class="lead-subname">· {name}</span>
            </div>
            {header_web_html}
          </div>
        </div>
        <div class="lead-header-right">
          <a href="{direct_url}" target="_blank" class="header-action-btn direct-btn" title="Abrir Direct no Instagram">
            ✈️ Abrir Direct ↗
          </a>
          {f'<a href="{web_url}" target="_blank" class="header-action-btn" title="Acessar Website Oficial">🌐 Site ↗</a>' if web_url else ''}
          <span class="badge-pill {badge_class}">{badge_label}</span>
        </div>
      </div>
      <div class="lead-body">
        <div class="lead-meta-row">
          <div class="meta-col">
            <strong>Localização</strong>
            <span>{lead.get('location', 'N/D')}</span>
          </div>
          <div class="meta-col">
            <strong>Serviço VCR Recomendado</strong>
            <span style="color: var(--brand-primary); font-weight: 700;">{offered_serv}</span>
          </div>
          <div class="meta-col">
            <strong>Website Oficial</strong>
            <span>{meta_web_html}</span>
          </div>
          <div class="meta-col">
            <strong>Gargalo / Oportunidade</strong>
            <span>{lead.get('bottleneck', 'N/D')}</span>
          </div>
        </div>

        <div style="margin: 6px 0 6px 0; font-size: 9.5px; color: #475569; background: #f8fafc; padding: 6px 10px; border-radius: 4px; border: 1px solid #e2e8f0;">
          <strong>🎯 Estratégia de Atenção:</strong> {lead.get('warming', 'Visualizar Stories recentes e interagir antes do envio.')}
        </div>

        <!-- Action Bar: Message + Copy Button -->
        <div class="msg-action-bar">
          <div class="msg-label-wrap">
            <span class="msg-icon">💬</span>
            <span class="msg-label">Mensagem Curta de Abordagem (Dia 1)</span>
          </div>
          <div class="msg-buttons-wrap">
            <button type="button" class="btn-copy-action" id="btn-msg-{index}" data-target="msg-{index}" onclick="copyCardText(event, this, 'msg-{index}')" title="Copiar mensagem para a área de transferência">
              <span class="btn-icon">📋</span>
              <span class="btn-text">Copiar Mensagem</span>
            </button>
            <a href="{direct_url}" target="_blank" class="btn-direct-action" title="Abrir Instagram Direct de {clean_handle}">
              <span class="btn-icon">✈️</span>
              <span class="btn-text">Abrir Direct ↗</span>
            </a>
          </div>
        </div>
        <div class="msg-box" id="msg-{index}">{formatted_message}</div>

        <!-- Action Bar: Follow-up + Copy Button -->
        <div class="follow-action-bar">
          <div class="follow-label-wrap">
            <strong>🔁 Follow-up Assíncrono (Dia 4)</strong>
          </div>
          <button type="button" class="btn-copy-action btn-copy-sm" id="btn-fup-{index}" data-target="fup-{index}" onclick="copyCardText(event, this, 'fup-{index}')" title="Copiar follow-up">
            <span class="btn-icon">📋</span>
            <span class="btn-text">Copiar Follow-up</span>
          </button>
        </div>
        <div class="follow-box" id="fup-{index}">{formatted_follow_up}</div>
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
        <div><strong>Mercado:</strong> {market}</div>
        <div><strong>Total de Leads:</strong> {len(leads)} perfis</div>
      </div>
    </div>
    """)

    # Interactive Banner & Methodology Section
    content_parts.append(f"""
    <div class="interactive-banner">
      <div class="banner-left">
        <span class="banner-badge">INTERATIVO</span>
        <span><strong>Navegação & Cópia em 1 Clique:</strong> Clique em <strong>📋 Copiar Mensagem</strong> para transferir o texto e use os links <strong>✈️ Abrir Direct</strong> ou <strong>🌐 Site</strong> para acessar os canais do lead no navegador.</span>
      </div>
    </div>
    <div style="background: var(--brand-light-bg); border-left: 3.5px solid var(--brand-primary); padding: 7px 11px; border-radius: 4px; margin-bottom: 12px; font-size: 9.5px; color: var(--brand-dark);">
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

    date_str = datetime.date.today().strftime("%Y-%m-%d")
    raw_output = args.output
    base_name = os.path.basename(raw_output)
    stem, ext = os.path.splitext(base_name)
    if not stem:
        stem = "relatorio_prospeccao"

    folder_name = f"{stem}-{date_str}"

    raw_dir = os.path.dirname(raw_output)
    if "report" in raw_dir.split(os.sep) or "reports" in raw_dir.split(os.sep):
        target_dir = raw_dir
    else:
        target_dir = os.path.join("report", folder_name)

    os.makedirs(target_dir, exist_ok=True)

    if args.data and os.path.isfile(args.data):
        try:
            dest_data = os.path.join(target_dir, os.path.basename(args.data))
            if os.path.abspath(args.data) != os.path.abspath(dest_data):
                shutil.copy2(args.data, dest_data)
        except Exception:
            pass
    pdf_target = os.path.join(target_dir, f"{stem}.pdf")
    html_target = os.path.join(target_dir, f"{stem}.html")

    html_content = build_report_html(data)
    with open(html_target, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML estruturado com Manual da Marca gerado em: {html_target}")

    if not args.html_only:
        compile_pdf(html_target, pdf_target)
        print(f"🌐 Versão Web Interativa (com botões de cópia em 1 clique) mantida em: {html_target}")

if __name__ == "__main__":
    main()

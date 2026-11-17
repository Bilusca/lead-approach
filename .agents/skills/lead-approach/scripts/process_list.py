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
    lines = raw_text.splitlines()
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

        # Clean numbering (1. , - , * )
        name_part = re.sub(r'^\d+[\.\)\-]\s*', '', name_part)
        name_part = re.sub(r'^[\*\-\+]\s*', '', name_part).strip()

        if not name_part and found_handle:
            name_part = found_handle.replace("@", "").replace("_", " ").title()
        elif not name_part and found_url:
            domain = found_url.split("://")[-1].split("/")[0].replace("www.", "")
            name_part = domain.split(".")[0].title()

        if found_url or found_handle or (len(name_part) > 2 and not name_part.lower().startswith("http")):
            candidates.append({
                "raw": cleaned,
                "name": name_part or "Target Business",
                "url": None if is_gmaps else found_url,
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

    combined = f"{candidate['name']} {candidate.get('raw', '')} {recon_data.get('title', '')} {recon_data.get('description', '')}".lower()

    # Spanish cues
    if any(w in combined for w in ["estética", "medicina", "clínica", "abogados", "inmigración", "odontología", "diseño", "madrid", "bogotá", "méxico", "buenos aires", "orlando, fl", "miami"]):
        if any(w in combined for w in [" en ", " de ", " los ", " las ", " con ", " para ", " cirujano ", " citas "]):
            return ("es", "ESP")

    # Portuguese cues
    if ".br" in (candidate.get("url") or "") or any(w in combined for w in ["brasil", "são paulo", "rio de janeiro", "advocacia", "odontologia", "agendamento", "harmonização", "contato"]):
        if any(w in combined for w in [" em ", " de ", " com ", " para ", " seu ", " sua "]):
            return ("pt", "PT")

    # Default to English (Primary)
    return ("en", "ENG")

def generate_custom_copy(lead: dict, profile: dict, lang: str) -> dict:
    company_name = profile.get("company_name", "VCR Softwares")
    primary_service = profile.get("primary_service", "High-Performance Web Development & Conversion Landing Pages")
    value_prop = profile.get("value_proposition", "We build ultra-fast pages (< 1s on mobile) that eliminate client drop-off.")
    whatsapp_url = profile.get("whatsapp_url", "https://wa.me/XXXXXXXXXXX")
    
    lead_name = lead["name"]
    handle = lead.get("handle") or f"@{lead_name.lower().replace(' ', '')}"
    niche = lead.get("niche") or "high-end services"
    location = lead.get("location") or "your area"
    bottleneck = lead.get("bottleneck", "slow mobile load speeds and complex booking forms")

    if lang == "es":
        portfolio_url = profile.get("website_es") or profile.get("website_en") or "https://vcrsoftwares.com/es/"
        message = (
            f"¡Hola al equipo de {lead_name}! ¿Cómo están?\n\n"
            f"Vengo siguiendo de cerca su propuesta de {niche}. La calidad y el estándar de atención que transmiten en el perfil es impecable.\n\n"
            f"Les escribo muy brevemente: en {company_name} nos especializamos en {primary_service} para negocios de alto valor.\n\n"
            f"Notamos que en el móvil, {bottleneck}, lo que hace que muchos pacientes y clientes potenciales abandonen antes de consultar. Diseñamos plataformas ultra rápidas preparadas para convertir visitas en consultas directas a su WhatsApp en 1 toque.\n\n"
            f"Pueden ver algunos proyectos activos aquí:\n👉 {portfolio_url}\n\n"
            f"No hace falta coordinar llamadas ni reuniones; si les interesa, me pueden responder directamente por este chat y les paso 2 observaciones prácticas por texto. ¡Un saludo cordial!"
        )
        follow_up = (
            f"¡Hola {lead_name}! Quería pasar a saludarlos y confirmar si pudieron revisar el mensaje anterior. "
            f"Cero compromiso: si en algún momento quieren ver 2 observaciones prácticas sobre su presencia web por texto, "
            f"quedo a su disposición por aquí. ¡Mucho éxito esta semana!"
        )
        warming = f"Ver Stories de las últimas 24h de {handle}. Responder a un Story de resultado/caso de éxito aplicando el Gatilho 1."

    elif lang == "pt":
        portfolio_url = profile.get("website_pt") or "https://vcrsoftwares.com/"
        message = (
            f"Olá, equipe da {lead_name}, tudo bem?\n\n"
            f"Acompanho o trabalho de vocês e acho excelente o posicionamento em {niche}. O padrão de entrega de vocês é muito diferenciado.\n\n"
            f"Passando rapidamente: na {company_name}, somos especialistas em {primary_service}.\n\n"
            f"Sabemos que quando {bottleneck}, muitos clientes que chegam pelo celular acabam desistindo antes de entrar em contato. Nós eliminamos esse atrito com páginas instantâneas focadas em triagem de 1 toque no WhatsApp.\n\n"
            f"Você pode conferir alguns casos e clientes atendidos aqui:\n👉 {portfolio_url}\n\n"
            f"Não precisa agendar reunião ou ligação: se fizer sentido para você, me responda por aqui mesmo que te envio 2 pontos práticos por mensagem. Um abraço e boas vendas!"
        )
        follow_up = (
            f"Olá, {lead_name}! Passando só para confirmar se conseguiu dar uma olhada na mensagem anterior. "
            f"Sem compromisso nenhum: se quiser trocar uma ideia rápida por texto sobre a sua página mobile, estou por aqui. Uma ótima semana!"
        )
        warming = f"Assistir aos Stories ativos de {handle} e curtir as 2 postagens mais recentes para ativar notificação de reconhecimento."

    else: # English [Primary]
        portfolio_url = profile.get("website_en") or "https://vcrsoftwares.com/en/"
        message = (
            f"Hi {lead_name} team! Hope you're having a wonderful week.\n\n"
            f"I was reviewing your work in {niche} and really love your standard of service. The authority and quality you present in your business is top-tier.\n\n"
            f"I’m reaching out briefly: at {company_name}, we specialize in {primary_service} for luxury service businesses.\n\n"
            f"We noticed that on mobile, {bottleneck}. For premium clientele, having a mobile experience that loads under 1 second and enables 1-tap inquiries makes a huge difference in booking retention.\n\n"
            f"You can take a quick look at some of our live client work here:\n👉 {portfolio_url}\n\n"
            f"No phone calls needed—if you're open to it, just reply right here on chat and I’d be happy to share 2 quick practical ideas by text on optimizing client flow. Have a great day!"
        )
        follow_up = (
            f"Hi {lead_name} team! Just following up quickly in case my note got buried. "
            f"No pressure at all—if you ever want a couple of quick practical tips on your mobile intake flow, "
            f"feel free to drop a line here anytime. Have a great rest of the week!"
        )
        warming = f"Engage with {handle}'s active Stories. If a service demonstration or client result is active, send DM as a direct Story reply."

    return {
        "message": message,
        "follow_up": follow_up,
        "warming": warming,
        "portfolio_url": portfolio_url
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

        # Niche heuristics from recon title / description
        niche = cand.get("niche")
        if not niche and recon.get("title"):
            title = recon["title"]
            if any(k in title.lower() for k in ["medspa", "aesthetic", "estética", "spa", "beauty"]): niche = "Aesthetics & MedSpa"
            elif any(k in title.lower() for k in ["law", "legal", "attorney", "abogados", "advocacia"]): niche = "Legal Services & Law"
            elif any(k in title.lower() for k in ["arch", "interior", "arquitetura", "design"]): niche = "Architecture & Design"
            elif any(k in title.lower() for k in ["dental", "dentist", "odonto"]): niche = "Cosmetic Dentistry"
            elif any(k in title.lower() for k in ["real estate", "realtor", "imóveis"]): niche = "Luxury Real Estate"
        if not niche:
            niche = "High-Ticket Client Services"

        # Determine location
        location = cand.get("location") or "US / Global"

        # Language selection
        lang_code, badge = detect_language(cand, recon, force_lang)

        # Bottleneck formulation
        bottleneck = "the current page takes over 2.5s on mobile or relies on generic links"
        if recon.get("friction_points"):
            bottleneck = recon["friction_points"][0]
            # Clean technical jargon for conversational copy
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
    date_str = datetime.date.today().strftime("%Y-%m-%d")

    md = []
    md.append(f"# 🗺️ Outbound Execution Roadmap & Prospecting Plan")
    md.append(f"**Campaign Operator:** `{agency}` | **Date:** `{date_str}` | **Total Leads:** `{len(leads)}`\n")

    md.append("## 📊 1. Lead Prioritization Matrix")
    md.append("| # | Lead Name / Handle | Niche | Tier | Language | Digital Leak / Bottleneck |")
    md.append("| :-: | :--- | :--- | :--- | :-: | :--- |")
    for i, lead in enumerate(leads, 1):
        md.append(f"| {i} | **{lead['name']}** (`{lead['handle']}`) | {lead['niche']} | `{lead['tier']}` | {lead['badge']} | {lead['bottleneck'][:65]}... |")
    md.append("")

    md.append("## 📅 2. Multi-Day Execution Schedule")
    md.append("```text")
    md.append("┌────────────────────────────────────────────────────────────────────────┐")
    md.append("│ DAY 1: Warming Touchpoints & Initial 4-Block DMs                       │")
    md.append("│  • Like 2 recent posts + view active Stories                           │")
    md.append("│  • Send personalized 4-block DM (reply to Story if available)          │")
    md.append("├────────────────────────────────────────────────────────────────────────┤")
    md.append("│ DAY 4: Asynchronous Follow-Up Touchpoint                               │")
    md.append("│  • Check seen status. If unread or unanswered, send 1-sentence reminder│")
    md.append("│  • Zero pressure: reaffirm text conversation                           │")
    md.append("├────────────────────────────────────────────────────────────────────────┤")
    md.append("│ DAY 7: WhatsApp Bridge & Closing Transition                            │")
    md.append("│  • For leads who answered with interest: deliver 2 ideas               │")
    md.append("│  • Send link to official WhatsApp with concept dossier / proposal      │")
    md.append("└────────────────────────────────────────────────────────────────────────┘")
    md.append("```\n")

    md.append("## 🎯 3. Individual Lead Cards & Copy-Paste Scripts\n")
    for i, lead in enumerate(leads, 1):
        md.append(f"### Lead #{i}: {lead['name']} ({lead['badge']})")
        md.append(f"- **Handle / Profile:** `{lead['handle']}`")
        if lead.get("url"):
            md.append(f"- **Website:** `{lead['url']}` (Latency: `{lead.get('latency_ms', 'N/A')}ms` | Stack: `{lead['cms']}`)")
        md.append(f"- **Priority Tier:** `{lead['tier']}`")
        md.append(f"- **Warming Protocol (Day 1):** {lead['warming']}")
        md.append("")
        md.append(f"**💬 Initial 4-Block Outreach Message (Day 1):**")
        md.append("```text")
        md.append(lead["message"])
        md.append("```")
        md.append(f"**🔁 Asynchronous Follow-Up Message (Day 4):**")
        md.append("```text")
        md.append(lead["follow_up"])
        md.append("```")
        md.append("---\n")

    return "\n".join(md)

def main():
    parser = argparse.ArgumentParser(description="Batch lead list processor & outreach roadmap builder.")
    parser.add_argument("--file", "-f", help="Path to input file containing leads (PDF, TXT, MD, CSV, JSON).")
    parser.add_argument("--input", "-i", help="Direct text/URL list passed as a string.")
    parser.add_argument("--output", "-o", default="outreach_roadmap.md", help="Output path for the generated Markdown roadmap.")
    parser.add_argument("--json", help="Path to save the structured JSON leads output.")
    parser.add_argument("--pdf", help="Compile the executive A4 PDF dossier to this path.")
    parser.add_argument("--lang", choices=["en", "es", "pt"], help="Force specific language for all generated messages.")
    parser.add_argument("--fast", action="store_true", help="Fast mode: skip live HTTP technical recon checks.")
    args = parser.parse_args()

    raw_text = ""
    if args.file:
        print(f"Reading leads from file: {args.file}...")
        raw_text = extract_text_from_file(args.file)
    elif args.input:
        raw_text = args.input
    elif not sys.stdin.isatty():
        raw_text = sys.stdin.read()
    else:
        print("Error: Please provide a file (--file path) or inline input (--input '...')")
        sys.exit(1)

    if not raw_text.strip():
        print("Error: Input file or text is empty.")
        sys.exit(1)

    leads = process_leads_list(raw_text, force_lang=args.lang, fast_mode=args.fast)
    if not leads:
        print("Warning: No valid business entries or URLs could be parsed.")
        sys.exit(0)

    profile = load_profile()
    roadmap_md = build_roadmap_markdown(leads, profile)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(roadmap_md)
    print(f"\n✅ Outreach Roadmap saved to: {args.output}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(leads, f, indent=2, ensure_ascii=False)
        print(f"📁 JSON data saved to: {args.json}")

    if args.pdf:
        print(f"Compiling executive A4 PDF dossier...")
        report_data = {
            "title": f"Executive Outreach Dossier — {profile.get('company_name', 'VCR Softwares')}",
            "subtitle": f"Outbound Roadmap & Technical Audits ({len(leads)} Target Leads)",
            "agency": profile.get("company_name", "VCR Softwares"),
            "market": "US & International High-Ticket",
            "date": datetime.date.today().strftime("%Y-%m-%d"),
            "leads": leads
        }
        temp_html = os.path.splitext(args.pdf)[0] + ".html"
        html_code = build_report_html(report_data)
        with open(temp_html, "w", encoding="utf-8") as f:
            f.write(html_code)
        compile_pdf(temp_html, args.pdf)
        if os.path.exists(temp_html):
            os.remove(temp_html)

if __name__ == "__main__":
    main()

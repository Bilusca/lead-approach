#!/usr/bin/env python3
"""
Setup do Perfil de Prospecção & Manual da Marca — Lead Approach.
Configura e grava em memória permanente (config/profile.json e config/profile.md)
as informações da sua empresa/serviço, tom de voz, canais, links de portfólio e
o MANUAL DA MARCA (cores, tipografia, slogan, logo e regras visuais do relatório).

Compatível com Antigravity, Claude Code e OpenAI Codex.

Uso:
    python3 setup_profile.py                      # Modo interativo (perguntas no terminal)
    python3 setup_profile.py --show               # Exibe o perfil e manual da marca em memória
    python3 setup_profile.py --brand-color "#2563eb" --brand-tagline "Sua Tagline" ...
"""

import sys
import os
import argparse
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "config"))
CONFIG_JSON_PATH = os.path.join(DEFAULT_CONFIG_DIR, "profile.json")
CONFIG_MD_PATH = os.path.join(DEFAULT_CONFIG_DIR, "profile.md")

TONE_DESCRIPTIONS = {
    "consultivo": "Consultive & Specialized: Focuses on pointing out technical opportunities with respect, elegance, and expertise without sounding condescending.",
    "direto": "Direct & ROI-Driven: Concise, action-oriented, emphasizing time savings, mobile conversion rate, and revenue protection.",
    "caloroso": "Warm & Relational: Native to aesthetic/lifestyle Instagram DMs, highly empathetic, genuine compliments, and relaxed conversational flow.",
    "executivo": "Executive & Sober: Tailored for law firms, wealth management, and corporate consulting. Subtle, formal, and discreet."
}

BRAND_COLOR_PRESETS = {
    "amethyst": {
        "primary_color": "#8338ec",
        "secondary_color": "#3a86ff",
        "dark_color": "#0f172a",
        "name": "Royal Amethyst (#8338ec - Tech Modern & Creative)"
    },
    "sapphire": {
        "primary_color": "#2563eb",
        "secondary_color": "#0284c7",
        "dark_color": "#0f172a",
        "name": "Tech Sapphire (#2563eb - Corporate, Trust & SaaS)"
    },
    "emerald": {
        "primary_color": "#059669",
        "secondary_color": "#10b981",
        "dark_color": "#064e3b",
        "name": "Emerald Prestige (#059669 - Growth, Health & Luxury)"
    },
    "gold": {
        "primary_color": "#b45309",
        "secondary_color": "#d97706",
        "dark_color": "#18181b",
        "name": "Obsidian & Gold (#b45309 - Ultra-Luxury, Legal & High Architecture)"
    },
    "crimson": {
        "primary_color": "#dc2626",
        "secondary_color": "#f43f5e",
        "dark_color": "#1e1e24",
        "name": "Crimson Impact (#dc2626 - Bold, High-Energy & Dynamic)"
    }
}

def derive_brand_tints(hex_color: str) -> tuple:
    h = hex_color.lstrip('#')
    if len(h) != 6:
        return "#f8fafc", "#e2e8f0"
    try:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        bg_r = int(r * 0.07 + 255 * 0.93)
        bg_g = int(g * 0.07 + 255 * 0.93)
        bg_b = int(b * 0.07 + 255 * 0.93)
        bd_r = int(r * 0.22 + 255 * 0.78)
        bd_g = int(g * 0.22 + 255 * 0.78)
        bd_b = int(b * 0.22 + 255 * 0.78)
        return f"#{bg_r:02x}{bg_g:02x}{bg_b:02x}", f"#{bd_r:02x}{bd_g:02x}{bd_b:02x}"
    except Exception:
        return "#f8fafc", "#e2e8f0"

def load_profile(config_path: str = None) -> dict:
    target_path = config_path or CONFIG_JSON_PATH
    if os.path.exists(target_path):
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Notice: Unable to read {target_path}: {e}")

    # Default fallback profile with complete Brand Guidelines
    light_bg, light_border = derive_brand_tints("#8338ec")
    return {
        "company_name": "VCR Softwares",
        "founder_name": "Commercial Team",
        "primary_service": "High-Performance Web Development & Conversion Landing Pages",
        "secondary_services": "Custom Web Systems, Lead Capture Funnels, Speed Optimization",
        "value_proposition": "We build ultra-fast pages (< 1s on mobile) that eliminate client drop-off and convert social media clicks into direct WhatsApp inquiries.",
        "tone": "consultivo",
        "tone_description": TONE_DESCRIPTIONS["consultivo"],
        "channels": ["Instagram Direct", "WhatsApp", "LinkedIn"],
        "website_en": "https://vcrsoftwares.com/en/",
        "website_es": "https://vcrsoftwares.com/es/",
        "website_pt": "https://vcrsoftwares.com/",
        "whatsapp_url": "https://wa.me/XXXXXXXXXXX",
        "pricing_range": "Custom projects starting from $800 USD / R$ 3.000",
        "target_niches": ["Luxury Aesthetics & MedSpas", "Law Firms", "High-End Architecture", "Cosmetic Dentistry", "Luxury Real Estate"],
        "brand": {
            "primary_color": "#8338ec",
            "secondary_color": "#3a86ff",
            "dark_color": "#0f172a",
            "light_bg": light_bg,
            "light_border": light_border,
            "font_family": "Plus Jakarta Sans",
            "tagline": "Soluções Digitais & Desenvolvimento Web de Alta Performance",
            "tag_badge": "Inteligência Comercial Outbound",
            "logo_url": "",
            "disclaimer": "Documento Confidencial · Uso Interno de Prospecção"
        },
        "configured": False
    }

def save_profile(data: dict, config_dir: str = None):
    target_dir = config_dir or DEFAULT_CONFIG_DIR
    os.makedirs(target_dir, exist_ok=True)

    json_path = os.path.join(target_dir, "profile.json")
    md_path = os.path.join(target_dir, "profile.md")

    data["configured"] = True
    if data.get("tone") in TONE_DESCRIPTIONS:
        data["tone_description"] = TONE_DESCRIPTIONS[data["tone"]]

    # Ensure brand guidelines and tints are calculated
    if "brand" not in data:
        data["brand"] = {}

    brand = data["brand"]
    primary = brand.get("primary_color", "#8338ec")
    if not brand.get("secondary_color"):
        brand["secondary_color"] = "#3a86ff"
    if not brand.get("dark_color"):
        brand["dark_color"] = "#0f172a"
    if not brand.get("font_family"):
        brand["font_family"] = "Plus Jakarta Sans"
    if not brand.get("tagline"):
        brand["tagline"] = data.get("primary_service", "Soluções Digitais de Alta Performance")
    if not brand.get("tag_badge"):
        brand["tag_badge"] = "Inteligência Comercial Outbound"
    if not brand.get("disclaimer"):
        brand["disclaimer"] = "Documento Confidencial · Uso Interno de Prospecção"

    # Derive tints
    bg, border = derive_brand_tints(primary)
    brand["light_bg"] = bg
    brand["light_border"] = border

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    md_content = f"""# Campaign Memory & Offer Profile (Lead Approach)

> **Generated automatically by `setup_profile.py`.**  
> AI Agents (Antigravity, Claude Code, and Codex) read this profile to align all outreach messages, DMs, and executive reports.

---

## 🏢 Business Identity
* **Company / Agency Name:** {data.get('company_name', 'N/A')}
* **Representative / Sign-off Name:** {data.get('founder_name', 'N/A')}
* **Primary Product / Service:** {data.get('primary_service', 'N/A')}
* **Secondary Services:** {data.get('secondary_services', 'N/A')}
* **Core Value Proposition:** {data.get('value_proposition', 'N/A')}

---

## 🎨 Manual de Identidade Visual da Marca (Brand Guidelines)
* **Cor Primária da Marca:** `{brand.get('primary_color')}`
* **Cor Secundária / Destaque:** `{brand.get('secondary_color')}`
* **Cor Escura / Cabeçalhos:** `{brand.get('dark_color')}`
* **Fundo Suave (Caixas de Mensagem):** `{brand.get('light_bg')}`
* **Borda Suave:** `{brand.get('light_border')}`
* **Tipografia Principal:** `{brand.get('font_family')}`
* **Slogan / Tagline do Relatório:** {brand.get('tagline')}
* **Badge Superior (Categoria):** {brand.get('tag_badge')}
* **Logo da Empresa:** {brand.get('logo_url') or "Monograma de Iniciais Dinâmico"}
* **Aviso de Confidencialidade:** {brand.get('disclaimer')}

---

## 🗣️ Tone of Voice & Outreach Style
* **Configured Tone:** `{data.get('tone', 'consultivo').upper()}`
* **Voice Directive:** {data.get('tone_description', '')}
* **Active Channels:** {", ".join(data.get('channels', []))}

---

## 🌐 Link Ecosystem & Conversion Funnel
* **English / US Portfolio (Primary):** {data.get('website_en', 'N/A')}
* **Spanish / Hispanic Portfolio:** {data.get('website_es', 'N/A')}
* **Portuguese / Brazil Portfolio:** {data.get('website_pt', 'N/A')}
* **Official WhatsApp Link (Transition):** {data.get('whatsapp_url', 'N/A')}
* **Price Range / Anchoring:** {data.get('pricing_range', 'Upon request')}

---

## 🎯 Target Niches & Ideal Customer Profile (ICP)
{chr(10).join([f"- {n}" for n in data.get('target_niches', [])])}

---

## 🧠 Mandatory Directives for AI Agents
1. **Report Visual Compliance:** Always inject the user's brand manual (`primary_color`, `secondary_color`, `dark_color`, `tagline`, `logo`) into all executive HTML/PDF reports compiled via `compile_report.py`.
2. **Block A (Praise):** Adopt the `{data.get('tone', 'consultivo')}` tone to craft a genuine, specific compliment.
3. **Block B (Diagnosis):** Connect the prospect's identified digital leak directly to the primary offer: *"{data.get('primary_service', '')}"*.
4. **Block C (Proof):** Use the matching localized link ({data.get('website_en', '')} for English, {data.get('website_es', '')} for Spanish, {data.get('website_pt', '')} for Portuguese).
5. **Block D (CTA):** Keep the conversation 100% text-driven without calls, transitioning interested leads to: *{data.get('whatsapp_url', '')}*.
"""

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"\n✅ Profile and Brand Guidelines saved successfully!")
    print(f"📁 JSON: {json_path}")
    print(f"📁 Markdown: {md_path}")
    print(f"🎨 Reports will now strictly follow your Brand Manual (Colors: {primary}, Font: {brand['font_family']}).")

def prompt_input(question: str, default: str = "") -> str:
    default_hint = f" [{default}]" if default else ""
    try:
        val = input(f"{question}{default_hint}: ").strip()
        return val if val else default
    except (KeyboardInterrupt, EOFError):
        print("\nOperation cancelled by user.")
        sys.exit(0)

def run_interactive_wizard():
    print("==================================================================")
    print("  🚀 SETUP DE PERFIL & MANUAL DA MARCA — LEAD APPROACH")
    print("  Configure sua oferta, tom de voz e a identidade visual do report.")
    print("==================================================================\n")

    current = load_profile()
    current_brand = current.get("brand", {})

    company_name = prompt_input("1. Nome da sua empresa ou agência", current.get("company_name", "VCR Softwares"))
    founder_name = prompt_input("2. Seu nome ou assinatura para mensagens", current.get("founder_name", "Equipe Comercial"))
    primary_service = prompt_input("3. Qual é o seu produto ou serviço principal?", current.get("primary_service", "Desenvolvimento Web de Alta Performance & Landing Pages"))
    secondary_services = prompt_input("4. Serviços secundários ou complementares", current.get("secondary_services", "Sistemas Web sob medida, Otimização de Velocidade"))
    value_proposition = prompt_input("5. Qual a dor que você resolve para o lead?", current.get("value_proposition", "Desenvolvemos páginas ultrarrápidas (< 1s no celular) que eliminam a perda de clientes e convertem cliques em conversas diretas no WhatsApp."))

    print("\n6. Escolha o tom de voz da abordagem:")
    print("   1) Consultivo (respeitoso, autoridade técnica, especialista)")
    print("   2) Direto (focado em ROI, velocidade, tempo)")
    print("   3) Caloroso (empático, estilo Instagram latino/estético)")
    print("   4) Executivo (formal, sóbrio, para advocacia/corporativo)")
    tone_choice = prompt_input("Escolha o tom [1-4]", "1")
    tone_map = {"1": "consultivo", "2": "direto", "3": "caloroso", "4": "executivo"}
    tone = tone_map.get(tone_choice, "consultivo")

    print("\n7. Canais ativos de prospecção (separe por vírgula):")
    channels_raw = prompt_input("Canais", ", ".join(current.get("channels", ["Instagram Direct", "WhatsApp", "LinkedIn"])))
    channels = [c.strip() for c in channels_raw.split(",") if c.strip()]

    print("\n8. Links de portfólio e prova social:")
    website_en = prompt_input("Link do seu site em Inglês (Primary/US)", current.get("website_en", "https://vcrsoftwares.com/en/"))
    website_es = prompt_input("Link do seu site em Espanhol", current.get("website_es", "https://vcrsoftwares.com/es/"))
    website_pt = prompt_input("Link do seu site em Português / Brasil", current.get("website_pt", "https://vcrsoftwares.com/"))

    print("\n9. Link de transição para o WhatsApp oficial:")
    whatsapp_url = prompt_input("Link do WhatsApp (ex: https://wa.me/5511...)", current.get("whatsapp_url", "https://wa.me/XXXXXXXXXXX"))

    print("\n10. Faixa de preço / ancoragem:")
    pricing = prompt_input("Faixa de preço", current.get("pricing_range", "Projetos sob medida a partir de $800 USD / R$ 3.000"))

    print("\n11. Nichos prioritários (separe por vírgula):")
    niches_raw = prompt_input("Nichos alvo", ", ".join(current.get("target_niches", ["Clínicas de Estética", "Advocacia", "Arquitetura", "Odontologia de Luxo", "Imobiliárias de Alto Padrão"])))
    target_niches = [n.strip() for n in niches_raw.split(",") if n.strip()]

    print("\n🎨 12. MANUAL DA MARCA & IDENTIDADE VISUAL DOS RELATÓRIOS (PDF):")
    print("   Escolha a paleta de cores da sua marca para os relatórios:")
    print("   1) Royal Amethyst (#8338ec - Roxo Moderno & Tech) [Padrão]")
    print("   2) Tech Sapphire (#2563eb - Azul Cobalto Corporativo)")
    print("   3) Emerald Prestige (#059669 - Verde Esmeralda & Crescimento)")
    print("   4) Obsidian & Gold (#b45309 - Dourado & Preto / Luxo / Advocacia)")
    print("   5) Crimson Impact (#dc2626 - Vermelho Executivo de Alto Impacto)")
    print("   6) Digitar código Hex personalizado")
    color_choice = prompt_input("Escolha a paleta [1-6]", "1")

    preset_keys = {"1": "amethyst", "2": "sapphire", "3": "emerald", "4": "gold", "5": "crimson"}
    if color_choice in preset_keys:
        chosen = BRAND_COLOR_PRESETS[preset_keys[color_choice]]
        primary_color = chosen["primary_color"]
        secondary_color = chosen["secondary_color"]
        dark_color = chosen["dark_color"]
    else:
        primary_color = prompt_input("Digite o código Hex da cor primária", current_brand.get("primary_color", "#8338ec"))
        secondary_color = prompt_input("Digite o código Hex da cor secundária/destaque", current_brand.get("secondary_color", "#3a86ff"))
        dark_color = prompt_input("Digite o código Hex da cor escura dos cabeçalhos", current_brand.get("dark_color", "#0f172a"))

    print("\n   Tipografia dos relatórios:")
    print("   1) Plus Jakarta Sans (Moderna, clean, alta legibilidade) [Padrão]")
    print("   2) Playfair Display (Editorial, sofisticação clássica, luxo)")
    print("   3) JetBrains Mono (Tech, minimalista)")
    font_choice = prompt_input("Escolha a fonte [1-3]", "1")
    font_map = {"1": "Plus Jakarta Sans", "2": "Playfair Display", "3": "JetBrains Mono"}
    font_family = font_map.get(font_choice, "Plus Jakarta Sans")

    tagline = prompt_input("   Slogan / Tagline da sua empresa para o cabeçalho do PDF", current_brand.get("tagline", "Soluções Digitais & Desenvolvimento Web de Alta Performance"))
    tag_badge = prompt_input("   Badge de Categoria superior (ex: Inteligência Comercial Outbound)", current_brand.get("tag_badge", "Inteligência Comercial Outbound"))
    logo_url = prompt_input("   URL ou caminho local do logo da sua empresa (ou deixe vazio para monograma)", current_brand.get("logo_url", ""))

    brand_data = {
        "primary_color": primary_color,
        "secondary_color": secondary_color,
        "dark_color": dark_color,
        "font_family": font_family,
        "tagline": tagline,
        "tag_badge": tag_badge,
        "logo_url": logo_url,
        "disclaimer": current_brand.get("disclaimer", "Documento Confidencial · Uso Interno de Prospecção")
    }

    profile_data = {
        "company_name": company_name,
        "founder_name": founder_name,
        "primary_service": primary_service,
        "secondary_services": secondary_services,
        "value_proposition": value_proposition,
        "tone": tone,
        "channels": channels,
        "website_en": website_en,
        "website_es": website_es,
        "website_pt": website_pt,
        "whatsapp_url": whatsapp_url,
        "pricing_range": pricing,
        "target_niches": target_niches,
        "brand": brand_data
    }

    save_profile(profile_data)

def show_profile():
    profile = load_profile()
    if os.path.exists(CONFIG_MD_PATH):
        with open(CONFIG_MD_PATH, "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print(json.dumps(profile, indent=2, ensure_ascii=False))

def main():
    parser = argparse.ArgumentParser(description="Assistente de configuração de perfil e manual da marca para a skill lead-approach.")
    parser.add_argument("--show", action="store_true", help="Exibe o perfil e manual da marca atualmente salvos em memória.")
    parser.add_argument("--name", help="Nome da empresa ou agência.")
    parser.add_argument("--founder", help="Nome do fundador ou consultor para assinatura.")
    parser.add_argument("--service", help="Produto ou serviço principal oferecido.")
    parser.add_argument("--secondary", help="Serviços secundários.")
    parser.add_argument("--value-prop", help="Proposta única de valor / dor resolvida.")
    parser.add_argument("--tone", choices=["consultivo", "direto", "caloroso", "executivo"], help="Tom de voz da abordagem.")
    parser.add_argument("--channels", help="Canais de prospecção (separados por vírgula).")
    parser.add_argument("--website", help="URL do site principal (PT).")
    parser.add_argument("--website-es", help="URL do site em Espanhol.")
    parser.add_argument("--website-en", help="URL do site em Inglês.")
    parser.add_argument("--whatsapp", help="URL do WhatsApp para fechamento (ex: https://wa.me/...).")
    parser.add_argument("--pricing", help="Faixa de preço / ancoragem.")
    parser.add_argument("--niches", help="Nichos prioritários (separados por vírgula).")
    parser.add_argument("--config-dir", help="Diretório onde salvar os arquivos de configuração.")
    # Brand guidelines CLI flags
    parser.add_argument("--brand-preset", choices=list(BRAND_COLOR_PRESETS.keys()), help="Preset de cores da marca (amethyst, sapphire, emerald, gold, crimson).")
    parser.add_argument("--brand-color", help="Cor primária da marca em formato Hex (ex: '#2563eb').")
    parser.add_argument("--brand-secondary", help="Cor secundária da marca em formato Hex (ex: '#38bdf8').")
    parser.add_argument("--brand-dark", help="Cor escura dos cartões/cabeçalho (ex: '#0f172a').")
    parser.add_argument("--brand-font", help="Fonte principal do relatório (ex: 'Plus Jakarta Sans', 'Playfair Display').")
    parser.add_argument("--brand-tagline", help="Slogan ou subtítulo da empresa para os relatórios.")
    parser.add_argument("--brand-tag", help="Badge superior da marca no relatório (ex: 'Inteligência Comercial Outbound').")
    parser.add_argument("--brand-logo", help="URL ou caminho local da imagem do logo.")
    parser.add_argument("--interactive", "-i", action="store_true", help="Executa o assistente de perguntas interativas no terminal.")
    args = parser.parse_args()

    if args.show:
        show_profile()
        return

    if args.interactive:
        run_interactive_wizard()
        return

    # Se parâmetros foram passados por CLI, salva diretamente
    if args.name or args.service or args.tone or args.website or args.whatsapp or args.channels or args.brand_color or args.brand_preset:
        current = load_profile(os.path.join(args.config_dir, "profile.json") if args.config_dir else None)
        current_brand = current.get("brand", {})

        primary_col = current_brand.get("primary_color", "#8338ec")
        secondary_col = current_brand.get("secondary_color", "#3a86ff")
        dark_col = current_brand.get("dark_color", "#0f172a")

        if args.brand_preset and args.brand_preset in BRAND_COLOR_PRESETS:
            p = BRAND_COLOR_PRESETS[args.brand_preset]
            primary_col = p["primary_color"]
            secondary_col = p["secondary_color"]
            dark_col = p["dark_color"]

        if args.brand_color:
            primary_col = args.brand_color
        if args.brand_secondary:
            secondary_col = args.brand_secondary
        if args.brand_dark:
            dark_col = args.brand_dark

        brand_data = {
            "primary_color": primary_col,
            "secondary_color": secondary_col,
            "dark_color": dark_col,
            "font_family": args.brand_font or current_brand.get("font_family", "Plus Jakarta Sans"),
            "tagline": args.brand_tagline or current_brand.get("tagline", "Soluções Digitais & Desenvolvimento Web de Alta Performance"),
            "tag_badge": args.brand_tag or current_brand.get("tag_badge", "Inteligência Comercial Outbound"),
            "logo_url": args.brand_logo or current_brand.get("logo_url", ""),
            "disclaimer": current_brand.get("disclaimer", "Documento Confidencial · Uso Interno de Prospecção")
        }

        profile_data = {
            "company_name": args.name or current.get("company_name", "VCR Softwares"),
            "founder_name": args.founder or current.get("founder_name", "Commercial Team"),
            "primary_service": args.service or current.get("primary_service", "High-Performance Web Development"),
            "secondary_services": args.secondary or current.get("secondary_services", ""),
            "value_proposition": args.value_prop or current.get("value_proposition", ""),
            "tone": args.tone or current.get("tone", "consultivo"),
            "channels": [c.strip() for c in args.channels.split(",")] if args.channels else current.get("channels", ["Instagram Direct", "WhatsApp"]),
            "website_en": args.website_en or current.get("website_en", "https://vcrsoftwares.com/en/"),
            "website_es": args.website_es or current.get("website_es", "https://vcrsoftwares.com/es/"),
            "website_pt": args.website or current.get("website_pt", "https://vcrsoftwares.com/"),
            "whatsapp_url": args.whatsapp or current.get("whatsapp_url", "https://wa.me/"),
            "pricing_range": args.pricing or current.get("pricing_range", "$800 USD / R$ 3.000"),
            "target_niches": [n.strip() for n in args.niches.split(",")] if args.niches else current.get("target_niches", ["Serviços de Alto Valor"]),
            "brand": brand_data
        }
        save_profile(profile_data, config_dir=args.config_dir)
        return

    if sys.stdin.isatty():
        run_interactive_wizard()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

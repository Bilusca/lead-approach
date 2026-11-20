#!/usr/bin/env python3
"""
Setup do Perfil de Prospecção & Manual da Marca — Lead Approach.
Configura e grava em memória permanente (config/profile.json e config/profile.md)
as informações da sua empresa/serviço, tom de voz, canais, links de portfólio e
o MANUAL DA MARCA (cores, tipografia, slogan, logo e regras visuais do relatório).

Cada setup é único e exclusivo para a marca/empresa que está operando a Skill.
Não existe configuração padrão predefinida.

Compatível com Antigravity, Claude Code e OpenAI Codex.

Uso:
    python3 setup_profile.py                      # Modo interativo (perguntas no terminal)
    python3 setup_profile.py --check              # Verifica se o perfil está configurado (exit 0/1)
    python3 setup_profile.py --show               # Exibe o perfil e manual da marca em memória
    python3 setup_profile.py --name "Empresa" --service "Serviços" --tone consultivo ... # Direto
    python3 setup_profile.py --from-json dados.json # Importa dados estruturados diretamente
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
    "sapphire": {
        "primary_color": "#2563eb",
        "secondary_color": "#0284c7",
        "dark_color": "#0f172a",
        "name": "Tech Sapphire (#2563eb - Corporate, Trust & SaaS)"
    },
    "amethyst": {
        "primary_color": "#8338ec",
        "secondary_color": "#3a86ff",
        "dark_color": "#0f172a",
        "name": "Royal Amethyst (#8338ec - Tech Modern & Creative)"
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

def is_profile_configured(profile: dict = None, config_path: str = None) -> bool:
    """
    Verifica se o perfil de negócio foi devidamente configurado.
    Retorna True apenas se possuir configured == True e campos essenciais preenchidos.
    """
    if profile is None:
        target_path = config_path or CONFIG_JSON_PATH
        if not os.path.exists(target_path):
            return False
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                profile = json.load(f)
        except Exception:
            return False

    if not isinstance(profile, dict):
        return False

    if not profile.get("configured", False):
        return False

    company = str(profile.get("company_name", "")).strip()
    service = str(profile.get("primary_service", "")).strip()

    return bool(company and service)

def load_profile(config_path: str = None) -> dict:
    """
    Carrega o perfil salvo em config/profile.json.
    Se não existir ou for inválido, retorna um modelo em branco com configured=False.
    Não existe perfil ou marca padrão.
    """
    target_path = config_path or CONFIG_JSON_PATH
    if os.path.exists(target_path):
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception as e:
            print(f"Notice: Unable to read {target_path}: {e}")

    # Perfil em branco / Não configurado (Zero config padrão)
    light_bg, light_border = derive_brand_tints("#2563eb")
    return {
        "company_name": "",
        "founder_name": "",
        "primary_service": "",
        "secondary_services": "",
        "value_proposition": "",
        "tone": "consultivo",
        "tone_description": TONE_DESCRIPTIONS["consultivo"],
        "channels": ["Instagram Direct", "WhatsApp", "LinkedIn"],
        "cta_channel": "call",
        "call_duration": "10 a 15 minutos",
        "website_en": "",
        "website_es": "",
        "website_pt": "",
        "whatsapp_url": "",
        "pricing_range": "",
        "target_niches": [],
        "brand": {
            "primary_color": "#2563eb",
            "secondary_color": "#0284c7",
            "dark_color": "#0f172a",
            "light_bg": light_bg,
            "light_border": light_border,
            "font_family": "Plus Jakarta Sans",
            "tagline": "",
            "tag_badge": "Relatório Executivo de Prospecção",
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
    if "brand" not in data or not isinstance(data["brand"], dict):
        data["brand"] = {}

    brand = data["brand"]
    primary = brand.get("primary_color", "#2563eb")
    if not brand.get("secondary_color"):
        brand["secondary_color"] = "#0284c7"
    if not brand.get("dark_color"):
        brand["dark_color"] = "#0f172a"
    if not brand.get("font_family"):
        brand["font_family"] = "Plus Jakarta Sans"
    if not brand.get("tagline"):
        brand["tagline"] = data.get("primary_service", "Soluções e Serviços de Alto Padrão")
    if not brand.get("tag_badge"):
        brand["tag_badge"] = "Relatório Executivo de Prospecção"
    if not brand.get("disclaimer"):
        brand["disclaimer"] = "Documento Confidencial · Uso Interno de Prospecção"

    # Derive tints
    bg, border = derive_brand_tints(primary)
    brand["light_bg"] = bg
    brand["light_border"] = border

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    md_content = f"""# Campaign Memory & Offer Profile (Lead Approach)

> **Gerado automaticamente por `setup_profile.py`.**  
> Agentes de IA (Antigravity, Claude Code e Codex) leem este perfil para alinhar todas as abordagens, DMs e relatórios executivos.

---

## 🏢 Identidade do Negócio & Oferta
* **Nome da Marca / Empresa:** {data.get('company_name', 'N/A')}
* **Responsável / Assinatura:** {data.get('founder_name', 'Equipe Comercial')}
* **Produto / Serviço Principal:** {data.get('primary_service', 'N/A')}
* **Serviços Secundários:** {data.get('secondary_services', 'N/A')}
* **Proposta Única de Valor (Dor Resolvida):** {data.get('value_proposition', 'N/A')}

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

## 🗣️ Tom de Voz, CTA & Estilo de Abordagem
* **Tom Configurado:** `{data.get('tone', 'consultivo').upper()}`
* **Diretriz de Voz:** {data.get('tone_description', '')}
* **Canais Ativos:** {", ".join(data.get('channels', []))}
* **Canal Preferido de Fechamento (CTA):** `{data.get('cta_channel', 'call').upper()}`
* **Duração da Call no Hook Final:** `{data.get('call_duration', '10 a 15 minutos')}`

---

## 🌐 Ecossistema de Links & Portfólio
* **Portfólio em Inglês (Primary/US):** {data.get('website_en', 'N/A')}
* **Portfólio em Espanhol:** {data.get('website_es', 'N/A')}
* **Portfólio em Português / Brasil:** {data.get('website_pt', 'N/A')}
* **Link Oficial do WhatsApp:** {data.get('whatsapp_url', 'N/A')}
* **Faixa de Preço / Ancoragem:** {data.get('pricing_range', 'Sob consulta')}

---

## 🎯 Nichos Prioritários & Perfil de Cliente Ideal (ICP)
{chr(10).join([f"- {n}" for n in data.get('target_niches', [])]) if data.get('target_niches') else "- Empresas e Profissionais de Alto Padrão"}

---

## 🧠 Diretrizes Obrigatórias para os Agentes de IA
1. **Conformidade Estrita com o Manual da Marca:** Utilizar sempre as cores (`primary_color`, `secondary_color`, `dark_color`), tipografia e slogan em todos os relatórios HTML/PDF gerados via `compile_report.py`.
2. **Hook de Abertura com a Dor do Cliente:** Começar a abordagem destacando a DOR identificada no scanner do lead (no tom `{data.get('tone', 'consultivo')}`).
3. **Solução do Setup:** Apresentar a empresa (*{data.get('company_name', '')}*) e sua solução (*{data.get('primary_service', '')}*) para resolver essa dor.
4. **Prova Social:** Inserir o link de portfólio no idioma correspondente ({data.get('website_en', '')} para EN, {data.get('website_es', '')} para ES, {data.get('website_pt', '')} para PT).
5. **Hook Provocativo de Fechamento:** Finalizar SEMPRE com uma pergunta provocativa chamando para uma conversa rápida de {data.get('call_duration', '10 a 15 minutos')} (ou para o canal pré-definido: {data.get('cta_channel', 'call')}).
"""

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"\n✅ Perfil e Manual da Marca salvos com sucesso!")
    print(f"📁 JSON: {json_path}")
    print(f"📁 Markdown: {md_path}")
    print(f"🎨 Relatórios e mensagens agora seguirão a sua marca ({data.get('company_name')}).")

def prompt_input(question: str, default: str = "", required: bool = False) -> str:
    default_hint = f" [{default}]" if default else ""
    while True:
        try:
            val = input(f"{question}{default_hint}: ").strip()
            if val:
                return val
            if default:
                return default
            if not required:
                return ""
            print("  ⚠️ Este campo é obrigatório. Por favor, forneça uma resposta.")
        except (KeyboardInterrupt, EOFError):
            print("\nOperação cancelada pelo usuário.")
            sys.exit(0)

def run_interactive_wizard(config_dir: str = None):
    print("==================================================================")
    print("  🚀 SETUP DE PERFIL & MANUAL DA MARCA — LEAD APPROACH")
    print("  Cada setup é único e exclusivo para sua marca/empresa.")
    print("  Não existe configuração padrão — responda para configurar seu negócio.")
    print("==================================================================\n")

    current = load_profile(os.path.join(config_dir, "profile.json") if config_dir else None)
    is_already_cfg = is_profile_configured(current)
    current_brand = current.get("brand", {})

    if is_already_cfg:
        print(f"ℹ️  Perfil atual detectado: {current.get('company_name')} ({current.get('primary_service')})")
        print("Pressione [Enter] em qualquer pergunta para manter o valor atual.\n")

    company_name = prompt_input(
        "1. Nome da sua empresa, agência ou marca/produto",
        current.get("company_name", ""),
        required=True
    )
    founder_name = prompt_input(
        "2. Seu nome ou assinatura para mensagens (ex: João Silva, Equipe Comercial)",
        current.get("founder_name", "Equipe Comercial")
    )
    primary_service = prompt_input(
        "3. Qual é o seu produto ou serviço principal oferecido?",
        current.get("primary_service", ""),
        required=True
    )
    secondary_services = prompt_input(
        "4. Serviços secundários ou complementares (opcional)",
        current.get("secondary_services", "")
    )
    value_proposition = prompt_input(
        "5. Qual a Dor principal que você resolve para o seu lead? (Proposta única de valor)",
        current.get("value_proposition", "")
    )

    print("\n6. Escolha o tom de voz da abordagem:")
    print("   1) Consultivo (respeitoso, autoridade técnica, especialista) [Recomendado]")
    print("   2) Direto (focado em ROI, velocidade, tempo e objetividade)")
    print("   3) Caloroso (empático, estilo Instagram latino/estético)")
    print("   4) Executivo (formal, sóbrio, para advocacia/corporativo)")
    tone_default = "1"
    if current.get("tone") == "direto":
        tone_default = "2"
    elif current.get("tone") == "caloroso":
        tone_default = "3"
    elif current.get("tone") == "executivo":
        tone_default = "4"
    tone_choice = prompt_input("Escolha o tom [1-4]", tone_default)
    tone_map = {"1": "consultivo", "2": "direto", "3": "caloroso", "4": "executivo"}
    tone = tone_map.get(tone_choice, "consultivo")

    print("\n7. Público-alvo / Nichos prioritários que você atende (separe por vírgula):")
    niches_default = ", ".join(current.get("target_niches", [])) if current.get("target_niches") else "Empresas e Profissionais de Alto Padrão"
    niches_raw = prompt_input("Nichos alvo", niches_default)
    target_niches = [n.strip() for n in niches_raw.split(",") if n.strip()]

    print("\n8. Canais ativos de prospecção (separe por vírgula):")
    channels_default = ", ".join(current.get("channels", [])) if current.get("channels") else "Instagram Direct, WhatsApp, LinkedIn"
    channels_raw = prompt_input("Canais", channels_default)
    channels = [c.strip() for c in channels_raw.split(",") if c.strip()]

    print("\n9. Links de portfólio e prova social:")
    website_pt = prompt_input("Link do seu site/portfólio em Português / Brasil", current.get("website_pt", ""))
    website_en = prompt_input("Link do seu site em Inglês (Primary/US - opcional)", current.get("website_en", ""))
    website_es = prompt_input("Link do seu site em Espanhol (opcional)", current.get("website_es", ""))

    print("\n10. Link ou número de transição para o WhatsApp oficial:")
    whatsapp_url = prompt_input("Link do WhatsApp (ex: https://wa.me/55...)", current.get("whatsapp_url", ""))

    print("\n11. Canal preferido de fechamento no hook final da mensagem:")
    print("   1) Call (Reunião rápida de 10 a 15 min) [Padrão de alta conversão]")
    print("   2) WhatsApp (Continuar a conversa no WhatsApp oficial)")
    print("   3) Direct (Responder diretamente por aqui no Direct/LinkedIn)")
    print("   4) Flexível (A critério da resposta)")
    cta_default = "1"
    if current.get("cta_channel") == "whatsapp":
        cta_default = "2"
    elif current.get("cta_channel") == "direct":
        cta_default = "3"
    elif current.get("cta_channel") == "flexible":
        cta_default = "4"
    cta_choice = prompt_input("Escolha o canal de fechamento [1-4]", cta_default)
    cta_map = {"1": "call", "2": "whatsapp", "3": "direct", "4": "flexible"}
    cta_channel = cta_map.get(cta_choice, "call")

    call_duration = current.get("call_duration", "10 a 15 minutos")
    if cta_channel == "call":
        call_duration = prompt_input("Duração sugerida da call no hook final (ex: '10 minutos', '10 a 15 minutos')", call_duration)

    print("\n12. Faixa de preço / ancoragem comercial (opcional):")
    pricing = prompt_input("Faixa de preço", current.get("pricing_range", ""))

    print("\n🎨 13. MANUAL DA MARCA & IDENTIDADE VISUAL DOS RELATÓRIOS (PDF):")
    print("   Escolha a paleta de cores da sua marca para os relatórios executivos:")
    print("   1) Tech Sapphire (#2563eb - Azul Cobalto, Confiança & SaaS) [Padrão]")
    print("   2) Royal Amethyst (#8338ec - Roxo Moderno & Tech)")
    print("   3) Emerald Prestige (#059669 - Verde Esmeralda & Crescimento)")
    print("   4) Obsidian & Gold (#b45309 - Dourado & Preto / Luxo / Advocacia)")
    print("   5) Crimson Impact (#dc2626 - Vermelho Executivo de Alto Impacto)")
    print("   6) Digitar código Hex personalizado")
    color_choice = prompt_input("Escolha a paleta [1-6]", "1")

    preset_keys = {"1": "sapphire", "2": "amethyst", "3": "emerald", "4": "gold", "5": "crimson"}
    if color_choice in preset_keys:
        chosen = BRAND_COLOR_PRESETS[preset_keys[color_choice]]
        primary_color = chosen["primary_color"]
        secondary_color = chosen["secondary_color"]
        dark_color = chosen["dark_color"]
    else:
        primary_color = prompt_input("Digite o código Hex da cor primária", current_brand.get("primary_color", "#2563eb"))
        secondary_color = prompt_input("Digite o código Hex da cor secundária/destaque", current_brand.get("secondary_color", "#0284c7"))
        dark_color = prompt_input("Digite o código Hex da cor escura dos cabeçalhos", current_brand.get("dark_color", "#0f172a"))

    print("\n   Tipografia dos relatórios:")
    print("   1) Plus Jakarta Sans (Moderna, clean, alta legibilidade) [Padrão]")
    print("   2) Playfair Display (Editorial, sofisticação clássica, luxo)")
    print("   3) JetBrains Mono (Tech, minimalista)")
    font_choice = prompt_input("Escolha a fonte [1-3]", "1")
    font_map = {"1": "Plus Jakarta Sans", "2": "Playfair Display", "3": "JetBrains Mono"}
    font_family = font_map.get(font_choice, "Plus Jakarta Sans")

    tagline_default = current_brand.get("tagline") or primary_service
    tagline = prompt_input("   Slogan / Tagline da sua empresa para o cabeçalho do PDF", tagline_default)
    tag_badge = prompt_input("   Badge de Categoria superior (ex: Relatório Executivo de Prospecção)", current_brand.get("tag_badge", "Relatório Executivo de Prospecção"))
    logo_url = prompt_input("   URL ou caminho local do logo da sua empresa (deixe vazio para monograma)", current_brand.get("logo_url", ""))

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
        "cta_channel": cta_channel,
        "call_duration": call_duration,
        "website_en": website_en,
        "website_es": website_es,
        "website_pt": website_pt,
        "whatsapp_url": whatsapp_url,
        "pricing_range": pricing,
        "target_niches": target_niches,
        "brand": brand_data
    }

    save_profile(profile_data, config_dir=config_dir)

def show_profile(config_dir: str = None):
    md_path = os.path.join(config_dir or DEFAULT_CONFIG_DIR, "profile.md")
    json_path = os.path.join(config_dir or DEFAULT_CONFIG_DIR, "profile.json")
    if os.path.exists(md_path):
        with open(md_path, "r", encoding="utf-8") as f:
            print(f.read())
    elif os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print("ℹ️  Nenhum perfil de prospecção configurado ainda em config/profile.json.")
        print("👉 Execute `python3 scripts/setup_profile.py` para configurar seu perfil.")

def main():
    parser = argparse.ArgumentParser(description="Assistente de configuração de perfil e manual da marca para a skill lead-approach.")
    parser.add_argument("--check", action="store_true", help="Verifica se o perfil está configurado (retorna exit code 0 se sim, 1 se não).")
    parser.add_argument("--show", action="store_true", help="Exibe o perfil e manual da marca atualmente salvos em memória.")
    parser.add_argument("--from-json", help="Caminho de arquivo JSON estruturado para salvar diretamente sem interação.")
    parser.add_argument("--name", help="Nome da empresa, agência ou marca/produto.")
    parser.add_argument("--founder", help="Nome do fundador, consultor ou equipe para assinatura.")
    parser.add_argument("--service", help="Produto ou serviço principal oferecido.")
    parser.add_argument("--secondary", help="Serviços secundários ou complementares.")
    parser.add_argument("--value-prop", help="Proposta única de valor / dor resolvida.")
    parser.add_argument("--tone", choices=["consultivo", "direto", "caloroso", "executivo"], help="Tom de voz da abordagem.")
    parser.add_argument("--channels", help="Canais de prospecção (separados por vírgula).")
    parser.add_argument("--cta-channel", choices=["call", "whatsapp", "direct", "chat", "flexible"], default=None, help="Canal de fechamento do hook final: call (padrão), whatsapp, direct, chat, flexible.")
    parser.add_argument("--call-duration", help="Duração sugerida da call no hook de fechamento (ex: '10 minutos', '10 a 15 minutos').")
    parser.add_argument("--website", help="URL do site principal (PT).")
    parser.add_argument("--website-es", help="URL do site em Espanhol.")
    parser.add_argument("--website-en", help="URL do site em Inglês.")
    parser.add_argument("--whatsapp", help="URL do WhatsApp para fechamento (ex: https://wa.me/...).")
    parser.add_argument("--pricing", help="Faixa de preço / ancoragem.")
    parser.add_argument("--niches", help="Nichos prioritários (separados por vírgula).")
    parser.add_argument("--config-dir", help="Diretório onde salvar os arquivos de configuração.")
    # Brand guidelines CLI flags
    parser.add_argument("--brand-preset", choices=list(BRAND_COLOR_PRESETS.keys()), help="Preset de cores da marca (sapphire, amethyst, emerald, gold, crimson).")
    parser.add_argument("--brand-color", help="Cor primária da marca em formato Hex (ex: '#2563eb').")
    parser.add_argument("--brand-secondary", help="Cor secundária da marca em formato Hex (ex: '#0284c7').")
    parser.add_argument("--brand-dark", help="Cor escura dos cartões/cabeçalho (ex: '#0f172a').")
    parser.add_argument("--brand-font", help="Fonte principal do relatório (ex: 'Plus Jakarta Sans', 'Playfair Display').")
    parser.add_argument("--brand-tagline", help="Slogan ou subtítulo da empresa para os relatórios.")
    parser.add_argument("--brand-tag", help="Badge superior da marca no relatório (ex: 'Relatório Executivo de Prospecção').")
    parser.add_argument("--brand-logo", help="URL ou caminho local da imagem do logo.")
    parser.add_argument("--interactive", "-i", action="store_true", help="Executa o assistente de perguntas interativas no terminal.")
    args = parser.parse_args()

    # 1. Checagem rápida de status
    if args.check:
        cfg_path = os.path.join(args.config_dir, "profile.json") if args.config_dir else None
        if is_profile_configured(config_path=cfg_path):
            p = load_profile(cfg_path)
            print(f"CONFIGURED: {p.get('company_name')} | {p.get('primary_service')}")
            sys.exit(0)
        else:
            print("NOT_CONFIGURED: Nenhum perfil de negócio configurado. Execute setup_profile.py para configurar.")
            sys.exit(1)

    # 2. Exibição de perfil
    if args.show:
        show_profile(args.config_dir)
        return

    # 3. Importação direta via JSON
    if args.from_json:
        if not os.path.exists(args.from_json):
            print(f"❌ Erro: Arquivo JSON não encontrado: {args.from_json}")
            sys.exit(1)
        with open(args.from_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        save_profile(data, config_dir=args.config_dir)
        return

    # 4. Configuração direta por argumentos CLI
    if args.name or args.service or args.tone or args.website or args.whatsapp or args.channels or args.brand_color or args.brand_preset:
        current = load_profile(os.path.join(args.config_dir, "profile.json") if args.config_dir else None)
        current_brand = current.get("brand", {})

        primary_col = current_brand.get("primary_color", "#2563eb")
        secondary_col = current_brand.get("secondary_color", "#0284c7")
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
            "tagline": args.brand_tagline or current_brand.get("tagline", args.service or ""),
            "tag_badge": args.brand_tag or current_brand.get("tag_badge", "Relatório Executivo de Prospecção"),
            "logo_url": args.brand_logo or current_brand.get("logo_url", ""),
            "disclaimer": current_brand.get("disclaimer", "Documento Confidencial · Uso Interno de Prospecção")
        }

        profile_data = {
            "company_name": args.name or current.get("company_name", ""),
            "founder_name": args.founder or current.get("founder_name", "Equipe Comercial"),
            "primary_service": args.service or current.get("primary_service", ""),
            "secondary_services": args.secondary or current.get("secondary_services", ""),
            "value_proposition": args.value_prop or current.get("value_proposition", ""),
            "tone": args.tone or current.get("tone", "consultivo"),
            "channels": [c.strip() for c in args.channels.split(",")] if args.channels else current.get("channels", ["Instagram Direct", "WhatsApp", "LinkedIn"]),
            "cta_channel": args.cta_channel or current.get("cta_channel", "call"),
            "call_duration": args.call_duration or current.get("call_duration", "10 a 15 minutos"),
            "website_en": args.website_en or current.get("website_en", ""),
            "website_es": args.website_es or current.get("website_es", ""),
            "website_pt": args.website or current.get("website_pt", ""),
            "whatsapp_url": args.whatsapp or current.get("whatsapp_url", ""),
            "pricing_range": args.pricing or current.get("pricing_range", ""),
            "target_niches": [n.strip() for n in args.niches.split(",")] if args.niches else current.get("target_niches", []),
            "brand": brand_data
        }
        save_profile(profile_data, config_dir=args.config_dir)
        return

    # 5. Modo interativo (se solicitado por flag ou se o terminal for TTY interativo)
    if args.interactive or sys.stdin.isatty():
        run_interactive_wizard(config_dir=args.config_dir)
        return

    # 6. Fallback não interativo sem argumentos
    if is_profile_configured():
        show_profile(args.config_dir)
    else:
        print("==================================================================")
        print("  ⚠️  SETUP DO PERFIL NECESSÁRIO — LEAD APPROACH")
        print("==================================================================")
        print("Nenhum perfil de negócio configurado em config/profile.json.")
        print("Cada setup é único e exclusivo para sua marca/empresa.")
        print("Não existe configuração padrão predefinida.\n")
        print("👉 Execute interativamente no terminal:")
        print("   python3 scripts/setup_profile.py\n")
        print("👉 Ou passe os dados diretamente:")
        print("   python3 scripts/setup_profile.py --name \"Sua Empresa\" --service \"Seus Serviços\" --tone consultivo ...\n")
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()

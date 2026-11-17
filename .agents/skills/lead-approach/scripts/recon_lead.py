#!/usr/bin/env python3
"""
Recon Lead — Ferramenta de Varredura e Diagnóstico Técnico de Websites e Links de Bio.
Compatível com Antigravity, Claude Code e OpenAI Codex.
Não requer dependências externas (utiliza biblioteca padrão do Python 3).

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
        "description": None,
        "detected_cms": [],
        "detected_tools": [],
        "friction_points": [],
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
        return result
    except urllib.error.URLError as e:
        result["error"] = f"Connection Error: {e.reason}"
        return result
    except Exception as e:
        result["error"] = f"Unexpected Error: {str(e)}"
        return result

    # Meta Title
    title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    if title_match:
        result["title"] = re.sub(r'\s+', ' ', title_match.group(1)).strip()

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

    # Friction Diagnosis & Strategic Angles
    if "Linktree" in result["detected_cms"] or "Beacons" in result["detected_cms"] or "Bento" in result["detected_cms"]:
        result["friction_points"].append("Generic link aggregator (Linktree/Beacons) detected: high decision fatigue and up to 50% drop-off.")
        result["recommended_angle"] = "Replace generic linktree with a dedicated, ultra-fast mobile landing page featuring a 1-tap direct inquiry route."

    if any(b in result["detected_tools"] for b in ["Acuity Scheduling", "Booksy", "Fresha", "Calendly"]):
        result["friction_points"].append("Direct-to-calendar route: forces prospective clients into a cold booking calendar before presenting authority or social proof.")
        if not result["recommended_angle"]:
            result["recommended_angle"] = "Introduce an authority transformation showcase with before/after results prior to calendar booking."

    if result["response_time_ms"] and result["response_time_ms"] > 1800:
        result["friction_points"].append(f"Elevated server response time ({result['response_time_ms']}ms TTFB): mobile traffic experiences significant bounce rates above 1.5s.")
        if not result["recommended_angle"]:
            result["recommended_angle"] = "Optimize speed for sub-second loading (< 1s) to retain high-intent mobile visitors from social media."

    if "WordPress" in result["detected_cms"] and "Elementor (WP)" in result["detected_cms"]:
        result["friction_points"].append("WordPress + Elementor stack detected: typically prone to DOM bloating and render-blocking script latency on mobile 4G/5G.")

    if not result["friction_points"]:
        result["friction_points"].append("Standard functional layout; prime opportunity lies in 1-tap direct messaging funnels and interactive social proof.")
        result["recommended_angle"] = "Mobile acceleration and frictionless 1-tap direct consultation funnel."

    return result

def format_markdown(data: dict) -> str:
    md = []
    md.append(f"# 🔍 Technical Website & Bio Audit (Lead Recon)")
    md.append(f"**Target URL:** `{data['url']}`  ")
    if data['final_url'] != data['url']:
        md.append(f"**Redirects To:** `{data['final_url']}`  ")
    md.append(f"**HTTP Status:** `{data['status_code']}` | **Initial Latency (TTFB):** `{data['response_time_ms']} ms`  \n")

    if data.get("title"):
        md.append(f"**Page Title:** {data['title']}  ")
    if data.get("description"):
        md.append(f"**Meta Description:** {data['description']}  ")
    md.append("")

    md.append("### 🛠️ Detected Stack & Platforms")
    cms_str = ", ".join(data["detected_cms"]) if data["detected_cms"] else "Custom / Static / Unidentified"
    tools_str = ", ".join(data["detected_tools"]) if data["detected_tools"] else "No third-party booking tools detected"
    md.append(f"- **CMS / Builder:** {cms_str}")
    md.append(f"- **Booking & Inquiry Tools:** {tools_str}")
    md.append(f"- **Mobile Responsiveness:** {'✅ Viewport Tag Present' if data['has_viewport'] else '⚠️ Missing or Broken Viewport Tag'}")
    md.append("")

    md.append("### ⚠️ Identified Digital Bottlenecks")
    for fp in data["friction_points"]:
        md.append(f"- {fp}")
    md.append("")

    md.append("### 🎯 Recommended Outreach Angle")
    md.append(f"> **{data['recommended_angle']}**")
    md.append("")
    md.append("---")
    md.append("💡 *Use these specific facts in Block B of the outreach message.*")
    return "\n".join(md)

def main():
    parser = argparse.ArgumentParser(description="Varredura técnica de websites e links de bio para cold outreach.")
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

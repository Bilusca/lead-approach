#!/usr/bin/env python3
"""
generate_v22_carousel.py
Compiles a 6-slide Neo-Brutalist LinkedIn Carousel (1080x1350, 4:5 portrait)
for lead-approach v2.2 into individual PNGs and a combined PDF.
"""

import os
import sys
import subprocess
import shutil

CAROUSEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "carousel", "v22"))
os.makedirs(CAROUSEL_DIR, exist_ok=True)

SLIDES_DATA = [
    # SLIDE 1: Cover
    {
        "id": "slide_01",
        "bg": "#FFE600",
        "badge_bg": "#8B5CF6",
        "badge_color": "#FFFFFF",
        "badge_text": "★ WHAT'S NEW // v2.3 UPDATE",
        "slide_num": "01 / 06",
        "title": "STOP MESSAGING AN @HANDLE. OUTBOUND JUST GOT HUMAN.",
        "content_html": """
        <div class="card neo-card-white" style="margin-top: 25px;">
            <div class="card-header-tag red-tag">THE BOT OUTBOUND EPIDEMIC</div>
            <div class="pain-list">
                <div class="pain-item">
                    <span class="cross">✕</span>
                    <div><strong>"Olá @clinica_xyz, tudo bem?"</strong> makes you sound like a cheap automated spam bot.</div>
                </div>
                <div class="pain-item">
                    <span class="cross">✕</span>
                    <div><strong>Treating high-ticket specialists as handles</strong> slashes open and reply rates to zero.</div>
                </div>
                <div class="pain-item">
                    <span class="cross">✕</span>
                    <div><strong>Generic AI scrapers</strong> ignore the real humans and teams behind businesses.</div>
                </div>
            </div>
        </div>

        <div class="card neo-card-black" style="margin-top: 30px;">
            <div class="card-title-neon">INTRODUCING LEAD-APPROACH v2.3:</div>
            <div class="card-sub-neon">
                Automatic <strong>person vs. company AI recon</strong>, genuine name extraction, <strong>Tailwind CSS HTML dashboards</strong>, and instant Trello Kanban export.
            </div>
        </div>
        """,
        "footer_badge": "SWIPE TO SEE WHAT'S NEW ➔",
        "footer_badge_bg": "#000000",
        "footer_badge_color": "#FFE600"
    },

    # SLIDE 2: Feature 1 - Entity Intelligence
    {
        "id": "slide_02",
        "bg": "#00F59B",
        "badge_bg": "#000000",
        "badge_color": "#00F59B",
        "badge_text": "01 // ENTITY INTELLIGENCE",
        "slide_num": "02 / 06",
        "title": "NOBODY TALKS TO AN ARROBA. MEET REAL HUMANS.",
        "content_html": """
        <div class="terminal-box" style="margin-top: 20px;">
            <div class="terminal-bar">
                <span class="dot dot-red"></span>
                <span class="dot dot-yellow"></span>
                <span class="dot dot-green"></span>
                <span class="terminal-title">bash — lead-approach recon @dr_joao_silva</span>
            </div>
            <div class="terminal-code" style="font-size: 20px;">
                <span class="prompt">$</span> lead-approach recon @dr_joao_silva<br>
                <span style="color:#00F59B; font-weight:800;">✔ Person Classified:</span> Dr. João Silva (Specialist)<br>
                <span style="color:#FFE600; font-weight:800;">✔ Grammar:</span> Singular & personal ("Olá, Dr. João! Olhei seus serviços...")
            </div>
        </div>

        <div class="feature-grid" style="margin-top: 22px;">
            <div class="card neo-card-white">
                <div class="card-num">01</div>
                <div>
                    <div class="card-heading">SPECIALIST / PERSON RECON</div>
                    <p>Detects doctors, lawyers, architects, and founders from bios and schemas. Speaks directly to the person in the singular.</p>
                </div>
            </div>
            <div class="card neo-card-white">
                <div class="card-num">02</div>
                <div>
                    <div class="card-heading">CLINIC & COMPANY RECON</div>
                    <p>Identifies multi-doctor clinics and corporate firms (e.g. <em>Lumina Odontologia</em>) and addresses the team in the plural.</p>
                </div>
            </div>
            <div class="card neo-card-white">
                <div class="card-num">03</div>
                <div>
                    <div class="card-heading">TRI-LINGUAL FLUENCY (PT / EN / ES)</div>
                    <p>Native grammar adaptation across Portuguese, English, and Spanish with zero awkward translation artifacts.</p>
                </div>
            </div>
        </div>

        <div class="highlight-banner" style="background: #FFE600; margin-top: 20px;">
            ⚡ <strong>Natural Human Outreach:</strong> Prospects feel recognized as real experts, not as rows in a scraped spreadsheet.
        </div>
        """,
        "footer_badge": "NEXT: INTERACTIVE DASHBOARDS ➔",
        "footer_badge_bg": "#000000",
        "footer_badge_color": "#00F59B"
    },

    # SLIDE 3: Feature 2 - Tailwind CSS & Clickable Links
    {
        "id": "slide_03",
        "bg": "#00F0FF",
        "badge_bg": "#FF4B72",
        "badge_color": "#FFFFFF",
        "badge_text": "02 // SPEED & MODERN UI",
        "slide_num": "03 / 06",
        "title": "TAILWIND CSS DASHBOARD & CLICKABLE PDF DOSSIERS",
        "content_html": """
        <div class="card neo-card-white" style="margin-top: 25px;">
            <div class="card-header-tag blue-tag">MODERN UI & ZERO FRICTION</div>
            <div class="audit-item">
                <span class="audit-badge blue-bg">TAILWIND CSS</span>
                <span>HTML dashboards run on <strong>Tailwind CSS</strong>, strictly encapsulated in <code>&lt;main class="container mx-auto"&gt;</code> with dynamic brand theme config.</span>
            </div>
            <div class="audit-item">
                <span class="audit-badge purple-bg">CLICKABLE IG</span>
                <span>Handles in PDF and HTML now link directly to official profiles (<code>instagram.com/...</code>) without URL shorteners.</span>
            </div>
            <div class="audit-item">
                <span class="audit-badge green-bg">1-CLICK COPY</span>
                <span>Interactive dashboard features 1-click clipboard copy buttons with instant visual toast feedback.</span>
            </div>
            <div class="audit-item">
                <span class="audit-badge orange-bg">MULTICHANNEL</span>
                <span>Immediate direct action links to WhatsApp (<code>wa.me/</code>), Google Maps, Phone, Email, and LinkedIn.</span>
            </div>
        </div>

        <div class="highlight-banner" style="background: #00F59B; margin-top: 25px;">
            🎯 <strong>Modern App Experience:</strong> Review dossiers in a clean Tailwind UI and fire personalized DMs in seconds.
        </div>
        """,
        "footer_badge": "NEXT: 360° TRELLO SUITE ➔",
        "footer_badge_bg": "#000000",
        "footer_badge_color": "#00F0FF"
    },

    # SLIDE 4: Feature 3 - Trello Kanban Suite
    {
        "id": "slide_04",
        "bg": "#B8A4FF",
        "badge_bg": "#000000",
        "badge_color": "#B8A4FF",
        "badge_text": "03 // KANBAN WORKFLOW",
        "slide_num": "04 / 06",
        "title": "GENERATE 50 TRELLO LEADS IN 1 SECOND FLAT",
        "content_html": """
        <div class="terminal-box" style="margin-top: 20px;">
            <div class="terminal-bar">
                <span class="dot dot-red"></span>
                <span class="dot dot-yellow"></span>
                <span class="dot dot-green"></span>
                <span class="terminal-title">bash — lead-approach batch list</span>
            </div>
            <div class="terminal-code" style="font-size: 19px; line-height: 1.45;">
                <span class="prompt">$</span> lead-approach list leads.pdf --output roadmap.pdf<br>
                <span style="color:#00F59B;">✔ Generated:</span> report/roadmap-2026-11-20/<br>
                &nbsp;&nbsp;├── roadmap.pdf + roadmap.html<br>
                &nbsp;&nbsp;└── <strong>roadmap-trello.md + .csv + .json</strong>
            </div>
        </div>

        <div class="blocks-container" style="margin-top: 22px;">
            <div class="block-card block-a">
                <div class="block-label">SECTION 1 // 1-SECOND BATCH CARDS</div>
                <div class="block-desc">Copy and paste all lead titles into Trello at once. Trello prompts <em>"Create 50 cards?"</em> -> Click YES.</div>
            </div>
            <div class="block-card block-b">
                <div class="block-label">SECTION 2 // RICH CARDS MARKDOWN</div>
                <div class="block-desc">Ready card descriptions with mapped contacts, diagnosed core pain, Day 1 Hook DM, Day 4 Follow-up & checklists.</div>
            </div>
            <div class="block-card block-c">
                <div class="block-label">CSV & JSON EXPORTS // AUTOMATION READY</div>
                <div class="block-desc">Structured formats ready for Trello Power-Ups, Zapier, Make, or custom CRM webhook pipelines.</div>
            </div>
        </div>
        """,
        "footer_badge": "NEXT: LOCAL PRIVACY & REPORTS ➔",
        "footer_badge_bg": "#000000",
        "footer_badge_color": "#B8A4FF"
    },

    # SLIDE 5: Feature 4 - Isolated Reports & Privacy
    {
        "id": "slide_05",
        "bg": "#FF8DA1",
        "badge_bg": "#000000",
        "badge_color": "#FFE600",
        "badge_text": "04 // ENTERPRISE SECURITY",
        "slide_num": "05 / 06",
        "title": "ISOLATED REPORT FOLDERS & ZERO LOCAL LEAKS",
        "content_html": """
        <div class="card neo-card-white" style="margin-top: 25px;">
            <div class="card-header-tag purple-tag">CLEAN ARCHITECTURE & ABSOLUTE PRIVACY</div>
            <div class="dossier-features">
                <div class="d-item">
                    <span class="check">✔</span>
                    <div><strong>Dedicated Report Folders:</strong> Every execution creates an isolated date-stamped folder (<code>report/&lt;name&gt;-&lt;date&gt;/</code>) keeping outputs organized.</div>
                </div>
                <div class="d-item">
                    <span class="check">✔</span>
                    <div><strong>Strict Local Profile Privacy:</strong> Your business memory (<code>profile.json</code> / <code>profile.md</code>) is 100% blocked from Git and NPM packages.</div>
                </div>
                <div class="d-item">
                    <span class="check">✔</span>
                    <div><strong>Full Brand Manual Compliance:</strong> Renders dossiers in your exact brand colors (like VCR's Electric Violet <code>#8338ec</code>), typography, and dynamic monogram.</div>
                </div>
            </div>
        </div>

        <div class="highlight-banner" style="background: #FFE600; margin-top: 30px;">
            🔒 <strong>Confidential By Design:</strong> Client research, private phone numbers, and pitch archives stay exclusively on your local machine.
        </div>
        """,
        "footer_badge": "NEXT: RUN IT TODAY ➔",
        "footer_badge_bg": "#000000",
        "footer_badge_color": "#FFFFFF"
    },

    # SLIDE 6: CTA / Deploy
    {
        "id": "slide_06",
        "bg": "#FFE600",
        "badge_bg": "#000000",
        "badge_color": "#FFE600",
        "badge_text": "DEPLOY TODAY // v2.3 LIVE ON NPM",
        "slide_num": "06 / 06",
        "title": "UPGRADE YOUR OUTBOUND ENGINE IN 30 SECONDS",
        "content_html": """
        <div class="terminal-box" style="margin-top: 25px;">
            <div class="terminal-bar">
                <span class="dot dot-red"></span>
                <span class="dot dot-yellow"></span>
                <span class="dot dot-green"></span>
                <span class="terminal-title">bash — instant execution</span>
            </div>
            <div class="terminal-code" style="font-size: 24px; line-height: 1.6;">
                <span class="comment"># Zero-install execution via npx:</span><br>
                <span class="prompt">$</span> <strong style="color: #00F59B;">npx lead-approach install --all</strong><br><br>
                <span class="comment"># Or update globally via npm:</span><br>
                <span class="prompt">$</span> npm install -g lead-approach@latest
            </div>
        </div>

        <div class="agent-badges" style="margin-top: 25px;">
            <div class="agent-pill">
                <span class="agent-name">Google Antigravity</span>
                <span class="agent-sub">Gemini 2.0 / Pro</span>
            </div>
            <div class="agent-pill">
                <span class="agent-name">Anthropic Claude</span>
                <span class="agent-sub">Claude Code CLI</span>
            </div>
            <div class="agent-pill">
                <span class="agent-name">OpenAI Codex</span>
                <span class="agent-sub">Agent Skills AAIF</span>
            </div>
        </div>

        <div class="card neo-card-black" style="margin-top: 30px; text-align: center;">
            <div style="font-size: 26px; font-weight: 800; color: #FFE600;">
                ★ 100% Free & Open-Source on GitHub & NPM
            </div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 20px; color: #FFFFFF; margin-top: 8px;">
                github.com/Bilusca/lead-approach · npmjs.com/package/lead-approach
            </div>
        </div>
        """,
        "footer_badge": "REPOST & SHARE ♻️",
        "footer_badge_bg": "#FF4B72",
        "footer_badge_color": "#FFFFFF"
    }
]

SLIDE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;800;900&family=JetBrains+Mono:wght@600;700;800&display=swap');

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    width: 1080px;
    height: 1350px;
    overflow: hidden;
    font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
    background-color: var(--slide-bg);
    background-image: radial-gradient(#000000 2px, transparent 2px);
    background-size: 26px 26px;
    color: #000000;
}

.slide-container {
    width: 1080px;
    height: 1350px;
    padding: 65px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    position: relative;
    border: 10px solid #000000;
}

/* Header */
.header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.top-badge {
    display: inline-block;
    padding: 10px 22px;
    font-size: 16px;
    font-weight: 900;
    letter-spacing: 1.5px;
    border: 4px solid #000000;
    box-shadow: 4px 4px 0px #000000;
    transform: rotate(-1.5deg);
    text-transform: uppercase;
}

.counter-badge {
    background: #FFFFFF;
    color: #000000;
    font-family: 'JetBrains Mono', monospace;
    font-size: 18px;
    font-weight: 800;
    padding: 10px 18px;
    border: 4px solid #000000;
    box-shadow: 4px 4px 0px #000000;
}

/* Main Title */
.main-title {
    font-size: 52px;
    font-weight: 900;
    line-height: 1.12;
    letter-spacing: -1.5px;
    text-transform: uppercase;
    margin-top: 20px;
    color: #000000;
    text-shadow: 2px 2px 0px rgba(255,255,255,0.8);
}

/* Middle Content */
.content-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

/* Neo-Cards */
.card {
    border: 4px solid #000000;
    padding: 26px 30px;
    position: relative;
}

.neo-card-white {
    background: #FFFFFF;
    box-shadow: 8px 8px 0px #000000;
}

.neo-card-black {
    background: #000000;
    color: #FFFFFF;
    box-shadow: 8px 8px 0px #FFFFFF, 12px 12px 0px #000000;
}

.card-title-neon {
    font-size: 28px;
    font-weight: 900;
    color: #FFE600;
    letter-spacing: 0.5px;
}

.card-sub-neon {
    font-size: 22px;
    line-height: 1.45;
    margin-top: 10px;
    color: #E2E8F0;
}

.card-header-tag {
    display: inline-block;
    padding: 6px 14px;
    font-size: 14px;
    font-weight: 900;
    letter-spacing: 1px;
    border: 3px solid #000000;
    margin-bottom: 16px;
    box-shadow: 3px 3px 0px #000000;
}

.red-tag { background: #FF4B72; color: #FFFFFF; }
.blue-tag { background: #00F0FF; color: #000000; }
.purple-tag { background: #8B5CF6; color: #FFFFFF; }

/* Pain List */
.pain-list {
    display: flex;
    flex-direction: column;
    gap: 14px;
}

.pain-item {
    display: flex;
    align-items: center;
    gap: 16px;
    font-size: 22px;
    line-height: 1.35;
}

.cross {
    background: #FF4B72;
    color: #FFFFFF;
    width: 36px;
    height: 36px;
    min-width: 36px;
    border: 3px solid #000000;
    box-shadow: 3px 3px 0px #000000;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 20px;
}

/* Terminal Box */
.terminal-box {
    background: #000000;
    border: 4px solid #000000;
    box-shadow: 8px 8px 0px #000000;
    overflow: hidden;
}

.terminal-bar {
    background: #1A1A1A;
    padding: 10px 16px;
    border-bottom: 3px solid #333333;
    display: flex;
    align-items: center;
    gap: 10px;
}

.dot {
    width: 13px;
    height: 13px;
    border-radius: 50%;
    border: 2px solid #000000;
}

.dot-red { background: #FF5F56; }
.dot-yellow { background: #FFBD2E; }
.dot-green { background: #27C93F; }

.terminal-title {
    color: #A0AEC0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    margin-left: 8px;
    font-weight: 700;
}

.terminal-code {
    padding: 18px 22px;
    color: #FFFFFF;
    font-family: 'JetBrains Mono', monospace;
    font-size: 21px;
    line-height: 1.45;
}

.terminal-code .prompt { color: #00F59B; font-weight: 800; }
.terminal-code .comment { color: #718096; font-size: 17px; }

/* Feature Grid */
.feature-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 14px;
}

.feature-grid .card {
    padding: 16px 20px;
    display: flex;
    align-items: flex-start;
    gap: 16px;
}

.card-num {
    background: #000000;
    color: #FFE600;
    font-family: 'JetBrains Mono', monospace;
    font-size: 16px;
    font-weight: 900;
    padding: 5px 10px;
    border: 3px solid #000000;
}

.card-heading {
    font-size: 18px;
    font-weight: 900;
    margin-bottom: 4px;
}

.feature-grid p {
    font-size: 17px;
    line-height: 1.35;
    color: #2D3748;
}

.highlight-banner {
    border: 4px solid #000000;
    box-shadow: 6px 6px 0px #000000;
    padding: 16px 22px;
    font-size: 19px;
    line-height: 1.4;
}

/* Audit Items */
.audit-item {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 12px 0;
    border-bottom: 2px dashed #CBD5E0;
    font-size: 19px;
    line-height: 1.35;
}

.audit-item:last-child { border-bottom: none; }

.audit-badge {
    padding: 6px 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    font-weight: 900;
    border: 3px solid #000000;
    color: #FFFFFF;
    box-shadow: 3px 3px 0px #000000;
    white-space: nowrap;
}

.red-bg { background: #FF4B72; }
.orange-bg { background: #FF7A00; }
.purple-bg { background: #8B5CF6; }
.green-bg { background: #00C853; }
.blue-bg { background: #2563eb; }

/* Blocks Container */
.blocks-container {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.block-card {
    background: #FFFFFF;
    border: 4px solid #000000;
    box-shadow: 6px 6px 0px #000000;
    padding: 16px 20px;
}

.block-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 15px;
    font-weight: 900;
    margin-bottom: 5px;
    display: inline-block;
    padding: 4px 10px;
    border: 2px solid #000000;
}

.block-a .block-label { background: #FFE600; color: #000000; }
.block-b .block-label { background: #FF4B72; color: #FFFFFF; }
.block-c .block-label { background: #00F0FF; color: #000000; }

.block-desc {
    font-size: 19px;
    line-height: 1.35;
    color: #1A202C;
}

/* Dossier Features */
.dossier-features {
    display: flex;
    flex-direction: column;
    gap: 14px;
}

.d-item {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    font-size: 20px;
    line-height: 1.35;
}

.check {
    background: #00F59B;
    color: #000000;
    width: 30px;
    height: 30px;
    min-width: 30px;
    border: 3px solid #000000;
    box-shadow: 3px 3px 0px #000000;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 17px;
}

/* Agent Pills */
.agent-badges {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 14px;
}

.agent-pill {
    background: #FFFFFF;
    border: 4px solid #000000;
    box-shadow: 5px 5px 0px #000000;
    padding: 16px;
    text-align: center;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.agent-name {
    font-size: 18px;
    font-weight: 900;
}

.agent-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: #718096;
    font-weight: 700;
}

/* Footer */
.footer-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 18px;
    border-top: 4px solid #000000;
}

.author-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 15px;
    font-weight: 800;
    background: #FFFFFF;
    padding: 8px 16px;
    border: 3px solid #000000;
    box-shadow: 4px 4px 0px #000000;
}

.swipe-button {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 17px;
    font-weight: 900;
    padding: 11px 22px;
    border: 4px solid #000000;
    box-shadow: 5px 5px 0px #000000;
    display: flex;
    align-items: center;
    gap: 10px;
    text-transform: uppercase;
    transform: rotate(-1deg);
}
"""

def generate_html_files():
    generated_files = []
    for s in SLIDES_DATA:
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{s['id']}</title>
    <style>
        :root {{
            --slide-bg: {s['bg']};
        }}
        {SLIDE_CSS}
    </style>
</head>
<body>
    <div class="slide-container">
        <!-- Header Row -->
        <div class="header-row">
            <div class="top-badge" style="background: {s['badge_bg']}; color: {s['badge_color']};">
                {s['badge_text']}
            </div>
            <div class="counter-badge">
                {s['slide_num']}
            </div>
        </div>

        <!-- Main Title -->
        <h1 class="main-title">
            {s['title']}
        </h1>

        <!-- Content Area -->
        <div class="content-area">
            {s['content_html']}
        </div>

        <!-- Footer Row -->
        <div class="footer-row">
            <div class="author-tag">
                GITHUB.COM/BILUSCA/LEAD-APPROACH
            </div>
            <div class="swipe-button" style="background: {s['footer_badge_bg']}; color: {s['footer_badge_color']};">
                {s['footer_badge']}
            </div>
        </div>
    </div>
</body>
</html>
"""
        file_path = os.path.join(CAROUSEL_DIR, f"{s['id']}.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        generated_files.append((s['id'], file_path))
    return generated_files

def render_pngs(html_files):
    user_data_dir = "/tmp/chromium_carousel_v22"
    if os.path.exists(user_data_dir):
        shutil.rmtree(user_data_dir, ignore_errors=True)
    os.makedirs(user_data_dir, exist_ok=True)

    png_files = []
    for slide_id, html_path in html_files:
        png_path = os.path.join(CAROUSEL_DIR, f"{slide_id}.png")
        cmd = [
            "chromium",
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            f"--user-data-dir={user_data_dir}",
            "--window-size=1080,1350",
            "--hide-scrollbars",
            f"--screenshot={png_path}",
            f"file://{html_path}"
        ]
        print(f"Rendering {slide_id}.png (1080x1350)...")
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            print(f"Error rendering {slide_id}: {res.stderr}")
            sys.exit(1)
        if not os.path.exists(png_path) or os.path.getsize(png_path) == 0:
            print(f"Failed to generate {png_path}")
            sys.exit(1)
        print(f"  ✔ Generated {slide_id}.png ({os.path.getsize(png_path) // 1024} KB)")
        png_files.append(png_path)
    return png_files

def compile_pdf(png_files):
    pdf_path = os.path.join(CAROUSEL_DIR, "lead-approach-v2.2-linkedin-carousel.pdf")
    cmd = ["magick"] + png_files + [pdf_path]
    print(f"Compiling PDF carousel: {pdf_path}...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"Error compiling PDF: {res.stderr}")
        return None
    print(f"  ✔ PDF Carousel compiled ({os.path.getsize(pdf_path) // 1024} KB)")
    return pdf_path

def main():
    print("=" * 60)
    print("  Generating Neo-Brutalist LinkedIn Carousel v2.2 (1080x1350)")
    print("=" * 60)
    html_files = generate_html_files()
    png_files = render_pngs(html_files)
    pdf_path = compile_pdf(png_files)
    print("\n✅ All 6 carousel slides successfully generated!")
    print(f"PNG Slides: {CAROUSEL_DIR}/slide_01.png ... slide_06.png")
    if pdf_path:
        print(f"Multi-Page LinkedIn PDF: {pdf_path}")

if __name__ == "__main__":
    main()

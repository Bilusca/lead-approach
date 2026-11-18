#!/usr/bin/env python3
"""
generate_carousel.py
Compiles a 6-slide Neo-Brutalist LinkedIn Carousel (1080x1350, 4:5 portrait)
for lead-approach into individual PNGs and a combined PDF.
"""

import os
import sys
import subprocess
import shutil

CAROUSEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "carousel"))
os.makedirs(CAROUSEL_DIR, exist_ok=True)

SLIDES_DATA = [
    # SLIDE 1: Cover
    {
        "id": "slide_01",
        "bg": "#FFE600",
        "badge_bg": "#8B5CF6",
        "badge_color": "#FFFFFF",
        "badge_text": "B2B OUTBOUND ENGINEERING // v2.1",
        "slide_num": "01 / 06",
        "title": "STOP FORCING 30-MIN ZOOM CALLS ON COLD PROSPECTS.",
        "content_html": """
        <div class="card neo-card-white" style="margin-top: 30px;">
            <div class="card-header-tag red-tag">TRADITIONAL OUTBOUND IS BROKEN</div>
            <div class="pain-list">
                <div class="pain-item">
                    <span class="cross">✕</span>
                    <div><strong>98% drop-off</strong> when forcing cold calendar links.</div>
                </div>
                <div class="pain-item">
                    <span class="cross">✕</span>
                    <div><strong>10-field contact forms</strong> get instantly abandoned on mobile.</div>
                </div>
                <div class="pain-item">
                    <span class="cross">✕</span>
                    <div><strong>Cold calling & generic pitches</strong> get blocked as spam.</div>
                </div>
            </div>
        </div>

        <div class="card neo-card-black" style="margin-top: 35px;">
            <div class="card-title-neon">THE BREAKTHROUGH:</div>
            <div class="card-sub-neon">
                The <strong>100% Text-Driven "No-Call" Outbound Engine</strong> that converts social discovery into paying clients.
            </div>
        </div>
        """,
        "footer_badge": "SWIPE TO SEE THE WORKFLOW ➔",
        "footer_badge_bg": "#000000",
        "footer_badge_color": "#FFE600"
    },

    # SLIDE 2: Step 1 Setup
    {
        "id": "slide_02",
        "bg": "#00F59B",
        "badge_bg": "#000000",
        "badge_color": "#00F59B",
        "badge_text": "STEP 01 // 60-SECOND ONBOARDING",
        "slide_num": "02 / 06",
        "title": "SETUP YOUR OFFER & BRAND MANUAL MEMORY",
        "content_html": """
        <div class="terminal-box" style="margin-top: 25px;">
            <div class="terminal-bar">
                <span class="dot dot-red"></span>
                <span class="dot dot-yellow"></span>
                <span class="dot dot-green"></span>
                <span class="terminal-title">bash — lead-approach setup</span>
            </div>
            <div class="terminal-code">
                <span class="prompt">$</span> npx lead-approach setup --interactive
            </div>
        </div>

        <div class="feature-grid" style="margin-top: 30px;">
            <div class="card neo-card-white">
                <div class="card-num">01</div>
                <div class="card-heading">CAMPAIGN MEMORY</div>
                <p>Stores company name, core service, portfolio links, and closing WhatsApp in <code>config/profile.json</code>.</p>
            </div>
            <div class="card neo-card-white">
                <div class="card-num">02</div>
                <div class="card-heading">BRAND MANUAL</div>
                <p>Configures primary & secondary hex colors, typography, dynamic monogram, and report tagline.</p>
            </div>
            <div class="card neo-card-white">
                <div class="card-num">03</div>
                <div class="card-heading">4 TONE PRESETS</div>
                <p>Switches between <code>consultivo</code>, <code>direto</code>, <code>caloroso</code>, and <code>executivo</code> styles.</p>
            </div>
        </div>

        <div class="highlight-banner" style="background: #FFE600; margin-top: 25px;">
            ⚡ <strong>Mandatory Agent Memory:</strong> AI agents strictly inject your brand & links into every message.
        </div>
        """,
        "footer_badge": "NEXT: BATCH DISCOVERY ➔",
        "footer_badge_bg": "#000000",
        "footer_badge_color": "#00F59B"
    },

    # SLIDE 3: Step 2 List & Recon
    {
        "id": "slide_03",
        "bg": "#00F0FF",
        "badge_bg": "#FF4B72",
        "badge_color": "#FFFFFF",
        "badge_text": "STEP 02 // BATCH DISCOVERY & RECON",
        "slide_num": "03 / 06",
        "title": "DROP YOUR LEAD LIST (ANY FORMAT)",
        "content_html": """
        <div class="terminal-box" style="margin-top: 25px;">
            <div class="terminal-bar">
                <span class="dot dot-red"></span>
                <span class="dot dot-yellow"></span>
                <span class="dot dot-green"></span>
                <span class="terminal-title">bash — lead-approach list</span>
            </div>
            <div class="terminal-code">
                <span class="prompt">$</span> lead-approach list leads.pdf --output roadmap.md
            </div>
        </div>

        <div class="formats-bar" style="margin-top: 20px;">
            <span class="fmt-pill">PDF</span>
            <span class="fmt-pill">TXT</span>
            <span class="fmt-pill">CSV</span>
            <span class="fmt-pill">MARKDOWN</span>
            <span class="fmt-pill">JSON</span>
        </div>

        <div class="card neo-card-white" style="margin-top: 25px;">
            <div class="card-header-tag blue-tag">AUTOMATED RECON ENGINE (CLI)</div>
            <div class="audit-item">
                <span class="audit-badge red-bg">LATENCY LEAK</span>
                <span>Measures server response time (TTFB) & flags mobile lag > 2.5s.</span>
            </div>
            <div class="audit-item">
                <span class="audit-badge orange-bg">MOBILE VIEW</span>
                <span>Detects missing mobile meta-tags & broken responsive layouts.</span>
            </div>
            <div class="audit-item">
                <span class="audit-badge purple-bg">STACK RECON</span>
                <span>Identifies CMS: WordPress, Elementor, Webflow, Linktree, Bento.</span>
            </div>
            <div class="audit-item">
                <span class="audit-badge green-bg">BOOKING LEAK</span>
                <span>Spots 10-field bureaucratic forms losing high-ticket patients & clients.</span>
            </div>
        </div>
        """,
        "footer_badge": "NEXT: THE 4-BLOCK COPY ➔",
        "footer_badge_bg": "#000000",
        "footer_badge_color": "#00F0FF"
    },

    # SLIDE 4: Step 3 The 4-Block Copy
    {
        "id": "slide_04",
        "bg": "#FF8DA1",
        "badge_bg": "#000000",
        "badge_color": "#FFE600",
        "badge_text": "STEP 03 // 4-BLOCK COPYWRITING",
        "slide_num": "04 / 06",
        "title": "THE 4-BLOCK ZERO-FRICTION FORMULA",
        "content_html": """
        <div class="rule-box" style="margin-top: 20px;">
            🔥 <strong>Axiom:</strong> Max 120-150 words. Zero call friction. Deliver a 30s technical diagnostic.
        </div>

        <div class="blocks-container" style="margin-top: 25px;">
            <div class="block-card block-a">
                <div class="block-label">BLOCK A // HUMAN CONNECTION</div>
                <div class="block-desc">Specific verifiable praise referencing real work or case results.</div>
            </div>
            <div class="block-card block-b">
                <div class="block-label">BLOCK B // INVISIBLE DIGITAL LEAK</div>
                <div class="block-desc">Diagnostic of where mobile visitors bounce (TTFB lag, clunky linktree).</div>
            </div>
            <div class="block-card block-c">
                <div class="block-label">BLOCK C // PROOF & LOCALIZED LINK</div>
                <div class="block-desc">High-authority portfolio match: <code>/en/</code> (US/Global), <code>/es/</code>, or <code>/</code> (BR).</div>
            </div>
            <div class="block-card block-d">
                <div class="block-label">BLOCK D // ZERO-CALL "NO-CALL" CTA</div>
                <div class="block-desc"><em>"No phone calls needed; reply right here and I'll share 2 bullet points by text."</em></div>
            </div>
        </div>
        """,
        "footer_badge": "NEXT: EXECUTIVE DOSSIERS ➔",
        "footer_badge_bg": "#000000",
        "footer_badge_color": "#FFFFFF"
    },

    # SLIDE 5: Step 4 PDF Dossiers
    {
        "id": "slide_05",
        "bg": "#B8A4FF",
        "badge_bg": "#000000",
        "badge_color": "#B8A4FF",
        "badge_text": "STEP 04 // EXECUTIVE PROPOSALS",
        "slide_num": "05 / 06",
        "title": "COMPILE BRAND-COMPLIANT A4 DOSSIERS",
        "content_html": """
        <div class="terminal-box" style="margin-top: 25px;">
            <div class="terminal-bar">
                <span class="dot dot-red"></span>
                <span class="dot dot-yellow"></span>
                <span class="dot dot-green"></span>
                <span class="terminal-title">bash — lead-approach report</span>
            </div>
            <div class="terminal-code">
                <span class="prompt">$</span> lead-approach report --sample --output executive.pdf
            </div>
        </div>

        <div class="card neo-card-white" style="margin-top: 25px;">
            <div class="card-header-tag purple-tag">STRICT BRAND MANUAL COMPLIANCE</div>
            <div class="dossier-features">
                <div class="d-item">
                    <span class="check">✔</span>
                    <div><strong>Custom Brand Palette:</strong> Automatically renders in your primary, secondary, and dark hex colors.</div>
                </div>
                <div class="d-item">
                    <span class="check">✔</span>
                    <div><strong>Executive Typography:</strong> Uses Plus Jakarta Sans, Playfair Display, or JetBrains Mono.</div>
                </div>
                <div class="d-item">
                    <span class="check">✔</span>
                    <div><strong>Headless Chromium Engine:</strong> Vector-sharp text, custom badges, and responsive tables.</div>
                </div>
                <div class="d-item">
                    <span class="check">✔</span>
                    <div><strong>Monogram & Tagline:</strong> Generates initial monogram or embeds your official logo URL.</div>
                </div>
            </div>
        </div>

        <div class="highlight-banner" style="background: #00F59B; margin-top: 25px;">
            🎯 <strong>The Result:</strong> Delivers a $5,000 corporate audit presentation in under 10 seconds.
        </div>
        """,
        "footer_badge": "NEXT: GET STARTED ➔",
        "footer_badge_bg": "#000000",
        "footer_badge_color": "#B8A4FF"
    },

    # SLIDE 6: CTA / Install
    {
        "id": "slide_06",
        "bg": "#FFE600",
        "badge_bg": "#000000",
        "badge_color": "#FFE600",
        "badge_text": "DEPLOY TODAY // 100% OPEN SOURCE",
        "slide_num": "06 / 06",
        "title": "RUN IT IN YOUR TERMINAL RIGHT NOW.",
        "content_html": """
        <div class="terminal-box" style="margin-top: 25px;">
            <div class="terminal-bar">
                <span class="dot dot-red"></span>
                <span class="dot dot-yellow"></span>
                <span class="dot dot-green"></span>
                <span class="terminal-title">bash — instant install</span>
            </div>
            <div class="terminal-code" style="font-size: 26px; line-height: 1.6;">
                <span class="comment"># Zero-install execution via npx:</span><br>
                <span class="prompt">$</span> <strong style="color: #00F59B;">npx lead-approach install --all</strong><br><br>
                <span class="comment"># Or install globally as a permanent CLI:</span><br>
                <span class="prompt">$</span> npm install -g lead-approach
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
                ★ Star the Project on GitHub
            </div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 20px; color: #FFFFFF; margin-top: 8px;">
                github.com/Bilusca/lead-approach
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
    font-size: 54px;
    font-weight: 900;
    line-height: 1.12;
    letter-spacing: -1.5px;
    text-transform: uppercase;
    margin-top: 25px;
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
    padding: 30px;
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
    font-size: 30px;
    font-weight: 900;
    color: #FFE600;
    letter-spacing: 0.5px;
}

.card-sub-neon {
    font-size: 24px;
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
    margin-bottom: 20px;
    box-shadow: 3px 3px 0px #000000;
}

.red-tag { background: #FF4B72; color: #FFFFFF; }
.blue-tag { background: #00F0FF; color: #000000; }
.purple-tag { background: #8B5CF6; color: #FFFFFF; }

/* Pain List */
.pain-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.pain-item {
    display: flex;
    align-items: center;
    gap: 16px;
    font-size: 24px;
    line-height: 1.35;
}

.cross {
    background: #FF4B72;
    color: #FFFFFF;
    width: 38px;
    height: 38px;
    min-width: 38px;
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
    padding: 12px 18px;
    border-bottom: 3px solid #333333;
    display: flex;
    align-items: center;
    gap: 10px;
}

.dot {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    border: 2px solid #000000;
}

.dot-red { background: #FF5F56; }
.dot-yellow { background: #FFBD2E; }
.dot-green { background: #27C93F; }

.terminal-title {
    color: #A0AEC0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    margin-left: 8px;
    font-weight: 700;
}

.terminal-code {
    padding: 22px 26px;
    color: #FFFFFF;
    font-family: 'JetBrains Mono', monospace;
    font-size: 24px;
    line-height: 1.4;
}

.terminal-code .prompt { color: #00F59B; font-weight: 800; }
.terminal-code .comment { color: #718096; font-size: 18px; }

/* Feature Grid */
.feature-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 16px;
}

.feature-grid .card {
    padding: 20px 24px;
    display: flex;
    align-items: flex-start;
    gap: 20px;
}

.card-num {
    background: #000000;
    color: #FFE600;
    font-family: 'JetBrains Mono', monospace;
    font-size: 18px;
    font-weight: 900;
    padding: 6px 12px;
    border: 3px solid #000000;
}

.card-heading {
    font-size: 20px;
    font-weight: 900;
    margin-bottom: 4px;
}

.feature-grid p {
    font-size: 19px;
    line-height: 1.35;
    color: #2D3748;
}

.highlight-banner {
    border: 4px solid #000000;
    box-shadow: 6px 6px 0px #000000;
    padding: 18px 24px;
    font-size: 20px;
    line-height: 1.4;
}

/* Formats Bar */
.formats-bar {
    display: flex;
    gap: 12px;
}

.fmt-pill {
    background: #FFFFFF;
    color: #000000;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 800;
    font-size: 16px;
    padding: 8px 16px;
    border: 3px solid #000000;
    box-shadow: 4px 4px 0px #000000;
}

/* Audit Items */
.audit-item {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 12px 0;
    border-bottom: 2px dashed #CBD5E0;
    font-size: 20px;
}

.audit-item:last-child { border-bottom: none; }

.audit-badge {
    padding: 6px 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
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

/* Blocks Container */
.rule-box {
    background: #000000;
    color: #FFFFFF;
    padding: 16px 22px;
    font-size: 20px;
    border: 4px solid #000000;
    box-shadow: 6px 6px 0px #FFFFFF, 8px 8px 0px #000000;
}

.blocks-container {
    display: flex;
    flex-direction: column;
    gap: 14px;
}

.block-card {
    background: #FFFFFF;
    border: 4px solid #000000;
    box-shadow: 6px 6px 0px #000000;
    padding: 18px 22px;
}

.block-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 16px;
    font-weight: 900;
    margin-bottom: 6px;
    display: inline-block;
    padding: 4px 10px;
    border: 2px solid #000000;
}

.block-a .block-label { background: #FFE600; color: #000000; }
.block-b .block-label { background: #FF4B72; color: #FFFFFF; }
.block-c .block-label { background: #00F0FF; color: #000000; }
.block-d .block-label { background: #00F59B; color: #000000; }

.block-desc {
    font-size: 20px;
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
    font-size: 21px;
    line-height: 1.35;
}

.check {
    background: #00F59B;
    color: #000000;
    width: 32px;
    height: 32px;
    min-width: 32px;
    border: 3px solid #000000;
    box-shadow: 3px 3px 0px #000000;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 18px;
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
    padding-top: 20px;
    border-top: 4px solid #000000;
}

.author-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 16px;
    font-weight: 800;
    background: #FFFFFF;
    padding: 8px 16px;
    border: 3px solid #000000;
    box-shadow: 4px 4px 0px #000000;
}

.swipe-button {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 18px;
    font-weight: 900;
    padding: 12px 24px;
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
        <!-- Top Row -->
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

        <!-- Middle Dynamic Content Area -->
        <div class="content-area">
            {s['content_html']}
        </div>

        <!-- Footer Row -->
        <div class="footer-row">
            <div class="author-tag">
                BY @BILUSCA // OPEN SOURCE
            </div>
            <div class="swipe-button" style="background: {s['footer_badge_bg']}; color: {s['footer_badge_color']};">
                {s['footer_badge']}
            </div>
        </div>
    </div>
</body>
</html>"""
        file_path = os.path.join(CAROUSEL_DIR, f"{s['id']}.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        generated_files.append((s['id'], file_path))
    return generated_files

def render_pngs(html_files):
    png_files = []
    user_data_dir = "/tmp/chromium-carousel-data"
    os.makedirs(user_data_dir, exist_ok=True)
    
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
    pdf_path = os.path.join(CAROUSEL_DIR, "lead-approach-linkedin-carousel.pdf")
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
    print("  Generating Neo-Brutalist LinkedIn Carousel (1080x1350)")
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

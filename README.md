# Lead Approach — B2B Cold Outreach & "No-Call" Conversion Engineering

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platforms: Antigravity | Claude Code | Codex](https://img.shields.io/badge/Platforms-Antigravity%20%7C%20Claude%20Code%20%7C%20Codex-purple.svg)](./SKILL.md)
[![Niches: 100% Universal Any-Niche](https://img.shields.io/badge/Niches-100%25%20Universal%20Any--Niche-teal.svg)](#-universal-any-niche-prospecting-engine)
[![Standard: Agent Skills Spec](https://img.shields.io/badge/Standard-AAIF%20%2F%20Agent%20Skills-green.svg)](https://agentskills.io)
[![Languages: English | Español | Português](https://img.shields.io/badge/Languages-EN%20%7C%20ES%20%7C%20PT-orange.svg)](#-trilingual-architecture-english-primary--spanish--portuguese)

> **Universal outbound skill and cold messaging framework for selling high-ticket digital services.**  
> Built natively for **Google Antigravity**, **Anthropic Claude Code**, and **OpenAI Codex**.  
> **Primary Language:** English (US / Global High-Ticket) with full native support for Spanish and Portuguese.

🌐 **Translations:** [🇧🇷 Versão em Português](./README.pt-BR.md)

---

## 🎯 Executive Overview

**lead-approach** is an end-to-end sales engineering skill and laboratory designed to transform raw social media links (Instagram, LinkedIn, WhatsApp, Google Business) into qualified closing opportunities for high-value digital services (sub-second websites, conversion-focused landing pages, custom web systems, and brand identity).

### The Core "No-Call" Axiom
> **"The outreach, value delivery, and closing must be conducted 100% via asynchronous text (Direct / WhatsApp / LinkedIn / Email), without ever forcing or demanding synchronous phone or video calls."**

### 🏹 The 4 Pillars of Outbound Prospecting
Unlike passive inbound marketing (waiting for leads to find you), this skill is built around **disciplined, active Outbound hunting**:
1. **Active Target Hunting:** We actively discover, audit, and initiate contact with high-ticket businesses that have active cash flow but suffer from digital bottlenecks.
2. **Value-First Interruption:** Cold prospects do not know you. Never interrupt their day with an "ask" (pitch, meeting request). Interrupt with an unignorable "give": a 30-second technical diagnostic of where their mobile website is leaking clients.
3. **The "No-Call" Barrier Removal:** Traditional cold outreach fails because it demands too much psychological commitment upfront (*"Hop on a 30-min Zoom call"*). We slash friction to zero: *"No calls needed; we can chat right here by text."*
4. **Structured Multi-Touch Cadence:** Outbound is a system: **Pre-Warming** (Day 0) ➔ **Personalized 4-Block DM** (Day 1) ➔ **Asynchronous Follow-Up** (Day 4) ➔ **WhatsApp Closing Bridge** (Day 7).

---

## 🌐 Universal Any-Niche Prospecting Engine

This skill is **100% agnostic and engineered for ANY industry, vertical, or market**:

* **Adaptable to Any Offer:** Websites, custom software, landing pages, marketing automation, branding, SEO, or B2B consulting. The engine reads your offering from `config/profile.json`.
* **Adaptable to Any Target Vertical:** Works seamlessly across:
  * 💻 **B2B SaaS & Tech** (Demo conversions, sub-second product pages)
  * ⚖️ **Law Firms & Legal** (Confidential intake, 1-tap mobile consultations)
  * 🏛️ **Architecture & Construction** (High-speed 4K portfolios, commercial RFQs)
  * 🦷 **Luxury Dentistry & Ortho** (Smile makeover proof, direct concierge routing)
  * 🏥 **Medical Clinics & MedSpas** (High-ticket aesthetic treatment funnels)
  * 🏡 **Real Estate & Brokerages** (Single-property landing pages, instant brochures)
  * 💼 **Consulting & M&A** (Executive authority, institutional partner intake)
  * ☀️ **Home Services, Roofing & Solar** (1-tap estimate dispatch, urgent repairs)
  * 🛍️ **E-Commerce & D2C Brands** (Mobile checkout speed, cart abandonment fixes)
  * 🚚 **Logistics & Industrial Supply** (Automated RFQ routing, B2B wholesale portals)
  * 📊 **Accounting & Tax Advisory** (Frictionless corporate client onboarding)
  * 🏋️ **Fitness & High-Ticket Wellness** (VIP intake funnels, private coaching)

---

## 🚀 Universal Multi-Agent Compatibility

Structured strictly under the open **Agent Skills Specification (AAIF)**, this repository provides 100% interoperability across all major AI coding and workflow agents without file duplication:

| Agent Platform | Skill Entrypoint / Discovery | Context & Rule File |
| :--- | :--- | :--- |
| **Google Antigravity** | `.agents/skills/lead-approach/SKILL.md` | [GEMINI.md](./GEMINI.md) / [AGENTS.md](./AGENTS.md) |
| **Anthropic Claude Code** | `.claude/skills/lead-approach/SKILL.md` *(symlink)* | [CLAUDE.md](./CLAUDE.md) |
| **OpenAI Codex** | `.agents/skills/lead-approach/SKILL.md` | [AGENTS.md](./AGENTS.md) |

### Global System Installation (One Command)
To make `lead-approach` globally accessible across all your local projects and agent harnesses:

```bash
./install.sh --all
```
*Or install selectively: `./install.sh --antigravity`, `./install.sh --claude`, or `./install.sh --codex`.*

---

## 🌍 Trilingual Architecture (English Primary · Spanish · Portuguese)

The skill operates **primarily in English** for optimal reasoning depth, token economy, and alignment with the highest-ticket global markets, while maintaining fluid native switching:

1. **English (Primary / Default):** Standard for United States, United Kingdom, Canada, and global high-ticket businesses (`https://vcrsoftwares.com/en/`).
2. **Spanish (Native):** Seamlessly activated for prospects in Latin America, Spain, or Hispanic US metro areas like Miami, Orlando, and Texas (`https://vcrsoftwares.com/es/`).
3. **Portuguese (Native):** Activated for the Brazilian corporate market and Lusophone communities (`https://vcrsoftwares.com/`).

---

## 📂 Repository Architecture

```text
lead-approach/
├── .agents/
│   └── skills/
│       └── lead-approach/             # Canonical Skill Package (Agent Skills Spec)
│           ├── SKILL.md               # 7-Step Operational Lifecycle Definition
│           ├── config/                # Persistent Campaign & Brand Memory
│           │   ├── profile.json       # Machine-readable JSON configuration
│           │   └── profile.md         # Formatted Brand Manual & Agent context
│           ├── references/
│           │   ├── copy-frameworks.md # 4-block copy models (EN, ES, PT), Stories & Audio notes
│           │   ├── niche-playbooks.md # Vertical playbooks: Legal, Architecture, Dental, Real Estate
│           │   ├── profiling-guide.md # 5-minute commercial reconnaissance checklist
│           │   └── objection-closing.md # Text-based objection handling & WhatsApp closing
│           ├── scripts/
│           │   ├── setup_profile.py   # Offer, memory & Brand Manual setup wizard
│           │   ├── process_list.py    # Batch lead processor (PDF/TXT/CSV) & Roadmap generator
│           │   ├── recon_lead.py      # Automated website & link-in-bio technical auditor
│           │   ├── generate_pdf.py    # Headless Chromium PDF compiler
│           │   └── compile_report.py  # JSON-to-PDF executive dossier compiler
│           └── templates/
│               └── report-template.html # CSS Custom Properties A4 executive template
├── .claude/
│   └── skills/
│       └── lead-approach -> symlink to .agents/skills/lead-approach
├── config -> symlink to .agents/skills/lead-approach/config
├── CLAUDE.md                          # Memory guidelines for Claude Code
├── AGENTS.md                          # Universal directives for Codex & Antigravity
├── GEMINI.md                          # Specialized rules for Google Antigravity
├── install.sh                         # Multi-platform global installer script
├── README.md                          # Primary English Documentation
└── README.pt-BR.md                    # Portuguese Documentation
```

---

## 🛠️ Command-Line Tools & Scripts

### 1. Offer Setup, Memory & Brand Manual (`setup_profile.py`)
Configures your company identity, tone of voice, outreach channels, portfolio links, and **Brand Guidelines (Colors, Typography, Slogan, Logo)**. All agents read this configuration automatically before drafting copy or generating reports:

```bash
# Interactive Wizard (step-by-step terminal prompt):
python3 scripts/setup_profile.py -i

# Direct CLI Configuration (using color presets or custom hex):
python3 scripts/setup_profile.py \
  --name "Apex Growth Agency" \
  --service "Ultra-Fast Websites & Conversion Funnels" \
  --tone consultivo \
  --brand-preset sapphire \
  --brand-tagline "High-Performance Growth & Conversion Engineering" \
  --brand-color "#2563eb" \
  --website-en "https://youragency.com/en/" \
  --whatsapp "https://wa.me/13055551234"

# Display currently active profile and brand manual:
python3 scripts/setup_profile.py --show
```

### 2. Batch Processing & Outreach Roadmap (`process_list.py` / `list` Command)
Ingests prospect lists from **PDF, TXT, Markdown, CSV, or JSON** files or inline text. Audits every business link, cross-references your campaign memory, and outputs a prioritized multi-day execution roadmap:

```bash
# From a PDF or text file:
python3 scripts/process_list.py --file prospects.pdf --output roadmap.md

# From a CSV spreadsheet, automatically compiling an executive A4 PDF dossier:
python3 scripts/process_list.py --file leads.csv --pdf executive_roadmap.pdf

# From an inline list of URLs/handles:
python3 scripts/process_list.py --input "https://medspa1.com, @lawfirm2, https://studio3.com"
```

### 3. Website & Bio Technical Reconnaissance (`recon_lead.py`)
Extracts server response latency (TTFB), mobile viewport compliance, CMS/builders (WordPress, Elementor, Divi, Webflow, Linktree, Beacons), and appointment booking tools (Acuity, Booksy, Calendly, WhatsApp):

```bash
# Markdown formatted report for AI context:
python3 scripts/recon_lead.py --url https://targetbusiness.com

# Structured JSON export:
python3 scripts/recon_lead.py --url https://linktr.ee/targetclinic --format json
```

### 4. Brand-Compliant Executive PDF Compiler (`compile_report.py`)
Compiles structured lead audits into print-ready A4 executive PDF dossiers. Strictly follows your **Brand Guidelines** (primary/secondary colors, auto-derived harmonic tints, custom typography, logo or dynamic monogram, and tagline):

```bash
# Compile from structured JSON data:
python3 scripts/compile_report.py --data leads.json --output executive_dossier.pdf

# Generate a sample demonstration dossier:
python3 scripts/compile_report.py --sample --output sample_dossier.pdf
```

---

## 🎯 The 4-Block Outreach Message Formula

Every message drafted by this skill adheres to a psychological 4-block architecture optimized for mobile readability:

```text
┌──────────────────────────────────────────────────────────────┐
│ BLOCK A: Specific Human Connection & Verifiable Praise       │
│ "Hi Dr. James! Love your team's work in Brickell..."         │
├──────────────────────────────────────────────────────────────┤
│ BLOCK B: Diagnostic of Invisible Digital Revenue Leak        │
│ "High-ticket treatments lose clients if mobile pages take    │
│ over 2.5s or force people through clunky booking links..."   │
├──────────────────────────────────────────────────────────────┤
│ BLOCK C: Tangible Solution & Social Proof (Localized Link)   │
│ "We build ultra-fast booking experiences for US clinics:     │
│ 👉 https://vcrsoftwares.com/en/ "                            │
├──────────────────────────────────────────────────────────────┤
│ BLOCK D: Frictionless "No-Call" Call to Action (100% Text)   │
│ "No need for phone calls; feel free to reply right here      │
│ and I'll share 2 practical ideas by text."                   │
└──────────────────────────────────────────────────────────────┘
```

---

## 🏛️ High-Ticket Vertical Playbooks

Dedicated frameworks and technical diagnostics for 4 of the most lucrative service sectors:
* **Law Firms & Attorneys:** Overcoming 10-field desktop intake forms with confidential 1-tap mobile triage routes in compliance with ethical bar advertising standards.
* **Architecture & Interior Design:** Eliminating 8-second 4K photography mobile lag without reducing sharpness, converting portfolio visitors into project briefings.
* **High-End Cosmetic Dentistry:** Bypassing cold calendar appointment links by leading with smile transformation before-and-after cases.
* **Luxury Real Estate:** Replacing bulky MLS portals with single-property micro-sites featuring instant WhatsApp brochure downloads.

---

## 💡 Example Prompts for AI Agents

* `"list leads.pdf"` (parses file, audits every website, and builds a prioritized outreach roadmap)
* `"Setup my offer and brand manual with primary color #2563eb and modern typography"`
* `"Audit the website https://targetclinic.com and identify the main digital leaks for Block B"`
* `"Draft a cold outreach DM in English for a plastic surgery practice in Miami using Linktree on bio"`
* `"How should I respond to a prospect who said 'send it to my email' to keep them on WhatsApp?"`
* `"Compile the last 5 audited prospects into a brand-compliant executive PDF dossier"`

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).

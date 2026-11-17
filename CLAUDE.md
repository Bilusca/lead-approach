# CLAUDE.md — Lead Approach Guidelines for Claude Code

This file defines the project instructions, architectural rules, and CLI workflows for **Claude Code** when working with this repository and the `lead-approach` skill.

---

## 📌 Project Overview
**lead-approach** is an outbound sales engineering skill and laboratory designed to turn social media profiles (Instagram, LinkedIn, WhatsApp) into high-converting client opportunities for custom digital services (ultra-fast websites, landing pages, digital booking, and branding) using a **100% text-driven ("No-Call") methodology**.

---

## 🚀 How Claude Code Discovers and Uses This Skill
Claude Code automatically loads this skill from:
* `.claude/skills/lead-approach/SKILL.md` (Project Scope)
* Personal/Global scope when installed in `~/.claude/skills/lead-approach/`

When a user asks to analyze leads, write outreach messages, diagnose website performance, or generate PDF proposals, Claude should immediately refer to the references in:
* `references/profiling-guide.md` — 5-minute lead reconnaissance protocol.
* `references/copy-frameworks.md` — 4-block copy models (ESP, ENG, PT), story triggers, voice notes.
* `references/niche-playbooks.md` — High-ticket verticals (Law, Architecture, Dentistry, Real Estate).
* `references/objection-closing.md` — Text-based objection handling and WhatsApp closing.

---

## 🛠️ CLI Tools & Available Scripts
Claude Code can run these scripts directly via Bash:

1. **Offer & Campaign Setup Wizard:**
   ```bash
   python3 scripts/setup_profile.py --name "Agency Name" --service "Services" ...
   # Show current configuration:
   python3 scripts/setup_profile.py --show
   ```
   *Saves business identity, tone of voice, outreach channels, and portfolio links to `config/profile.json` and `config/profile.md`.*

2. **Batch Lead List Processor & Roadmap Generator (`list` command):**
   ```bash
   python3 scripts/process_list.py --file leads.pdf --output outreach_roadmap.md
   # Or with automatic PDF generation:
   python3 scripts/process_list.py --file leads.txt --pdf executive_roadmap.pdf
   ```
   *Parses PDF, TXT, Markdown, CSV, or JSON lead lists, audits each URL/handle, and generates a prioritized multi-day outreach plan.*

3. **Website & Link-in-Bio Reconnaissance:**
   ```bash
   python3 scripts/recon_lead.py --url https://target-business.com
   # Output formats: markdown (default) or json (--format json)
   ```
   *Instantly checks TTFB latency, mobile viewport, CMS (WordPress, Elementor, Wix, Webflow, Linktree), and booking tools (Acuity, Booksy, Calendly).*

4. **Executive PDF Dossier Compilation:**
   ```bash
   python3 scripts/compile_report.py --data leads.json --output relatorio.pdf
   # For sample demonstration report:
   python3 scripts/compile_report.py --sample --output sample.pdf
   ```
   *Requires Chromium/Chrome headless (`--headless=new`).*

---

## 💎 Core Behavioral Rules for Claude Code
1. **Mandatory Campaign Profile Memory:**
   * Always check if `config/profile.json` (or `config/profile.md`) exists.
   * If configured, prioritize the user's saved company name, primary service, custom tone of voice (`consultivo`, `direto`, `caloroso`, `executivo`), channels, and localized portfolio/WhatsApp links over any generic defaults.
2. **The Inviolable "No-Call" Axiom:**
   * Never propose Zoom calls, Google Meet, or phone calls in cold outreach messages.
   * Always frame the CTA around zero-friction text: *"No need for calls; just reply here on chat and I'll share 2 quick ideas by text."*
3. **Language Priority & Synchronization:**
   * **Primary Language: English (US / Global High-Ticket)**: Default for US, UK, and all prospects unless identified as Hispanic or Brazilian. Link: `https://vcrsoftwares.com/en/` (or user's `website_en`).
   * **Spanish (ESP · Latin America & US Hispanic)**: Natural Latin American Spanish for leads in LatAm, Spain, or Hispanic US metros. Link: `https://vcrsoftwares.com/es/` (or user's `website_es`).
   * **Portuguese (PT · Brazil)**: Results-driven Brazilian Portuguese for Brazilian prospects. Link: `https://vcrsoftwares.com/` (or user's `website_pt`).
4. **4-Block Message Architecture:**
   * **Block A:** Specific human connection & verifiable praise.
   * **Block B:** Technical bottleneck diagnosis (backed by `recon_lead.py` data).
   * **Block C:** Tangible proof & localized portfolio link.
   * **Block D:** Frictionless "No-Call" call-to-action.
5. **Brand Manual Compliance for Reports:**
   * All reports and executive dossiers compiled via `compile_report.py` must strictly reflect the user's brand manual configured in `config/profile.json` (colors, fonts, tagline, logo/monogram, and category tags).
6. **Universal Niche Adaptability (Outbound for ANY Industry):**
   * This skill is designed for **ANY industry or market** (SaaS, Healthcare, Legal, Architecture, Dentistry, Real Estate, Consulting, Home Services, E-commerce, Logistics, Fitness, etc.).
   * Never restrict outreach to a single vertical. Adapt the 4-block copy, diagnosis, and value proposition dynamically to whatever sector the prospect operates in and whatever service the operator offers.

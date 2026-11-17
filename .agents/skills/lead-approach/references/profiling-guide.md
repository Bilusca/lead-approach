# Lead Profiling & Commercial Reconnaissance Guide (Lead Recon)

This guide provides a rapid 5-minute protocol for extracting high-value commercial intelligence from any business profile or website before crafting an outreach message.

---

## 1. The 5-Minute Reconnaissance Checklist

For every target lead, gather the answers to these 5 core questions:

```text
┌─────────────────────────────────────────────────────────────────┐
│ 1. WHO IS THE DECISION MAKER?                                   │
│ Doctor, owner, managing partner, head architect, or founder.    │
├─────────────────────────────────────────────────────────────────┤
│ 2. PHYSICAL LOCATION & DISTRICT AFFLUENCE                       │
│ City, state, and specific neighborhood (identifies purchasing   │
│ power, e.g., Brickell, Beverly Hills, Mayfair, Itaim Bibi).     │
├─────────────────────────────────────────────────────────────────┤
│ 3. WHAT IS THEIR HIGHEST-MARGIN / FLAGSHIP OFFER?               │
│ High-ticket service highlighted in pins, stories, or bio.       │
├─────────────────────────────────────────────────────────────────┤
│ 4. WHAT IS THEIR CURRENT BOOKING / INQUIRY ROUTE?               │
│ Link in bio: Custom site, Linktree, Booksy, Acuity, WhatsApp?   │
├─────────────────────────────────────────────────────────────────┤
│ 5. WHAT IS THE INVISIBLE DIGITAL REVENUE BOTTLENECK?            │
│ Slow loading speed, clunky booking, missing mobile viewport.    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Analyzing the "Link in Bio" Route

The link in an Instagram or LinkedIn bio immediately reveals the business's digital maturity:

| Current Bio Link | Technical Diagnostic | Ideal Sales Angle |
| :--- | :--- | :--- |
| **Linktree / Beacons with 6+ buttons** | Decision fatigue. Prospects are overwhelmed by generic choices and drop off. | *"Multiple generic buttons disperse attention; a dedicated mobile landing page doubles direct inquiries."* |
| **Direct Acuity / Booksy / Fresha link** | Cold and transactional. Prospects are forced to pick dates before seeing authority. | *"High-ticket services require clients to see social proof and transformations before facing a cold calendar."* |
| **Legacy WordPress / Wix Website** | Sluggish mobile speed (> 3 to 6s load), unoptimized mobile viewport. | *"Over 90% of Instagram traffic is mobile; if the page takes > 1.5s, you lose almost half your visitors."* |
| **Only "DM to Book / Direct inquiries"** | High administrative overhead, lost inquiries from clients wanting quick specs/pricing. | *"A fast mobile micro-site filters unqualified traffic and delivers pre-sold inquiries ready to convert."* |

---

## 3. Language & Cultural Synchronization Protocol

* **English (US / UK / Global) — [PRIMARY]:**
  * Use concise, ROI-driven, professional yet approachable phrasing.
  * Direct to `https://vcrsoftwares.com/en/` (or user's `website_en`).
* **Spanish (Latin America & US Hispanic Metros):**
  * Common in Florida (Miami, Orlando, Tampa), Texas, California, and throughout Latin America.
  * If captions and stories are in Spanish, craft the message in natural Latin American Spanish.
  * Use warm, respectful *tuteo* (*"¡Hola Dr. Marcos! ¿Cómo estás? Estuve viendo tu trabajo..."*). Avoid overly bureaucratic stiffness (*"Estimada señora"* sounds like a legal summons).
  * Direct to `https://vcrsoftwares.com/es/` (or user's `website_es`).
* **Portuguese (Brazil & Lusophone Markets):**
  * Strategic, consultive tone focused on eliminating friction and driving WhatsApp direct appointments.
  * Direct to `https://vcrsoftwares.com/` (or user's `website_pt`).

---

## 4. Rapid External OSINT Checks

If the bio provides minimal detail:
1. Search Google Maps: `"business_name" city google maps` (checks address, reviews, photos, business hours).
2. Run Technical Recon: `python3 scripts/recon_lead.py --url <URL>` (measures TTFB latency and identifies tech stack in seconds).

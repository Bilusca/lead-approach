# GEMINI.md — Diretrizes de Projeto para o Google Antigravity

Este arquivo define as regras de workspace e procedimentos operacionais para o **Google Antigravity (AGY)** ao trabalhar neste repositório.

---

## 🚀 Descoberta da Skill no Antigravity
* O Antigravity carrega a skill automaticamente a partir de `.agents/skills/lead-approach/SKILL.md`.
* Ao receber solicitações de prospecção, cold outreach ou criação de mensagens de abordagem, ative a skill `lead-approach`.

---

## 🛠️ Scripts & Execução de Ferramentas
* **Configuração de Perfil & Memória:** Use `scripts/setup_profile.py` para salvar ou carregar as preferências e o manual da marca do usuário (`config/profile.json`).
* **Processamento de Listas & Roadmap:** Use `scripts/process_list.py` para receber arquivos com listas de leads (PDF, TXT, MD, CSV, JSON) e gerar o plano de ação priorizado.
* **Diagnóstico de Website:** Use `scripts/recon_lead.py` para fazer a análise técnica instantânea antes de redigir a mensagem.
* **Geração de PDF (Manual da Marca):** Use `scripts/compile_report.py` para produzir o dossiê executivo A4 seguindo rigorosamente a paleta de cores, tipografia e logo configurados no manual da marca.
* **Execução do Chromium Headless:** O script utiliza `--headless=new --disable-gpu --no-sandbox --disable-dev-shm-usage`. Caso o sandbox bloqueie a chamada do navegador, oriente o usuário ou execute com a elevação necessária.

---

## 🎯 Padrão de Redação (Outbound No-Call)
* **Memória de Campanha:** Consulte sempre `config/profile.json` ou `config/profile.md` antes de redigir para adotar a empresa, o tom de voz e os links do usuário.
* **Idioma Primário:** Opere prioritariamente em **Inglês** (US/Global), chaveando fluentemente para **Espanhol** ou **Português** conforme a localização ou solicitação do usuário.
* **Zero Fricção de Reunião:** Nunca sugira chamadas telefônicas ou videoconferências. Sempre posicione a conversa como 100% por texto no Direct ou WhatsApp.
* **Sincronia de Idiomas e Links:**
  * Inglês (Principal): `https://vcrsoftwares.com/en/`
  * Espanhol: `https://vcrsoftwares.com/es/`
  * Português: `https://vcrsoftwares.com/`
* **Universalidade de Nicho (Qualquer Segmento):** Esta skill foi construída para prospectar em **qualquer nicho, indústria ou mercado** (SaaS, Médicos, Estética, Direito, Arquitetura, Imobiliário, Finanças, Consultoria, Serviços Locais, E-commerce, Logística, etc.). Adapte os 4 blocos e o diagnóstico ao segmento do prospect.
* **Consultas de Referência:**
  * Para matriz de adaptação e playbooks setoriais, leia `references/niche-playbooks.md`.
  * Para modelos universais de abordagem e frameworks de copy, leia `references/copy-frameworks.md`.
  * Para quebra de objeções por texto, leia `references/objection-closing.md`.

# GEMINI.md — Diretrizes de Projeto para o Google Antigravity

Este arquivo define as regras de workspace e procedimentos operacionais para o **Google Antigravity (AGY)** ao trabalhar neste repositório.

---

## 🚀 Descoberta da Skill no Antigravity
* O Antigravity carrega a skill automaticamente a partir de `.agents/skills/lead-approach/SKILL.md`.
* Ao receber solicitações de prospecção, cold outreach ou criação de mensagens de abordagem, ative a skill `lead-approach`.

---

## 🛠️ Scripts & Execução de Ferramentas
* **Passo 0 Obrigatório: Verificação de Setup Único (Zero Config Padrão):**
  * Cada setup é único e exclusivo para a marca/empresa do usuário. **Não existe configuração padrão.**
  * Ao receber uma tarefa de prospecção, verifique imediatamente `config/profile.json` (ou execute `python3 scripts/setup_profile.py --check`).
  * **Se os dados do negócio já vieram no prompt:** não faça perguntas interativas desnecessárias; salve diretamente os dados em `config/profile.json` via `setup_profile.py` e prossiga com a prospecção.
  * **Se o perfil NÃO estiver configurado e o usuário NÃO forneceu os dados:** PARE e conduza imediatamente a entrevista interativa de setup (nome da marca, produtos/serviços, dor central resolvida, tom de voz, público/nicho, links, canal de CTA e identidade visual).
* **Configuração de Perfil & Memória:** Use `scripts/setup_profile.py` para salvar ou carregar as preferências e o manual da marca do usuário (`config/profile.json`).
  * Suporta `--check` para validação rápida, `--from-json <arquivo>` para carga direta, modo interativo no terminal (`python3 scripts/setup_profile.py`) e argumentos CLI (`--name`, `--service`, etc.).
  * **Privacidade Local:** `config/profile.json` e `config/profile.md` são ignorados pelo git (`.gitignore`) e contêm dados privados do operador. O GitHub mantém apenas o template público `config/profile.example.json`.
* **Processamento de Listas & Roadmap:** Use `scripts/process_list.py` para receber arquivos com listas de leads (PDF, TXT, MD, CSV, JSON) e gerar o plano de ação priorizado.
  * Cada relatório e suas exportações são salvos em pasta própria em `report/<nome-do-report>-<data>/` (diretório ignorado pelo git).
  * Gera o pacote completo: `<stem>.pdf`, `<stem>.html` (com botões de cópia e links clicáveis), `<stem>.md`, `<stem>-trello.md` (formatação para importação e cards), `<stem>-trello.csv` e `<stem>-trello.json`.
* **Diagnóstico de Website:** Use `scripts/recon_lead.py` para fazer a análise técnica instantânea antes de redigir a mensagem.
* **Geração de PDF (Manual da Marca):** Use `scripts/compile_report.py` para produzir o dossiê executivo A4 seguindo rigorosamente a paleta de cores, tipografia e logo configurados no manual da marca. Salva automaticamente em `report/<nome-do-report>-<data>/`.
* **Execução do Chromium Headless:** O script utiliza `--headless=new --disable-gpu --no-sandbox --disable-dev-shm-usage`. Caso o sandbox bloqueie a chamada do navegador, execute com elevação de permissão (`BypassSandbox: true`).

---

## 🎯 Padrão de Redação & Engenharia de Conversão
* **Memória de Campanha:** Consulte sempre `config/profile.json` ou `config/profile.md` antes de redigir para adotar a empresa, os serviços, o canal de CTA, a duração da call e os links do usuário.
* **Idioma Primário:** Opere prioritariamente em **Inglês** (US/Global), chaveando fluentemente para **Espanhol** ou **Português** conforme a localização ou solicitação do usuário.
* **Mensagem Curta & Sem Tecnicês:** O lead NÃO é técnico. Mensagens curtas (~50 a 80 palavras), sem jargões como "blinda", "ecossistema digital", "gargalos" ou termos de TI. Fale de forma simples e humana sobre o que o cliente sente no dia a dia (site demorando no celular, pessoas desistindo antes de mandar mensagem, link confuso na bio).
* **Framework de Conversão (Dor -> Solução -> Pergunta Provocativa):**
  1. **Hook da Dor:** Inicia com a Dor Central diagnosticada no scanner (ex: velocidade lenta, ausência de página mobile, abandono em árvore de links, atrito de agendamento).
  2. **Solução do Setup:** Apresenta a empresa e o serviço configurado no setup com link de portfólio.
  3. **Pergunta Provocativa de Fechamento:** Sempre encerra com uma pergunta provocativa chamando para uma Call rápida de 10 a 15 minutos (ou canal predefinido no setup, como WhatsApp ou Direct).
* **Scanner Multicanal & Multi-Origem:** Aceita leads de Google Business (Google Maps), Instagram, LinkedIn, Facebook, Websites e listas de contatos com links. Extrai automaticamente todos os pontos de contato e diagnostica a Dor Central.
* **Sincronia de Idiomas e Links:**
  * Inglês (Principal): `https://vcrsoftwares.com/en/`
  * Espanhol: `https://vcrsoftwares.com/es/`
  * Português: `https://vcrsoftwares.com/`
* **Universalidade de Nicho (Qualquer Segmento):** Esta skill foi construída para prospectar em **qualquer nicho, indústria ou mercado** (SaaS, Médicos, Estética, Direito, Arquitetura, Imobiliário, Finanças, Consultoria, Serviços Locais, E-commerce, Logística, etc.). Adapte a dor e a solução ao segmento do prospect.
* **REGRA MANDATÓRIA: Nome Real da Pessoa/Empresa vs. ID do IG (Anti-Handle):**
  * O agente **NUNCA** deve usar o ID/handle do Instagram (ex: `@clinica_xyz`, `dr_joao_silva`) como o nome do lead na abordagem ou nos relatórios.
  * O agente **DEVE SEMPRE** identificar e trazer o **Nome Real da Pessoa/Especialista** (ex: *Dr. João Silva*, *Dra. Mariana Costa*) ou o **Nome Fantasia Oficial da Empresa** (ex: *Clínica Sorriso & Arte*, *Moreira Odontologia Digital*).
  * **Especialista / Pessoa Física:** aborde diretamente a pessoa (*"Olá, Dr. João! Tudo bem?"*, *"Oi, Mariana!"*), tratando no singular (*"seu perfil"*, *"seus serviços"*, *"seus pacientes"*). Jamais use *"pessoal da Dr. Fulano"*.
  * **Empresa / Clínica / Escritório:** aborde a equipe pelo nome comercial (*"Olá, equipe da Lumina Odontologia!"*, *"Olá, pessoal da Sorriso & Arte!"*).
  * Busque o nome oficial nas meta tags (`og:site_name`, `og:title`, `<title>`, JSON-LD), no Google Business ou no Nome de Exibição (Display Name) da bio. Se só houver o handle, humanize-o de forma limpa (*"Dr. Marcelo Albuquerque"*), removendo `_sp`, `_oficial`, etc.
* **Consultas de Referência:**
  * Para matriz de adaptação e playbooks setoriais, leia `references/niche-playbooks.md`.
  * Para modelos universais de abordagem e frameworks de copy, leia `references/copy-frameworks.md`.
  * Para quebra de objeções por texto, leia `references/objection-closing.md`.

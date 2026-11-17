# Lead Approach — Laboratório de Prospecção Ativa B2B & Conversão "No-Call"

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platforms: Antigravity | Claude Code | Codex](https://img.shields.io/badge/Platforms-Antigravity%20%7C%20Claude%20Code%20%7C%20Codex-purple.svg)](./SKILL.md)
[![Standard: Agent Skills Spec](https://img.shields.io/badge/Standard-AAIF%20%2F%20Agent%20Skills-green.svg)](https://agentskills.io)
[![Languages: English | Español | Português](https://img.shields.io/badge/Languages-EN%20%7C%20ES%20%7C%20PT-orange.svg)](#-arquitetura-tril%C3%ADngue-ingl%C3%AAs-principal--espanhol--portugu%C3%AAs)

> **Skill universal de outbound e engenharia de abordagem fria (Cold DMs) para venda de serviços digitais de alto valor.**  
> Compatível nativamente com **Google Antigravity**, **Anthropic Claude Code** e **OpenAI Codex**.  
> **Idioma Principal:** Inglês (US / Global High-Ticket) com suporte nativo e chaveamento fluente para Espanhol e Português.

🌐 **Traduções:** [🇺🇸 English Version](./README.md)

---

## 🎯 Visão Executiva do Projeto

O **lead-approach** é um laboratório e skill de engenharia de vendas outbound desenhada para transformar links brutos de redes sociais (Instagram, LinkedIn, WhatsApp, Google Business) em oportunidades qualificadas de fechamento para serviços digitais de alto padrão (sites ultrarrápidos, landing pages de alta conversão, sistemas web sob medida e identidade de marca).

### O Axioma Central da Metodologia "No-Call"
> **"A abordagem, a entrega de valor inicial e o fechamento devem ser conduzidos 100% por texto assíncrono (Direct / WhatsApp / LinkedIn / E-mail), sem jamais forçar ou exigir chamadas síncronas de voz ou vídeo."**

### 🏹 Os 4 Pilares da Metodologia Outbound Ativa
Diferente do marketing inbound passivo (esperar o lead encontrar seu site), esta skill foi desenhada para a **prospecção ativa (Hunting)**:
1. **Hunting Ativo de Decisores:** Em vez de esperar, identificamos ativamente clínicas, escritórios e negócios de alto padrão com demanda comprovada, mas com gargalos visíveis em suas páginas.
2. **Interrupção com Entrega de Valor:** O lead frio não te conhece. Nunca interrompa o dia dele com um pedido ("vamos marcar uma reunião?"), mas sim com um presente: um diagnóstico técnico de 30 segundos revelando onde o site mobile dele está perdendo clientes.
3. **Eliminação do Atrito de Compromisso ("No-Call"):** O cold outreach tradicional morre porque exige alto esforço no primeiro contato ("posso te ligar 15 minutos?"). Reduzimos o atrito a zero: *"Não precisa de reunião; podemos conversar por texto por aqui mesmo"*.
4. **Cadência Estruturada Multitoque:** Outbound é um processo: **Aquecimento Social** (Dia 0) ➔ **DM de 4 Blocos** (Dia 1) ➔ **Follow-up Assíncrono** (Dia 4) ➔ **Ponte de Fechamento no WhatsApp** (Dia 7).

---

## 🚀 Compatibilidade Multi-Agente (Antigravity · Claude Code · Codex)

A skill adota estritamente o padrão aberto da **Agent Skills Specification (AAIF)**, garantindo interoperabilidade total sem duplicar arquivos:

| Plataforma | Ponto de Entrada / Descoberta | Arquivo de Regras & Memória |
| :--- | :--- | :--- |
| **Google Antigravity** | `.agents/skills/lead-approach/SKILL.md` | [GEMINI.md](./GEMINI.md) / [AGENTS.md](./AGENTS.md) |
| **Anthropic Claude Code** | `.claude/skills/lead-approach/SKILL.md` *(symlink)* | [CLAUDE.md](./CLAUDE.md) |
| **OpenAI Codex** | `.agents/skills/lead-approach/SKILL.md` | [AGENTS.md](./AGENTS.md) |

### Instalação Global no Sistema (1 Comando)
Para disponibilizar a skill globalmente na sua máquina para todos os assistentes de uma só vez:

```bash
./install.sh --all
```
*Ou selecione individualmente: `./install.sh --antigravity`, `./install.sh --claude` ou `./install.sh --codex`.*

---

## 🌍 Arquitetura Trilíngue (Inglês Principal · Espanhol · Português)

A skill opera **primariamente em Inglês** para máxima capacidade de raciocínio dos modelos e alinhamento com o mercado de maior ticket médio global, mantendo chaveamento nativo:

1. **Inglês (Principal / Default):** Padrão para os Estados Unidos, Reino Unido, Canadá e empresas globais (`https://vcrsoftwares.com/en/`).
2. **Espanhol (Nativo):** Ativado para leads na América Latina, Espanha ou comunidades hispânicas nos EUA (Miami, Orlando, Texas) (`https://vcrsoftwares.com/es/`).
3. **Português (Nativo):** Ativado para o mercado corporativo brasileiro e comunidades lusófonas (`https://vcrsoftwares.com/`).

---

## 📂 Arquitetura do Repositório

```text
lead-approach/
├── .agents/
│   └── skills/
│       └── lead-approach/             # Pacote canônico da Skill (Agent Skills Spec)
│           ├── SKILL.md               # Definição e workflow operacional em 7 etapas
│           ├── config/                # Memória persistente da agência & Manual da Marca
│           │   ├── profile.json       # Configuração estruturada em JSON
│           │   └── profile.md         # Manual da Marca e diretrizes em Markdown
│           ├── references/
│           │   ├── copy-frameworks.md # Modelos em 4 blocos (EN, ES, PT), Stories & Áudios
│           │   ├── niche-playbooks.md # Playbooks: Advocacia, Arquitetura, Odonto e Imóveis
│           │   ├── profiling-guide.md # Roteiro de 5 minutos de varredura comercial
│           │   └── objection-closing.md # Quebra de objeções por texto & fechamento WhatsApp
│           ├── scripts/
│           │   ├── setup_profile.py   # Assistente de setup da oferta e Manual da Marca
│           │   ├── process_list.py    # Processador de listas (PDF/TXT/CSV) & Roadmap
│           │   ├── recon_lead.py      # Varredura técnica de websites e links de bio
│           │   ├── generate_pdf.py    # Compilador de PDF via Chromium headless
│           │   └── compile_report.py  # Compilador de dossiê A4 com Manual da Marca
│           └── templates/
│               └── report-template.html # Template A4 parametrizado por CSS Variables
├── .claude/
│   └── skills/
│       └── lead-approach -> symlink para .agents/skills/lead-approach
├── config -> symlink para .agents/skills/lead-approach/config
├── CLAUDE.md                          # Instruções para Claude Code
├── AGENTS.md                          # Instruções universais para Codex e Antigravity
├── GEMINI.md                          # Regras específicas para Antigravity
├── install.sh                         # Script de instalação global multi-plataforma
├── README.md                          # Documentação principal em Inglês
└── README.pt-BR.md                    # Documentação em Português
```

---

## 🛠️ Ferramentas e Scripts CLI

### 1. Setup de Perfil, Memória & Manual da Marca (`setup_profile.py`)
Configura a sua empresa, tom de voz, canais, links de portfólio e o **Manual de Identidade Visual da Marca (Brand Guidelines)** para que todos os relatórios em PDF adotem automaticamente suas cores, tipografia, slogan e logo:

```bash
# Modo Interativo (perguntas guiadas passo a passo no terminal):
python3 scripts/setup_profile.py -i

# Configuração direta via parâmetros (com preset de cores e slogan):
python3 scripts/setup_profile.py \
  --name "Apex Growth Agency" \
  --service "Sites Ultrarrápidos & Landing Pages de Conversão" \
  --tone consultivo \
  --brand-preset sapphire \
  --brand-tagline "Engenharia de Conversão & Crescimento Digital" \
  --brand-color "#2563eb" \
  --website-en "https://suaempresa.com/en/" \
  --whatsapp "https://wa.me/5511999999999"

# Visualizar o perfil e manual da marca ativos em memória:
python3 scripts/setup_profile.py --show
```

### 2. Processamento em Lote & Roadmap de Abordagem (`process_list.py` / Comando `list`)
Ingere listas de leads a partir de arquivos (**PDF, TXT, Markdown, CSV, JSON**) ou texto direto. O script executa a varredura técnica de cada link, consulta a memória da sua agência e monta um roadmap completo de execução multidias:

```bash
# A partir de um arquivo PDF ou texto:
python3 scripts/process_list.py --file lista_empresas.pdf --output roadmap.md

# Gerando simultaneamente o dossiê executivo em PDF diagramado com sua marca:
python3 scripts/process_list.py --file leads.csv --pdf roadmap_executivo.pdf

# A partir de uma lista direta de URLs/handles em texto:
python3 scripts/process_list.py --input "https://clinica1.com, @advocacia2, https://studio3.com"
```

### 3. Varredura Técnica de Websites (`recon_lead.py`)
Mede a latência inicial do servidor (TTFB), identifica viewport mobile, CMS (WordPress, Elementor, Divi, Webflow, Linktree, Beacons) e ferramentas de agendamento (Acuity, Booksy, Calendly, WhatsApp):

```bash
# Diagnóstico em formato Markdown para contexto do agente:
python3 scripts/recon_lead.py --url https://sitexemplo.com

# Exportação estruturada em JSON:
python3 scripts/recon_lead.py --url https://linktr.ee/clinica --format json
```

### 4. Compilação de Dossiê Executivo A4 com Manual da Marca (`compile_report.py`)
Gera relatórios executivos em formato A4 que aplicam rigorosamente as cores primárias e secundárias da sua empresa, fundos suaves calculados, tipografia, monograma/logo e slogan configurados no setup:

```bash
# A partir de um arquivo JSON estruturado:
python3 scripts/compile_report.py --data leads.json --output relatorio_prospeccao.pdf

# Geração de exemplo para testes visuais:
python3 scripts/compile_report.py --sample --output exemplo_executivo.pdf
```

---

## 🎯 A Fórmula dos 4 Blocos da Mensagem

Toda mensagem gerada pela skill segue uma estrutura psicológica testada para leitura em smartphones:

```text
┌──────────────────────────────────────────────────────────────┐
│ BLOCO A: Conexão Humana & Elogio Concreto Verificável       │
│ "¡Hola Dra. Carolina! Sigo su trabajo con K-Beauty..."       │
├──────────────────────────────────────────────────────────────┤
│ BLOCO B: Apresentação & Diagnóstico do Gargalo Digital        │
│ "Tratamientos tan exclusivos pierden pacientes si usan links │
│ genéricos o páginas lentas en el móvil..."                   │
├──────────────────────────────────────────────────────────────┤
│ BLOCO C: Solução Tangível & Prova Social (Link Localizado)   │
│ "Creamos páginas ultra rápidas para clínicas de EE.UU.:      │
│ 👉 https://vcrsoftwares.com/es/ "                            │
├──────────────────────────────────────────────────────────────┤
│ BLOCO D: Chamada para Ação "No-Call" (100% por Texto)        │
│ "No hace falta coordinar llamada; me pueden responder por    │
│ este chat y les paso 2 ideas puntuales por texto."           │
└──────────────────────────────────────────────────────────────┘
```

---

## 🏛️ Playbooks Verticais para Nichos High-Ticket

Diagnósticos técnicos e roteiros especializados para os 4 setores mais rentáveis:
* **Escritórios de Advocacia:** Substituição de formulários estáticos de 10 campos por triagem confidencial em 1 toque no WhatsApp, respeitando o código de ética.
* **Arquitetura & Design de Interiores:** Eliminação da lentidão de 8s de fotos em 4K no mobile sem perder nitidez, transformando visitantes do feed em briefings.
* **Odontologia Estética de Luxo:** Foco em transformações de sorriso (facetas, Invisalign) antes do agendamento, evitando telas frias de calendário.
* **Imobiliárias de Alto Padrão:** Substituição de portais MLS engessados por páginas únicas de empreendimento com download direto de catálogo no WhatsApp.

---

## 💡 Exemplos de Prompts para o Agente

* `"list leads.pdf"` (lê o arquivo, audita cada link e monta o roadmap de abordagem)
* `"Configure meu manual da marca com a cor #2563eb, slogan 'Engenharia de Conversão' e tipografia moderna"`
* `"Faça a varredura do site https://clinicaexemplo.com e aponte os vazamentos de receita para o Bloco B"`
* `"Gere uma abordagem no-call em inglês para uma clínica de estética em Miami que usa Linktree na bio"`
* `"Como respondo a este lead que disse 'me mande a proposta por e-mail' para mantê-lo conversando no WhatsApp?"`
* `"Compile os últimos leads auditados em um dossiê executivo em PDF seguindo o manual da minha marca"`

---

## 📄 Licença
Projeto de código aberto sob a [Licença MIT](LICENSE).

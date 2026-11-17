# Lead Approach — Laboratório de Prospecção & Conversão Ativa B2B

Projeto dedicado ao desenvolvimento, teste, documentação e aprimoramento contínuo da **Skill `lead-approach`**.

O objetivo desta skill é fornecer um ecossistema completo para transformar listas de perfis de redes sociais (Instagram, LinkedIn, etc.) em oportunidades reais de vendas para serviços digitais (sites ultrarrápidos, landing pages de alta conversão, branding e sistemas), utilizando uma **metodologia 100% orientada a texto (sem necessidade de chamadas de voz ou vídeo)**.

---

## 📂 Estrutura do Projeto

```text
Projects/lead-approach/
├── .agents/
│   └── skills/
│       └── lead-approach/
│           ├── SKILL.md                 # Definição principal da Skill
│           ├── references/
│           │   ├── copy-frameworks.md   # Frameworks de copy (ESP, ENG, PT) e nichos
│           │   ├── profiling-guide.md   # Guia de varredura e diagnóstico de leads
│           │   └── objection-closing.md # Tratamento de objeções e transição para WhatsApp
│           ├── scripts/
│           │   └── generate_pdf.py      # Automação para gerar PDFs executivos (Chromium)
│           └── templates/
│               └── report-template.html # Template base em HTML/CSS para relatórios A4
├── SKILL.md                             # Cópia raiz da Skill para edição e consulta rápida
└── README.md                            # Documentação geral do laboratório
```

---

## 🎯 Por que a Metodologia "No-Call" (100% por Texto)?

1. **Eliminação de Barreira Linguística:** Permite que o operador prospecte em mercados internacionais (EUA, América Latina, Europa) em inglês ou espanhol sem travar ou se sentir inseguro em ligações síncronas.
2. **Tempo de Resposta Estratégico:** A conversa assíncrona permite traduzir, revisar métricas e estruturar argumentos cirúrgicos antes de enviar cada resposta.
3. **Respeito ao Tempo do Lead:** Donos de clínicas, médicos e gestores de serviços de luxo raramente têm tempo para chamadas de vendas frias. Uma mensagem objetiva que diagnostica um problema real e oferece 2 ideias por texto gera muito mais adesão e respeito.
4. **Fechamento Ágil no WhatsApp:** A transição do Direct do Instagram para o WhatsApp corporativo (`wa.me`) concentra o lead no canal onde orçamentos são aprovados e contratos são fechados rapidamente.

---

## 🚀 Roadmap de Evolução da Skill

- [x] Estrutura base da Skill e documentação de frameworks (Espanhol, Inglês e Português).
- [x] Protocolo anti-spam com aquecimento prévio de Stories e feed.
- [x] Scripts de fechamento e transição suave para WhatsApp corporativo.
- [x] Template e script de compilação de dossiês executivos em PDF via Chromium.
- [ ] Implementação de analisador automático de links na bio (Acuity, Booksy, Fresha, Linktree).
- [ ] Módulo de análise de velocidade web em lote (Lighthouse / PageSpeed CLI).
- [ ] Criação de matriz de abordagens para novos nichos (Advogados, Arquitetos, E-commerces, Clínicas Odontológicas).

# 02 · Requisitos

[← Documentação](../README.md)

O que o Steely precisa fazer (requisitos funcionais), com que qualidade (requisitos não funcionais), como cada funcionalidade acontece (casos de uso) e quais regras precisa respeitar (regras de negócio).

| Documento / pasta | O que é |
|---|---|
| [documento-de-requisitos-v2.docx](documento-de-requisitos-v2.docx) | **Versão vigente (v2.0).** 22 RFs, cada um com entradas, ações e saídas, e 13 RNFs mensuráveis |
| [casos-de-uso/](casos-de-uso/) | Especificação dos 58 casos de uso (`STY001`–`STY058`) e diagramas por pacote |
| [regras-de-negocio/](regras-de-negocio/) | Regras por caso de uso (`STYxxx-RNyy`), parâmetros (`PRM`) e regras transversais (`RB`) |
| [rastreabilidade/](rastreabilidade/) | Matrizes que ligam cada RF aos casos de uso, regras, RNFs, ADRs e testes |

> Os requisitos do 1º semestre (RF-01 a RF-21, outra numeração) estão em [historico/](../historico/).

## Requisitos funcionais (RF)

| ID | Requisito |
|---|---|
| RF-01 | Gestão de acesso, autenticação e 2FA |
| RF-02 | Gestão de perfil, reputação e conformidade com a LGPD |
| RF-03 | Construtor de setups com verificação de compatibilidade |
| RF-04 | Análise de desempenho, tendências de preço e falhas crônicas |
| RF-05 | Publicação e triagem técnica de hardware (manual e por IA) |
| RF-06 | Busca textual e filtros granulares multicritério |
| RF-07 | Gestão de status e impulsionamento de ofertas |
| RF-08 | Chat interno com respostas automáticas e proteção de dados |
| RF-09 | Gestão de propostas e negociação de lotes |
| RF-10 | Agendamento de encontros, rotas e pontos de coleta (offline-first) |
| RF-11 | Validação de entrega por QR Code e emissão de comprovante |
| RF-12 | Emissão de laudo técnico pericial |
| RF-13 | Garantia de 7 dias, devoluções e arbitragem |
| RF-14 | Carteira digital de moedas virtuais (cashback e resgate) |
| RF-15 | Leilões exclusivos com moeda social (anti-sniping) |
| RF-16 | Desafio Hardware Captcha gamificado |
| RF-17 | Homologação institucional e Mural de Doações (ONGs) |
| RF-18 | Sugestão inteligente de ecopontos e logística reversa |
| RF-19 | Apuração e dashboard de métricas ESG |
| RF-20 | Painel de moderação, bloqueio e gestão de conteúdo |
| RF-21 | Relatórios de inteligência comercial e confiabilidade (DaaS) |
| RF-22 | Auditoria centralizada, trilha de logs e curadoria de IA |

## Requisitos não funcionais (RNF)

| ID | Requisito | Meta principal |
|---|---|---|
| RNF-01 | Criptografia em trânsito e em repouso | TLS 1.3, Argon2id/bcrypt, AES-256-GCM |
| RNF-02 | Validação offline do QR Code | Assinatura Ed25519, conferida em ≤ 150 ms sem internet |
| RNF-03 | LGPD e k-anonimato | DaaS com k ≥ 30; expurgo de contas em até 30 dias |
| RNF-04 | Latência das APIs | Leitura p95 ≤ 200 ms, escrita p99 ≤ 500 ms com 1.000 usuários |
| RNF-05 | Latência do Scanner IA | ≤ 4 s, com circuit breaker para preenchimento manual |
| RNF-06 | Leilões em tempo real | Lances propagados em ≤ 100 ms via WebSocket |
| RNF-07 | Offline-first | Sincronização em até 10 s após reconectar |
| RNF-08 | Disponibilidade | 99,5% ao mês, RTO ≤ 2 h, RPO ≤ 5 min |
| RNF-09 | Idempotência e consistência | Operações financeiras atômicas, com Idempotency-Key |
| RNF-10 | Responsividade e acessibilidade | 360–2560 px, Lighthouse ≥ 90, WCAG 2.1 AA, Android 8+ |
| RNF-11 | Trilha de auditoria | Logs JSON imutáveis, conforme o Marco Civil da Internet |
| RNF-12 | Metodologia ESG auditável | Fatores de conversão abertos e versionados |
| RNF-13 | Proteção de borda | Rate limiting (ex.: 5 tentativas de login a cada 5 min) e mitigação de DDoS |

# 05 · Design

[← Documentação](../README.md)

| Documento | O que é |
|---|---|
| [brand-guidelines.pdf](brand-guidelines.pdf) | Manual da marca v1.0 (ago/2026, 30 páginas): missão, valores, logo, paleta de cores e tipografia |
| [prototipos/](prototipos/) | Telas de alta fidelidade do app (PNG e HTML) |
| [GUIA-DE-PROTOTIPOS.md](GUIA-DE-PROTOTIPOS.md) | Passo a passo para gerar uma tela nova com Claude ou Gemini, verificar e colocar no Figma |

Os componentes de interface seguem o design system compartilhado entre web e mobile ([ADR-19](../04-arquitetura/adr/adr-19-design-system-compartilhado.pdf)) e as regras de acessibilidade do [ADR-20](../04-arquitetura/adr/adr-20-acessibilidade-e-responsividade.pdf).

## Design System em resumo

Valores tirados do [manual da marca](brand-guidelines.pdf) e das telas já aprovadas. Toda tela nova usa **só** isto — as verificações automáticas reprovam o resto.

| Cor | Hex | Uso |
|---|---|---|
| Charcoal | `#0D1B2A` | Fundo do app, texto sobre o verde |
| Fundo da página | `#070F18` | Em volta do celular, notch |
| Superfície | `#11233A` | Cartões |
| Borda | `#1A3250` | Bordas, divisórias, trilhos |
| Verde Steely | `#1DDB6A` | Ação principal, preço, item ativo |
| Verde ESG | `#A8EFC4` | Sustentabilidade, moedas, reuso |
| Branco | `#FFFFFF` | Texto principal |
| Cinza | `#6B7A8D` | Texto secundário, ícones inativos |
| Alerta | `#FF5A5F` | Só campo obrigatório, erro e segurança |

Transparências dessas mesmas cores são permitidas (ex.: `rgba(29,219,106,0.12)` no fundo de um ícone verde).

| Estilo | Fonte | Tamanho / peso |
|---|---|---|
| Título da tela | Space Grotesk | 24 Bold |
| Título de seção | Space Grotesk | 18 Bold |
| Subtítulo | Space Grotesk | 16 Medium |
| Preço | Space Grotesk | 16–24 Bold, verde |
| Texto | DM Sans | 14 Regular |
| Texto pequeno | DM Sans | 13 Regular |
| Rótulo / botão | DM Sans | 15 ou 13 SemiBold |
| Legenda | DM Sans | 11 Medium |

Escala permitida: **11, 13, 14, 15, 16, 18, 20, 24 px**. Cantos: 8 (botão pequeno), 12 (campo, cartão, botão), 18 (destaque), 44 (celular). Margem lateral do conteúdo: 24 px. Ícones: [Lucide](https://lucide.dev), traço 2.

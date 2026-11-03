# Regras de negócio

[← Requisitos](../README.md)

| Arquivo | O que é | Situação |
|---|---|---|
| [regras-de-negocio-v2.xlsx](regras-de-negocio-v2.xlsx) | 280 regras por caso de uso (`STYxxx-RNyy`), aba de **controle de alterações** em relação à v1 e 67 **parâmetros** (`PRM`) com prazos, limites e valores | **Vigente** |
| [regras-de-negocio-v1.xlsx](regras-de-negocio-v1.xlsx) | Primeira versão: 250 regras em 59 casos de uso | Substituída pela v2, mantida como referência |
| [regras-transversais-rb-01-a-15.pdf](regras-transversais-rb-01-a-15.pdf) | 15 regras que valem para o sistema todo (`RB-01`–`RB-15`) | **Vigente** — os ADRs citam essas regras com frequência |

## Como ler

- **Regra de caso de uso** — `STY017-RN03` é a regra 03 do caso de uso STY017 (Scanner IA). Está na v2.
- **Regra transversal** — `RB-06` vale para qualquer caso de uso. Está no PDF das regras transversais.
- **Parâmetro** — `PRM-15` é um valor configurável (ex.: um prazo em dias) usado pelas regras. Está na v2.

## Da v1 para a v2

A v2 é uma revisão da v1, feita logo depois: das 250 regras, 208 foram mantidas, 41 ajustadas e 31 criadas. A aba *Controle de Alterações* da v2 registra cada mudança.

> **Ponto conhecido:** a regra `STY051-RN01` (suspender a remoção de um post quando há transação em andamento) aparece como "ajustada" no controle de alterações, mas não está na aba do STY051 na v2. O texto original está na v1.

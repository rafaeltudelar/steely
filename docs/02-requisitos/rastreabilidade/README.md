# Matriz de rastreabilidade

[← Requisitos](../README.md)

A rastreabilidade mostra, para cada requisito, de onde ele veio e onde ele é atendido.

| Arquivo | O que é |
|---|---|
| [matriz-de-rastreabilidade-v2.xlsx](matriz-de-rastreabilidade-v2.xlsx) | **Principal.** Cadeia completa: RF → origem (TAP ou lei) → casos de uso → regras → parâmetros → RNF → ADR → casos de teste. Inclui a rastreabilidade de volta (do caso de uso até o RF) |
| [matriz-de-rastreabilidade-v1-detalhada.xlsx](matriz-de-rastreabilidade-v1-detalhada.xlsx) | **Complementar.** Cruza RF × casos de uso e traz a *Matriz Detalhada*, que dá, para cada caso de uso, pré-condição, critério de aceite e exceções (o nível de detalhe de um teste) |

```
RF ─► origem (TAP / lei) ─► STY ─► STYxxx-RNyy ─► PRM ─► RNF ─► ADR ─► caso de teste
```

## Pontos conhecidos

- Os casos `STY045` (método de pagamento) e `STY057` (guia informativo) não estão ligados a nenhum RF.
- Na v2, os 22 RFs aparecem como "Coberto", mas os casos de teste (`CT`) ainda não foram especificados.

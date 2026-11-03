# ADR-03 — Escrow simulado e retenção de 7 dias
**Architecture Decision Record · Projeto Steely · Escola de TI · UniCesumar**

| Campo | Valor | Campo | Valor |
| --- | --- | --- | --- |
| **Status** | ☒ Proposto ☐ Aceito ☐ Rejeitado ☐ Substituído pelo ADR-___ | **Data** | 01/11/2026 |
| **Responsável** | Augusto Palma Guglielmi | **Sprint** | Entrega até 23/11 (Sprints 15 a 17) |
| **Participantes** | Augusto Palma Guglielmi, Fabrício Notoya Thomas, Pietro Pasqual Silva, Rafael Tudela Rizental, Thiago Lopes Martins | | |
| **Vínculos** | R-03 (Matriz GUT) · RF-11 e RF-13 · STY028, STY031 e STY033–STY035 · RB-09 · D3 da Matriz CSD · PRM-29 · RNF-09 · ADR-05, ADR- 06, ADR-08, ADR-09, ADR-10, ADR-14 e ADR-16 | | |

## 1. Contexto

O Steely garante ao comprador 7 dias, contados da entrega, para testar o hardware (PRM-29). Nesse período o valor da compra fica retido e só chega ao
vendedor se o prazo terminar sem devolução nem reclamação. Esse mecanismo é o escrow (custódia). A Matriz CSD (D3) deixa em aberto como reter o
valor: gateway, conta intermediária ou saldo simulado.
O projeto é acadêmico e não pode movimentar dinheiro real. A regra, porém, precisa funcionar e ser demonstrada na defesa. Ciclo esperado:
A entrega é confirmada pela leitura do QR Code (STY028) e o valor passa a ficar retido.
Sem devolução, laudo em análise ou disputa em 7 dias, o valor é liberado ao vendedor e a transação passa a concluída.
Com devolução ou reclamação aberta (STY031, STY033–STY035), a liberação fica bloqueada até a decisão.
Se a decisão favorecer o comprador, o valor é estornado.
Restrições já fixadas pelo grupo: o banco é o PostgreSQL do Supabase (ADR-08), que já prevê a custódia como saldo simulado; o backend é FastAPI
chamando funções SQL do schema private (ADR-09); a idempotência usa escrow.transaction_id e (escrow_id, tipo_final) (ADR-14); o prazo
roda por varredura do pg_cron, com custodia_libera_em = entregue_em + 168 h e a função release_escrow(transaction_id) (ADR-16). A RB-
09 proíbe converter moeda virtual em dinheiro real, então o escrow não pode usar o ledger de moedas do ADR-10. O risco R-03 (pontuação 80) trata da
responsabilidade sobre a custódia.

## 2. Direcionadores da decisão

Fidelidade à regra de negócio: reter, liberar, bloquear e estornar.
Separação do ledger de moedas: respeitar a RB-09 (nenhuma conversão para valor monetário).
Independência de terceiros: a defesa não pode falhar por causa de um serviço externo.
Esforço até 23/11: caber nas sprints restantes junto com o fluxo de entrega.
Atomicidade e idempotência (RNF-09): nunca reter, liberar ou estornar duas vezes.
Demonstrabilidade: mostrar o ciclo completo em minutos, sem esperar 7 dias.
Evolução: permitir trocar a simulação por um meio de pagamento real no futuro.

## 3. Opções consideradas

| Opção A — Saldo contábil simulado, em tabela própria | Opção B — Gateway em sandbox | Opção C — Conta intermediária fictícia no ledger |
| --- | --- | --- |
| Descrição: o valor retido é um registro no<br>schema escrow do Supabase Core, com<br>estados Retido, Liberado e Estornado, separado<br>do ledger de moedas.<br>Prós:<br>Dentro do PostgreSQL, atômico e auditável<br>Sem dependência externa nem custo<br>Respeita a RB-09<br>Ciclo completo demonstrável<br>Prazo parametrizável<br>Contras:<br>Não comprova integração com pagamento<br>real<br>Exige aviso claro de saldo simulado | Descrição: usar o ambiente de testes de um<br>meio de pagamento para reter e liberar valores.<br>Prós:<br>Mais realista<br>Mostra pagamento e estorno de verdade<br>Contras:<br>Cadastro, chaves e webhooks externos<br>Nem todo sandbox oferece custódia<br>Risco de falha na defesa<br>Pode exigir dados de cobrança, contra o<br>orçamento de R$ 0 | Descrição: uma conta da plataforma, dentro do<br>ledger de moedas, recebe o valor e depois o<br>repassa.<br>Prós:<br>Representa o papel de intermediário<br>Reaproveita o ledger do ADR-10<br>Contras:<br>Mistura reais simulados com moedas virtuais<br>(fere a RB-09)<br>Exige conciliação entre contas<br>Complexidade sem ganho claro |

## 4. Decisão

Opção escolhida: A — Saldo contábil simulado, em tabela própria no schema escrow, com estados Retido, Liberado e Estornado.
Justificativa: é a única opção que cumpre a regra de 7 dias, o bloqueio por reclamação e o estorno sem depender de terceiros, e que mantém o dinheiro
simulado fora do ledger de moedas (RB-09). Reaproveita o que o grupo já definiu: banco do ADR-08, funções SECURITY DEFINER do ADR-09, chaves
naturais do ADR-14 e varredura do ADR-16. A Opção B fica como evolução futura. A Opção C foi descartada por misturar as duas contabilidades.
Modelo de dados (schema escrow, não exposto pela API; acesso só por funções do schema private):
escrow.escrow: escrow_id, transaction_id (UNIQUE), comprador, vendedor, valor_centavos, status (RETIDO, LIBERADO, ESTORNADO),
retido_em, custodia_libera_em, finalizado_em e tipo_final (LIBERACAO_AUTOMATICA, LIBERACAO_ANTECIPADA, ESTORNO).
escrow.escrow_evento: registro append-only de cada mudança de estado, com chave idempotente e Correlation ID.
Máquina de estados de uma só saída: de RETIDO só se vai para LIBERADO ou ESTORNADO, uma única vez, garantida por UNIQUE (escrow_id,
tipo_final).
Funções (private, SECURITY DEFINER, EXECUTE só para o papel de serviço):
reter_escrow(transaction_id): chamada quando o QR Code é validado (STY028); define custodia_libera_em = entregue_em + 168 h.
Quando a leitura do QR Code vem offline (ADR-23), o horário do celular é só informativo para auditoria; entregue_em é a hora em que o servidor
recebe a confirmação (com Idempotency-Key), e é ela que conta os 7 dias (ADR-16).
release_escrow(transaction_id): chamada pela varredura sweep_custodia_7d (ADR-16) ou por laudo validado. Recusa se houver devolução
aberta, laudo em análise ou disputa.
estornar_escrow(transaction_id, decisao_id): exige uma decisão registrada: de moderador com dupla aprovação ou de revelia do vendedor,
que é automática (ADR-06). Sem decisão registrada, a função recusa.
Regras complementares: não há taxa nem comissão da plataforma nesta versão, e valor_centavos registra o valor da oferta em centavos. O prazo
(PRM-29) fica em app_config. O cashback em moedas, creditado em saldo bloqueado (STY028 RN04), é liberado no mesmo evento de liberação do
escrow (modelagem aplicada no ADR-10), por crédito no ledger com (user_id, source_type, source_id) do ADR-14. Todo evento é gravado em
audit.financial_and_dispute_logs (ADR-05). O app e a web exibem o aviso de que o saldo é simulado, e os termos de uso não trazem cláusula de
isenção de indenização (mitigação do R-03).

## 5. Consequências

Positivas:
Regra completa, testável no próprio banco, sem custo nem serviço externo.
Não interfere no ledger de moedas, que continua conforme a RB-09.
Demonstração previsível com o endpoint POST /api/v1/admin/demo/fast-forward-timers do ADR-16, que antecipa os 7 dias e fica registrado na
auditoria.
Negativas ou riscos aceitos:
Não há dinheiro real. O app deve avisar que o saldo é simulado e a defesa deve explicar o limite do escopo.
O R-03 é reduzido na parte de regra, mas riscos de pagamento e fraude reais ficam fora do escopo.
O endpoint de demonstração é um caminho de código a mais e será desligado após a banca; a tarefa de encerramento está registrada nos ADRs 03,
04 e 16.
O que muda:
Banco: schema escrow (2 tabelas) e 3 funções em private.
Código: chamada de reter_escrow na confirmação do QR (inclusive a sincronizada pelo app, com Idempotency-Key).
Diagramas: o gateway sandbox não existe na arquitetura; o diagrama de estados da transação mostra Retido, Liberado e Estornado.
Testes: pgTAP do escrow (ADR-17).

## 6. Validação

| # | Cenário de teste | Resultado esperado |
| --- | --- | --- |
| 1 | Validar o QR Code da entrega | Escrow criado em RETIDO com custodia_libera_em 168 h à frente |
| 2 | Repetir a validação do mesmo QR ou a mesma chamada | Nenhum segundo escrow (UNIQUE transaction_id) |
| 3 | Prazo vencido sem devolução, laudo nem disputa (varredura rodada duas<br>vezes) | Liberado uma única vez e transação concluída |
| 4 | Devolução ou reclamação aberta com o prazo vencido | release_escrow recusa; estado continua RETIDO |
| 5 | Decisão favorável ao comprador: por revelia do vendedor ou por<br>moderadores | Estornado; decisão de moderador com um só aprovador é recusada |
| 6 | Fluxo completo com fast-forward-timers | Do QR à liberação em menos de 10 minutos, com tudo na auditoria |
| 7 | Confirmação de entrega offline com horário do celular adulterado | custodia_libera_em calculado com a hora de recebimento no<br>servidor |
| 8 | Consultar tabelas e funções pelo papel anônimo e autenticado | Acesso negado ao schema escrow (ADR-09) |

## 7. Plano de implementação

| # | Tarefa | Responsável (proposta) | Sprint (proposta) |
| --- | --- | --- | --- |
| 1 | Migração do schema escrow e das tabelas | Fabrício e Augusto | 15 |
| 2 | reter_escrow, release_escrow e estornar_escrow | Augusto | 16 |
| 3 | sweep_custodia_7d, colunas de prazo e modo demonstração | Thiago | 16 |
| 4 | Chamada de retenção na confirmação do QR (web e app offline) | Thiago e Rafael | 16 |
| 5 | Aviso de saldo simulado e estados do escrow nas telas | Pietro | 16 |
| 6 | pgTAP do escrow e teste ponta a ponta | Augusto e Fabrício | 17 |
| 7 | Desligar fast-forward-timers após a banca | Thiago | Após a banca |

## 8. Referências

Matriz GUT (R-03), Matriz de Rastreabilidade (RF-11, RF-13, STY028), Matriz CSD (D3) e regras de negócio (RB-09, PRM-29).
ADR-05 (logs), ADR-08 (banco), ADR-09 (autorização), ADR-10 (ledger de moedas), ADR-14 (idempotência), ADR-16 (tarefas agendadas) e ADR-06
(arbitragem).
Documentação do PostgreSQL: SECURITY DEFINER e restrições UNIQUE. Modelo MADR: adr.github.io/madr.

## Histórico de revisões

| Versão | Data | Autor | Alteração |
| --- | --- | --- | --- |
| 1.0 | 01/11/2026 | Augusto Palma Guglielmi | Versão inicial, em status Proposto |
| 1.1 | 01/11/2026 | Augusto Palma Guglielmi | Alinhamento final do grupo: sem taxa, hora do servidor na entrega offline, cashback no ADR-10 e<br>desligamento do modo demonstração |

# ADR-10 — Ledger de moedas
*Architecture Decision Record · Projeto Steely · Escola de TI · UniCesumar*

| Campo | Valor | Campo | Valor |
| :--- | :--- | :--- | :--- |
| **Status** | ☒ Proposto ☐ Aceito ☐ Rejeitado ☐ Substituído pelo ADR-___ | **Data** | 01/11/2026 |
| **Responsável** | Fabrício Notoya Thomas | **Sprint** | Sprint 8 (15–17) |
| **Participantes** | Fabrício Notoya Thomas, Augusto Palma Guglielmi, Thiago Lopes Martins, Pietro Pasqual Silva, Rafael Tudela Rizental | | |
| **Vínculos** | `RF-14` · `RF-15` · `RF-16` · `RNF-09` · `RB-08` · `RB-09` · `RB-10` · `STY001-RN07` · `STY028-RN04` · `STY037-RN04` · `STY042` · `STY043` · `STY044` · `ADR-03` · `ADR-05` · `ADR-07` · `ADR-08` · `ADR-09` · `ADR-14` · `ADR-15` · `ADR-16` | | |

---

## 1. Contexto *(obrigatória)*
A gamificação e o engajamento comunitário do Steely baseiam-se em uma moeda virtual interna, com paridade de referência de **1 moeda = R$ 0,01** e vedação expressa de saque ou conversão para dinheiro real (`fiat` — `RB-09`, `TAP` seção 7). Os usuários conquistam moedas ao ativar a conta (`STY001-RN07`), usar o Scanner IA (`RF-05`), resolver desafios do Hardware Captcha (`RF-16`), emitir Laudos/Avaliações (`RF-12`, `STY012-RN05`) e comprovar descarte em Ecopontos (`STY058-RN03`).

Em contrapartida, a queima (*burn*) e utilização de moedas ocorrem prioritariamente nos **Leilões Exclusivos** (`RF-15`) e na contratação de **Impulsionamento/Boost** (`RF-07`, `STY018`), além de conceder um **desconto básico limitado em serviços internos** (inspirado no modelo de moedas do AliExpress — `STY043`, `STY044`). Para atender ao `RNF-09` e alinhar o banco de dados com os ADRs `09` (Autorização), `14` (Idempotência), `15` (Concorrência dos lances) e `16` (Tarefas agendadas), é necessário especificar:
1. As colunas exatas de idempotência na tabela do *ledger*;
2. Os lançamentos contábeis de reserva (`BID_HOLD`), liberação (`BID_RELEASE`) e queima (`BID_CAPTURE_BURN`) de moedas nos lances de leilão, bem como a compatibilização com a regra de desistência/não comparecimento do vencedor (`STY037-RN04`);
3. A conciliação entre a expiração de 365 dias por lote (`BPMN P6a`, `STY042-RN03`) e a expiração por 365 dias de inatividade da conta (`RF-14`).

## 2. Direcionadores da decisão *(recomendada)*
* **Consistência Transacional e Prevenção de Gasto Duplo (`RNF-09`, `ADR-14`, `ADR-15`):** Impedir que requisições concorrentes deixem o saldo negativo ou utilizem as mesmas moedas em dois lances simultâneos, alinhando a ordem de locks (`leiloes` $\rightarrow$ `wallets`).
* **Segurança em Profundidade nas Funções Contábeis (`ADR-09`):** Isolar as funções `SECURITY DEFINER` no schema não exposto `private` e validar `KYC` e `Trust Score >= 70%` dentro da própria função SQL.
* **Rastreabilidade de Expiração Conciliada (`RF-14`, `STY042`, `BPMN P6a`):** Consumir primeiro as moedas mais antigas (*First-In, First-Out — `FIFO`*) e unificar a regra de expiração de 365 dias (por lote ou por inatividade).

## 3. Opções consideradas *(obrigatória)*

| Aspecto | Opção A — Saldo Mutável Simples (`UPDATE` em coluna única) | Opção B — Ledger Puro sem Snapshot (Soma calculada em toda leitura) | Opção C — Ledger Imutável (*Append-Only*) + Snapshot de Saldo na Carteira + Consumo FIFO por Lote |
| :--- | :--- | :--- | :--- |
| **Descrição** | Manter apenas uma tabela `wallets` com a coluna `balance` sobrescrita via `UPDATE wallets SET balance = balance + X` a cada evento. | Manter apenas a tabela de lançamentos `wallet_ledger` e calcular `SELECT SUM(amount)` em toda leitura ou lance de leilão. | Combinar uma tabela imutável `wallet_ledger` (histórico contábil *append-only* com colunas de idempotência e controle de lotes `FIFO`) e uma tabela `wallets` (snapshot de `available_balance`, `locked_balance` e `pending_balance`), atualizadas juntas dentro de funções transacionais no schema privado `private` do PostgreSQL com `SELECT ... FOR UPDATE`. |
| **Prós** | • Implementação inicial simples.<br>• Consulta de saldo rápida. | • Histórico 100% preservado sem risco de dessincronização. | • **Auditabilidade total (`RNF-09`, `RNF-11`):** nenhuma linha é apagada; reservas de lance, estornos e expirações geram novos lançamentos.<br>• **Performance máxima em Leilões (`RNF-06`):** leitura de saldo em `O(1)` e trava atômica na linha da carteira.<br>• **Suporte exato a `FIFO` e Idempotência (`ADR-14`).** |
| **Contras** | • **Inviável para os requisitos:** destrói o histórico contábil, impede calcular a expiração individual de 365 dias (`FIFO`) e impossibilita auditar fraudes (`UC-16`). | • Lento conforme o número de lançamentos cresce, prejudicando o SLA de `<= 100 ms` nos lances de leilão (`RNF-06`). | • Exige centralizar toda movimentação de moedas em funções SQL `private.rpc_*` com `SECURITY DEFINER` e `search_path` fixo. |

## 4. Decisão *(obrigatória)*
**Opção escolhida:** ☐ A ☐ B ☒ **C**

Adota-se a arquitetura de **Ledger Imutável (*Append-Only*) combinado com Snapshot de Saldo Transacional e Consumo `FIFO`**, regida pelas seguintes especificações técnicas:

1. **Schema da Carteira, Colunas de Idempotência (`ADR-14`) e Imutabilidade (`ADR-08`):**
   * **Tabela `public.wallets`:**
     * Colunas: `user_id UUID PRIMARY KEY`, `available_balance INT NOT NULL DEFAULT 0 CHECK (available_balance >= 0)`, `locked_balance INT NOT NULL DEFAULT 0 CHECK (locked_balance >= 0)`, `pending_balance INT NOT NULL DEFAULT 0 CHECK (pending_balance >= 0)`, `is_frozen BOOLEAN NOT NULL DEFAULT FALSE`, `last_activity_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`, `updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`.
   * **Tabela `public.wallet_ledger` (Imutável):**
     * Colunas Contábeis: `id UUID PRIMARY KEY`, `user_id UUID NOT NULL REFERENCES public.wallets(user_id)`, `entry_type VARCHAR(40) NOT NULL`, `delta_available INT NOT NULL DEFAULT 0`, `delta_locked INT NOT NULL DEFAULT 0`, `delta_pending INT NOT NULL DEFAULT 0`, `lot_remaining_amount INT` (usado nos lotes de crédito para consumo `FIFO`), `reference_type VARCHAR(40)`, `reference_id UUID`, `expires_at TIMESTAMPTZ`, `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`.
     * **Colunas de Idempotência (`ADR-14`):** `idempotency_key VARCHAR(128) NOT NULL`, `request_hash CHAR(64) NOT NULL` (SHA-256 dos parâmetros da chamada), `response_snapshot JSONB`, com constraint única `CONSTRAINT uq_ledger_idempotency UNIQUE (user_id, entry_type, idempotency_key)`. Se uma requisição repetir a mesma `idempotency_key` com o mesmo `request_hash`, a função retorna o `response_snapshot` sem duplicar o lançamento; se o `request_hash` divergir, lança erro `409/422`.
2. **Fluxo Contábil de Lances no Leilão e Compatibilização com `STY037-RN04` (`ADR-09` e `ADR-15`):**
   * As funções contábeis residem no schema não exposto **`private`** (`private.rpc_place_auction_bid`, `private.rpc_record_ledger_transaction`) e validam internamente no SQL se o usuário possui `status = 'ACTIVE'`, `kyc_verified = TRUE` (`RB-01`) e `trust_score >= 70` (`RB-10`), além de exigirem `ORDER BY` determinístico nos locks: **1º linha do leilão (`SELECT ... FROM public.leiloes WHERE id = p_auction_id FOR UPDATE`) $\rightarrow$ 2º linhas das carteiras envolvidas (`SELECT ... FROM public.wallets WHERE user_id IN (...) ORDER BY user_id FOR UPDATE`)**:
     * **Reserva do Novo Lance (`BID_HOLD`):** Insere `entry_type = 'BID_HOLD'` com `delta_available = -v_bid_amount` e `delta_locked = +v_bid_amount`.
     * **Liberação do Licitante Superado (`BID_RELEASE`):** Na mesma transação atômica, se havia um licitante anterior superado, insere para ele `entry_type = 'BID_RELEASE'` com `delta_available = +v_prev_bid` e `delta_locked = -v_prev_bid`.
     * **Liquidação/Queima no Arremate (`BID_CAPTURE_BURN`) e Regra do 2º Colocado (`STY037-RN04`):** No encerramento do leilão, as moedas já reservadas do vencedor são capturadas e queimadas imediatamente (`BID_CAPTURE_BURN` com `delta_locked = -v_winning_bid`, abatendo os lotes via `FIFO`). Como o pagamento do lance em moedas já está garantido pela reserva, a regra **`STY037-RN04`** aplica-se ao **prazo de 48 horas pós-arremate para o vencedor confirmar o resgate/agendamento da retirada física do hardware**: caso o vencedor abandone o resgate ou desista no prazo de 48h, aplica-se a penalidade (retenção de taxa de desistência em moedas + redução de *Trust Score*), estorna-se o saldo remanescente e oferece-se a compra do lote ao **segundo colocado** pelo valor do seu último lance registrado.
      * **Cashback de Compra em Moedas Bloqueado até o Fim da Garantia (`STY028-RN04`, `ADR-03`, `ADR-14`):** Como o escrow financeiro é mantido separado em centavos no schema `escrow` (`ADR-03` e `RB-09`), o cashback promocional em moedas concedido na entrega via QR Code (`STY028`) entra inicialmente bloqueado em `pending_balance` (`entry_type = 'CASHBACK_HOLD'`, `delta_pending = +v_cashback` durante `private.reter_escrow`). Ao término dos 7 dias de garantia sem disputa ou após laudo validado, a mesma transação de `private.release_escrow` libera o cashback para uso (`entry_type = 'CASHBACK_RELEASE'`, `delta_pending = -v_cashback`, `delta_available = +v_cashback`, abrindo o lote `FIFO` de 365 dias) com chave idempotente natural `(user_id, source_type='ESCROW', source_id=escrow_id)` (`ADR-14`). Caso o escrow seja estornado (`private.estornar_escrow`), o cashback pendente é anulado (`entry_type = 'CASHBACK_CANCEL'`, `delta_pending = -v_cashback`). Na eliminação de conta após 30 dias de carência (`ADR-07`), o pedido exige saldo zerado (`STY010-RN02`) e o `user_id` permanece em `wallet_ledger` como pseudônimo aleatório irreversível.
3. **Política de Utilização (Modelo "Moedas AliExpress") e Tetos:**
   * **Queima Integral (100% em Moedas):** Exclusiva para **Leilões Exclusivos** (`RF-15`) e **Impulsionamento/Boost** (`RF-07`, `STY018`).
   * **Desconto Básico em Serviços Internos (`STY043`, `STY044`):** Abatimento parcial limitado a **até 15% do valor do serviço (ou máximo de 500 moedas = R$ 5,00 por operação)**.
   * **Tetos de Ganho (*Minting Caps*):** Limite de **200 moedas/dia (R$ 2,00)** e **2.000 moedas/mês (R$ 20,00)** por usuário, somado ao *Diminishing Returns* do Hardware Captcha (`RF-16`) e bloqueio se `Trust Score < 70%` (`RB-10`).
4. **Conciliação da Regra de Expiração de 365 Dias (`RF-14` + `BPMN P6a` + `STY042-RN03`):**
   * Unificam-se as duas regras da documentação sob o critério **"o que ocorrer primeiro"**:
     1. **Expiração por Lote (`FIFO` — `BPMN P6a` / `STY042-RN03`):** Cada lote de crédito recebe `expires_at = created_at + INTERVAL '365 days'`. Gastos consomem sempre os lotes com `expires_at` mais próximo. Se sobrar `lot_remaining_amount > 0` após 365 dias da emissão do lote, o saldo remanescente daquele lote expira;
     2. **Expiração por Inatividade da Conta (`RF-14`):** Se `wallets.last_activity_at <= NOW() - INTERVAL '365 days'` (365 dias consecutivos sem login ou movimentação), todos os lotes ativos da carteira expiram.
   * Em ambos os casos, o job diário do `pg_cron` (`ADR-16`) emite alertas preventivos aos **30 dias** e **7 dias** antes da expiração e registra o lançamento `DEBIT_EXPIRATION` na data de vencimento.

## 5. Consequências *(obrigatória)*
* **Positivas:**
  * Fecha 100% do contrato entre `ADR-09`, `ADR-10`, `ADR-14`, `ADR-15` e `ADR-16`, incluindo a compatibilização de `STY037-RN04` com a reserva prévia de moedas.
  * Impede que usuários chamem funções do *ledger* diretamente pelo navegador (funções isoladas no schema `private` + Data API desligada + checagem interna de KYC e Trust Score no SQL).
* **Negativas ou riscos aceitos:**
  * Caso o vencedor desista após o `BID_CAPTURE_BURN` e o item vá ao 2º colocado (`STY037-RN04`), o segundo colocado precisará ter saldo disponível no momento do aceite da oferta de repescagem (já que seu `BID_HOLD` original foi liberado quando ele foi superado no pregão).
* **O que muda no código, no banco, na arquitetura e nos diagramas:**
  * Criação das tabelas `public.wallets` e `public.wallet_ledger` e das funções `private.rpc_record_ledger_transaction` e `private.rpc_place_auction_bid`.

## 6. Validação *(recomendada)*
* **Teste de Reserva, Liberação e Checagem Interna (`pytest` — `ADR-15` / `ADR-17`):** Usuário A dá lance de 100 moedas (`available` cai 100, `locked` sobe 100); Usuário B supera com 110 moedas $\rightarrow$ validar na mesma transação que o `available` do Usuário A voltou a 100 (`locked = 0`) e o do Usuário B teve 110 movidos para `locked`. Tentar chamar `private.rpc_place_auction_bid` com usuário de `trust_score = 60` $\rightarrow$ validar que a própria função SQL rejeita a operação.
* **Teste de Consumo `FIFO` e Idempotência:** Creditar Lote A (100 moedas) e Lote B (100 moedas), gastar 120 moedas e repetir a chamada com a mesma `Idempotency-Key` $\rightarrow$ comprovar que o débito ocorreu uma única vez, zerando o Lote A e deixando 80 moedas no Lote B.

## 7. Plano de implementação *(recomendada)*
1. **Criar migração SQL de `public.wallets`, `public.wallet_ledger` e funções `private.rpc_record_ledger_transaction` / `private.rpc_place_auction_bid`:** Fabrício e Thiago — *Sprint 8*.
2. **Implementar rotas de carteira, extrato e abatimento de serviços no FastAPI:** Fabrício — *Sprint 8/9*.
3. **Configurar job diário no `pg_cron` para alertas (30d/7d) e expiração unificada (lote 365d + inatividade 365d):** Fabrício e Thiago — *Sprint 9*.

## 8. Referências *(recomendada)*
* Documento de Requisitos v2.0 (`RF-14`, `RF-15`, `RF-16`, `RNF-09`).
* Regras de Negócio (`RB-08`, `RB-09`, `RB-10`, `STY001-RN07`, `STY010-RN02`, `STY028-RN04`, `STY037-RN04`, `STY042`, `STY043`, `STY044`, `BPMN P6a`).
* ADRs relacionados: `ADR-03`, `ADR-05`, `ADR-07`, `ADR-08`, `ADR-09`, `ADR-14`, `ADR-15`, `ADR-16`.

---

### Histórico de revisões
| Versão | Data | Autor | Alteração |
| :--- | :--- | :--- | :--- |
| 1.0 | 31/10/2026 | Fabrício Notoya Thomas | Definição do Ledger Imutável com Snapshot, regra FIFO, paridade R$ 0,01 e tetos. |
| 1.1 | 31/10/2026 | Fabrício Notoya Thomas | Especificação das colunas de idempotência (`ADR-14`), lançamentos de reserva/liberação de lance (`BID_HOLD`/`BID_RELEASE`/`BID_CAPTURE_BURN` para `ADR-15`) e unificação da regra de expiração de 365 dias (lote FIFO + inatividade). |
| 1.2 | 31/10/2026 | Fabrício Notoya Thomas | Isolamento das funções `SECURITY DEFINER` no schema não exposto `private` com revalidação SQL de KYC/Trust Score (`ADR-09`) e compatibilização do `STY037-RN04` (prazo de confirmação de retirada pós-arremate e repescagem do 2º colocado). |
| 1.3 | 01/11/2026 | Fabrício Notoya Thomas | Alinhamento com `ADR-03` e `ADR-07`: fluxo de cashback bloqueado (`CASHBACK_HOLD`/`CASHBACK_RELEASE`/`CASHBACK_CANCEL` em `pending_balance` — `STY028-RN04`) integrado ao escrow e preservação por pseudônimo irreversível na exclusão de conta. |

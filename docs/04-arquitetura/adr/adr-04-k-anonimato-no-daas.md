# ADR-04 — k-anonimato no DaaS (k ≥ 30)
**Architecture Decision Record · Projeto Steely · Escola de TI · UniCesumar**

| Campo | Valor | Campo | Valor |
| --- | --- | --- | --- |
| **Status** | ☒ Proposto ☐ Aceito ☐ Rejeitado ☐ Substituído pelo ADR-___ | **Data** | 01/11/2026 |
| **Responsável** | Augusto Palma Guglielmi | **Sprint** | Entrega até 23/11 (Sprints 15 a 17) |
| **Participantes** | Augusto Palma Guglielmi, Fabrício Notoya Thomas, Pietro Pasqual Silva, Rafael Tudela Rizental, Thiago Lopes Martins | | |
| **Vínculos** | RNF-03 · R-10 (Matriz GUT) · RF-21 e RF-04 · STY053 e STY055 · PRM-61 e PRM-64 · LGPD art. 12 · ADR-05, ADR-08, ADR-16 e ADR-22 | | |

## 1. Contexto

O DaaS (Data as a Service) vende relatórios de inteligência de mercado sobre hardware reutilizado. A LGPD (art. 12) só considera anonimizado o dado
que não permite reidentificar a pessoa por meios razoáveis. Por isso o RNF-03 exige amostra mínima de k ≥ 30 registros por modelo, e a regra STY053-
RN01 proíbe gerar ou exportar qualquer indicador com menos de 30 registros válidos. A STY053-RN02 exige base segregada e remoção de
identificadores indiretos.
O risco R-10 (pontuação 45) lembra o outro lado: com pouco volume, o limiar trava o DaaS. A STY053-RN01 resolve apurando no nível de agregação
imediatamente superior.
Já definido pelo grupo: o ADR-08 prevê dois projetos Supabase gratuitos, sendo o Projeto 2 uma base DaaS fisicamente separada; o pg_cron aciona,
via pg_net, o endpoint POST /api/v1/internal/jobs/sync-daas no FastAPI, que agrega no Core com HAVING COUNT(DISTINCT transacao_id) >=
30, remove identificadores e grava no Projeto 2 por asyncpg (ADR-08 e ADR-16). O ADR-22 aplica o mesmo k ≥ 30 por região no painel ESG. Falta
formalizar o limiar, a segregação e o que a demonstração mostra quando não há volume.

## 2. Direcionadores da decisão

Privacidade (LGPD e RNF-03): nenhum dado reidentificável sai do Core.
Segregação física: falha ou vazamento do Core não expõe o DaaS, e o contrário também.
Custo zero: usar o segundo projeto gratuito já previsto.
Esforço até 23/11: reaproveitar o job e o endpoint já definidos no ADR-16.
Demonstrabilidade: mostrar o bloqueio abaixo de 30 e a liberação acima, mesmo com pouco volume real.
Utilidade do produto (R-10): o relatório precisa existir quando o modelo tem pouco volume.

## 3. Opções consideradas

| Opção A — Projeto Supabase separado, alimentado por job | Opção B — Schema daas no mesmo projeto | Opção C — Filtro k só na consulta da API |
| --- | --- | --- |
| Descrição: segundo banco PostgreSQL<br>independente, que só recebe pacotes agregados<br>e anonimizados enviados pelo FastAPI.<br>Prós:<br>Segregação física real<br>O Core nunca é lido pelo cliente do DaaS<br>Usa o plano gratuito<br>Já previsto nos ADRs 08 e 16<br>Contras:<br>Mais um banco para manter e manter ativo<br>Dados defasados até o próximo job<br>Dois pontos de configuração<br>(DATABASE_URL_CORE e _DAAS) | Descrição: views e políticas RLS no Core, com<br>um papel só de leitura para relatórios.<br>Prós:<br>Sem segundo projeto<br>Dados sempre atualizados<br>Contras:<br>Segregação apenas lógica (STY053-RN02<br>pede base segregada)<br>Erro de política expõe dados brutos<br>Consulta analítica compete com o<br>transacional | Descrição: a API consulta o Core e bloqueia<br>recortes com menos de 30 registros no momento<br>do relatório.<br>Prós:<br>Mais simples<br>Sem job de sincronização<br>Contras:<br>Dados brutos acessíveis ao módulo do DaaS<br>Proteção depende de código, não da<br>estrutura<br>Não atende à segregação |

## 4. Decisão

Opção escolhida: A — Projeto Supabase separado para o DaaS, com k ≥ 30 aplicado na agregação e novamente na consulta.
Justificativa: é a única opção que atende à base fisicamente segregada (STY053-RN02) a custo zero. O k é garantido na estrutura (o dado de recorte
pequeno nunca chega ao Projeto 2) e conferido de novo na consulta, em duas camadas independentes. As Opções B e C foram descartadas por
segregação apenas lógica.
Regras da decisão:
Limiar: k = 30 registros válidos (PRM-61), contados como COUNT(DISTINCT transacao_id) por recorte. O valor fica em app_config, e a
demonstração não o reduz.
Mínimo de vendedores: além das 30 transações, o recorte precisa de COUNT(DISTINCT vendedor_id) >= 3 (parâmetro em app_config), para que
30 vendas de um único vendedor não o identifiquem.
Parâmetro compartilhado: o k ≥ 30 do painel ESG (ADR-22) usa o mesmo valor de app_config, mantendo as bases separadas (esg.* no Core e
Projeto 2 no DaaS).
Massa sintética: aceita no Projeto 2 apenas durante a defesa, rotulada "DEMONSTRAÇÃO" em todos os relatórios, e removida após a banca (tarefa
de encerramento nos ADRs 03, 04 e 16).
Unidade do recorte: modelo, região e mês. O que for abaixo do limiar não é gravado no Projeto 2.
Escalonamento (R-10 e STY053-RN01): se o modelo não alcança 30, o job tenta o nível acima: modelo → família → fabricante → categoria. Cada
indicador informa o nível em que foi apurado.
Pacote enviado ao Projeto 2: apenas agregados (contagem, média, mediana e faixa de preço, taxa de falha), mês, região ampla e nível. Ficam de
fora usuário, vendedor, comprador, endereço, data exata, número de série e texto livre.
Sincronização: job diário (sync-daas, ADR-16) com UPSERT idempotente por chave natural do recorte.
Acesso: só o FastAPI conhece DATABASE_URL_DAAS. O painel e os relatórios leem o Projeto 2 por papel somente leitura, e o cliente web e o app não
acessam o Core para o DaaS.
Exportação: até 10.000 linhas de forma síncrona e acima disso assíncrona (PRM-64). Cada geração e exportação gera log em
audit.system_and_access_logs (ADR-05).
Sem volume: a resposta traz o aviso "volume insuficiente para o recorte" com o nível superior sugerido, e nenhum número do recorte é exibido.

## 5. Consequências

Positivas:
Privacidade garantida pela estrutura, com duas camadas de verificação do k.
Custo zero e nenhum serviço novo, usando o job e o endpoint do ADR-16.
Demonstração clara do bloqueio, do escalonamento e da liberação.
Negativas ou riscos aceitos:
Segundo banco para manter ativo: o /health do ADR-08 já o consulta para evitar a pausa de 7 dias.
Dados do DaaS ficam até 1 dia defasados.
No início o volume real será baixo, e muitos recortes ficarão agregados no nível superior ou bloqueados (R-10).
A massa sintética precisa estar sempre rotulada para não ser confundida com dado real e deve ser removida após a banca.
O que muda:
Banco: projeto 2 com tabelas de indicadores e papel somente leitura; função de agregação no Core.
Código: consulta do relatório com segunda verificação de k; tratamento do aviso de volume insuficiente.
Diagramas: o Projeto 2 aparece separado, ligado só ao FastAPI.

## 6. Validação

| # | Cenário de teste | Resultado esperado |
| --- | --- | --- |
| 1 | Recorte com 29 registros | Bloqueado, sem número exibido; sugere o nível superior |
| 2 | Recorte com 30 registros | Indicador liberado, com o nível informado |
| 3 | Recorte com 30 transações de apenas 2 vendedores | Bloqueado pelo mínimo de 3 vendedores |
| 4 | Modelo abaixo do limiar, família acima | Indicador apurado no nível família |
| 5 | Inspecionar as tabelas do Projeto 2 | Nenhuma coluna de usuário, endereço, série ou data exata |
| 6 | Rodar sync-daas duas vezes | Sem duplicação (UPSERT idempotente) |
| 7 | Tentar ler o Core com o papel do DaaS | Acesso negado |
| 8 | Exportar 10.001 linhas | Processamento assíncrono e registro em log |

## 7. Plano de implementação

| # | Tarefa | Responsável (proposta) | Sprint (proposta) |
| --- | --- | --- | --- |
| 1 | Criar o Projeto 2 e as tabelas de indicadores | Fabrício | 16 |
| 2 | Função de agregação com k e escalonamento de nível | Augusto | 16 |
| 3 | Endpoint sync-daas e agendamento no pg_cron | Thiago | 16 |
| 4 | Tela e mensagem de volume insuficiente nos relatórios | Pietro | 17 |
| 5 | pgTAP do limiar e teste de varredura de identificadores | Augusto e Fabrício | 17 |

## 8. Referências

Regras de negócio STY053 (RN01, RN02) e PRM-61 e PRM-64; Matriz GUT (R-10); RNF-03.
ADR-08 (projetos Supabase), ADR-16 (job sync-daas), ADR-22 (k ≥ 30 no ESG) e ADR-05 (logs).
LGPD, art. 12 (dado anonimizado). Modelo MADR: adr.github.io/madr.

## Histórico de revisões

| Versão | Data | Autor | Alteração |
| --- | --- | --- | --- |
| 1.0 | 01/11/2026 | Augusto Palma Guglielmi | Versão inicial, em status Proposto |
| 1.1 | 01/11/2026 | Augusto Palma Guglielmi | Alinhamento final do grupo: mínimo de 3 vendedores por recorte, massa sintética só na defesa e<br>parâmetro k compartilhado com o ADR-22 |

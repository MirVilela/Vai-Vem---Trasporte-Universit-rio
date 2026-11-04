# Plano de Correção e Teste — para Agentes

**Origem:** verificação funcional de 04/11/2026. **Objetivo:** todos os itens desbloqueados corrigidos e os três comandos da Seção 2 sem falhas nesses itens.

**Antes de alterar qualquer arquivo:**
1. Leia `CLAUDE.md`, `SCHEMA.md` e este plano.
2. Crie o VCC da sessão em `docs/vibes/`, a partir de `VCC_TEMPLATE.md`.
3. Confira na Seção 3 se o item depende de uma decisão humana. **Se depender e a decisão estiver em aberto, não implemente nem presuma a resposta: pergunte.**

---

## 1. Regras desta execução

- **Um item por vez.** Mudanças cirúrgicas; sem refatorar o que não está no item.
- **Sem dependências novas nem frameworks.** Flask, SQLite e JS Vanilla (`CLAUDE.md`).
- **`SCHEMA.md` é a lei.** Se o JSON ou uma tabela mudar, atualize o `SCHEMA.md` na mesma tarefa. O S13 já autoriza as mudanças descritas nele.
- **Nunca teste contra o `database.db` real.** `tests/` e `tests/e2e/` usam cópias temporárias. `stress_test.py` e `stress_test_embarque.py` chamam o servidor real da porta 5000 e já poluíram o banco uma vez (S16): só rode-os com o servidor apontando para uma cópia.
- **Não apague dados, não faça commit nem push** sem pedido explícito do responsável.
- **Não relate "corrigido" sem a evidência** do critério de aceite. Uma rota responder 200 não prova que a tela funciona.

**O que não existe no repositório**, apesar de citado no `CLAUDE.md` ou no `README.md`: `mcp_server.py`, `FINDINGS.md` na raiz (o arquivo é `05-FINDINGS.md`) e conteúdo em `rag/memoria/` e `agente/plugins/`. O acesso ao banco é pelo `sqlite3` do Python. A skill disponível está em `.agent/skills/engenharia/SKILL.md`.

---

## 2. Como testar

Execute na raiz do projeto:

| Comando | O que cobre | Requisito |
| :--- | :--- | :--- |
| `python -m unittest discover tests` | Regras isoladas (padrão AAA) | Python + Flask |
| `python tests/e2e/verifica_api.py` | Fluxos completos pela API | Python + Flask |
| `node tests/e2e/verifica_telas.mjs` | Uso real das telas em Chrome headless, largura de celular, modo avião e servidor fora | Node 22+ e Chrome/Edge (`CHROME_PATH` se estiver em outro caminho) |

Cada caso imprime `OK`, `FALHA` ou `PULOU`, com o item entre colchetes. `[BASE]` é o que já funciona e **não pode regredir**. O último comando também imprime a pasta das capturas de tela: abra-as ao mexer em uma tela. Os testes funcionam sem `database.db` (clone novo): nesse caso usam um banco temporário com os dados de teste.

**O banco é de protótipo, sem dados reais, e fica fora do git.** O `python app.py` o recria com os dados básicos: 3 alunos (João `1234`, Maria `5678`, Carlos `0000`), 4 veículos e 2 rotas.

### Resultado de referência (04/11/2026, 14h50, quarta-feira, banco recém-criado)

| Comando | Resultado | Itens com falha |
| :--- | :--- | :--- |
| `unittest` | 42 testes OK | — |
| `verifica_api.py` | 11 falhas | S09 (3), S12 (2), S13 (3), S14 (2), S14-D3 (1) |
| `verifica_telas.mjs` | 6 falhas | S10 (1), S11 (2), S12 (1), S15 (1), S18 (1) |

**Casos dependentes do calendário:**
- O cenário de reservar e desmarcar pela tela é `PULOU` se a semana tiver menos de 2 dias liberados (ex.: sexta após o corte). Repita em outro dia antes de encerrar o S12.
- O caso S18 ajusta o corte conforme a hora atual e é `PULOU` em fins de semana.

**Falha esperada ao final se as decisões continuarem em aberto:** `S14-D3`. O S08 ainda não tem caso automatizado.

---

## 3. Decisões humanas pendentes

| ID | Pergunta | Bloqueia | Enquanto não houver resposta |
| :--- | :--- | :--- | :--- |
| **D1** | Como blindar as vagas de exceção com vários veículos? Reservar em cada veículo ou vincular a exceção a um veículo? (detalhes no S08 do backlog) | S08 | Não implementar. O responsável adiou a decisão em 28/10. |
| **D3** | Quem não reservou pode embarcar? | Só a regra "sem reserva" do S14 | Implementar o resto do S14 e deixar esse caso como está. |

---

## 4. Ordem de execução

| # | Item | Persona | Prioridade | Situação |
| :--- | :--- | :--- | :--- | :--- |
| 1 | S11 Rastreamento na tela do motorista | José | Essencial | Livre |
| 2 | S12 Desmarcar dia cancela a reserva | José + Ana | Essencial | Livre |
| 3 | S18 Calendário obedece ao corte e à recusa do servidor | José | Essencial | Fazer depois do S12 (mesmo trecho) |
| 4 | S13 Login obrigatório para reservar e consultar | Ana + José; Maria revisa | Essencial | Livre; mude o contrato com cuidado |
| 5 | S09 Validar dados de `/api/reservar` | Ana | Importante | Livre |
| 6 | S14 Validar check-in | Ana | Importante | Parte aguarda D3 |
| 7 | S15 Horários em Brasília | Ana | Importante | Livre |
| 8 | S10 Viagem iniciada sem conexão | José | Importante | Livre |
| 9 | S08 Blindar vagas de exceção | Ana + José | Essencial | **Aguarda D1** |
| 10 | S19 Senha da gestora e modo debug | Ana | Essencial antes do piloto | Livre, mas alinhe com o responsável |
| 11 | S17 Leitura do painel | José | Desejável | Livre |

S16 (limpar dados de teste) foi concluído em 04/11/2026 com autorização do responsável.

**Tiago (QA) fecha cada item:** roda os três comandos, compara com a referência e confirma que nenhum `[BASE]` regrediu.

---

## 5. Tarefas

Localize o código pelo nome da função; os números de linha mudam.

### S11 — Rastreamento na tela do motorista
- **Sintoma:** o seletor de rota mostra `undefined` e nenhum botão de ponto aparece.
- **Causa:** `carregarRotasDisponiveis` e `renderizarTrackingControls`, em `static/motorista.html`, leem `p.rota`. A API e o `SCHEMA.md` definem `rota_id` e `rota_nome`.
- **Correção:** deduplicar por `rota_id`; usar `rota_id` como valor e `rota_nome` como texto; filtrar os pontos por `p.rota_id`. Não altere a API.
- **Atenção:** os botões nunca foram exercitados por este caminho. Teste também a troca de ponto marcado em `atualizarStatusViagem`, inclusive o texto do botão anterior.
- **Aceite:** casos S11 em OK; pela captura, nomes de rota legíveis e o ponto marcado em destaque.

### S12 — Desmarcar dia cancela a reserva
- **Sintoma:** o aluno desmarca, a tela confirma, mas a reserva segue ativa no painel, na frota sugerida e na lista do motorista.
- **Causa:** `btnConfirmar` em `static/index.html` filtra os dias sem ida e sem volta e exige ao menos um dia marcado; `api_reservar` ignora `ida=0, volta=0`.
- **Correção:**
  - Tela: enviar também os dias zerados que **não** estão encerrados. Permitir confirmar com tudo desmarcado quando havia reserva, e adaptar a tela de sucesso ("reservas canceladas").
  - API: aplicar `is_hard_locked` **antes** de tratar o zero. Com `ida=0, volta=0`, fazer `UPDATE ... SET status='CANCELADA'` na reserva existente, sem criar linha nova. `CANCELADA` já existe no `SCHEMA.md`.
  - Reservar de novo o mesmo dia deve voltar a `ATIVA` (o `ON CONFLICT` já faz isso).
- **Aceite:** casos S12 em OK; novo teste AAA para cancelar, cancelar dia encerrado (não muda) e reativar.

### S18 — Calendário obedece ao corte e à recusa do servidor
- **Sintoma:** `renderDays` em `static/index.html` trava com `serverHora >= 14` fixo, ignorando `horario_corte` e `trava_manual`. Além disso, `showSuccess` aparece mesmo se o servidor recusar: `api_reservar` responde `sucesso: true` com `total_registradas` menor, em silêncio.
- **Correção:** ler `horario_corte` e `trava_manual` de `GET /api/status-inscricoes` (já público) e replicar a regra de `is_hard_locked`, inclusive minutos. Comparar `total_registradas` com o enviado e avisar quais dias não foram aceitos. O servidor continua sendo a autoridade.
- **Aceite:** caso S18 em OK; dia recusado não aparece como reservado. O caso cobre o corte; confira `trava_manual` e a recusa em teste manual e registre a evidência no VCC.

### S13 — Login obrigatório para reservar e consultar
- **Sintoma:** `POST /api/reservar` e `GET /api/semana` aceitam qualquer CPF sem PIN. Problema de LGPD.
- **Contrato a implementar** (os testes já o reconhecem):
  - `POST /api/login` passa a devolver também `"token"`.
  - Rotas do aluno exigem `Authorization: Bearer <token>`: sem token ou inválido → **401**.
  - CPF de outro aluno em relação ao token → **401 ou 403**. O servidor usa o CPF do token, não o enviado.
- **Implementação:** `itsdangerous.URLSafeTimedSerializer` (já instalado como dependência do Flask), com expiração e chave em variável de ambiente. Sem tabela de sessão.
- **Frente:** guardar o token em `currentUser`; enviá-lo em `/api/reservar`, `/api/semana` e `syncPendingReservas`. Hoje `syncPendingReservas` descarta a reserva da fila em qualquer resposta: com 401, mantenha-a e peça novo login. Trate 401 nas demais chamadas com mensagem clara.
- **Não mexa:** `/api/avisos` e `/api/status-viagem/<data>` continuam públicos.
- **Testes:** atualizar `TestReserva` em `tests/test_hard_lock.py`, que hoje chama sem token. Atualizar `SCHEMA.md` e `GUIA_DO_USUARIO.md`.
- **Aceite:** casos S13 em OK e nenhum `[BASE]` regredido. Maria registra a revisão no `05-FINDINGS.md`.

### S09 — Validar dados de `/api/reservar`
- **Causa:** `int(r.get(...))` e `r.get` sem validação (erro 500); `is_hard_locked` devolve `False` em data inválida, então ela é gravada.
- **Correção:** `reservas` não-lista ou item não-objeto → 400. Item com data não ISO, ou `ida`/`volta` fora de 0 e 1 → ignorar, sem gravar. Não altere o `except` de `is_hard_locked` sem conferir `tests/test_hard_lock.py`.
- **Aceite:** casos S09 em OK e teste AAA novo.

### S14 — Validar check-in
- **Causa:** `api_checkin` não valida tipo nem reserva, e o ID composto inclui o veículo.
- **Correção livre:** tipo fora de IDA/VOLTA → 400. Aluno já embarcado no mesmo dia e trecho em qualquer veículo → 409.
- **Depende de D3:** aluno sem reserva ativa naquele trecho → rejeitar só se a resposta for "não pode embarcar". O caso `[S14-D3]` assume essa resposta: se for "pode", inverta o caso.
- **Atenção:** `sincronizarFila` tira da fila itens com 409 sem avisar o motorista. Se o check-in offline for recusado, ele precisa saber: mostre o motivo.
- **Aceite:** casos S14 em OK e testes em `tests/test_checkin.py`.

### S15 — Horários em Brasília
- **Sintoma:** aviso das 14:22 aparece como 17:22.
- **Causa:** `criado_em` e `confirmado_em` usam `datetime('now')` (UTC), e o navegador os lê como hora local. `api_avisos_listar` e `api_avisos_criar` comparam `expira_em` com `date('now')`: à noite, em UTC já é o dia seguinte, e o aviso expira cerca de 3h antes.
- **Correção:** gravar com `get_server_now()`, como `status_viagem`, e usar `get_server_now().date()` nas comparações. Inclua `confirmado_em` (vai para o relatório CSV). O banco real tem 0 avisos, mas confira os check-ins existentes antes de converter qualquer dado.
- **Aceite:** caso S15 em OK.

### S10 — Viagem iniciada sem conexão (RNF02)
- **Sintoma:** com o app aberto já sem rede, veículos e passageiros não carregam; `carregarVeiculos` também gera exceção não tratada.
- **Correção:** ao carregar, salvar veículos, pontos de rota e lista por `data` + `tipo` no `localStorage`; em falha, usar a cópia e indicar a hora da lista. Sem bibliotecas.
- **Aceite:** caso S10 em OK; lista "Excecoes de JavaScript" vazia; teste manual iniciando a viagem com o servidor fora.

### S08 — Blindar vagas de exceção (**aguarda D1**)
Ver backlog. Ao implementar, corrigir também a contagem que ignora o trecho, aplicar a regra em `contarConfirmados` (modo offline) e criar caso em `verifica_api.py`.

### S19 — Senha da gestora e modo debug
- **Situação:** `ADMIN_TOKEN = "vem-admin-2026"` está no `app.py`, no guia e nos testes; `app.run(debug=True)` expõe o depurador.
- **Correção:** token por variável de ambiente, sem valor de produção no código, e debug desligado por padrão. Combine com o responsável: os testes e o guia dependem do valor atual.

### S17 — Leitura do painel
Ver backlog. Mudança só em `static/gestora.html`, sem alterar o JSON.

---

## 6. Definição de pronto de cada item

- [ ] Critério de aceite atendido, com a evidência citada no VCC.
- [ ] Teste AAA novo em `tests/` para regra de backend alterada.
- [ ] Três comandos da Seção 2 executados; nenhum `[BASE]` regrediu.
- [ ] `05-FINDINGS.md`: coluna "Correção" do item preenchida.
- [ ] `docs/sugestoes/README.md`: status atualizado.
- [ ] `GUIA_DO_USUARIO.md` e `SCHEMA.md` atualizados, se aplicável.
- [ ] `docs/RESUMO_EXECUTIVO.md`: status corrigido quando o item afetar um requisito. **O rastreamento consta como pronto, e não está** até o S11.
- [ ] Esta tabela de referência atualizada ao fim da sessão, para o próximo agente.

---

## 7. Prompt para iniciar uma sessão

> Leia `docs/PLANO_CORRECAO_AGENTES.md`, `CLAUDE.md` e `SCHEMA.md`. Rode os três comandos da Seção 2 e compare com a referência. Execute o próximo item livre da Seção 4, assumindo a persona indicada. Crie o VCC antes de alterar arquivos. Não presuma decisões da Seção 3. Conclua cada item com a Definição de pronto e relate o resultado com a saída dos testes. Não faça commit nem push sem pedido.

# 📋 Backlog de Sugestões (S01–S19)

> S18 e S19, e as instruções de execução de S08 a S19, estão em `docs/PLANO_CORRECAO_AGENTES.md`.

> Origem: análise comparativa com o TCC do IFPI e revisão do código em 2026-10-28. Cada item respeita os limites do `01-NORTH_STAR.md` (sem frameworks pesados, sem OAuth, offline-first).

---

## S01 — Hash do PIN com salt (Segurança / LGPD)

- **Persona:** Maria (auditoria) → Ana (implementação)
- **Prioridade:** Essencial
- **Problema:** `hash_pin` em `app.py` usa SHA-256 **sem salt**. Como só existem 10.000 PINs de 4 dígitos, quem obtiver o `database.db` reverte todos os PINs em milissegundos (tabela pré-calculada).
- **Proposta:** `hashlib.pbkdf2_hmac("sha256", pin, salt, 200_000)` com salt aleatório por aluno (`os.urandom(16)`), armazenado como `salt$hash`. Biblioteca padrão — não fere o Anti-Bloat.
- **Atenção:** exige migração dos PINs existentes (re-hash no próximo login válido) e verificação no `SCHEMA.md` (campo `pin` continua TEXT).
- **Complemento:** limitar tentativas de login por CPF (ex.: 5 erros → bloqueio de 5 min), pois o espaço de PINs é pequeno.
- **Critério de aceite:** PINs no banco não se repetem para PINs iguais; login antigo continua funcionando; teste AAA cobrindo hash e verificação.
- **✅ Implementado (2026-10-28):** `hash_pin` / `verificar_pin` / `pin_legado` em `app.py`, 200.000 iterações (~70 ms). Migração transparente no login. Bloqueio de 5 min após 5 erros por CPF (HTTP 429). Testes em `tests/test_login.py`.
- **Limites que continuam valendo:**
  - Com apenas 10.000 PINs possíveis, quem roubar o `database.db` ainda consegue descobrir o PIN de **um** aluno por força bruta (~12 min por aluno em um núcleo). O salt impede atacar todos de uma vez; a proteção principal continua sendo não expor o arquivo do banco.
  - O bloqueio é por CPF e fica em memória: zera se o servidor reiniciar e não impede testar **um mesmo PIN em muitos CPFs**. Evolução possível: limite também por IP.
  - Alunos que nunca mais logarem continuam com o hash antigo no banco.

## S02 — Ampliar a suíte de testes AAA

- **Persona:** Tiago (QA)
- **Prioridade:** Essencial
- **Situação:** `tests/test_sugerir_frota.py` criado (9 testes). O resto das regras críticas não tem teste.
- **Proposta (por ordem de risco):**
  1. `is_hard_locked` — antes/depois do corte, trava manual, fuso horário (RS03).
  2. Check-in — trava ao atingir capacidade, descontando exceções (RS04/RS05/RN02).
  3. Login — CPF inválido, PIN errado (RF01).
  4. Reserva — uma reserva ativa por aluno/dia.
- **Critério de aceite:** `python -m unittest discover tests` verde; testes usam banco temporário (não o `database.db` real).
- **✅ Implementado (2026-10-28):** 37 testes AAA — `test_sugerir_frota.py` (9), `test_login.py` (12), `test_hard_lock.py` (11: hard lock + reserva), `test_checkin.py` (5). Apoio com banco temporário em `tests/apoio.py`. O desconto de exceções no check-in **não** foi testado porque não está implementado (ver S08).

## S03 — Avaliação de usabilidade com usuários

- **Persona:** Maria / José
- **Prioridade:** Importante
- **Proposta:** aplicar o **SUS completo** (10 itens, com escore) — o TCC do IFPI não aplicou — mais os itens de utilidade do TCC (I5–I7) para permitir comparação. Buscar equilíbrio entre perfis (alunos, gestora, motorista), falha apontada no TCC (14/4/1).
- **Critério de aceite:** escore SUS calculado por perfil; achados registrados no `05-FINDINGS.md`.

## S04 — Ajustes de UX vindos do feedback do TCC

- **Persona:** José (Frontend)
- **Prioridade:** Importante
- **Proposta:**
  - Mensagens de erro que digam **causa e correção** (ex.: "Reservas de hoje encerradas às 14h. Escolha outro dia.").
  - Atalho visível para a tela inicial em todas as telas.
  - Nomear pontos como **"Ponto de embarque"** / **"Ponto de desembarque"** (não "parada").
  - Revisar telas da gestora com muitos campos.
- **Critério de aceite:** nenhuma mensagem genérica de erro restante nos três HTMLs; touch targets ≥ 48px mantidos (RNF03).

## S05 — Quadro comparativo de trabalhos relacionados

- **Persona:** Maria
- **Prioridade:** Importante
- **Proposta:** incorporar ao material acadêmico do projeto um quadro no formato do "Quadro 6" do TCC do IFPI, usando o [01-ESTADO_DA_ARTE.md](01-ESTADO_DA_ARTE.md) como base. Critérios sugeridos: domínio, otimização de frota, embarque justo, offline, avaliação com usuários, testes.

## S06 — Taxa de ocupação prevista no painel

- **Persona:** José / Ana
- **Prioridade:** Desejável
- **Inspiração:** alerta de "viagem com risco de cancelamento" do TCC.
- **Proposta:** exibir no painel da gestora `ocupação = passageiros ÷ assentos sugeridos` por dia/trecho, destacando dias com ociosidade alta. Valor derivado no frontend a partir de `total_ida`/`sugestao_frota` — **sem alterar o JSON do `SCHEMA.md`**.

## S07 — Refinamentos da sugestão de frota

- **Persona:** Ana
- **Prioridade:** Desejável
- **Contexto:** a correção de 2026-10-28 (S00) tornou o cálculo ótimo e limitado aos veículos ativos. Ficaram decisões em aberto:
  1. **Demanda acima da frota:** hoje o cálculo ignora o limite de unidades e sugere o que seria preciso contratar, mas o painel não sinaliza isso. Proposta: aviso visual quando a sugestão exceder a frota cadastrada.
  2. **Capacidades diferentes no mesmo tipo:** o cálculo usa a maior capacidade de cada tipo. Se houver, por exemplo, uma van de 15 e outra de 12, o resultado pode superestimar assentos.
  3. **Custo operacional:** o critério atual é menos assentos vazios e, no empate, menos veículos. Se a gestora preferir minimizar motoristas/combustível, o critério de desempate deve ser revisto com ela.

## S08 — Blindar vagas de exceção no check-in (RN02 / RS05)

- **Persona:** Ana (backend) / José (motorista.html)
- **Prioridade:** Essencial — é regra de negócio do DERS que hoje **não é cumprida**.
- **Problema (encontrado em 2026-10-28):**
  - `api_checkin` em `app.py` conta as exceções do dia (`excecoes`), mas **não usa o valor**: as vagas restantes são só `capacidade - checkins`. Um aluno comum pode ocupar o assento de um aluno de rota distante.
  - A contagem de exceções também não filtra o trecho (IDA/VOLTA).
  - O modo offline de `motorista.html` (trava local de lotação) igualmente ignora as exceções.
- **Opções levantadas:**
  1. **Reservar em cada veículo:** aluno comum só embarca se `embarcados + exceções do trecho ainda não embarcadas < capacidade`; exceção sempre embarca até a capacidade. Exato com 1 veículo por trecho; conservador com vários.
  2. **Vincular exceção a um veículo:** exato com vários veículos, mas exige campo novo no banco, atualização do `SCHEMA.md` e da tela da gestora.
- **Status:** decisão adiada pelo responsável em 2026-10-28 ("só documentar por agora").
- **Critério de aceite (quando decidido):** teste AAA em `tests/test_checkin.py` em que um aluno comum é rejeitado quando os assentos restantes estão reservados para exceções; mesma regra aplicada no modo offline do motorista.

## S09 — Validar formato de data em `/api/reservar`

- **Persona:** Ana
- **Prioridade:** Importante
- **Problema:** `is_hard_locked` retorna `False` quando a data não é ISO válida (`ValueError`), então `/api/reservar` grava reservas com datas como `"abc"`, que poluem o painel da gestora.
- **Proposta:** em `api_reservar`, ignorar (ou rejeitar com 400) itens cuja data não passe em `date.fromisoformat`.
- **Critério de aceite:** teste AAA mostrando que data inválida não é gravada.

## S10 — Motorista iniciar viagem já sem conexão (RNF02 completo)

- **Persona:** José (motorista.html)
- **Prioridade:** Importante
- **Situação (2026-10-28):** depois da correção do PWA, a página do motorista abre sem conexão e os check-ins feitos offline são guardados e sincronizados. Mas, se o app for aberto **já sem rede**, a lista de veículos (`carregarVeiculos`) e a de passageiros (`carregarChecklist`) não carregam, porque nada fica salvo no aparelho. O motorista não consegue iniciar a viagem.
- **Proposta:** ao carregar com sucesso, salvar no `localStorage` os veículos e a lista de passageiros por `data`+`tipo`; em falha de rede, usar a cópia salva e indicar "lista de HH:MM".
- **Critério de aceite:** com o servidor desligado e o app recém-aberto, o motorista consegue selecionar o veículo, ver a lista salva e fazer check-ins que sincronizam depois.

---

> S11–S17 vêm da verificação funcional de 2026-11-04. Causas em `05-FINDINGS.md`.

## S11 — Corrigir rastreamento na tela do motorista (RF07)

- **Prioridade:** Essencial
- **Proposta:** em `motorista.html`, usar `rota_id` (valor) e `rota_nome` (texto) do JSON da API.
- **Critério de aceite:** o seletor lista as rotas pelo nome, os botões de ponto aparecem e o toque atualiza a tela do aluno.

## S12 — Desmarcar dia deve cancelar a reserva

- **Prioridade:** Essencial — a tela confirma um cancelamento que não aconteceu e a demanda fantasma infla a frota sugerida.
- **Proposta:** enviar também os dias desmarcados e, em `api_reservar`, marcar como `CANCELADA` a reserva com `ida=0, volta=0`, respeitando o Hard Lock. Permitir confirmar quando todos os dias foram desmarcados.
- **Critério de aceite:** teste AAA e fluxo na tela: o dia desmarcado some da agenda, do painel e da lista do motorista.

## S13 — Exigir login para reservar e consultar agenda (LGPD)

- **Prioridade:** Essencial antes do piloto
- **Proposta:** token de sessão assinado, emitido no login, com biblioteca padrão ou a sessão do Flask. Reservar e consultar passam a usar o CPF do token, não o enviado pela página.
- **Critério de aceite:** sem token → 401; token de um aluno não altera nem lê dados de outro.

## S14 — Validar check-in

- **Prioridade:** Importante
- **Proposta:** rejeitar tipo diferente de IDA/VOLTA, aluno sem reserva ativa naquele dia e trecho (a confirmar com a gestora: pode embarcar quem não reservou?) e aluno já embarcado em outro veículo.
- **Critério de aceite:** testes AAA em `tests/test_checkin.py`.

## S15 — Corrigir horário dos avisos

- **Prioridade:** Importante
- **Proposta:** gravar `criado_em` com `get_server_now()`, como já faz `status_viagem`, ou converter na exibição. Os registros antigos em UTC também precisam de tratamento.
- **Critério de aceite:** aviso publicado às 14:22 aparece como 14:22.

## S16 — Limpar dados de teste do banco

- **Prioridade:** Importante; exige autorização, pois apaga dados.
- **Proposta:** com backup, remover os 100 alunos "Stress Test" e seus check-ins e o ponto "Ponto Editado". Rodar futuros testes de estresse em uma cópia.
- **Critério de aceite:** viagem da Cidade A finaliza em "Campus (Chegada)".

## S17 — Ajustes de leitura no painel da gestora

- **Prioridade:** Desejável
- **Proposta:** ocultar ou recolher dias passados (hoje os cards de junho aparecem antes da semana atual) e trocar "Inscrições: FECHADO" após o corte por "Reservas de hoje encerradas", pois os dias seguintes continuam abertos.

## Nota sobre S09

Na mesma verificação, `/api/reservar` também respondeu **erro 500** com `ida` não numérico e com `reservas` que não é lista. Só ocorre em chamadas diretas à API, mas deve ser tratado junto com a validação de data.

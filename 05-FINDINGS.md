# 🧠 05-FINDINGS.md: Memória Técnica e Log de Autocura

## 🎯 1. Propósito e Uso

Este arquivo é o **Cérebro de Recuperação** do projeto. Sempre que ocorrer um erro de execução, bug visual ou inconsistência de lógica, o erro deve ser colado aqui antes de solicitar a correção à IA.

**Protocolo de Autocura:**

1. Copie o erro/traceback do terminal ou console.
2. Cole na seção **"Log de Incidentes"** abaixo.
3. Invoque a IA com o comando: *"Analise os erros no FINDINGS.md, identifique a causa raiz e aplique uma correção cirúrgica no código"*.

---

## 📋 2. Log de Incidentes e Erros (The Log)

*Utilize esta tabela para registrar falhas técnicas e comportamentais da IA durante as sessões.*

| Data | Sessão (VCC) | Descrição do Erro / Traceback | Causa Raiz | Correção Cirúrgica Aplicada |
| :--- | :--- | :--- | :--- | :--- |
| [Data] | [ID-VCC] | [Cole o erro aqui] | [Ex: Alucinação de biblioteca] | [Resumo da mudança] |
| 2026-10-28 | 2026-10-28-correcao-sugestao-frota | `sugerir_frota` superdimensionava a frota: 3 alunos → 1 Ônibus (44); 47 → 2 Ônibus (88); 60 → 2 Ônibus + 1 Van (103). Viola RN03. | (1) No tratamento da sobra, o laço `reversed(ordem)` sobrescrevia `melhor` e terminava sempre em ÔNIBUS; (2) algoritmo guloso não encontra a combinação ótima; (3) não considerava quantas unidades de cada tipo existem. | Nova `combinacao_otima`: busca exaustiva (itertools) pela menor capacidade ≥ demanda, desempate por menos veículos, limitada às unidades ativas. Formato JSON inalterado. Testes em `tests/test_sugerir_frota.py`. |
| 2026-10-28 | 2026-10-28-seguranca-pin-e-testes | PIN armazenado como SHA-256 sem salt: com apenas 10.000 PINs possíveis, todos os hashes do banco são revertidos em milissegundos. Login sem limite de tentativas. | Hash rápido e determinístico escolhido no MVP; risco não avaliado (LGPD). | `hash_pin` passou a usar PBKDF2-SHA256 (200k iterações) com salt por aluno; `verificar_pin` aceita o formato antigo e o login migra o hash. Bloqueio de 5 min após 5 erros por CPF (HTTP 429). Testes em `tests/test_login.py`. |
| 2026-10-28 | 2026-10-28-seguranca-pin-e-testes | **Lacuna (não corrigida):** check-in não desconta vagas de exceção (RN02/RS05). Em `api_checkin`, `excecoes` é calculado e nunca usado; `motorista.html` (offline) também ignora. | Regra implementada só pela metade; ambígua com vários veículos por trecho. | Nenhuma — decisão adiada pelo responsável. Registrado como S08 em `docs/sugestoes/02-BACKLOG_SUGESTOES.md`. |
| 2026-10-28 | 2026-10-28-seguranca-pin-e-testes | **Bug (não corrigido):** `POST /api/reservar` com `"data": "abc"` responde sucesso e grava a reserva `12345678901_abc`. | `is_hard_locked` retorna `False` em `ValueError`, então datas inválidas passam pela trava. | Nenhuma ainda — registrado como S09 no backlog. |
| 2026-10-28 | 2026-10-28-correcao-pwa-e-modo-offline | Console: `Manifest fetch from /manifest.json failed, code 404` e `A bad HTTP response code (404) was received when fetching the script` (sw.js). App não instalável (RNF01) e sem cache offline. | `index.html` usa `manifest.json` e `sw.js` relativos a `/`, mas o Flask só servia em `/static/`. Além disso, o `sw.js` pré-cacheava `/index.html`, que não existe → `cache.addAll` falharia inteiro. | Rotas `/sw.js` (com `Cache-Control: no-cache`) e `/manifest.json` em `app.py`; lista de pré-cache corrigida para `['/', '/manifest.json']`. Testes em `tests/test_pwa.py`. |
| 2026-10-28 | 2026-10-28-correcao-pwa-e-modo-offline | **Perda silenciosa de check-ins:** com o servidor inacessível e o celular "online" (sinal fraco), o embarque aparecia como "Sincronizando ✓", mas sumia — 0 check-ins gravados quando o servidor voltou. | `enviarCheckinBackend` enfileirava → `atualizarStatusConexao` disparava `sincronizarFila` → o reenvio falhava e `sincronizarFila` apagava a fila **inteira** sem checar o resultado. | `sincronizarFila` só remove da fila o que o servidor respondeu; falhas de rede ficam. Trava `sincronizando` e fim da chamada recursiva (evita loop de reenvio). `carregarChecklist` mantém a lista na tela se a rede falhar. |
| 2026-10-28 | 2026-10-28-correcao-pwa-e-modo-offline | Trava de lotação offline contava cada check-in pendente duas vezes (van de 15 "lotaria" com 8). Bug latente, exposto pela correção acima. | Contagem = `passageiros marcados + checkinQueue.length`, mas quem está na fila já é marcado na tela (atualização otimista). Também somava filas de outras viagens. | Funções `estaPendente` / `contarConfirmados`: cada passageiro da viagem atual conta uma vez. |
| 2026-10-28 | 2026-10-28-correcao-pwa-e-modo-offline | **Risco evitado:** o `sw.js` antigo respondia a qualquer `/api/` sem rede com um 503 falso. Ao consertar o caminho do SW, isso faria o motorista mostrar "Erro no check-in" e esvaziar a lista em vez de enfileirar. | O motorista detecta "sem rede" pelo `.catch` do `fetch`; o 503 do SW chegava como resposta normal. | SW não intercepta mais `/api/` nem requisições que não sejam GET. Páginas passaram de cache-first para rede-primeiro (cache só sem conexão). |
| 2026-11-04 | 2026-11-04-verificacao-funcional | **Não corrigido (S11):** seletor de rota do motorista mostra `undefined` e nenhum botão de ponto aparece; o rastreamento (RF07) não pode ser usado pela tela. | `motorista.html` lê `p.rota`; a API e o `SCHEMA.md` definem `rota_id`. | Nenhuma ainda. |
| 2026-11-04 | 2026-11-04-verificacao-funcional | **Não corrigido (S12):** aluno desmarca um dia, a tela confirma, mas a reserva continua ativa e segue contando no painel e na lista do motorista. | `index.html` filtra os dias desmarcados do envio e `api_reservar` ignora `ida=0, volta=0`. | Nenhuma ainda. |
| 2026-11-04 | 2026-11-04-verificacao-funcional | **Não corrigido (S13):** `POST /api/reservar` e `GET /api/semana` funcionam só com o CPF, sem PIN: é possível alterar reservas e ler a agenda de outro aluno. | O login não gera sessão/token; as rotas confiam no CPF enviado. | Nenhuma ainda. |
| 2026-11-04 | 2026-11-04-verificacao-funcional | **Não corrigido (S14):** `/api/checkin` aceita aluno sem reserva, o mesmo aluno em dois veículos e tipo de viagem inválido (`XPTO`). | Rota não valida reserva nem tipo; o ID composto inclui o veículo. | Nenhuma ainda. |
| 2026-11-04 | 2026-11-04-verificacao-funcional | **Não corrigido (S15):** aviso publicado às 14:22 aparece como 17:22 para o aluno. | `criado_em` é gravado em UTC (`datetime('now')`) e exibido como hora local. | Nenhuma ainda. |
| 2026-11-04 | 2026-11-04-verificacao-funcional | **S16:** `database.db` continha dados de teste: 100 de 103 alunos e 100 check-ins de stress test, e o ponto "Ponto Editado" (ordem 10) depois de "Campus (Chegada)", que impede a viagem da Cidade A de finalizar ao chegar ao campus. | Testes rodados contra o banco real. | **Corrigido em 2026-11-04**, com autorização do responsável (protótipo, sem dados reais): banco recriado com os dados básicos; cópia anterior local em `database.db.bak-2026-11-04`, fora do git. |
| 2026-11-04 | 2026-11-04-verificacao-funcional | **Não corrigido (S18):** com o corte em 23:59, o calendário continua encerrando hoje às 14h. A tela também confirma dias que o servidor recusou. | `renderDays` usa `serverHora >= 14` fixo e ignora `horario_corte`/`trava_manual`; `showSuccess` não compara `total_registradas`. | Nenhuma ainda. |
| 2026-11-04 | 2026-11-04-verificacao-funcional | **Não corrigido (S19):** senha da gestora fixa no código e no guia; servidor em modo debug. | Configuração de desenvolvimento do MVP. | Nenhuma ainda. Plano de execução completo em `docs/PLANO_CORRECAO_AGENTES.md`. |

---

## 🔬 3. Análise de Causa Raiz (Root Cause) e Padrões

*Espaço para Maria (Revisora) ou Tiago (QA) documentarem por que erros recorrentes estão acontecendo.*

* **Padrão Detectado:** (Ex: A IA insiste em usar caminhos relativos em vez de `os.path.abspath`) [histórico de conversa].
* **Ação Preventiva:** (Ex: Reforçar a regra no `VIBE_MANIFEST.md` e no Seed Prompt da Ana).

---

## 💡 4. Decisões Técnicas e Trade-offs (Findings)

*Conforme as Karpathy Guidelines ("Think Before Coding"), registre aqui as premissas assumidas antes de grandes mudanças [histórico de conversa].*

* **Decisão:** Uso de SQLite puro sem ORM.
  * **Justificativa:** Garantir latência zero e seguir a regra de simplicidade 80/20.
* **Decisão:** Design Glassmorphism Mobile-First.
  * **Justificativa:** Foco na experiência do usuário Lucas (Alunos) para registros rápidos.
* **Decisão Validada:** Uso de SQLite em modo WAL suporta concorrência perfeitamente.
  * **Justificativa:** Teste de estresse realizado com sucesso (100 requisições concorrentes de cadastro no backend via threads em ~2.5 segundos, zero erros e sem bloqueio de concorrência). A arquitetura atual se provou robusta e a prova de carga.
* **Decisão (2026-10-28):** Sugestão de frota por busca exaustiva, não por solver/programação linear.
  * **Justificativa:** Com 3 tipos de veículo e frota pequena, o espaço de combinações é de dezenas a poucos milhares — resolvido em microssegundos com `itertools` (biblioteca padrão). Critério: menos assentos vazios → menos veículos → respeitar unidades ativas; acima da frota, ignora o limite para indicar contratação. Pontos em aberto em `docs/sugestoes/02-BACKLOG_SUGESTOES.md` (S07).
* **Decisão (2026-10-28):** Testes com `unittest` (biblioteca padrão) em vez de `pytest`.
  * **Justificativa:** Anti-Bloat — nenhuma dependência nova. Executar: `python -m unittest discover tests`. Testes de rota usam banco temporário (`tests/apoio.py`), nunca o `database.db`.
* **Decisão (2026-10-28):** Hash do PIN com `hashlib.pbkdf2_hmac` (200.000 iterações), não bcrypt/argon2.
  * **Justificativa:** Biblioteca padrão (Anti-Bloat), ~70 ms por hash. As iterações ficam gravadas no próprio hash, então podem ser aumentadas no futuro sem invalidar PINs existentes. Limitação conhecida: com PIN de 4 dígitos, um atacante com o arquivo do banco ainda quebra o PIN de um aluno em minutos — proteger o `database.db` continua essencial.
* **Decisão (2026-10-28):** Service worker em "rede primeiro" para páginas e sem interceptar `/api/`.
  * **Justificativa:** Com cache-first, os celulares continuariam exibindo a versão antiga das telas após cada atualização (até trocar `CACHE_NAME`). As APIs ficam fora do SW porque o modo offline do motorista depende do `fetch` falhar de verdade para enfileirar o check-in.
* **Decisão (2026-10-28):** Bloqueio de tentativas de login em memória, por CPF.
  * **Justificativa:** Sem tabela nova (preserva o `SCHEMA.md`) e sem dependência externa. Zera ao reiniciar o servidor e não cobre tentativa de um mesmo PIN em vários CPFs — aceitável para o MVP.

---

## 🚧 5. Devedor Técnico e Lições Aprendidas

*O que ficou para o próximo giro do PDCA ou o que aprendemos que não deve ser repetido.*

1. **Lição:** Nunca importar fontes externas via CDN para manter o princípio **Offline-First**.
2. **Dívida:** O campo 'Telefone' solicitado pela Ana será implementado na Fase 7 (Evolução).

---

### 🛂 Instrução para a IA
>
> *"Antes de cada correção, consulte as seções 2 e 4 deste arquivo para garantir que a nova solução não repita erros do passado e mantenha as decisões arquiteturais já validadas"*.

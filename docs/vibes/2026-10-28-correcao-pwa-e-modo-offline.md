# 📑 VCC — Correção do PWA e do Modo Offline do Motorista

## 📅 Identificação da Sessão

- **Projeto:** SPTU (VEM)
- **Data:** 28/10/2026
- **Responsável:** Equipe VEM (sessão assistida por Claude Code)

---

## 🧠 1. Contexto do Problema

- **A Dor:** "Fazer o programa voltar a funcionar." Varredura completa (19 rotas da API + teste E2E em Chrome headless das 3 telas) mostrou backend saudável, mas o PWA e o modo offline do motorista quebrados.
- **O que já está pronto:**
  - [x] 02-DERS_MESTRE.md (RNF01 PWA, RNF02 Tolerância Offline)
  - [x] Código Existente: `static/sw.js`, `static/manifest.json`, `static/motorista.html`
- **Fase do Ciclo de Vida (VEM):**
  - [x] Fase 6: Build - Deploy & Resilience (Piloto)

---

## 🤖 2. Papel da IA (Persona)

- [x] **Testadora (Tiago):** varredura E2E e testes AAA.
- [x] **Implementadora (José/Ana):** rotas do PWA, service worker e fila offline.

---

## 👤 3. Papel do Humano

- [x] **Validador Final**
- **Nível de Supervisão (0-10):** 4

---

## 🚀 4. Prompt de Abertura

> `Faça as correções necessárias para fazer o programa voltar a funcionar.`

---

## ⚙️ 5. Restrições Técnicas

- **Linguagem/Framework:** Flask + Vanilla JS, sem dependências novas.
- **Padrões Obrigatórios:** [x] Offline-First | [x] Mudanças cirúrgicas.

---

## ✅ 6. Critérios de Aceite

- [x] `/manifest.json` e `/sw.js` respondem 200; service worker registrado no navegador.
- [x] Check-in feito com servidor inacessível fica na fila e é gravado quando o servidor volta.
- [x] Contador de lotação não conta duas vezes check-ins pendentes.
- [x] Página do motorista reabre do cache sem servidor.
- [x] `python -m unittest discover tests` → 42 testes OK.
- [x] Fluxo completo (aluno reserva → gestora vê → motorista embarca) testado em Chrome headless.

---

## 📦 8. Artefatos Gerados

- **Código:** `app.py` (rotas `/sw.js` e `/manifest.json`), `static/sw.js`, `static/motorista.html`.
- **Testes:** `tests/test_pwa.py`.
- **Documentação:** `05-FINDINGS.md`, `GUIA_DO_USUARIO.md`, `docs/sugestoes/`.

---

## 📝 10. Observações Pós-Sessão

- **O que funcionou:** Teste E2E via Chrome DevTools Protocol (Node puro, sem bibliotecas) pegou erros que os testes unitários não pegam: 404 de arquivos do PWA e perda silenciosa de check-ins.
- **Armadilha evitada:** Corrigir apenas o caminho do `sw.js` ativaria o service worker antigo, que respondia às APIs offline com um 503 falso. O motorista então perderia check-ins e a lista ficaria vazia. Por isso o SW passou a não interceptar `/api/`.
- **Suposições assumidas:** Páginas em "rede primeiro" (cache só sem conexão), para que atualizações cheguem aos celulares sem precisar trocar a versão do cache.
- **Próximo Passo:** S10 — guardar veículos e lista de passageiros no aparelho para iniciar viagem já sem conexão.

# 📑 VCC — Segurança do PIN (S01) e Testes AAA (S02)

## 📅 Identificação da Sessão

- **Projeto:** SPTU (VEM)
- **Data:** 28/10/2026
- **Responsável:** Equipe VEM (sessão assistida por Claude Code)

---

## 🧠 1. Contexto do Problema

- **A Dor:** PINs salvos como SHA-256 sem salt (reversíveis em milissegundos com o banco em mãos) e regras críticas (hard lock, login, check-in) sem nenhum teste automatizado.
- **O que já está pronto:**
  - [x] 02-DERS_MESTRE.md (RF01, RS01, RS03, RS04)
  - [x] SCHEMA.md (tabela `alunos`, `/api/login`)
  - [x] Código Existente: `hash_pin`, `api_login`, `is_hard_locked`, `api_reservar`, `api_checkin`
  - [x] Backlog: `docs/sugestoes/02-BACKLOG_SUGESTOES.md` (S01, S02)
- **Fase do Ciclo de Vida (VEM):**
  - [x] Fase 5: Build - Productize (Ana)

---

## 🤖 2. Papel da IA (Persona)

- [x] **Revisora (Maria):** auditoria do armazenamento do PIN (LGPD).
- [x] **Implementadora (Ana):** hash com salt, migração e bloqueio de tentativas.
- [x] **Testadora (Tiago):** suíte AAA com banco temporário.

---

## 👤 3. Papel do Humano

- [x] **Validador Final**
- **Nível de Supervisão (0-10):** 5
- **Justificativa:** Regra de negócio ambígua (exceções no check-in) foi levada ao humano; ele decidiu adiar.

---

## 🚀 4. Prompt de Abertura

> `Continue` (seguir com S01 e S02 do backlog)

---

## ⚙️ 5. Restrições Técnicas

- **Linguagem/Framework:** Python 3 / Flask — apenas biblioteca padrão (`hashlib.pbkdf2_hmac`, `hmac`, `threading`, `unittest`).
- **Bibliotecas Proibidas:** bcrypt, argon2, pytest, Flask-Limiter (Anti-Bloat).
- **Padrões Obrigatórios:** [x] Karpathy Style | [x] JSON is Law (SCHEMA.md atualizado para o formato do hash e o HTTP 429).

---

## ✅ 6. Critérios de Aceite

- [x] PIN salvo como `pbkdf2_sha256$iteracoes$salt$hash`; PINs iguais geram hashes diferentes.
- [x] Alunos com hash antigo continuam logando e são migrados no login.
- [x] 5 erros seguidos bloqueiam o CPF por 5 min (HTTP 429).
- [x] `python -m unittest discover tests` → 37 testes OK, sem tocar o `database.db` real.
- [ ] Testado manualmente no navegador (pendente — validar login e mensagem de bloqueio no PWA).

---

## 📦 8. Artefatos Gerados

- **Código:** `app.py` (`hash_pin`, `verificar_pin`, `pin_legado`, controle de falhas, `api_login`).
- **Testes:** `tests/apoio.py`, `tests/test_login.py`, `tests/test_hard_lock.py`, `tests/test_checkin.py`.
- **Documentação:** `SCHEMA.md`, `05-FINDINGS.md`, `GUIA_DO_USUARIO.md`, `docs/sugestoes/`.

---

## 🛂 9. Checklist Karpathy

- [x] Suposições explicitadas (Seção 10).
- [x] Regra 80/20: PBKDF2 da biblioteca padrão em vez de bcrypt; bloqueio em memória em vez de Redis.
- [x] Mudanças cirúrgicas: o frontend não precisou mudar (já exibe o campo `erro`).

---

## 📝 10. Observações Pós-Sessão

- **O que funcionou:** Trocar `DB_PATH` por um banco temporário no `setUp` permitiu testar rotas reais pelo `test_client` sem risco aos dados.
- **Achados durante os testes:**
  - **S08:** o check-in não desconta vagas de exceção (RN02/RS05) — nem no backend nem no modo offline. Humano optou por só documentar.
  - **S09:** `/api/reservar` aceita e grava datas inválidas (ex.: `"abc"`).
- **Suposições assumidas:**
  1. 200.000 iterações (~70 ms por hash) equilibram custo de ataque e tempo de login/cadastro em massa.
  2. Bloqueio por CPF em memória é suficiente para o MVP (zera ao reiniciar o servidor).
- **Próximo Passo:** Decidir a regra do S08; corrigir S09.

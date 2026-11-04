# 📑 VCC — Correção da Sugestão de Frota (RN03)

## 📅 Identificação da Sessão

- **Projeto:** SPTU (VEM)
- **Data:** 28/10/2026
- **Responsável:** Equipe VEM (sessão assistida por Claude Code)

---

## 🧠 1. Contexto do Problema

- **A Dor:** A sugestão de frota do painel da gestora indicava veículos maiores que o necessário (ex.: 3 alunos → 1 ônibus de 44 lugares), contrariando a RN03 (mínima ociosidade).
- **O que já está pronto:**
  - [x] 01-NORTH_STAR.md
  - [x] 02-DERS_MESTRE.md (RF03, RN03)
  - [x] SCHEMA.md (`sugestao_frota` em `/api/painel`)
  - [x] Código Existente: `sugerir_frota` em `app.py`
- **Fase do Ciclo de Vida (VEM):**
  - [x] Fase 5: Build - Productize (Ana)

---

## 🤖 2. Papel da IA (Persona)

- [x] **Implementadora (Ana):** correção do algoritmo.
- [x] **Testadora (Tiago):** testes AAA em `tests/`.

---

## 👤 3. Papel do Humano

- [x] **Validador Final**
- **Nível de Supervisão (0-10):** 5
- **Justificativa:** Correção pontual com critério matemático verificável por testes.

---

## 🚀 4. Prompt de Abertura

> `Corrija o problema das sugestões. Documente as sugestões em uma pasta separada.`

---

## ⚙️ 5. Restrições Técnicas

- **Linguagem/Framework:** Python 3 / Flask (biblioteca padrão apenas: `itertools`, `unittest`).
- **Bibliotecas Proibidas:** qualquer dependência nova (pytest, numpy, solvers).
- **Padrões Obrigatórios:** [x] Karpathy Style | [x] JSON is Law (formato de `sugestao_frota` inalterado).

---

## ✅ 6. Critérios de Aceite

- [x] Código roda sem tracebacks (`/api/painel` responde 200).
- [x] Atende RN03: menor número de assentos vazios usando apenas veículos ativos.
- [x] Passa nos testes unitários AAA (9/9, incluindo verificação por força bruta de 1 a 131 passageiros).
- [ ] Testado manualmente no navegador (pendente — validar no painel da gestora).

---

## 📦 8. Artefatos Gerados

- **Código:** `app.py` (`sugerir_frota` + nova `combinacao_otima`), `tests/test_sugerir_frota.py`.
- **Documentação:** `05-FINDINGS.md`, `GUIA_DO_USUARIO.md`, `docs/sugestoes/`.

---

## 🛂 9. Checklist Karpathy

- [x] Suposições explicitadas (ver Seção 10).
- [x] Regra 80/20: busca exaustiva simples em vez de solver.
- [x] Mudança cirúrgica: só `sugerir_frota` foi alterada; contrato JSON preservado.

---

## 📝 10. Observações Pós-Sessão

- **O que funcionou:** Separar o cálculo puro (`combinacao_otima`) da leitura do banco permitiu testar sem tocar no `database.db`.
- **O que falhou:** A primeira versão da correção ignorava a quantidade de veículos disponíveis e sugeria, por exemplo, 6 vans para 90 alunos quando a frota só tem 1 van. Corrigido usando o "veículos disponíveis" da RN03.
- **Suposições assumidas:**
  1. Critério principal: menos assentos vazios; desempate: menos veículos.
  2. Cada tipo usa a maior capacidade cadastrada para aquele tipo (comportamento anterior mantido).
  3. Se a demanda supera a frota ativa, o limite de unidades é ignorado para indicar o que seria preciso contratar.
- **Próximo Passo:** Ver `docs/sugestoes/02-BACKLOG_SUGESTOES.md` (S01 hash do PIN e S02 testes são os mais urgentes).

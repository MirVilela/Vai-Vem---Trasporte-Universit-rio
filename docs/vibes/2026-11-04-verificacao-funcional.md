# 📑 VCC — Verificação Funcional do Programa

## 📅 Identificação da Sessão

- **Projeto:** SPTU (VEM)
- **Data:** 04/11/2026
- **Responsável:** Equipe VEM (sessão assistida por Claude Code)
- **Persona:** Tiago (QA)
- **Prompt:** `Verifique o funcionamento do programa`
- **Restrição:** somente verificação; nenhum código alterado. Testes em cópias do banco (`database.db` com o mesmo MD5 antes e depois da inicialização real).

## ✅ Como foi verificado

- `python -m unittest discover tests` → 42 testes OK.
- Inicialização com o banco real: páginas, `/sw.js`, `/manifest.json` e APIs públicas → 200.
- API com o cliente de testes do Flask: cadastros, reserva, tracking, embarque, robustez e controle de acesso.
- Chrome headless em largura de celular (390 px): formulários da gestora, aluno, motorista, modo avião e capturas de tela.

## 🟢 Funcionou

- Login do aluno, bloqueio na 6ª tentativa e aluno recém-cadastrado entrando.
- Reserva, hard lock, painel e sugestão de frota.
- Cadastro de veículo e aluno, publicação de aviso e configurações.
- Check-in online, lotação, modo avião e sincronização automática ao voltar a rede.
- Tela do aluno exibindo avisos e posição do veículo quando há status gravado.
- Sem rolagem horizontal; botões de ida/volta e check-in com 48 px.

## 🔴 Falhou

Registrado em `05-FINDINGS.md` e em `docs/sugestoes/` como S09 e S11 a S17.

## 📝 Observações Pós-Sessão

- **Lição:** "todas as rotas respondem 200" não prova o uso real. O defeito do tracking só apareceu ao operar a tela do motorista, e o de cancelamento só ao comparar a confirmação da tela com o servidor.
- **Correção de registro:** a verificação de 28/10 e o `docs/RESUMO_EXECUTIVO.md` marcaram o rastreamento como pronto sem exercitar os botões do motorista.
- **Próximo Passo:** seguir `docs/PLANO_CORRECAO_AGENTES.md`. Testes repetíveis em `tests/e2e/`.

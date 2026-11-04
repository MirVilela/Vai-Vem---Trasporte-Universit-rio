# 💡 Sugestões de Evolução — SPTU (VEM)

Pasta dedicada a **sugestões ainda não implementadas**, levantadas em análises externas (pesquisa de mercado, trabalhos acadêmicos, revisões de código). Nada aqui é requisito: para virar trabalho, a sugestão precisa ser aprovada, entrar no `02-DERS_MESTRE.md` e ganhar um VCC em `docs/vibes/`.

## 📂 Arquivos

| Arquivo | Conteúdo |
| :--- | :--- |
| [01-ESTADO_DA_ARTE.md](01-ESTADO_DA_ARTE.md) | Softwares e trabalhos similares ao SPTU e o que nos diferencia (inclui análise do TCC do IFPI). |
| [02-BACKLOG_SUGESTOES.md](02-BACKLOG_SUGESTOES.md) | Lista priorizada de melhorias (S01–S07) com origem e critério de aceite. |

## 🚦 Status das Sugestões

| ID | Sugestão | Persona | Prioridade | Status |
| :--- | :--- | :--- | :--- | :--- |
| S00 | Corrigir `sugerir_frota` (RN03) | Ana / Tiago | Essencial | ✅ Implementada em 2026-10-28 |
| S01 | Hash do PIN com salt (PBKDF2) + bloqueio de tentativas | Maria / Ana | Essencial | ✅ Implementada em 2026-10-28 |
| S02 | Ampliar testes AAA em `tests/` | Tiago | Essencial | ✅ Implementada em 2026-10-28 (37 testes) |
| S03 | Avaliação de usabilidade (SUS) | Maria / José | Importante | ⏳ Pendente |
| S04 | Ajustes de UX (erros, navegação, nomes) | José | Importante | ⏳ Pendente |
| S05 | Quadro comparativo de trabalhos relacionados | Maria | Importante | ⏳ Pendente |
| S06 | Taxa de ocupação prevista no painel | José / Ana | Desejável | ⏳ Pendente |
| S07 | Refinamentos da sugestão de frota | Ana | Desejável | ⏳ Pendente |
| S08 | Blindar vagas de exceção no check-in (RN02/RS05) | Ana / José | Essencial | ⏸️ Aguardando decisão da regra |
| S09 | Validar formato de data em `/api/reservar` | Ana | Importante | ⏳ Pendente |
| S10 | Motorista iniciar viagem já sem conexão (RNF02 completo) | José | Importante | ⏳ Pendente |
| S11 | Corrigir rastreamento na tela do motorista (RF07) | José | Essencial | ⏳ Pendente |
| S12 | Desmarcar dia deve cancelar a reserva | José / Ana | Essencial | ⏳ Pendente |
| S13 | Exigir login para reservar e consultar agenda (LGPD) | Maria / Ana | Essencial | ⏳ Pendente |
| S14 | Validar check-in (reserva, veículo único, tipo) | Ana | Importante | ⏳ Pendente |
| S15 | Corrigir horário dos avisos (UTC → Brasília) | Ana / José | Importante | ⏳ Pendente |
| S16 | Limpar dados de teste do banco | Ana | Importante | ⏸️ Aguardando autorização |
| S17 | Ajustes de leitura no painel da gestora | José | Desejável | ⏳ Pendente |
| S18 | Calendário obedecer ao corte configurado e à recusa do servidor | José | Essencial | ⏳ Pendente |
| S19 | Senha da gestora fora do código e modo debug desligado | Ana | Essencial antes do piloto | ⏳ Pendente |

> **Para executar as correções:** siga `docs/PLANO_CORRECAO_AGENTES.md`.

> Ao implementar uma sugestão, atualize o status aqui e registre a mudança no `05-FINDINGS.md` e no `GUIA_DO_USUARIO.md` (quando afetar o usuário).

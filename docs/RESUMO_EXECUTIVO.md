# Resumo Executivo — SPTU (Sistema Preditivo de Transporte Universitário)

> Situação em 28/10/2026. Valores são **estimativas** com as premissas da Seção 4.

## 1. O problema

O transporte intermunicipal de universitários é organizado hoje por **grupos de WhatsApp**. A gestora tem cerca de **1h30** para contar quem vai viajar e decidir quantos veículos mandar. Resultado:

- **Ônibus saindo com assentos vazios**, um custo pago todos os dias;
- alunos que **só vão** ou **só voltam** não ficam registrados;
- na **volta**, em dias cheios, não há controle nem critério justo de quem embarca.

**Solução proposta:** um app web instalável no celular (PWA) em que o aluno marca a semana em segundos. A gestora vê com antecedência quantos vão e recebe a **sugestão de frota com menos assentos vazios**. O motorista confirma o embarque com um toque, mesmo sem internet.

## 2. Requisitos e situação atual

| Requisito | Para quem | Situação |
| :--- | :--- | :--- |
| Login com CPF + PIN de 4 dígitos | Aluno | ✅ Pronto (PIN protegido e bloqueio após 5 erros) |
| Agenda semanal de ida/volta, com corte às 14h | Aluno | ✅ Pronto |
| Painel com total de alunos e sugestão de frota | Gestora | ✅ Pronto (cálculo corrigido em 28/10) |
| Vagas garantidas para alunos de rotas distantes | Gestora | ⚠️ Marcação existe, mas o embarque ainda não reserva esses assentos |
| Lista de embarque que trava ao lotar, funciona offline | Motorista | ✅ Pronto (offline depois de iniciar a viagem com internet) |
| Mural de avisos | Gestora → Aluno | ✅ Pronto |
| Acompanhamento da viagem por pontos de referência | Motorista → Aluno | ✅ Pronto |
| Relatório de faltas (reservou e não embarcou) | Gestora | ⚠️ Só existe relatório de quem embarcou |

**Fora do escopo:** integração com WhatsApp, apps de loja (Play Store/App Store), pagamentos e login por e-mail.

## 3. Custos previstos por fase

| Fase | O que entrega | Esforço | Mão de obra* | Gastos diretos |
| :--- | :--- | :--- | :--- | :--- |
| **1. MVP** ✅ concluída | Requisitos, protótipo e sistema funcionando em rede local | 150–200 h | R$ 12.000 – 30.000 (equivalente; já realizado) | — |
| **2. Ajustes pré-piloto** | Blindar vagas de exceção, relatório de faltas, senha individual da gestora (hoje fixa no código), mensagens de erro claras, termo de uso/LGPD | 30–50 h | R$ 2.400 – 7.500 | ~R$ 100/mês (assistente de IA) |
| **3. Piloto (1 rota, 1 mês)** | Servidor na internet com HTTPS, domínio, backup, cadastro dos alunos, treinamento, acompanhamento | 30–50 h | R$ 2.400 – 7.500 | ~R$ 75 (domínio + 1º mês de servidor) |
| **4. Operação** (mensal) | Servidor no ar e manutenção | 4–8 h/mês | R$ 320 – 1.200/mês | **R$ 35 – 75/mês** |
| **5. Evolução** (opcional) | Avaliação de usabilidade com usuários, indicador de ocupação, refinamentos da frota | 20–34 h | R$ 1.600 – 5.100 | — |

\* Mão de obra só vira gasto se for contratada. Feita pela própria equipe, o custo em dinheiro se limita aos gastos diretos.

**Para colocar em produção (Fases 2 + 3):** 60–100 h de trabalho, ou R$ 4.800 – 15.000 se contratado, **mais cerca de R$ 300 em gastos diretos**. Depois disso, **R$ 35 – 75 por mês** para manter no ar.

**Retorno:** o sistema se paga quando o custo das viagens vazias evitadas no mês supera o custo mensal. Com R$ 35 – 75/mês de infraestrutura, evitar **uma** viagem de van desnecessária por mês tende a bastar. Esse ponto precisa ser confirmado com o custo real por viagem da operadora.

## 4. Premissas

- **Valor-hora:** R$ 80 (júnior) a R$ 150 (pleno), conforme referências de mercado de 2026.
- **Servidor:** VPS básica de R$ 28 – 40/mês em promoção, que pode subir para ~R$ 70/mês na renovação. **Domínio** .com.br: R$ 40/ano. **Certificado HTTPS:** gratuito (Let's Encrypt).
- **Assistente de IA:** US$ 20/mês por desenvolvedor (≈ R$ 100), só nos meses de desenvolvimento.
- **Celulares:** os de alunos e motoristas já existentes; nenhum aparelho comprado.
- **Não incluídos:** revisão jurídica da LGPD por advogado, impostos/CNPJ, aparelhos dedicados e reserva para imprevistos (recomenda-se +20%).

> **Decisão pendente:** as regras do projeto pedem operação "100% em rede local". Mas o aluno reserva de casa, em outra cidade, e o app só pode ser instalado no celular se for servido com HTTPS. Por isso a Fase 3 prevê um **servidor na internet**. O funcionamento offline continua garantido onde mais importa: no embarque, com o motorista.

## Fontes de preço

- Domínio .br (NIC.br/Registro.br): [Teletime](https://teletime.com.br/14/10/2026/br-6-milhoes/)
- VPS: [Hora de Codar — preço VPS 2026](https://horadecodar.com.br/valor-vps/) · [Hostinger KVM 2](https://www.vpsbenchmarks.com/hosters/hostinger/plans/1055)
- Valor-hora: [Monitor do Mercado — freelancer 2026](https://monitordomercado.com.br/noticias/399275-quanto-um-programador-freelancer-cobra-por-hora-no-brasil-em-2026-e-o-que-define-o-nivel-junior-pleno-e-senior/)
- Assistente de IA: [ScreenApp — Claude pricing 2026](https://www.screenapp.io/blog/claude-ai-pricing)

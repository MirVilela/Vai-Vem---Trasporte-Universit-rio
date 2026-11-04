# 🔎 Estado da Arte — Softwares Similares ao SPTU

> Pesquisa realizada em 2026-10-28. As informações de produtos comerciais vêm das páginas dos próprios fabricantes e não foram testadas na prática.

## 1. Conclusão Geral

Não foi encontrado software que faça **exatamente** o que o SPTU propõe. As funções existem de forma fragmentada:

- **Apps brasileiros de van** cobrem a confirmação de ida/volta.
- **Plataformas internacionais** cobrem frota, embarque e rastreamento.
- **Nenhum** combina *otimização da frota a partir da intenção semanal* com *embarque justo por ordem de chegada* e *operação offline do motorista*.

## 2. Mapeamento por Categoria

### 2.1 Trabalhos acadêmicos brasileiros

| Projeto | O que faz | Relação com o SPTU |
| :--- | :--- | :--- |
| **TCC IFPI 2026** (Bandeira) | SaaS multi-tenant: reservas, capacidade, presença e pagamentos (rota Campo Maior–Piripiri). | Mesma dor (WhatsApp). Ver Seção 3. |
| **NaviApp** (SBC/WICS 2026) | Gestão colaborativa do transporte acadêmico fretado por prefeitura. | Argumenta que Uber/99/Moovit não servem para transporte coletivo. |
| **TCC UNIVEM** (Tupã/Marília) | Perfis universitário e coordenador; verificação de presença diária. | Similar ao fluxo aluno → gestora. |
| **AcadBus** (Unoesc) | Embarque com QR Code e comunicação em tempo real. | Similar a RF05/RF06/RF07. |
| **Intercampi** (UNILAB 2024) | Consulta de horários e rotas, com acesso offline. | Só informa; não reserva. |
| **PickBus** (2021) | Transporte fretado para eventos. | Fretamento eventual, não recorrente. |

### 2.2 Produtos comerciais no Brasil (vans)

| App | Recursos relevantes | Lacuna frente ao SPTU |
| :--- | :--- | :--- |
| **UniVans** | Presença confirmada pelo passageiro; financeiro; cita van universitária. | Sem dimensionamento de frota, hard lock ou exceções. |
| **Vanzinha** | Falta "só na ida", "só na volta" ou dia todo. | Foco escolar (pais). |
| **Rota Van / Via Van** | Ausência entra na rota do motorista; geolocalização. | Foco escolar. |
| **SETE (FNDE)** | Sistema público gratuito de frota e roteirização escolar. | Sem reserva pelo aluno. |

### 2.3 Produtos internacionais

| Produto | Recursos relevantes | Diferença |
| :--- | :--- | :--- |
| **Zeelo** | Reserva de assento, validação de embarque, ajuste do tamanho do veículo pelo uso real. | Serviço corporativo pago, dependente de internet. |
| **TransLoc** | Rastreamento GPS, transporte sob demanda, mural de avisos. | Sem reserva semanal nem cálculo de frota. |
| **Mobisoft** | Reserva de assento e app do motorista. | Solução sob encomenda. |

## 3. Análise do TCC do IFPI (concorrente conceitual mais próximo)

**Referência:** BANDEIRA, R. S. *Desenvolvimento e avaliação de uma solução SaaS multi-tenant para gestão do transporte universitário intermunicipal*. TCC (Tecnólogo em ADS) — IFPI Campus Piripiri, 2026. Orientador: Prof. Me. Jeferson do Nascimento Soares. Disponível no repositório BIA/IFPI.

### 3.1 Comparação direta

| Dimensão | TCC IFPI | SPTU |
| :--- | :--- | :--- |
| Quem decide a frota | Frota fixa; só limita reservas à capacidade. | **Sugere o mix de veículos** pela demanda (RF03/RN03). |
| Unidade de reserva | Inscrição em viagem do catálogo. | Agenda semanal de intenção (ida/volta). |
| Prazo | Cancelamento até 30 min antes. | Hard lock às 14h (RS03). |
| Embarque de volta | Lista nominal fixa. | **Ordem de chegada + vagas de exceção** (RN01/RN02). |
| Offline | Não. | **Motorista offline-first** (RNF02). |
| Login | E-mail + senha (bcrypt) + JWT. | CPF + PIN. |
| Pagamento | ✅ Controle operacional e receita mínima. | ❌ Fora de escopo. |
| Multi-empresa | ✅ Multi-tenant. | ❌ Operação única. |
| Avisos / tracking | ❌ (evolução futura). | ✅ RF06 / RF07. |
| Stack | NestJS, Prisma, PostgreSQL, React, nuvem. | Flask, SQLite, Vanilla JS (Anti-Bloat). |
| Testes | 458 testes unitários. | Iniciados em 2026-10-28 (`tests/`). |
| Avaliação com usuários | n=19, médias Likert 4,37–4,89. | Ainda não realizada. |

### 3.2 Leitura

Os projetos são **complementares**: o TCC responde "esta viagem é financeiramente viável?"; o SPTU responde "quantos e quais veículos mandar, e quem embarca de forma justa?". O diferencial central do SPTU (RN03 — mínima ociosidade) não existe no TCC.

### 3.3 Feedback dos usuários do TCC aplicável ao SPTU

- Mensagens de erro genéricas ("erro ao realizar") frustram — indicar causa e correção.
- Falta de atalho para voltar à tela inicial.
- "Parada" foi entendida como ponto de descanso — usar "ponto de embarque/desembarque".
- Áreas administrativas com muitos campos por tela concentraram as notas mais baixas.

## 4. Fontes

- [TCC IFPI (BIA)](https://bia.ifpi.edu.br/jspui/bitstream/123456789/5794/1/Artigo_Acad%c3%aamico_Rauan__.pdf)
- [NaviApp (SBC)](https://sol.sbc.org.br/index.php/wics/article/view/43227)
- [TCC UNIVEM](https://aberto.univem.edu.br/handle/11077/1593)
- [AcadBus (Unoesc)](https://periodicos.unoesc.edu.br/siepe/article/download/36243/20196/126250)
- [UniVans](https://univans.com.br/) · [Vanzinha](https://www.vanzinha.com.br/) · [Rota Van](https://rotavan.app.br/) · [Via Van](https://viavan.com.br/)
- [SETE/FNDE](https://brasil61.com/noticias/programa-de-computador-vai-ajudar-na-gestao-do-transporte-escolar-em-municipios-estados-e-distrito-federal-bras203036)
- [Zeelo](https://zeelo.co/technology/rider-app) · [TransLoc](https://transloc.com/universities/) · [Mobisoft](https://mobisoftinfotech.com/solutions/campus-transportation-software)

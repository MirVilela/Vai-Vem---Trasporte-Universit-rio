# 📖 Guia do Usuário — VEM Transporte Universitário

> **O que é este documento?**  
> Um guia simples e direto para qualquer pessoa que queira entender como o sistema funciona, como rodá-lo e como testar cada tela. Sem jargão técnico desnecessário.

---

## 🚀 Como Rodar o Sistema

### Pré-requisitos

- **Python 3.10+** instalado
- Instalar as dependências:

```bash
pip install -r requirements.txt
```

### Iniciar o servidor

```bash
python app.py
```

O terminal vai mostrar:

```
VEM SPTU — Motor Backend
http://127.0.0.1:5000
Admin Token: vem-admin-2026
```

**Pronto!** Abra o navegador e acesse: **http://127.0.0.1:5000**

---

## 👥 Credenciais de Teste

O sistema já vem com 3 alunos cadastrados para testes:

| Nome             | CPF           | PIN    | Rota                | Tipo de Vaga |
|:-----------------|:--------------|:-------|:--------------------|:-------------|
| João Silva       | `12345678901` | `1234` | Cidade A → Campus   | NORMAL       |
| Maria Souza      | `98765432100` | `5678` | Cidade B → Campus   | EXCEÇÃO      |
| Carlos Oliveira  | `11122233344` | `0000` | Cidade A → Campus   | NORMAL       |

### Senha do Painel Administrativo (Gestora e Motorista)

| Dado          | Valor             |
|:--------------|:------------------|
| Admin Token   | `vem-admin-2026`  |

> **Nota:** Nas telas de gestora e motorista, o sistema pede essa senha ao entrar.

---

## 📱 As 3 Telas do Sistema

### 1. Tela do Aluno — `http://127.0.0.1:5000/`

**Para quem?** Estudantes que usam o transporte universitário.

**O que faz:**
1. **Login** → Digita CPF e PIN de 4 dígitos
2. **Avisos e Rastreamento** → Vê banners de avisos da gestora e acompanha a posição do ônibus em tempo real.
3. **Calendário Semanal** → Marca para cada dia da semana se vai de **IDA**, **VOLTA**, ou ambos
4. **Confirmação** → Tela de sucesso mostrando o resumo das reservas

**Fluxo rápido de teste:**
1. Acesse `http://127.0.0.1:5000/`
2. CPF: `123.456.789-01` | PIN: `1234`
3. Clique em "Entrar"
4. Marque ida/volta nos dias desejados
5. Clique em "Confirmar Semana"

---

### 2. Painel da Gestora — `http://127.0.0.1:5000/gestora`

**Para quem?** A gestora do transporte que precisa dimensionar a frota.

**O que faz:**
- Mostra o **total de alunos por dia** (ida e volta separados)
- **Sugere a combinação de veículos** ideal para cada trecho (ex: 2 Ônibus + 1 Van) — a que deixa **menos assentos vazios** usando apenas os veículos ativos. Se a demanda passar da frota cadastrada, a sugestão mostra o que seria necessário contratar.
- Permite visualizar as **vagas de exceção** (alunos de locais distantes com assento garantido)
- **Mural de Avisos**: Permite publicar e arquivar avisos (Informativos ou Urgentes) para os alunos.
- **Pontos de Rota**: Cadastro das paradas do ônibus (para uso no rastreamento do motorista).

**Fluxo rápido de teste:**
1. Acesse `http://127.0.0.1:5000/gestora`
2. Digite a senha admin: `vem-admin-2026`
3. Veja o painel com os dados consolidados

---

### 3. Checklist do Motorista — `http://127.0.0.1:5000/motorista`

**Para quem?** O motorista na hora do embarque.

**O que faz:**
- Lista os passageiros que reservaram vaga para aquele dia e trecho (IDA ou VOLTA)
- O motorista **clica no nome** para confirmar o embarque (check-in)
- O sistema **trava automaticamente** quando o veículo lota (capacidade máxima atingida)
- **Sem conexão:** o embarque fica guardado no celular com a marca "Sincronizando..." e é enviado quando a conexão voltar. Se não enviar sozinho, toque em **Sincronizar**. Para isso, a viagem precisa ter sido iniciada com internet (a lista de passageiros ainda não fica salva no aparelho).
- **Atualização de Posição**: Na tela de checklist, o motorista clica nos botões dos pontos da rota (ex: Rodoviária) conforme passa por eles, informando os alunos em tempo real.

**Fluxo rápido de teste:**
1. Acesse `http://127.0.0.1:5000/motorista`
2. Digite a senha admin: `vem-admin-2026`
3. Selecione a data e o trecho (IDA/VOLTA)
4. Confirme o embarque clicando nos nomes

---

## 🚌 Frota de Veículos Disponíveis

| Código     | Tipo    | Capacidade (assentos) |
|:-----------|:--------|:----------------------|
| ONIBUS-01  | Ônibus  | 44                    |
| ONIBUS-02  | Ônibus  | 44                    |
| MICRO-01   | Micro   | 28                    |
| VAN-01     | Van     | 15                    |

---

## ⚙️ Regras Importantes

| Regra                    | Descrição                                                                                       |
|:-------------------------|:------------------------------------------------------------------------------------------------|
| **Hard Lock (14h)**      | Não é possível reservar para o dia atual após as 14h. Planeje com antecedência!                  |
| **Vaga de Exceção**      | Alunos de locais distantes têm assento garantido — seus lugares são descontados antes da fila.   |
| **Ordem de Chegada**     | O embarque de volta é por ordem de chegada física na porta do veículo, não por reserva de lugar. |
| **Uma reserva por dia**  | Cada aluno pode ter apenas uma reserva ativa por dia (ida, volta ou ambos).                     |
| **Bloqueio de login**    | Após 5 PINs errados seguidos, o CPF fica bloqueado por 5 minutos (proteção contra adivinhação).  |

---

## 🗂️ Estrutura de Arquivos (visão simplificada)

```
VEM-main/
├── app.py              ← Motor do sistema (Flask)
├── database.db         ← Banco de dados SQLite (criado automaticamente)
├── requirements.txt    ← Dependências Python
├── static/
│   ├── index.html      ← Tela do Aluno (PWA)
│   ├── gestora.html    ← Painel da Gestora
│   ├── motorista.html  ← Checklist do Motorista
│   ├── manifest.json   ← Configuração PWA
│   └── sw.js           ← Service Worker (cache offline)
├── tests/              ← Testes automáticos (python -m unittest discover tests)
└── docs/               ← Documentação do projeto
    ├── vibes/          ← Registro das sessões de desenvolvimento (VCC)
    └── sugestoes/      ← Ideias de melhoria ainda não implementadas
```

---

## 📝 Histórico de Atualizações

> **Instrução para agentes de IA:** Sempre que uma funcionalidade nova for adicionada, uma tela for modificada, credenciais de teste forem alteradas, ou veículos forem adicionados/removidos, **esta seção deve ser atualizada** com a data e a descrição da mudança.

| Data       | O que mudou                                                  |
|:-----------|:-------------------------------------------------------------|
| 2026-06-10 | Criação do documento com o estado inicial do MVP funcional.   |
| 2026-06-17 | Adicionado Mural de Avisos e Rastreamento de Status de Viagem. |
| 2026-10-28 | Corrigida a sugestão de frota do Painel da Gestora: agora escolhe a combinação com menos assentos vazios, respeitando os veículos ativos (antes, 3 alunos geravam 1 ônibus). Criada a pasta `tests/` (rodar com `python -m unittest discover tests`) e a pasta `docs/sugestoes/` com o backlog de melhorias. |
| 2026-10-28 | Segurança do login: PIN agora é salvo com hash PBKDF2 + salt (alunos antigos são migrados automaticamente no próximo login; credenciais de teste não mudaram). Novo bloqueio de 5 min após 5 PINs errados. Suíte de testes ampliada para 37 testes (login, hard lock, reservas, check-in). |
| 2026-10-28 | Corrigido o PWA: novas rotas `/sw.js` e `/manifest.json` (antes davam 404, o app não podia ser instalado nem funcionar offline). Corrigida a perda de embarques no modo offline do motorista e a contagem dobrada de lotação sem conexão. 42 testes. |

---

## ❓ Problemas Comuns

| Problema                             | Solução                                                                        |
|:-------------------------------------|:-------------------------------------------------------------------------------|
| "Erro de conexão" no login           | Verifique se o servidor está rodando (`python app.py`)                         |
| CPF não aceito                       | Use apenas os 11 dígitos numéricos (sem pontos ou traços)                      |
| "Muitas tentativas incorretas"       | O CPF errou o PIN 5 vezes. Aguarde 5 minutos (ou reinicie o servidor em ambiente de teste) |
| Não consigo reservar para hoje       | O horário de corte é 14h — após esse horário, reservas do dia são bloqueadas   |
| Tela da gestora não carrega dados    | Certifique-se de usar a senha admin correta: `vem-admin-2026`                  |
| O banco está vazio                   | Delete o `database.db` e reinicie o servidor — os dados de teste serão recriados |

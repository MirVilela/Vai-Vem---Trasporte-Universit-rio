"""
Verificacao funcional da API contra uma COPIA temporaria do database.db.
Executar na raiz do projeto: python tests/e2e/verifica_api.py
Cada caso traz o item do backlog (docs/PLANO_CORRECAO_AGENTES.md). Sai com codigo 1 se houver FALHA.
"""
import json
import logging
import os
import shutil
import sys
import tempfile
from datetime import date, timedelta

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAIZ)
sys.stdout.reconfigure(encoding="utf-8")
import app  # noqa: E402

pasta = tempfile.mkdtemp(prefix="vem_api_")
app.DB_PATH = os.path.join(pasta, "copia.db")
if os.path.exists(os.path.join(RAIZ, "database.db")):  # clone novo ainda nao tem banco
    shutil.copy(os.path.join(RAIZ, "database.db"), app.DB_PATH)
logging.getLogger("VEM").setLevel(logging.CRITICAL)
app.init_db()
app.app.logger.disabled = True
app.app.config["PROPAGATE_EXCEPTIONS"] = False

c = app.app.test_client()
H = {"X-Admin-Token": app.ADMIN_TOKEN}
hoje = date.today()
D = (hoje + timedelta(days=7 - hoje.weekday())).isoformat()  # proxima segunda
JOAO, MARIA, CARLOS = "12345678901", "98765432100", "11122233344"
PINS = {JOAO: "1234", MARIA: "5678", CARLOS: "0000"}
falhas = []


def r(metodo, url, corpo=None, h=None):
    resp = c.open(url, method=metodo, json=corpo, headers=h or {})
    return resp.status_code, resp.get_json(silent=True)


def h_aluno(cpf):
    """Login real; se a API devolver token (S13), envia como Bearer."""
    _, j = r("POST", "/api/login", {"cpf": cpf, "pin": PINS[cpf]})
    token = (j or {}).get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def reservar(cpf, itens):
    return r("POST", "/api/reservar", {"cpf": cpf, "reservas": itens}, h_aluno(cpf))


def semana(cpf):
    return json.dumps(r("GET", f"/api/semana?cpf={cpf}", None, h_aluno(cpf))[1])


def caso(tag, nome, cond, det=""):
    print(f"{'OK   ' if cond else 'FALHA'} [{tag}] {nome}" + (f"  -> {det}" if det != "" else ""))
    if not cond:
        falhas.append(tag)


print("== Cadastros da gestora ==")
s, _ = r("POST", "/api/veiculos", {"id": "VAN-T", "nome": "Teste", "tipo": "VAN", "capacidade": 12}, H)
caso("BASE", "criar veiculo", s == 201, s)
s, _ = r("PUT", "/api/veiculos/VAN-T", {"capacidade": 13, "nome": "T2", "tipo": "VAN", "ativo": 1}, H)
caso("BASE", "editar veiculo", s == 200, s)
s, _ = r("DELETE", "/api/veiculos/VAN-T", None, H)
caso("BASE", "remover veiculo", s == 200, s)
s, _ = r("POST", "/api/passageiros", {"cpf": "55566677788", "nome": "Novo", "rota": "Cidade A -> Campus", "pin": "4321"}, H)
caso("BASE", "cadastrar aluno", s == 201, s)
s, _ = r("POST", "/api/login", {"cpf": "55566677788", "pin": "4321"})
caso("BASE", "aluno novo faz login", s == 200, s)
s, _ = r("DELETE", "/api/passageiros/55566677788", None, H)
caso("BASE", "remover aluno", s == 200, s)
s, _ = r("POST", "/api/login", {"cpf": "55566677788", "pin": "4321"})
caso("BASE", "aluno removido nao entra", s == 401, s)
s, j = r("POST", "/api/avisos", {"titulo": "Teste", "mensagem": "Msg", "tipo": "URGENTE"}, H)
caso("BASE", "publicar aviso", s == 201, s)
s2, j2 = r("GET", "/api/avisos")
caso("BASE", "aluno ve o aviso", "Teste" in json.dumps(j2))
s, j = r("POST", "/api/rotas", {"nome": "Rota Teste"}, H)
caso("BASE", "criar rota", s == 201, s)
s, _ = r("POST", "/api/pontos-rota", {"rota_id": (j or {}).get("id"), "nome": "P1", "ordem": 1}, H)
caso("BASE", "criar ponto", s == 201, s)
s, _ = r("PUT", "/api/configuracoes", {"horario_corte": "15:30"}, H)
_, j2 = r("GET", "/api/configuracoes", None, H)
caso("BASE", "alterar horario de corte", s == 200 and "15:30" in json.dumps(j2), s)
r("PUT", "/api/configuracoes", {"horario_corte": "14:00"}, H)
s, _ = r("GET", "/api/relatorios/viagens?data_inicio=2020-01-01&data_fim=2030-01-01", None, H)
caso("BASE", "relatorio CSV", s == 200, s)

print("\n== Reserva ==")
s, j = reservar(JOAO, [{"data": D, "ida": 1, "volta": 1}])
caso("BASE", "reservar ida e volta", s == 200 and j["total_registradas"] == 1, D)
caso("BASE", "aluno ve a reserva", D in semana(JOAO))
_, j = r("GET", "/api/painel", None, H)
dia = next((d for d in j["resumo_diario"] if d["data"] == D), {})
caso("BASE", "painel conta o aluno", dia.get("total_ida") == 1)
reservar(JOAO, [{"data": D, "ida": 0, "volta": 0}])
caso("S12", "ida=0 e volta=0 cancelam a reserva", D not in semana(JOAO))
_, j = r("GET", "/api/painel", None, H)
dia = next((d for d in j["resumo_diario"] if d["data"] == D), {})
caso("S12", "reserva cancelada sai do painel", not dia.get("total_ida"), dia.get("total_ida"))

print("\n== Rastreamento ==")
s, j = r("PUT", "/api/status-viagem", {"veiculo_id": "VAN-01", "data": D, "tipo": "IDA", "ponto_id": "PR-CIDADEA-2"}, H)
caso("BASE", "marcar ponto", s == 200 and j["status"] == "EM_ROTA", s)
_, j = r("GET", f"/api/status-viagem/{D}")
caso("BASE", "aluno ve a posicao", "Rodoviaria" in json.dumps(j))
s, j = r("PUT", "/api/status-viagem", {"veiculo_id": "VAN-01", "data": D, "tipo": "IDA", "ponto_id": "PR-CIDADEA-4"}, H)
caso("S16", "chegada ao campus finaliza a viagem", s == 200 and j["status"] == "FINALIZADA", (j or {}).get("status"))

print("\n== Embarque ==")
s, j = r("POST", "/api/checkin", {"cpf": CARLOS, "veiculo_id": "VAN-01", "data": D, "tipo": "IDA"}, H)
caso("S14-D3", "check-in de quem nao reservou e rejeitado (depende da Decisao 3)", s >= 400, s)
reservar(MARIA, [{"data": D, "ida": 1, "volta": 0}])
s1, _ = r("POST", "/api/checkin", {"cpf": MARIA, "veiculo_id": "VAN-01", "data": D, "tipo": "IDA"}, H)
s2, _ = r("POST", "/api/checkin", {"cpf": MARIA, "veiculo_id": "MICRO-01", "data": D, "tipo": "IDA"}, H)
caso("BASE", "check-in de quem reservou", s1 == 200, s1)
caso("S14", "mesmo aluno em 2 veiculos e rejeitado", s2 >= 400, s2)
s, _ = r("POST", "/api/checkin", {"cpf": MARIA, "veiculo_id": "VAN-01", "data": D, "tipo": "XPTO"}, H)
caso("S14", "tipo de viagem invalido e rejeitado", s >= 400, s)
s, _ = r("POST", "/api/checkin", {"cpf": "00000000000", "veiculo_id": "VAN-01", "data": D, "tipo": "IDA"}, H)
caso("BASE", "CPF inexistente nao causa erro 500", s < 500, s)

print("\n== Dados invalidos ==")
s, _ = reservar(JOAO, [{"data": D, "ida": "abc", "volta": 0}])
caso("S09", "ida nao numerica nao causa erro 500", s < 500, s)
s, _ = reservar(JOAO, "texto")
caso("S09", "reservas que nao e lista nao causa erro 500", s < 500, s)
reservar(JOAO, [{"data": "2099-13-45", "ida": 1, "volta": 0}])
caso("S09", "data invalida nao e gravada", "2099-13-45" not in semana(JOAO))
s, _ = r("POST", "/api/veiculos", {"id": "ZERO-2", "nome": "Z", "tipo": "VAN", "capacidade": -3}, H)
s2, _ = r("GET", "/api/painel", None, H)
caso("BASE", "capacidade negativa e rejeitada e o painel segue no ar", s == 400 and s2 == 200, f"{s}, {s2}")
s, _ = r("DELETE", "/api/rotas/ROTA-CIDADEA", None, H)
caso("BASE", "rota com pontos nao e removida", s == 409, s)

print("\n== Acesso ==")
for u in ["/api/painel", "/api/veiculos", "/api/passageiros", f"/api/checklist/{D}", "/api/configuracoes"]:
    s, _ = r("GET", u)
    caso("BASE", f"{u} exige token de admin", s == 403, s)
s, _ = r("POST", "/api/reservar", {"cpf": CARLOS, "reservas": [{"data": D, "ida": 1, "volta": 0}]})
caso("S13", "reservar sem login e rejeitado", s == 401, s)
s, _ = r("GET", f"/api/semana?cpf={CARLOS}")
caso("S13", "ler agenda sem login e rejeitado", s == 401, s)
s, _ = r("GET", f"/api/semana?cpf={CARLOS}", None, h_aluno(JOAO))
caso("S13", "login de um aluno nao le a agenda de outro", s in (401, 403), s)

shutil.rmtree(pasta, ignore_errors=True)
print(f"\nRESULTADO API: {len(falhas)} falha(s). Itens: {', '.join(sorted(set(falhas))) or 'nenhum'}")
sys.exit(1 if falhas else 0)

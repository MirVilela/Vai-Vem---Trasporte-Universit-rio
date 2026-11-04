// Verificacao das telas em Chrome headless (largura de celular), sem bibliotecas externas.
// Requer Node 22+ e Chrome ou Edge. Navegador em outro caminho: variavel CHROME_PATH.
// Executar na raiz do projeto: node tests/e2e/verifica_telas.mjs
// Usa uma COPIA temporaria do database.db. Sai com codigo 1 se houver FALHA.
import { spawn } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const AQUI = dirname(fileURLToPath(import.meta.url));
const RAIZ = resolve(AQUI, "..", "..");
const PORTA_APP = 5055, PORTA_CDP = 9335;
const BASE = `http://127.0.0.1:${PORTA_APP}`;
const ADMIN = "vem-admin-2026";
const pasta = mkdtempSync(join(tmpdir(), "vem_telas_"));
const CAPTURAS = join(pasta, "capturas");
mkdirSync(CAPTURAS);
const COPIA = join(pasta, "copia.db");
copyFileSync(join(RAIZ, "database.db"), COPIA);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const navegador = [process.env.CHROME_PATH,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  "/usr/bin/google-chrome"].find((p) => p && existsSync(p));
if (!navegador) { console.error("Navegador nao encontrado. Defina CHROME_PATH."); process.exit(2); }

let servidor;
const subirServidor = async () => {
  servidor = spawn("python", [join(AQUI, "servidor_teste.py"), COPIA, String(PORTA_APP)], { stdio: "ignore" });
  for (let i = 0; i < 60; i++) { try { await fetch(`${BASE}/api/server-time`); return; } catch { await sleep(250); } }
  throw new Error("Servidor de teste nao subiu");
};
const derrubarServidor = async () => { servidor.kill(); await sleep(1000); };

await subirServidor();
const chrome = spawn(navegador, ["--headless=new", `--remote-debugging-port=${PORTA_CDP}`,
  `--user-data-dir=${join(pasta, "perfil")}`, "--no-first-run", "--no-default-browser-check", "about:blank"]);
let pronto = false;
for (let i = 0; i < 60 && !pronto; i++) { try { await fetch(`http://127.0.0.1:${PORTA_CDP}/json/version`); pronto = true; } catch { await sleep(250); } }
const alvo = await (await fetch(`http://127.0.0.1:${PORTA_CDP}/json/new?about:blank`, { method: "PUT" })).json();
const ws = new WebSocket(alvo.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r));

let seq = 0, etapa = "", envios = 0;
const pend = new Map(), excecoes = [], alertas = [], falhas = [];
ws.addEventListener("message", (m) => {
  const msg = JSON.parse(m.data);
  if (msg.id && pend.has(msg.id)) { pend.get(msg.id)(msg); pend.delete(msg.id); return; }
  const p = msg.params || {};
  if (msg.method === "Page.javascriptDialogOpening") {
    alertas.push(`[${etapa}] ${p.message}`);
    ws.send(JSON.stringify({ id: ++seq, method: "Page.handleJavaScriptDialog", params: { accept: true } }));
  } else if (msg.method === "Runtime.exceptionThrown") {
    const d = p.exceptionDetails;
    excecoes.push(`[${etapa}] ${d.text} ${d.exception?.description?.split("\n")[0] || ""}`);
  } else if (msg.method === "Network.requestWillBeSent" && p.request.url.endsWith("/api/checkin")) envios++;
});
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pend.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const ev = async (expr) => {
  const r = await send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true });
  if (r.result?.exceptionDetails) return "ERRO_JS: " + (r.result.exceptionDetails.exception?.description || "").split("\n")[0];
  return r.result?.result?.value;
};
const ir = async (url) => { await send("Page.navigate", { url }); await sleep(2000); };
const foto = async (nome) => {
  const r = await send("Page.captureScreenshot", { format: "png" });
  writeFileSync(join(CAPTURAS, nome + ".png"), Buffer.from(r.result.data, "base64"));
};
const caso = (tag, nome, cond, det = "") => {
  console.log(`${cond ? "OK   " : "FALHA"} [${tag}] ${nome}${det !== "" ? "  -> " + det : ""}`);
  if (!cond) falhas.push(tag);
};
const pulado = (tag, nome, motivo) => console.log(`PULOU [${tag}] ${nome}  -> ${motivo}`);
const set = (id, v) => `document.getElementById('${id}').value=${JSON.stringify(v)};`;
const texto = (id) => ev(`(document.getElementById('${id}')?.innerText||'').replace(/\\s+/g,' ').trim().slice(0,260)`);
const semEstouro = () => ev(`document.documentElement.scrollWidth <= window.innerWidth`);
const adminApi = async (metodo, caminho, corpo) => {
  const r = await fetch(BASE + caminho, { method: metodo, headers: { "Content-Type": "application/json", "X-Admin-Token": ADMIN }, body: corpo ? JSON.stringify(corpo) : undefined });
  return r.json();
};
const naLista = async (data, tipo, nome) => (await adminApi("GET", `/api/checklist/${data}?tipo=${tipo}`)).passageiros.some((p) => p.nome === nome);
const entrar = async (cpf, pin) => {
  await ev(`document.getElementById('input-cpf').value='${cpf}'; document.getElementById('input-cpf').dispatchEvent(new Event('input',{bubbles:true}));
    document.getElementById('input-pin').value='${pin}'; document.getElementById('input-pin').dispatchEvent(new Event('input',{bubbles:true}));
    document.getElementById('form-login').requestSubmit(); 'ok'`);
  await sleep(1500);
};
const reservarApi = async (cpf, pin, data) => {
  const login = await (await fetch(`${BASE}/api/login`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ cpf, pin }) })).json();
  const h = { "Content-Type": "application/json" };
  if (login.token) h.Authorization = `Bearer ${login.token}`;
  await fetch(`${BASE}/api/reservar`, { method: "POST", headers: h, body: JSON.stringify({ cpf, reservas: [{ data, ida: 1, volta: 0 }] }) });
};

for (const d of ["Page", "Runtime", "Network"]) await send(`${d}.enable`);
await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
await send("Emulation.setTimezoneOverride", { timezoneId: "America/Sao_Paulo" });
const horaServidor = (await (await fetch(`${BASE}/api/server-time`)).json()).local; // 2026-11-04T14:21:05...
const HOJE = horaServidor.slice(0, 10), HORA = Number(horaServidor.slice(11, 13));
const proxSegunda = (() => { const d = new Date(HOJE + "T12:00:00"); d.setDate(d.getDate() + ((8 - d.getDay()) % 7 || 7)); return d.toISOString().slice(0, 10); })();

// ── GESTORA ──
console.log("== Gestora ==");
etapa = "gestora";
await ir(`${BASE}/gestora`);
await ev(`${set("admin-token", "errado")} tentarLogin(); 'ok'`); await sleep(1200);
caso("BASE", "chave errada mostra erro", await ev(`getComputedStyle(document.getElementById('login-error')).display !== 'none'`));
await ev(`${set("admin-token", ADMIN)} tentarLogin(); 'ok'`); await sleep(2000);
await foto("gestora-painel");
caso("BASE", "painel abre", await ev(`getComputedStyle(document.getElementById('app-layout')).display !== 'none'`));
caso("BASE", "painel sem rolagem lateral no celular", await semEstouro());
await ev(`navigateTo('veiculos'); 'ok'`); await sleep(1000);
await ev(`${set("v-id", "VAN-02")}${set("v-nome", "Van Dois")}${set("v-capacidade", "12")} adicionarVeiculo(); 'ok'`); await sleep(1000);
caso("BASE", "formulario cadastra veiculo", await ev(`document.getElementById('veiculos-table-body').innerText.includes('VAN-02')`));
await ev(`navigateTo('passageiros'); 'ok'`); await sleep(1000);
await ev(`const r=document.getElementById('p-rota'); if(r.tagName==='SELECT'){r.selectedIndex=r.options.length>1?1:0}else{r.value='Cidade A -> Campus'}
  ${set("p-cpf", "555.666.777-88")}${set("p-nome", "Aluna Nova")}${set("p-pin", "4321")} cadastrarPassageiro(); 'ok'`); await sleep(1200);
caso("BASE", "formulario cadastra aluno", await ev(`document.getElementById('passageiros-table-body').innerText.includes('Aluna Nova')`));
await ev(`navigateTo('avisos'); 'ok'`); await sleep(1000);
await ev(`${set("av-titulo", "Ponte interditada")}${set("av-mensagem", "Saida 15 min antes.")} document.getElementById('av-tipo').selectedIndex=1; criarAviso(); 'ok'`); await sleep(1200);

// ── ALUNO ──
console.log("\n== Aluno ==");
etapa = "aluno";
await ir(`${BASE}/`);
await entrar("11122233344", "9999");
caso("BASE", "PIN errado mostra mensagem", (await texto("cpf-error")).includes("incorretos"));
for (let i = 0; i < 4; i++) await entrar("11122233344", "9999");
await entrar("11122233344", "0000");
caso("BASE", "6a tentativa bloqueada mesmo com PIN certo", (await texto("cpf-error")).includes("Muitas tentativas"));
await ir(`${BASE}/`);
await entrar("55566677788", "4321"); await sleep(1000);
caso("BASE", "aluna cadastrada entra", (await texto("user-name-dash")).includes("Aluna"));
const avisoTela = await texto("avisos-container");
caso("BASE", "aviso aparece para o aluno", avisoTela.includes("Ponte interditada"));
caso("S15", "aviso mostra a hora de Brasilia", avisoTela.includes(`${String(HORA).padStart(2, "0")}:`), avisoTela.slice(-12));
caso("BASE", "aluno sem rolagem lateral", await semEstouro());
await foto("aluno-inicio");
caso("BASE", "service worker registrado", (await ev(`navigator.serviceWorker.getRegistrations().then(r => r.length)`)) >= 1);
await ev(`document.querySelector('.nav-btn[data-target=screen-calendar]').click(); 'ok'`); await sleep(1200);
await foto("aluno-calendario");
const dias = String(await ev(`[...new Set([...document.querySelectorAll('.toggle-btn')].filter(b=>!b.disabled).map(b=>b.dataset.date))].join(',')`)).split(",").filter(Boolean);
caso("BASE", "botoes de ida/volta com 48px ou mais", dias.length === 0 || (await ev(`Math.min(...[...document.querySelectorAll('.toggle-btn')].map(b=>b.getBoundingClientRect().height))`)) >= 48);
const clicar = (d, dir) => ev(`document.querySelector('.toggle-btn[data-date="${d}"][data-direction="${dir}"]').click(); 'ok'`);
if (dias.length >= 2) {
  const [d1, d2] = dias;
  await clicar(d1, "ida"); await clicar(d1, "volta"); await clicar(d2, "ida"); await sleep(300);
  await ev(`document.getElementById('btn-confirmar').click(); 'ok'`); await sleep(2000);
  caso("BASE", "confirmacao aparece", (await texto("success-summary")).includes("Ida e Volta"));
  caso("BASE", "reserva chega ao servidor", (await naLista(d1, "IDA", "Aluna Nova")) && (await naLista(d2, "IDA", "Aluna Nova")));
  await ev(`document.getElementById('btn-alterar').click(); 'ok'`); await sleep(1200);
  await clicar(d2, "ida"); await sleep(300);
  await ev(`document.getElementById('btn-confirmar').click(); 'ok'`); await sleep(2000);
  caso("S12", "dia desmarcado sai do servidor, como a tela confirma", !(await naLista(d2, "IDA", "Aluna Nova")), d2);
  caso("BASE", "dia mantido continua reservado", await naLista(d1, "IDA", "Aluna Nova"));
} else pulado("S12", "reservar e desmarcar pela tela", `apenas ${dias.length} dia(s) liberado(s) nesta semana; rode em outro dia`);

// Calendario deve obedecer ao horario de corte configurado
etapa = "aluno:corte";
const fimDeSemana = [0, 6].includes(new Date(HOJE + "T12:00:00").getDay());
if (fimDeSemana) pulado("S18", "calendario obedece ao corte configurado", "hoje nao aparece no calendario");
else {
  const corte = HORA >= 14 ? "23:59" : "00:00";
  await adminApi("PUT", "/api/configuracoes", { horario_corte: corte });
  await ir(`${BASE}/`);
  await entrar("55566677788", "4321");
  await ev(`document.querySelector('.nav-btn[data-target=screen-calendar]').click(); 'ok'`); await sleep(1200);
  const hojeAberto = await ev(`!!document.querySelector('.toggle-btn[data-date="${HOJE}"]')`);
  caso("S18", `com corte ${corte}, hoje fica ${corte === "23:59" ? "aberto" : "encerrado"}`, hojeAberto === (corte === "23:59"), `aberto=${hojeAberto}`);
  await adminApi("PUT", "/api/configuracoes", { horario_corte: "14:00" });
}

// ── MOTORISTA ──
console.log("\n== Motorista ==");
etapa = "motorista";
await reservarApi("98765432100", "5678", proxSegunda);
await reservarApi("12345678901", "1234", proxSegunda);
await ir(`${BASE}/motorista`); await sleep(1200);
await ev(`${set("login-token", ADMIN)} tentarLogin(); 'ok'`); await sleep(2000);
const rotas = await ev(`[...document.getElementById('setup-rota').options].map(o=>o.value+'|'+o.textContent).join(', ')`);
caso("S11", "seletor de rota sem 'undefined'", !String(rotas).includes("undefined"), rotas);
await ev(`${set("setup-date", proxSegunda)}${set("setup-type", "IDA")}${set("setup-vehicle", "VAN-02")}
  const r=document.getElementById('setup-rota'); r.selectedIndex=r.options.length>1?1:0; iniciarViagem(); 'ok'`);
await sleep(2000);
caso("BASE", "lista mostra os passageiros", (await texto("passenger-list")).includes("Maria"));
caso("BASE", "ocupacao mostra a capacidade do veiculo", await texto("capacity-count") === "0 / 12", await texto("capacity-count"));
caso("BASE", "motorista sem rolagem lateral", await semEstouro());
caso("BASE", "botao de check-in com 48px ou mais", (await ev(`document.querySelector('.checkin-btn').getBoundingClientRect().height`)) >= 48);
const qtdPontos = await ev(`document.getElementById('tracking-points').querySelectorAll('button').length`);
caso("S11", "botoes de ponto da rota aparecem", qtdPontos > 0, qtdPontos);
await foto("motorista-lista");
if (qtdPontos > 0) {
  await ev(`document.getElementById('tracking-points').querySelector('button').click(); 'ok'`); await sleep(1500);
  const st = await (await fetch(`${BASE}/api/status-viagem/${proxSegunda}?tipo=IDA`)).json();
  caso("S11", "toque no ponto atualiza a posicao no servidor", st.viagens?.some((v) => v.veiculo_id === "VAN-02"));
}

// Modo aviao: navegador sabe que esta offline
etapa = "motorista:modo-aviao";
await send("Network.emulateNetworkConditions", { offline: true, latency: 0, downloadThroughput: -1, uploadThroughput: -1 });
await sleep(800);
await ev(`document.querySelectorAll('.checkin-btn')[0].click(); 'ok'`); await sleep(1200);
caso("BASE", "modo aviao: check-in fica na fila", (await ev(`JSON.parse(localStorage.getItem('checkinQueue')||'[]').length`)) === 1);
caso("BASE", "modo aviao: ocupacao conta 1", await texto("capacity-count") === "1 / 12", await texto("capacity-count"));
await send("Network.emulateNetworkConditions", { offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1 });
await sleep(2500);
caso("BASE", "rede volta: fila e enviada sozinha", !(await ev(`localStorage.getItem('checkinQueue')`)));
const checados = async () => (await adminApi("GET", `/api/checklist/${proxSegunda}?tipo=IDA`)).passageiros.filter((p) => p.checkin).length;
caso("BASE", "rede volta: check-in gravado no servidor", (await checados()) === 1);

// Sinal fraco: celular "online", servidor inacessivel
etapa = "motorista:servidor-fora";
await derrubarServidor();
envios = 0;
const antes = await ev(`document.querySelectorAll('.passenger-item:not(.confirmed) .checkin-btn').length`);
await ev(`document.querySelector('.passenger-item:not(.confirmed) .checkin-btn').click(); 'ok'`); await sleep(3000);
caso("BASE", "servidor fora: check-in permanece na fila", (await ev(`JSON.parse(localStorage.getItem('checkinQueue')||'[]').length`)) === 1, `pendentes antes: ${antes}`);
caso("BASE", "servidor fora: sem reenvio em loop", envios <= 4, `${envios} envios`);
await foto("motorista-servidor-fora");
await ir(`${BASE}/motorista`);
caso("BASE", "servidor fora: pagina abre pelo cache", await ev(`!!document.getElementById('screen-setup')`));
const veiculosOff = await ev(`document.getElementById('setup-vehicle').options.length`);
caso("S10", "servidor fora: app recem-aberto lista os veiculos", veiculosOff > 0, veiculosOff);
await subirServidor();
await ir(`${BASE}/motorista`); await sleep(1500);
await ev(`${set("setup-date", proxSegunda)}${set("setup-type", "IDA")}${set("setup-vehicle", "VAN-02")} iniciarViagem(); 'ok'`); await sleep(1500);
await ev(`sincronizarFila(); 'ok'`); await sleep(2500);
caso("BASE", "servidor volta: fila sincroniza", (await checados()) === 2, `${await checados()} gravados`);

// Aluno ve a posicao marcada hoje
etapa = "aluno:rastreamento";
for (const tipo of ["IDA", "VOLTA"]) await adminApi("PUT", "/api/status-viagem", { veiculo_id: "VAN-02", data: HOJE, tipo, ponto_id: "PR-CIDADEA-2" });
await ir(`${BASE}/`);
await entrar("55566677788", "4321"); await sleep(1500);
caso("BASE", "aluno ve a posicao do veiculo", (await texto("tracking-container")).includes("Rodoviaria"));
await foto("aluno-rastreamento");

console.log("\nAlertas exibidos:", alertas.length ? alertas : "(nenhum)");
console.log("Excecoes de JavaScript:", excecoes.length ? excecoes : "(nenhuma)");
console.log("Capturas de tela:", CAPTURAS);
console.log(`\nRESULTADO TELAS: ${falhas.length} falha(s). Itens: ${[...new Set(falhas)].sort().join(", ") || "nenhum"}`);
ws.close(); chrome.kill(); servidor.kill();
process.exit(falhas.length ? 1 : 0);

import { CONFIG, bildPfad, befundText } from './config.js';
import { RemoteLink, getRoom, lastRoom, normalizeRoom } from './remote.js';

const $ = (id) => document.getElementById(id);
const TIERE = CONFIG.tiere;
const DIAGNOSEN = CONFIG.diagnosen;
const SCANNER_TEXT = {
  idle: 'Scanner bereit',
  warmup: 'Gerät fährt hoch …',
  exposing: 'Aufnahme läuft …',
  result: 'Scanner zeigt Befund',
};

const params = new URLSearchParams(location.search);
const room = params.has('neu') ? '' : getRoom({ create: false });

if (!room) showJoin();
else showController(room);

function showJoin() {
  $('join').hidden = false;
  $('joinInput').value = lastRoom();
  $('joinForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const code = normalizeRoom($('joinInput').value);
    if (code) location.href = `steuerung.html?raum=${code}`;
  });
}

function makeButton(className, emoji, label, num) {
  const btn = document.createElement('button');
  btn.className = className;
  btn.setAttribute('aria-pressed', 'false');
  if (num) {
    const n = document.createElement('span');
    n.className = 'num';
    n.textContent = num;
    btn.append(n);
  }
  const icon = document.createElement('span');
  icon.className = 'icon';
  icon.textContent = emoji;
  const name = document.createElement('span');
  name.className = 'name';
  name.textContent = label;
  btn.append(icon, name);
  return btn;
}

function showController(room) {
  $('app').hidden = false;
  $('room').textContent = room;
  const remote = new RemoteLink(room, 'controller');
  let tier = TIERE[0];
  let diagnose = DIAGNOSEN[0];

  const tierButtons = TIERE.map((t, i) => {
    const btn = makeButton('choice animal', t.emoji, t.name, String(i + 1));
    btn.addEventListener('click', () => choose(t, diagnose));
    $('animals').append(btn);
    return btn;
  });
  const diagButtons = DIAGNOSEN.map((d) => {
    const btn = makeButton('choice diagnosis', d.emoji, d.name);
    btn.addEventListener('click', () => choose(tier, d));
    $('diagnoses').append(btn);
    return btn;
  });

  function render() {
    TIERE.forEach((t, i) => tierButtons[i].setAttribute('aria-pressed', String(t === tier)));
    DIAGNOSEN.forEach((d, i) => diagButtons[i].setAttribute('aria-pressed', String(d === diagnose)));
    $('previewImg').src = bildPfad(tier, diagnose);
    $('previewTitle').textContent = `${tier.emoji} ${tier.name} · ${diagnose.name}`;
    $('previewText').textContent = befundText(tier, diagnose);
  }

  function choose(t, d) {
    tier = t;
    diagnose = d;
    render();
    navigator.vibrate?.(15);
    remote.send('select', { tier: t.id, diagnose: d.id }, { retain: true });
  }

  $('scanBtn').addEventListener('click', () => {
    navigator.vibrate?.(30);
    remote.send('cmd', { action: 'scan' });
  });
  $('resetBtn').addEventListener('click', () => remote.send('cmd', { action: 'reset' }));

  remote.addEventListener('connection', (e) => {
    const { connected, error } = e.detail;
    $('connDot').className = `dot ${connected ? 'ok' : 'bad'}`;
    $('connText').textContent = connected ? 'Verbunden' : error ? 'Fehler' : 'Getrennt …';
    if (error) $('scannerText').textContent = error;
  });

  remote.addEventListener('select', (e) => {
    const t = TIERE.find((x) => x.id === e.detail.tier);
    const d = DIAGNOSEN.find((x) => x.id === e.detail.diagnose);
    if (!t || !d) return;
    tier = t;
    diagnose = d;
    render();
  });

  remote.addEventListener('status', (e) => {
    const { online, state } = e.detail;
    const t = TIERE.find((x) => x.id === e.detail.tier);
    const d = DIAGNOSEN.find((x) => x.id === e.detail.diagnose);
    const busy = state === 'warmup' || state === 'exposing';
    $('scannerDot').className = `dot ${!online ? 'bad' : busy ? 'warn' : 'ok'}`;
    $('scannerText').textContent = online
      ? `${SCANNER_TEXT[state] || 'Scanner online'}${t && d ? ` · ${t.emoji} ${t.name}, ${d.name}` : ''}`
      : 'Scanner offline – ist die Seite dort geöffnet?';
    $('scanBtn').disabled = online && busy;
  });

  render();
  remote.connect();
}

import { CONFIG } from './config.js';
import { RemoteLink, getRoom, lastRoom, normalizeRoom } from './remote.js';

const $ = (id) => document.getElementById(id);
const IMAGES = CONFIG.bilder;
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

function showController(room) {
  $('app').hidden = false;
  $('room').textContent = room;
  const remote = new RemoteLink(room, 'controller');
  const buttons = new Map();

  IMAGES.forEach((entry, i) => {
    const btn = document.createElement('button');
    btn.className = 'animal';
    btn.setAttribute('aria-pressed', 'false');

    const num = document.createElement('span');
    num.className = 'num';
    num.textContent = String(i + 1);

    const thumb = document.createElement('span');
    thumb.className = 'thumb';
    thumb.textContent = entry.emoji;
    const img = new Image();
    img.alt = '';
    img.onload = () => {
      thumb.textContent = '';
      thumb.classList.add('has-img');
      thumb.append(img);
    };
    img.src = entry.datei;

    const name = document.createElement('span');
    name.className = 'name';
    name.textContent = entry.name;

    btn.append(num, thumb, name);
    btn.addEventListener('click', () => {
      markSelected(entry.id);
      navigator.vibrate?.(15);
      remote.send('select', { id: entry.id }, { retain: true });
    });
    $('grid').append(btn);
    buttons.set(entry.id, btn);
  });

  function markSelected(id) {
    for (const [key, btn] of buttons) btn.setAttribute('aria-pressed', String(key === id));
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
    if (buttons.has(e.detail.id)) markSelected(e.detail.id);
  });

  remote.addEventListener('status', (e) => {
    const { online, state, id } = e.detail;
    const entry = IMAGES.find((img) => img.id === id);
    $('scannerDot').className = `dot ${!online ? 'bad' : state === 'exposing' || state === 'warmup' ? 'warn' : 'ok'}`;
    $('scannerText').textContent = online
      ? `${SCANNER_TEXT[state] || 'Scanner online'}${entry ? ` · ${entry.emoji} ${entry.name}` : ''}`
      : 'Scanner offline – ist die Seite dort geöffnet?';
    $('scanBtn').disabled = online && (state === 'warmup' || state === 'exposing');
  });

  remote.connect();
}

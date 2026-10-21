import { CONFIG } from './config.js';
import { XraySound } from './sound.js';
import { RemoteLink, getRoom, controllerUrl, store } from './remote.js';
import { SerialLight } from './light.js';
import { placeholderDataUrl } from './placeholder.js';

const $ = (id) => document.getElementById(id);
const IMAGES = CONFIG.bilder;
const STATUS_TEXT = { idle: 'BEREIT', warmup: 'VORLAUF', exposing: 'AUFNAHME', result: 'BEFUND' };

const sound = new XraySound();
const light = new SerialLight();
const room = getRoom({ create: true });
const remote = new RemoteLink(room, 'scanner');

let state = 'idle';
let started = false;
let selected = Math.max(0, IMAGES.findIndex((img) => img.id === store.get('xray-auswahl')));
let patientNo = Number(store.get('xray-patient-nr')) || 1;
let scanToken = 0;
let resultTimer = 0;
let lastScanEnd = 0;
let animations = [];

// Resolve every image up front; missing files fall back to a generated placeholder
const sources = IMAGES.map((entry, i) => new Promise((resolve) => {
  const img = new Image();
  img.onload = () => resolve(entry.datei);
  img.onerror = () => resolve(placeholderDataUrl(entry, i));
  img.src = entry.datei;
}));

// ── State & rendering ───────────────────────────────────────

function setState(next) {
  state = next;
  document.body.dataset.state = next;
  publishStatus();
}

function publishStatus() {
  if (remote.connected) remote.send('status', { online: true, state, id: IMAGES[selected].id }, { retain: true });
}

function renderPatient() {
  const entry = IMAGES[selected];
  $('patientName').textContent = `${entry.emoji} ${entry.name}`;
  $('idleEmoji').textContent = entry.emoji;
  $('idleName').textContent = `${selected + 1} · ${entry.name}`;
}

function select(index, { publish = true } = {}) {
  if (!Number.isInteger(index) || index < 0 || index >= IMAGES.length) return;
  const changed = index !== selected;
  selected = index;
  store.set('xray-auswahl', IMAGES[index].id);
  renderPatient();
  if (changed) sound.blip();
  if (publish) remote.send('select', { id: IMAGES[index].id }, { retain: true });
  publishStatus();
}

// ── Scan sequence ───────────────────────────────────────────

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function scan() {
  if (state === 'warmup' || state === 'exposing') return;
  if (performance.now() - lastScanEnd < 1000) return; // ignore button mashing
  const token = ++scanToken;
  const index = selected;
  const entry = IMAGES[index];
  const warm = CONFIG.aufwaermDauer;
  const expose = CONFIG.scanDauer;
  const start = performance.now();

  clearTimeout(resultTimer);
  cancelAnimations();
  document.body.classList.remove('has-image');
  $('patientNo').textContent = `#${String(patientNo).padStart(4, '0')}`;
  store.set('xray-patient-nr', String(++patientNo));
  setState('warmup');
  sound.unlock();
  sound.playScan(warm / 1000, expose / 1000);
  runReadouts(token, start, warm, expose);

  const xray = $('xray');
  xray.src = await sources[index];
  try { await xray.decode(); } catch { /* shown anyway */ }
  await sleep(Math.max(0, start + warm - performance.now()));
  if (token !== scanToken) return;

  setState('exposing');
  light.set(true);
  xray.style.clipPath = 'inset(0 0 100% 0)';
  document.body.classList.add('has-image');
  const timing = { duration: expose, easing: 'linear', fill: 'forwards' };
  animations = [
    xray.animate([{ clipPath: 'inset(0 0 100% 0)' }, { clipPath: 'inset(0 0 0% 0)' }], timing),
    $('scanbar').animate([{ top: '0%' }, { top: '100%' }], timing),
    $('flash').animate([{ opacity: 0.45 }, { opacity: 0 }], { duration: 450, easing: 'ease-out' }),
  ];
  try { await animations[0].finished; } catch { return; } // cancelled by reset
  if (token !== scanToken) return;

  light.set(false);
  $('findingText').textContent = entry.befund;
  setState('result');
  lastScanEnd = performance.now();
  if (CONFIG.ergebnisAnzeigen > 0) resultTimer = setTimeout(reset, CONFIG.ergebnisAnzeigen);
}

function reset() {
  scanToken++;
  clearTimeout(resultTimer);
  cancelAnimations();
  sound.stop();
  light.set(false);
  document.body.classList.remove('has-image');
  $('kv').textContent = '0';
  $('ma').textContent = '0';
  $('exp').textContent = '0.00';
  $('meter').style.width = '0%';
  setState('idle');
}

function cancelAnimations() {
  animations.forEach((a) => a.cancel());
  animations = [];
}

function runReadouts(token, start, warm, expose) {
  const kvTarget = 60 + Math.round(Math.random() * 30);
  const maTarget = 160 + Math.round(Math.random() * 80);
  const tick = (now) => {
    if (token !== scanToken) return;
    const t = now - start;
    const pw = Math.min(1, t / warm);
    const pe = Math.min(1, Math.max(0, (t - warm) / expose));
    const exposing = t >= warm && pe < 1;
    const jitter = () => (exposing ? Math.round((Math.random() - 0.5) * 4) : 0);
    $('kv').textContent = String(Math.round(kvTarget * (1 - (1 - pw) ** 3)) + jitter());
    $('ma').textContent = String(exposing ? maTarget + jitter() : 0);
    $('exp').textContent = ((pe * expose) / 1000).toFixed(2);
    $('meter').style.width = `${((pw * warm + pe * expose) / (warm + expose)) * 100}%`;
    if (state === 'warmup' || state === 'exposing') requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

// ── Start overlay / settings ────────────────────────────────

const overlay = $('overlay');

function openOverlay() {
  overlay.hidden = false;
  $('startBtn').focus();
}

function closeOverlay() {
  overlay.hidden = true;
  if (!started) {
    started = true;
    sound.unlock();
    document.documentElement.requestFullscreen?.().catch(() => {});
    keepAwake();
  }
}

// Keep the screen from going to sleep; the lock is dropped whenever the tab is hidden
async function keepAwake() {
  try { await navigator.wakeLock?.request('screen'); } catch { /* not supported */ }
}
document.addEventListener('visibilitychange', () => {
  if (started && document.visibilityState === 'visible') keepAwake();
});

function renderQr() {
  const url = controllerUrl(room);
  $('roomCode').textContent = room;
  $('controlLink').href = url;
  if (window.qrcode) {
    const qr = window.qrcode(0, 'M');
    qr.addData(url);
    qr.make();
    $('qr').innerHTML = qr.createSvgTag({ cellSize: 6, margin: 0, scalable: true });
  } else {
    $('qr').textContent = 'QR-Code offline nicht verfügbar';
  }
}

// The light button only appears with ?licht=1 in the address
const lightEnabled = new URLSearchParams(location.search).has('licht');

function renderLight() {
  const btn = $('lightBtn');
  btn.hidden = !lightEnabled || !light.supported;
  btn.textContent = light.connected ? '💡 Licht verbunden' : '💡 Licht verbinden (optional)';
}

$('startBtn').addEventListener('click', closeOverlay);
$('lightBtn').addEventListener('click', () => light.choose().catch(() => {}));
light.addEventListener('change', renderLight);

// ── Input ───────────────────────────────────────────────────

let digits = '';
let digitTimer = 0;

function typeDigit(d) {
  digits += d;
  clearTimeout(digitTimer);
  const commit = () => {
    select(Number(digits) - 1);
    digits = '';
  };
  // Wait briefly for a second digit unless no longer number could exist
  if (Number(digits) * 10 > IMAGES.length) commit();
  else digitTimer = setTimeout(commit, 700);
}

document.addEventListener('keydown', (e) => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  const action = e.code === 'Space' || e.code === 'Enter' || e.code === 'NumpadEnter';

  if (!overlay.hidden) {
    if (e.target instanceof HTMLButtonElement && action) return; // let the button handle it
    if (action || e.code === 'KeyQ' || e.code === 'Escape') {
      e.preventDefault();
      closeOverlay();
    }
    return;
  }

  if (action) {
    e.preventDefault();
    if (!e.repeat) scan();
  } else if (/^(Digit|Numpad)\d$/.test(e.code)) {
    typeDigit(e.code.slice(-1));
  } else if (e.code === 'ArrowRight' || e.code === 'ArrowDown') {
    select((selected + 1) % IMAGES.length);
  } else if (e.code === 'ArrowLeft' || e.code === 'ArrowUp') {
    select((selected - 1 + IMAGES.length) % IMAGES.length);
  } else if (e.code === 'Backspace' || e.code === 'Escape') {
    reset();
  } else if (e.code === 'KeyQ') {
    openOverlay();
  } else if (e.code === 'KeyF') {
    if (document.fullscreenElement) document.exitFullscreen();
    else document.documentElement.requestFullscreen?.().catch(() => {});
  } else if (e.code === 'KeyM') {
    sound.setMuted(!sound.muted);
  }
});

$('viewport').addEventListener('pointerdown', () => {
  if (overlay.hidden) scan();
});

// Hide the mouse cursor when it isn't moving
let cursorTimer = 0;
document.addEventListener('pointermove', () => {
  document.body.classList.remove('cursor-hidden');
  clearTimeout(cursorTimer);
  cursorTimer = setTimeout(() => document.body.classList.add('cursor-hidden'), 2500);
});

// ── Remote control ──────────────────────────────────────────

remote.addEventListener('connection', (e) => {
  const { connected, error } = e.detail;
  $('connDot').className = `dot ${connected ? 'ok' : 'bad'}`;
  $('connText').textContent = connected
    ? `Steuerung bereit · Raum ${room}`
    : error || `Steuerung offline – Tastatur geht trotzdem · Raum ${room}`;
  if (connected) publishStatus();
});

remote.addEventListener('select', (e) => {
  const index = IMAGES.findIndex((img) => img.id === e.detail.id);
  if (index >= 0 && index !== selected) select(index, { publish: false });
});

remote.addEventListener('cmd', (e) => {
  if (!started) return; // audio is still locked until someone presses "Starten"
  if (e.detail.action === 'scan') scan();
  else if (e.detail.action === 'reset') reset();
});

// ── Boot ────────────────────────────────────────────────────

$('title').textContent = CONFIG.titel;
$('subtitle').textContent = CONFIG.untertitel;
document.body.classList.toggle('no-tint', !CONFIG.toenung);

const clock = () => {
  $('clock').textContent = new Date().toLocaleString('de-DE', {
    weekday: 'short', day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit',
  });
};
clock();
setInterval(clock, 10000);

renderPatient();
renderQr();
renderLight();
if (lightEnabled) light.autoConnect();
remote.connect();
openOverlay();

if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {});

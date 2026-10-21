// Pairs the scanner and controller pages through a public MQTT broker.
// GitHub Pages is static, so this relay is what lets a phone control the scanner.
import { CONFIG } from './config.js';

const PREFIX = 'teddydocs-xray/v1';
const ROOM_CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
const ROOM_KEY = 'xray-raum';

export const store = {
  get(key) {
    try { return localStorage.getItem(key); } catch { return null; }
  },
  set(key, value) {
    try { localStorage.setItem(key, value); } catch { /* storage unavailable */ }
  },
};

export function normalizeRoom(value) {
  return String(value || '').toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 12);
}

function randomRoom() {
  let room = '';
  for (let i = 0; i < 5; i++) room += ROOM_CHARS[Math.floor(Math.random() * ROOM_CHARS.length)];
  return room;
}

/**
 * Reads the room code from ?raum=…; the scanner (create: true) falls back to
 * the last used code or a new random one and writes it back into the URL.
 */
export function getRoom({ create }) {
  const url = new URL(location.href);
  let room = normalizeRoom(url.searchParams.get('raum'));
  if (!room && create) room = normalizeRoom(store.get(ROOM_KEY)) || randomRoom();
  if (room) {
    store.set(ROOM_KEY, room);
    if (url.searchParams.get('raum') !== room) {
      url.searchParams.set('raum', room);
      history.replaceState(null, '', url);
    }
  }
  return room;
}

export function lastRoom() {
  return normalizeRoom(store.get(ROOM_KEY));
}

export function controllerUrl(room) {
  const url = new URL('steuerung.html', location.href);
  url.searchParams.set('raum', room);
  return url.href;
}

/**
 * Events: "connection" {connected}, "select" {id}, "cmd" {action}, "status" {online, state, id}
 */
export class RemoteLink extends EventTarget {
  constructor(room, role) {
    super();
    this.room = room;
    this.role = role;
    this.client = null;
    this.connected = false;
  }

  topic(kind) {
    return `${PREFIX}/${this.room}/${kind}`;
  }

  connect() {
    if (!this.room) return;
    if (!window.mqtt) {
      this.#emit('connection', { connected: false, error: 'MQTT-Bibliothek nicht geladen (offline?)' });
      return;
    }
    const options = {
      clientId: `xray-${this.role}-${Math.random().toString(16).slice(2, 10)}`,
      clean: true,
      keepalive: 30,
      reconnectPeriod: 3000,
      connectTimeout: 10000,
    };
    if (this.role === 'scanner') {
      // The broker announces "offline" for us if the scanner tab disappears
      options.will = { topic: this.topic('status'), payload: JSON.stringify({ online: false }), qos: 1, retain: true };
    }
    const client = window.mqtt.connect(CONFIG.mqttBroker, options);
    this.client = client;

    client.on('connect', () => {
      this.connected = true;
      const kinds = this.role === 'scanner' ? ['select', 'cmd'] : ['select', 'status'];
      client.subscribe(kinds.map((k) => this.topic(k)), { qos: 1 });
      this.#emit('connection', { connected: true });
    });
    const lost = () => {
      if (!this.connected) return;
      this.connected = false;
      this.#emit('connection', { connected: false });
    };
    client.on('close', lost);
    client.on('offline', lost);
    client.on('error', (err) => console.warn('MQTT:', err?.message || err));

    client.on('message', (topic, payload) => {
      const kind = topic.slice(topic.lastIndexOf('/') + 1);
      let data;
      try { data = JSON.parse(payload.toString()); } catch { return; }
      if (data && typeof data === 'object') this.#emit(kind, data);
    });
  }

  send(kind, data, { retain = false } = {}) {
    if (!this.client) return;
    this.client.publish(this.topic(kind), JSON.stringify(data), { qos: 1, retain });
  }

  #emit(type, detail) {
    this.dispatchEvent(new CustomEvent(type, { detail }));
  }
}

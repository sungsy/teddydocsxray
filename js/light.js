// Optional: switches a light via an Arduino connected over USB (Web Serial, Chrome/Edge only).
// The Arduino sketch in arduino/roentgen_licht understands '1' (on) and '0' (off).

export class SerialLight extends EventTarget {
  constructor() {
    super();
    this.port = null;
    this.writer = null;
    if (this.supported) {
      navigator.serial.addEventListener('connect', () => this.autoConnect());
      navigator.serial.addEventListener('disconnect', (e) => {
        if (e.target === this.port) this.#closed();
      });
    }
  }

  get supported() {
    return 'serial' in navigator;
  }

  get connected() {
    return Boolean(this.writer);
  }

  /** Reconnects to a port the user already granted earlier — no dialog needed. */
  async autoConnect() {
    if (!this.supported || this.connected) return;
    const [port] = await navigator.serial.getPorts();
    if (port) await this.#open(port).catch((err) => console.warn('Licht:', err));
  }

  /** Shows the browser's port picker; must be called from a click. */
  async choose() {
    const port = await navigator.serial.requestPort();
    await this.#open(port);
  }

  async set(on) {
    if (!this.writer) return;
    try {
      await this.writer.write(new TextEncoder().encode(on ? '1' : '0'));
    } catch (err) {
      console.warn('Licht:', err);
      this.#closed();
    }
  }

  async #open(port) {
    await port.open({ baudRate: 9600 });
    this.port = port;
    this.writer = port.writable.getWriter();
    this.dispatchEvent(new Event('change'));
  }

  #closed() {
    this.port = null;
    this.writer = null;
    this.dispatchEvent(new Event('change'));
  }
}

// Synthesised X-ray machine sounds via the Web Audio API (no audio files needed).

export class XraySound {
  constructor() {
    this.ctx = null;
    this.master = null;
    this.noise = null;
    this.current = null;
    this.muted = false;
  }

  /** Browsers only allow audio after a user gesture, so call this from a key press or click. */
  unlock() {
    if (!this.ctx) {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return;
      this.ctx = new AC();
      this.master = this.ctx.createGain();
      this.master.gain.value = this.muted ? 0 : 0.9;
      this.master.connect(this.ctx.destination);
      this.noise = this.#makeNoise();
    }
    if (this.ctx.state === 'suspended') this.ctx.resume();
  }

  setMuted(muted) {
    this.muted = muted;
    if (this.master) this.master.gain.value = muted ? 0 : 0.9;
  }

  /** Short confirmation blip, e.g. when a patient is selected. */
  blip() {
    if (!this.ctx) return;
    const bus = this.ctx.createGain();
    bus.connect(this.master);
    this.#tone(bus, [], this.ctx.currentTime, 1500, 0.06, 0.06);
  }

  /**
   * One full scan: relay clunk, rotor spin-up, steady exposure beep, spin-down.
   * @param {number} warm   seconds of warm-up
   * @param {number} expose seconds of exposure
   */
  playScan(warm, expose) {
    if (!this.ctx) return;
    this.stop();
    const ctx = this.ctx;
    const t0 = ctx.currentTime + 0.05;
    const tx = t0 + warm;   // exposure starts
    const te = tx + expose; // exposure ends
    const bus = ctx.createGain();
    bus.connect(this.master);
    const sources = [];
    this.current = { bus, sources };

    this.#clunk(bus, sources, t0);
    this.#tone(bus, sources, t0 + 0.12, 880, 0.12, 0.12);

    // Transformer hum, rising as the machine powers up
    const humFilter = ctx.createBiquadFilter();
    humFilter.type = 'lowpass';
    humFilter.frequency.setValueAtTime(180, t0);
    humFilter.frequency.exponentialRampToValueAtTime(1400, tx);
    const hum = ctx.createGain();
    envelope(hum.gain, [[t0, 0.0001], [tx, 0.1], [te, 0.1], [te + 1.2, 0.0001]]);
    humFilter.connect(hum).connect(bus);
    for (const detune of [0, 9]) {
      const osc = ctx.createOscillator();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(40, t0);
      osc.frequency.exponentialRampToValueAtTime(100, tx);
      osc.frequency.setValueAtTime(100, te);
      osc.frequency.exponentialRampToValueAtTime(50, te + 1.2);
      osc.detune.value = detune;
      osc.connect(humFilter);
      run(osc, sources, t0, te + 1.3);
    }

    // Rotating-anode whine: spins up during warm-up, spins down afterwards
    const whine = ctx.createOscillator();
    whine.type = 'sine';
    whine.frequency.setValueAtTime(150, t0);
    whine.frequency.exponentialRampToValueAtTime(2600, tx);
    whine.frequency.setValueAtTime(2600, te);
    whine.frequency.exponentialRampToValueAtTime(250, te + 2);
    const whineGain = ctx.createGain();
    envelope(whineGain.gain, [[t0, 0.0001], [tx, 0.03], [te, 0.03], [te + 2, 0.0001]]);
    whine.connect(whineGain).connect(bus);
    run(whine, sources, t0, te + 2.1);

    // Exposure: the classic steady beep plus an electrical buzz
    this.#tone(bus, sources, tx, 1050, expose, 0.09);
    const buzzEnv = [[tx, 0.0001], [tx + 0.03, 1], [te - 0.03, 1], [te, 0.0001]];
    const noise = ctx.createBufferSource();
    noise.buffer = this.noise;
    noise.loop = true;
    const band = ctx.createBiquadFilter();
    band.type = 'bandpass';
    band.frequency.value = 2500;
    band.Q.value = 0.8;
    const noiseGain = ctx.createGain();
    envelope(noiseGain.gain, buzzEnv.map(([t, v]) => [t, v * 0.05]));
    noise.connect(band).connect(noiseGain).connect(bus);
    run(noise, sources, tx, te + 0.05);
    const buzz = ctx.createOscillator();
    buzz.type = 'square';
    buzz.frequency.value = 120;
    const buzzFilter = ctx.createBiquadFilter();
    buzzFilter.type = 'lowpass';
    buzzFilter.frequency.value = 900;
    const buzzGain = ctx.createGain();
    envelope(buzzGain.gain, buzzEnv.map(([t, v]) => [t, v * 0.04]));
    buzz.connect(buzzFilter).connect(buzzGain).connect(bus);
    run(buzz, sources, tx, te + 0.05);

    // Done
    this.#clunk(bus, sources, te + 0.05);
    this.#tone(bus, sources, te + 0.35, 988, 0.12, 0.12);
    this.#tone(bus, sources, te + 0.55, 1318, 0.22, 0.12);
  }

  /** Abort whatever is currently playing. */
  stop() {
    if (!this.current) return;
    const { bus, sources } = this.current;
    const t = this.ctx.currentTime;
    bus.gain.cancelScheduledValues(t);
    bus.gain.setValueAtTime(bus.gain.value, t);
    bus.gain.linearRampToValueAtTime(0, t + 0.1);
    for (const src of sources) {
      try { src.stop(t + 0.15); } catch { /* already stopped */ }
    }
    setTimeout(() => bus.disconnect(), 400);
    this.current = null;
  }

  #tone(bus, sources, when, freq, dur, vol) {
    const osc = this.ctx.createOscillator();
    osc.type = 'triangle';
    osc.frequency.value = freq;
    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(0, when);
    gain.gain.linearRampToValueAtTime(vol, when + 0.01);
    gain.gain.setValueAtTime(vol, Math.max(when + 0.01, when + dur - 0.02));
    gain.gain.linearRampToValueAtTime(0, when + dur);
    osc.connect(gain).connect(bus);
    run(osc, sources, when, when + dur + 0.02);
  }

  #clunk(bus, sources, when) {
    const ctx = this.ctx;
    const noise = ctx.createBufferSource();
    noise.buffer = this.noise;
    const lp = ctx.createBiquadFilter();
    lp.type = 'lowpass';
    lp.frequency.value = 500;
    const ng = ctx.createGain();
    envelope(ng.gain, [[when, 0.5], [when + 0.06, 0.0001]]);
    noise.connect(lp).connect(ng).connect(bus);
    run(noise, sources, when, when + 0.08);

    const thump = ctx.createOscillator();
    thump.type = 'sine';
    thump.frequency.setValueAtTime(110, when);
    thump.frequency.exponentialRampToValueAtTime(40, when + 0.12);
    const tg = ctx.createGain();
    envelope(tg.gain, [[when, 0.4], [when + 0.14, 0.0001]]);
    thump.connect(tg).connect(bus);
    run(thump, sources, when, when + 0.16);
  }

  #makeNoise() {
    const length = this.ctx.sampleRate * 2;
    const buffer = this.ctx.createBuffer(1, length, this.ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < length; i++) data[i] = Math.random() * 2 - 1;
    return buffer;
  }
}

function run(src, sources, start, stop) {
  src.start(start);
  src.stop(stop);
  sources.push(src);
}

// points: [[time, value], ...]; first is set, the rest are exponential ramps
function envelope(param, points) {
  const [[t0, v0], ...rest] = points;
  param.setValueAtTime(v0, t0);
  for (const [t, v] of rest) param.exponentialRampToValueAtTime(Math.max(v, 0.0001), t);
}

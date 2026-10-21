// Draws a stand-in "X-ray" of a teddy so the app works before the real images exist.

export function placeholderDataUrl(entry, index) {
  const w = 900;
  const h = 1200;
  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  const g = canvas.getContext('2d');
  const rand = seeded(index + 1);

  g.fillStyle = '#000';
  g.fillRect(0, 0, w, h);

  // Plush body: overlapping parts add up and glow brighter, like soft tissue
  g.save();
  g.globalCompositeOperation = 'lighter';
  g.fillStyle = 'rgba(110, 140, 165, 0.28)';
  g.shadowColor = 'rgba(160, 205, 240, 0.55)';
  g.shadowBlur = 50;
  const parts = [
    [300, 210, 70, 70, 0], [600, 210, 70, 70, 0],         // ears
    [450, 360, 190, 170, 0],                               // head
    [450, 770, 230, 290, 0],                               // belly
    [235, 650, 70, 160, 0.55], [665, 650, 70, 160, -0.55], // arms
    [330, 1050, 95, 115, 0.2], [570, 1050, 95, 115, -0.2], // legs
  ];
  for (const [x, y, rx, ry, rot] of parts) {
    g.beginPath();
    g.ellipse(x, y, rx, ry, rot, 0, Math.PI * 2);
    g.fill();
  }
  g.restore();

  // Film grain / stuffing
  g.save();
  g.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 4000; i++) {
    g.fillStyle = `rgba(150, 190, 220, ${0.03 + rand() * 0.05})`;
    g.fillRect(rand() * w, rand() * h, 2, 2);
  }
  g.restore();

  // Seam down the belly
  g.save();
  g.strokeStyle = 'rgba(190, 225, 250, 0.35)';
  g.lineWidth = 3;
  g.setLineDash([10, 8]);
  g.beginPath();
  g.moveTo(450, 520);
  g.lineTo(450, 1030);
  g.stroke();
  g.restore();

  // Button eyes and nose
  g.save();
  g.shadowColor = 'rgba(220, 245, 255, 0.8)';
  g.shadowBlur = 20;
  g.fillStyle = 'rgba(230, 246, 255, 0.9)';
  for (const x of [385, 515]) {
    g.beginPath();
    g.arc(x, 330, 24, 0, Math.PI * 2);
    g.fill();
  }
  g.beginPath();
  g.moveTo(425, 400);
  g.lineTo(475, 400);
  g.lineTo(450, 430);
  g.closePath();
  g.fillStyle = 'rgba(230, 246, 255, 0.55)';
  g.fill();
  g.restore();
  g.fillStyle = 'rgba(0, 0, 0, 0.8)';
  for (const x of [385, 515]) {
    for (const [dx, dy] of [[-7, -7], [7, -7], [-7, 7], [7, 7]]) {
      g.beginPath();
      g.arc(x + dx, 330 + dy, 4, 0, Math.PI * 2);
      g.fill();
    }
  }

  // The swallowed Lego brick
  g.save();
  g.shadowColor = 'rgba(220, 245, 255, 0.9)';
  g.shadowBlur = 35;
  g.fillStyle = 'rgba(240, 250, 255, 0.96)';
  g.beginPath();
  g.roundRect(370, 760, 160, 86, 8);
  g.fill();
  for (let i = 0; i < 4; i++) {
    g.beginPath();
    g.roundRect(384 + i * 36, 736, 24, 26, 4);
    g.fill();
  }
  g.restore();

  // Labels
  g.fillStyle = 'rgba(150, 215, 245, 0.75)';
  g.font = '28px "Share Tech Mono", monospace';
  g.fillText('PLATZHALTER', 40, 64);
  g.fillText(entry.name.toUpperCase(), 40, 104);
  g.font = 'bold 56px monospace';
  g.fillText('R', w - 80, 90);

  return canvas.toDataURL('image/png');
}

function seeded(seed) {
  let a = seed * 2654435761;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

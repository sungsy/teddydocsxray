// ─────────────────────────────────────────────────────────────
//  Einstellungen der Teddy-Röntgen-Station
//  Hier können Tiere, Diagnosen und Befundtexte angepasst werden.
// ─────────────────────────────────────────────────────────────

export const CONFIG = {
  titel: 'Teddy-Docs FAU',
  untertitel: 'Standort Bayreuth',

  // Zeiten in Millisekunden
  aufwaermDauer: 1800,      // Maschine "fährt hoch"
  scanDauer: 3500,          // Scan-Balken läuft über das Bild
  ergebnisAnzeigen: 45000,  // danach automatisch zurück zu "Bereit" (0 = nie)

  // Bilder leicht bläulich einfärben (typischer Röntgen-Look)
  toenung: true,

  // Öffentlicher MQTT-Server für die Fernsteuerung (kostenlos, ohne Anmeldung)
  mqttBroker: 'wss://broker.hivemq.com:8884/mqtt',

  // Taste = Tastenkürzel am Scanner-Laptop
  diagnosen: [
    { id: 'gesund',     name: 'Gesund',           emoji: '💚', taste: 'G', befund: 'Kerngesund! Alles ist an seinem Platz.' },
    { id: 'bruch',      name: 'Knochenbruch',     emoji: '🦴', taste: 'B', befund: 'Knochenbruch! Ein Verband und viel Kuscheln helfen beim Heilen.' },
    { id: 'herz',       name: 'Gebrochenes Herz', emoji: '💔', taste: 'H', befund: 'Ein gebrochenes Herz! Da hilft nur ganz viel Kuscheln.' },
    { id: 'gegenstand', name: 'Verschluckt',      emoji: '🔎', taste: 'V', befund: 'Da wurde etwas verschluckt!' },
  ],

  // Reihenfolge = Nummer auf der Tastatur bzw. in der Steuerung.
  // Bilder liegen unter bilder/<tier>-<diagnose>.svg (erzeugt mit tools/roentgenbilder.py).
  // Mit "befunde" lässt sich der Text einzelner Diagnosen pro Tier überschreiben.
  tiere: [
    { id: 'hase',    name: 'Hase',    emoji: '🐰', befunde: { gegenstand: 'Eine ganze Karotte verschluckt!' } },
    { id: 'hund',    name: 'Hund',    emoji: '🐶', befunde: { gegenstand: 'Ein Schlüssel! Den haben alle gesucht.' } },
    { id: 'katze',   name: 'Katze',   emoji: '🐱', befunde: { gegenstand: 'Ein Glöckchen im Bauch – kling, kling!' } },
    { id: 'baer',    name: 'Bär',     emoji: '🐻', befunde: { gegenstand: 'Ein Legostein im Bauch!' } },
    { id: 'pferd',   name: 'Pferd',   emoji: '🐴', befunde: { gegenstand: 'Ein Hufeisen im Bauch – das bringt Glück!' } },
    { id: 'pinguin', name: 'Pinguin', emoji: '🐧', befunde: { gegenstand: 'Ein ganzer Fisch – nur noch die Gräten!' } },
    { id: 'elefant', name: 'Elefant', emoji: '🐘', befunde: { gegenstand: 'Eine Erdnuss verschluckt!' } },
    { id: 'puppe',   name: 'Puppe',   emoji: '👧', befunde: { gegenstand: 'Ein Schnuller im Bauch!' } },
    { id: 'dino',    name: 'Dino',    emoji: '🦖', befunde: { gegenstand: 'Ein Spielzeugauto verschluckt – brumm, brumm!' } },
    { id: 'ente',    name: 'Ente',    emoji: '🦆', befunde: { gegenstand: 'Eine Gummiente in der Ente!' } },
    { id: 'affe',    name: 'Affe',    emoji: '🐵', befunde: { gegenstand: 'Eine ganze Banane verschluckt!' } },
    { id: 'loewe',   name: 'Löwe',    emoji: '🦁', befunde: { gegenstand: 'Eine Krone im Bauch – ganz königlich!' } },
  ],
};

export function bildPfad(tier, diagnose) {
  return tier.bilder?.[diagnose.id] ?? `bilder/${tier.id}-${diagnose.id}.svg`;
}

export function befundText(tier, diagnose) {
  return tier.befunde?.[diagnose.id] ?? diagnose.befund;
}

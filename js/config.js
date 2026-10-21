// ─────────────────────────────────────────────────────────────
//  Einstellungen der Teddy-Röntgen-Station
//  Hier können Tiere, Bilder und Befunde angepasst werden.
// ─────────────────────────────────────────────────────────────

export const CONFIG = {
  titel: 'Teddy-Klinik',
  untertitel: 'Röntgenabteilung',

  // Zeiten in Millisekunden
  aufwaermDauer: 1800,      // Maschine "fährt hoch"
  scanDauer: 3500,          // Scan-Balken läuft über das Bild
  ergebnisAnzeigen: 45000,  // danach automatisch zurück zu "Bereit" (0 = nie)

  // Bilder leicht bläulich einfärben (typischer Röntgen-Look)
  toenung: true,

  // Öffentlicher MQTT-Server für die Fernsteuerung (kostenlos, ohne Anmeldung)
  mqttBroker: 'wss://broker.hivemq.com:8884/mqtt',

  // Reihenfolge = Nummer auf der Tastatur bzw. in der Steuerung.
  // Fehlt eine Bilddatei, wird automatisch ein Platzhalter angezeigt.
  bilder: [
    { id: 'baer',    name: 'Bär',      emoji: '🐻', datei: 'bilder/baer.jpg',    befund: 'Ein Legostein im Bauch!' },
    { id: 'hase',    name: 'Hase',     emoji: '🐰', datei: 'bilder/hase.jpg',    befund: 'Eine Karotte hat sich versteckt.' },
    { id: 'hund',    name: 'Hund',     emoji: '🐶', datei: 'bilder/hund.jpg',    befund: 'Ein Knochen – aber nicht seiner!' },
    { id: 'katze',   name: 'Katze',    emoji: '🐱', datei: 'bilder/katze.jpg',   befund: 'Ein verschluckter Wollknäuel.' },
    { id: 'elefant', name: 'Elefant',  emoji: '🐘', datei: 'bilder/elefant.jpg', befund: 'Eine Erdnuss im Rüssel.' },
    { id: 'loewe',   name: 'Löwe',     emoji: '🦁', datei: 'bilder/loewe.jpg',   befund: 'Eine Krone im Bauch – ganz königlich!' },
    { id: 'giraffe', name: 'Giraffe',  emoji: '🦒', datei: 'bilder/giraffe.jpg', befund: 'Ein Schlüssel ganz oben im Hals.' },
    { id: 'pferd',   name: 'Pferd',    emoji: '🐴', datei: 'bilder/pferd.jpg',   befund: 'Ein Hufeisen – das bringt Glück!' },
    { id: 'schaf',   name: 'Schaf',    emoji: '🐑', datei: 'bilder/schaf.jpg',   befund: 'Eine Murmel in der Wolle.' },
    { id: 'kuh',     name: 'Kuh',      emoji: '🐮', datei: 'bilder/kuh.jpg',     befund: 'Eine Glocke im Bauch – bimmel bimmel!' },
    { id: 'affe',    name: 'Affe',     emoji: '🐵', datei: 'bilder/affe.jpg',    befund: 'Eine ganze Banane!' },
    { id: 'pinguin', name: 'Pinguin',  emoji: '🐧', datei: 'bilder/pinguin.jpg', befund: 'Ein Fisch für unterwegs.' },
    { id: 'dino',    name: 'Dino',     emoji: '🦖', datei: 'bilder/dino.jpg',    befund: 'Ein Dino-Ei im Bauch!' },
    { id: 'einhorn', name: 'Einhorn',  emoji: '🦄', datei: 'bilder/einhorn.jpg', befund: 'Ein Glitzerstern im Herzen.' },
    { id: 'ente',    name: 'Ente',     emoji: '🦆', datei: 'bilder/ente.jpg',    befund: 'Eine Gummiente in der Ente!' },
  ],
};

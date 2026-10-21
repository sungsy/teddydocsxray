# 🩻 Teddy-Röntgen

Ein Röntgengerät zum Spielen für die Teddy-Klinik: Kinder legen ihr Kuscheltier unter das „Gerät", drücken die Leertaste, die Maschine summt und piept – und auf dem Bildschirm erscheint das Röntgenbild mit Befund („Ein Legostein im Bauch!").

- **`index.html`** – der Scanner-Bildschirm (Laptop/Monitor am Gerät)
- **`steuerung.html`** – die Fernsteuerung fürs Handy: Hier wählt eine Helferin oder ein Helfer aus, welches Bild als Nächstes erscheint.

Alles läuft als statische Seite auf GitHub Pages. Es braucht keinen eigenen Server.

## Bedienung am Veranstaltungstag

1. Auf dem Laptop am Gerät die Seite in **Chrome oder Edge** öffnen.
2. Es erscheint ein Startfenster mit QR-Code. Mit dem Handy den **QR-Code scannen**: Die Steuerung öffnet sich und ist mit diesem Laptop gekoppelt.
3. Am Laptop auf **Starten** klicken (oder Leertaste). Die Seite geht in den Vollbildmodus.
4. Am Handy das passende Tier antippen, Kind drückt die **Leertaste**, fertig.

Ohne Handy oder ohne Internet geht alles auch über die Tastatur am Laptop:

| Taste | Funktion |
|---|---|
| Leertaste / Enter | Aufnahme starten (oder auf den Bildschirm tippen/klicken) |
| `1` … `15` | Tier auswählen (Zahl tippen) |
| ← → | Tier vor/zurück |
| Rücktaste ⌫ | zurück zu „Bereit" |
| `F` | Vollbild an/aus |
| `M` | Ton aus/an |
| `Q` | Startfenster mit QR-Code wieder anzeigen |

**Tipp:** Ein großer USB-Buzzer oder Fußschalter, der als „Leertaste" arbeitet, macht Kindern viel mehr Spaß als die Laptop-Tastatur. Solche Buzzer gibt es günstig zu kaufen, sie funktionieren ohne Einrichtung.

**Raum-Code:** Der Scanner merkt sich seinen Code (z. B. `K7QF2`). Mehrere Stationen am selben Tag haben jeweils einen eigenen Code. Der Code steht auch in der Adresszeile (`?raum=K7QF2`).

## Bilder austauschen

1. Röntgenbilder in den Ordner [`bilder/`](bilder/) legen, z. B. `bilder/baer.jpg`.
2. In [`js/config.js`](js/config.js) Name, Emoji, Dateiname und Befundtext pro Tier anpassen. Die Reihenfolge dort ist auch die Nummer auf der Tastatur.

Solange eine Datei fehlt, zeigt die Seite automatisch einen gezeichneten Platzhalter-Teddy. Hochformat (z. B. 1200 × 1600 px) sieht am besten aus. JPG oder PNG gehen beide, die Bilder werden automatisch schwarz-weiß und leicht bläulich dargestellt (abschaltbar mit `toenung: false`).

## Veröffentlichen auf GitHub Pages

```sh
git init && git add . && git commit -m "Teddy-Röntgen"
git branch -M main
git remote add origin git@github.com:<benutzer>/teddydocsxray.git
git push -u origin main
```

Dann auf GitHub unter **Settings → Pages** bei „Branch" `main` und `/ (root)` auswählen. Nach ein bis zwei Minuten ist die Seite unter `https://<benutzer>.github.io/teddydocsxray/` erreichbar.

Lokal testen: `python3 -m http.server 8000` im Projektordner, dann `http://localhost:8000` öffnen (direkt per Doppelklick auf die Datei geht es nicht).

## Wie die Fernsteuerung funktioniert

Scanner und Handy tauschen kleine Nachrichten über den kostenlosen öffentlichen MQTT-Server von HiveMQ aus (`js/config.js` → `mqttBroker`). Gesendet wird nur, welches Tier gewählt ist und „Aufnahme starten" bzw. „Bereit". Bilder und andere Daten verlassen das Gerät nicht. Wer den Raum-Code kennt, kann mitsteuern, für eine Spielstation ist das in Ordnung.

Ist das Internet weg, zeigt der Scanner unten „Steuerung offline". Die Tastatur funktioniert dann weiterhin. Wurde die Seite einmal online geöffnet, lädt sie auch offline (Service Worker).

## Optional: Lampe über Arduino

Wer eine echte Lampe aufleuchten lassen will, solange „geröntgt" wird:

1. Den Sketch [`arduino/roentgen_licht/roentgen_licht.ino`](arduino/roentgen_licht/roentgen_licht.ino) einmalig mit der Arduino-IDE auf den Arduino laden.
2. Arduino per USB an den Scanner-Laptop stecken.
3. Den Scanner mit `&licht=1` in der Adresse öffnen (z. B. `…/teddydocsxray/?raum=K7QF2&licht=1`). Erst dann erscheint im Startfenster (Taste `Q`) der Knopf **💡 Licht verbinden**. Draufklicken und den Arduino auswählen. Beim nächsten Mal verbindet sich die Seite automatisch, sobald der Arduino eingesteckt ist.

Zum Testen reicht die eingebaute LED auf dem Arduino. Eine hellere Lampe (z. B. LED-Streifen) wird über ein Relais-Modul oder einen MOSFET an Pin 9 geschaltet, nie direkt an den Pin. Das funktioniert nur in Chrome/Edge (Web Serial). Ohne Arduino läuft alles ganz normal weiter.

## Lizenz

Der Code steht unter der [MIT-Lizenz](LICENSE) und darf frei weiterverwendet werden, zum Beispiel für andere Teddy-Kliniken. Die Bilder im Ordner `bilder/` sind davon ausgenommen; die Rechte daran liegen bei den jeweiligen Urhebern.

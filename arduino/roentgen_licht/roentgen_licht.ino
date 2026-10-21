// Röntgen-Licht für die Teddy-Klinik (optional)
//
// Die Webseite schickt über USB '1' (Licht an) und '0' (Licht aus).
// Die eingebaute LED leuchtet immer mit – so lässt sich alles ohne Verkabelung testen.
//
// Für eine helle Lampe (z. B. 12-V-LED-Streifen) NICHT direkt an den Pin anschließen,
// sondern über ein Relais-Modul oder einen Logic-Level-MOSFET an LICHT_PIN.

const int LICHT_PIN = 9;
const unsigned long SICHERHEITS_AUS_MS = 15000;  // geht von selbst aus, falls kein '0' kommt

unsigned long eingeschaltetSeit = 0;
bool istAn = false;

void setzeLicht(bool an) {
  istAn = an;
  digitalWrite(LICHT_PIN, an ? HIGH : LOW);
  digitalWrite(LED_BUILTIN, an ? HIGH : LOW);
  if (an) eingeschaltetSeit = millis();
}

void setup() {
  pinMode(LICHT_PIN, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  setzeLicht(false);
  Serial.begin(9600);
}

void loop() {
  while (Serial.available() > 0) {
    char befehl = Serial.read();
    if (befehl == '1') setzeLicht(true);
    else if (befehl == '0') setzeLicht(false);
  }
  if (istAn && millis() - eingeschaltetSeit > SICHERHEITS_AUS_MS) setzeLicht(false);
}

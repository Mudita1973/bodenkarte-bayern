# Bodenkarten · Bayern mobil

Installierbare Web-App (PWA) für iPhone, Android und Desktop. Grundlage sind amtliche bayerische Bodendaten und eigene, nachvollziehbar erklärte Merkmalsauswertungen.

## Funktionen

- Fünf Bodenansichten und nummerierte Vergleichsprofile mit Mehrfachauswahl
- Amtliche Originallegende und Belegstatus je Eigenschaft
- Luftbild/Topografie sowie separat geladene Nutzungs- und Moorflächen
- Punktlinks zu Google Maps und UmweltAtlas
- Merkpunkte, Notizen, Suchstände und JSON-/CSV-Export
- Offline-Pakete für gesicherte Ausschnitte
- Handy-Oberfläche mit Zwei-Finger-Zoom
- Installationshilfe und geprüfte Offline-Speicherung der Bodengrundlage

## Bereitstellung

`dist/` enthält die vollständige statische Web-App. Auf einem HTTPS-Hosting unverändert ausliefern. Kein eigener App-Server und keine Datenbank erforderlich. Ein Repository-Upload allein veröffentlicht noch keine Website.

Für GitHub Pages ist ein ausschließlich manuell gestarteter Workflow vorbereitet. Die öffentliche Veröffentlichung und die Repository-Sichtbarkeit werden dadurch nicht automatisch geändert. GitHub Free unterstützt Pages aus öffentlichen Repositories; private Quell-Repositories benötigen einen passenden kostenpflichtigen Plan. Auch dann ist die Pages-Website nicht automatisch privat.

Vor einer öffentlichen Freigabe Betreiberangaben und Datenschutzhinweise an das tatsächliche Angebot anpassen. Die aktuelle Oberfläche ist als private Testversion beschriftet. Eine kommerzielle SaaS-Veröffentlichung benötigt einen anderen Hosting-Weg als GitHub Pages.

## Nutzung

Nach Veröffentlichung: iPhone in Safari über Teilen → Zum Home-Bildschirm; Android über das Browsermenü → App installieren bzw. Zum Startbildschirm hinzufügen. Die Erstübertragung der gesamten Bodengrundlage umfasst ungefähr 27 MB. Unter Info die Offline-Speicherung prüfen. Zusatzebenen als Offline-Pakete separat sichern.

Merkpunkte und Notizen bleiben im Browser des jeweiligen Geräts. Keine automatische Kontensynchronisation.

## Grenzen und Quellen

ÜBK25 Bayern, Redaktion 2024; amtliche Quelle LfU Bayern, CC BY 4.0. Angezeigte Grenzen etwa 25 m vereinfacht. Kein parzellenscharfer Nachweis und keine gemessenen pH-/Feuchtewerte. Vergleichsprofile belegen Teilmerkmale, keine vollständige Übertragung einer ausländischen Klassifikation. Anmoor beweist keine Torfoberfläche. Die ÜMBK25 ist aus der ÜBK25 abgeleitet und kein unabhängiger Nachweis. Quellen und Lizenzen stehen vollständig in `dist/about.html`.

## Prüfung und Erzeugung

`node scripts/check_app.cjs` prüft den vollständigen Bodenbestand, Kartenfunktionen und mobile Gesten mit kontrollierten Canvas-/Dienstobjekten. `node scripts/check_worker.cjs` prüft den Service Worker. Ergebnisse unter `checks/`. Echte Geräte- und Browserprüfungen stehen aus.

`python3 scripts/prepare_pwa.py --source-html /absoluter/Pfad/Bodenkarte_Bayern_interaktiv.html` übernimmt eine validierte lokale Karte. `python3 scripts/finalize_pwa.py` erzeugt Symbole und Service Worker; dafür ist Pillow erforderlich. Für den normalen statischen Betrieb ist kein Python erforderlich.

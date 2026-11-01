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

## Soilscapes-Vergleichskarte (`dist/soilscapes/`)

Zweite, eigenständige Karte: ordnet die 695 Legendeneinheiten der ÜBK25 den britischen Soilscapes-Klassen zu (Schwerpunkt 6, 13, 16) und zeigt dazu amtliche LfU-Bodenkennwerte (Basensättigung, Grobboden, Humus, Carbonat), die Bodenausgangsgesteinskarte BAG500, die ÜMBK25-Moorbodenprüfung, Hangneigung aus dem DGM200, CORINE-Nutzung und eine Statistik je Landkreis.

- Nach der Veröffentlichung erreichbar unter `…/soilscapes/` (bei GitHub Pages: https://mudita1973.github.io/bodenkarte-bayern/soilscapes/).
- `index.html` enthält Übersicht, generalisierte Flächen und alle Sachdaten (komprimiert, 9,8 MB). `detail/r00.json` bis `detail/r38.json` (zusammen 35 MB) sind die auf etwa 12 m vereinfachten Originalflächen; die Karte lädt sie ab Zoomstufe 12 regionsweise nach.
- Der Service Worker der mobilen App betrifft diesen Unterordner nicht (er bedient nur die in `sw.js` gelisteten Dateien).
- Bedienung: Umrisse über Luftbild, Vergleichsregler, teilbarer Link (Ansicht im `#`-Teil der Adresse), Drucken, Karte als Bild, Merkpunkte und Suchstände (nur im jeweiligen Browser gespeichert).
- Erzeugt mit den Skripten in `scripts/soilscapes/` (Python, mapshaper). Die Rohdaten (ÜBK25-Geopackage, CORINE, DGM200) sind wegen ihrer Größe nicht im Repository.

Quellen und Lizenzen: ÜBK25, ÜMBK25, Bodenkennwerte und BAG500 © Bayerisches Landesamt für Umwelt (CC BY 4.0); CORINE Land Cover 5 ha 2021 und DGM200 © GeoBasis-DE / BKG 2026 (Daten verändert); Landkreisgrenzen: UmweltAtlas Bayern, Geobasisdaten © Bayerische Vermessungsverwaltung; Leaflet © Volodymyr Agafonkin (BSD-2-Clause).

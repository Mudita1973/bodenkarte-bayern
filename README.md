# Bodenkarten · Bayern mobil

Öffentliche, installierbare Web-App: https://mudita1973.github.io/bodenkarte-bayern/

## Version 3.1

Die App startet mit einer bewusst groben Bayern-Übersicht im 750-m-Raster. Index und Übersicht umfassen zusammen rund 1,5 MB. Ab vierfachem Zoom werden die benötigten Regionalpakete parallel geladen. Alle 175.354 Detailgeometrien bleiben unverändert; beim Start werden keine 175.354 Canvas-Pfade aufgebaut. Die Rasterübersicht ist kein Punktnachweis. Fehlende Detaildaten bleiben ausdrücklich erkennbar und können erneut geladen werden.

Die Nummern 6, 13 usw. bezeichnen Zielkategorien der Referenzabbildung. Die Filter heißen nach den tatsächlich geprüften Teilmerkmalen und stehen getrennt von den Zielbeschreibungen. Ein Treffer belegt keinen bestimmten pH-Wert und keine gemessene Durchlässigkeit. Suchprofil 6 schließt Vernässungshinweise einschließlich Nebenböden aus. Einheit 426b gehört daher zur Stauwasser-Suche 8, nicht mehr zu 6. Die verständliche Zusammenfassung erläutert Bodengesellschaft, oberes Substrat, Wasserstau- und Säureindizien. Die Originallegende bleibt erhalten.

## pH im Mittelpunkt jeder Punktanalyse

Beim Kartenklick werden auf Wunsch pH-Modellwerte aus ISRIC SoilGrids250m 2.0 abgefragt: Median und 90-%-Vorhersageintervall für 0–5, 5–15 oder 15–30 cm. Die Anzeige nennt pH(H₂O), 250-m-Raster, Quelle und Abrufdatum. Die vereinfachte Einordnung unter/gleich/über 7 gilt nur für den Modellmedian. Eine Spanne über den Neutralpunkt wird als unsicher gekennzeichnet. Es handelt sich um Modellschätzungen, keine lokalen Messwerte; pH(CaCl₂) ist nicht direkt vergleichbar.

Die App nutzt den im Browser überprüften WMS-Punktdienst, nicht die pausierte REST-API. Automatische Punktabfragen sind abschaltbar. Fehlende Daten, Dienstausfälle und Offline-Lücken erzeugen keine erfundenen Werte. Beim Speichern eines Merkpunktes werden bereits abgerufene pH-Daten mit der JSON-Sicherung übertragen.

## Funktionen und Nutzung

Fünf Bodenansichten, kombinierbare Suchprofile, Luftbild/Topografie, separat ladbare OSM-Nutzungs- und amtliche Moorflächen, Punktlinks zu UmweltAtlas und Google Maps, lokale Merkpunkte/Notizen, JSON-/CSV-Sicherungen und Offline-Pakete. iPhone: Safari → Teilen → Zum Home-Bildschirm. Android: Browsermenü → App installieren.

Unter Info kann die gesamte Bodengrundlage mit ungefähr 28 MB offline gesichert werden. Zusatzbilder und Nutzungs-/Moorflächen separat als Offline-Paket sichern. Merkpunkte und Notizen bleiben auf dem jeweiligen Gerät; keine automatische Synchronisation. Ältere Datenpakete bleiben für bestehende App-Versionen erreichbar, werden durch Version 3.1 aber nicht zusätzlich geladen oder offline gesichert.

## Daten und Grenzen

ÜBK25 Bayern, Redaktion 2024; LfU Bayern, CC BY 4.0. Detailgrenzen etwa 25 m vereinfacht; keine parzellenscharfe Standortbewertung. pH-Werte und hydraulische Messwerte sind nicht enthalten. Die ÜMBK25 ist aus der ÜBK25 abgeleitet und kein unabhängiger Nachweis. Quellen, Methodik und Hinweise: `dist/about.html`. Die App ist eine öffentliche Testversion. Tests auf echten iPhones und Android-Geräten stehen aus.

## Erzeugung und Prüfung

Statische App ohne Build-Abhängigkeiten, eigener Server oder Datenbank ist nicht erforderlich. GitHub Pages veröffentlicht ausschließlich `dist/`; der Workflow wird manuell gestartet. Ein Quellcode-Commit allein ändert die Live-Version nicht.

`python3 scripts/prepare_spatial.py` erzeugt Übersicht und Regionalpakete aus dem unveränderten älteren Index und dessen Datenpaketen in `dist/data/`; alternativ `--source /absoluter/Pfad/zum/ursprünglichen/dist`. Nach Änderungen `python3 scripts/update_release.py` ausführen.

Prüfungen:

- `node scripts/check_app.cjs`: vollständiger echter Datenbestand, instrumentierte Canvas-/Dienstobjekte
- `node scripts/check_spatial.cjs`: echter Start mit zwei Datenabrufen, Regionalnachladen, sichere Punktzuordnung, Beispiel 426b, Offline-Lücken und Wiederholung
- `node scripts/check_ph.cjs`: Skalierung, Abfragegeometrie, Modellintervalle, sauer/basisch, NoData, Importvalidierung und Dienstausfälle
- `node scripts/check_worker.cjs`: Service Worker und Offline-Vollständigkeit
- `python3 scripts/check_geometry_integrity.py`: Identität aller Geometrien, Häufigkeiten und amtlichen Legenden; vollständige Begrenzungsrahmen je Regionalpaket

Ergebnisse unter `checks/`. Instrumentierte Tests sind keine Browser- oder Geräte-Benchmarks.


## Soilscapes-Vergleichskarte (`dist/soilscapes/`)

Zweite, eigenständige Karte: ordnet die 695 Legendeneinheiten der ÜBK25 den britischen Soilscapes-Klassen zu (Schwerpunkt 6, 13, 16) und zeigt dazu amtliche LfU-Bodenkennwerte (Basensättigung, Grobboden, Humus, Carbonat), die Bodenausgangsgesteinskarte BAG500, die ÜMBK25-Moorbodenprüfung, Hangneigung aus dem DGM200, CORINE-Nutzung und eine Statistik je Landkreis.

- Nach der Veröffentlichung erreichbar unter `…/soilscapes/` (bei GitHub Pages: https://mudita1973.github.io/bodenkarte-bayern/soilscapes/).
- `index.html` enthält Übersicht, generalisierte Flächen und alle Sachdaten (komprimiert, 9,8 MB). `detail/r00.json` bis `detail/r38.json` (zusammen 35 MB) sind die auf etwa 12 m vereinfachten Originalflächen; die Karte lädt sie ab Zoomstufe 12 regionsweise nach.
- Der Service Worker der mobilen App betrifft diesen Unterordner nicht (er bedient nur die in `sw.js` gelisteten Dateien).
- Bedienung: Umrisse über Luftbild, Vergleichsregler, teilbarer Link (Ansicht im `#`-Teil der Adresse), Drucken, Karte als Bild, Merkpunkte und Suchstände (nur im jeweiligen Browser gespeichert).
- Erzeugt mit den Skripten in `scripts/soilscapes/` (Python, mapshaper). Die Rohdaten (ÜBK25-Geopackage, CORINE, DGM200) sind wegen ihrer Größe nicht im Repository.

Quellen und Lizenzen: ÜBK25, ÜMBK25, Bodenkennwerte und BAG500 © Bayerisches Landesamt für Umwelt (CC BY 4.0); CORINE Land Cover 5 ha 2021 und DGM200 © GeoBasis-DE / BKG 2026 (Daten verändert); Landkreisgrenzen: UmweltAtlas Bayern, Geobasisdaten © Bayerische Vermessungsverwaltung; Leaflet © Volodymyr Agafonkin (BSD-2-Clause).

Hinweis zu pH-Angaben dieser separaten Vergleichskarte: Aus Basensättigung abgeleitete pH-Bereiche sind Näherungen und keine amtlich gemessenen pH-Werte am ausgewählten Punkt. Die Hauptkarte zeigt davon getrennt ausdrücklich gekennzeichnete pH(H₂O)-Modellwerte aus SoilGrids mit Unsicherheitsintervall.


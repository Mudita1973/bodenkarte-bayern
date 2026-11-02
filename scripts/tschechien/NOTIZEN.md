# Soilscapes-Karte Tschechien: Arbeitsstand (2. November 2026)

## Auftrag (vom Nutzer bestätigt)
- Testgebiet: westliche Grenzregion zu Bayern = Karlovarský kraj, Plzeňský kraj, Jihočeský kraj (rund 21.000 km²).
- Inhalt: Soilscapes-Vergleich wie in Bayern plus Nutzungsebenen (Pilzsuche vorerst nicht verlangt).
- Lücken der Bodenkarte: Vorschlag SoilGrids (250 m) als deutlich markierter Ersatz plus alte Scans als Bild; Zustimmung noch offen.

## Benötigte Domains (Freigabe in Claude-Einstellungen > Capabilities)
mapy.geology.cz, mze.gov.cz, ags.cuzk.gov.cz, atom.cuzk.cz, maps.isric.org, files.isric.org

## Bodenkarte ČGS 1:50.000 (TKSP)
- REST: https://mapy.geology.cz/arcgis/rest/services/Pudy/pudni_typy50/MapServer, Layer 1 "Půdní typologie (TKSP ČR)", maxRecordCount 1000, Query erlaubt, CORS von github.io ok.
- 218.879 Flächen gesamt, 124.813 im Rechteck 12,09-15,6 E / 48,55-50,45 N.
- Felder: p1_jednot/p2_jednot/p3_jednot (dominant/begleitend/ergänzend), sg_txt, kod_s (Substrat Schuler), kod_n/n_txt (Substrat TKSP), p1_wrb22_sign/soilname/note (WRB 2022, auch p2/p3), p1_kod (Legendenreihenfolge), index_kart_mapa; Renderer uniqueValue auf n_leg_id mit 2.238 Legendeneinträgen.
- Lizenzlage widersprüchlich (Metadaten: frei zugänglich, zugleich "All Rights Reserved" und Preisliste). Für private Karte mit Live-Anzeige und Quellenangabe vertretbar, Datenweitergabe nicht.
- Lücken (nur Rasterscans, Dienst Pudy/pudni_mapa50_rastr): Böhmerwald Železná Ruda bis Vimperk, Raum Domažlice, Nepomuk/Blatná, Český Krumlov, Raum Hluboká; außerhalb des Testgebiets Kladno/Rakovník/Slaný. Gut abgedeckt: Egerland, Karlsbad, Tachov, Großraum Plzeň.

## Nutzung
- LPIS WFS: https://mze.gov.cz/public/app/wms/plpis_wfs.fcgi (CORS ok; eagri.cz scheitert)
- ZABAGED REST: https://ags.cuzk.gov.cz/arcgis/rest/services/ZABAGED_POLOHOPIS/MapServer (CORS ok)
- LPIS trennt Acker/Dauergrünland, nicht Wiese/Mähweide/Weide.

## Stand 2026-11-02: Version 1 gebaut

- Pipeline: dl.py, dlgeo.py, dlzab.py → units.py → run_cls.py (classify_cz.py) → props_cz.py → mapshaper → geopack_cz.py → raster_cz.py → pack_cz.py → lutiles_cz.py → mk_tpl_cz.py (template_cz aus template10) → build_cz.py.
- Prüfung (pruefung_2026-11-02.tsv): 278 Einheiten, 90 % der Fläche; 94,8 % richtig, 0,9 % fraglich, 4,3 % falsch. Alle 28 Beanstandungen (979 km²) umgesetzt; 283 Einheiten / 1.120 km² geändert. Unsicher: 72,8 % der Fläche.
- Nutzung: ZABAGED als statische Kacheln (lu/{ix}_{iy}.bin, UTM32-Raster 4 km, 1.484 Kacheln, 12 MB), ČÚZK CC BY 4.0. LPIS live nur mit PROPERTYNAME=ms:GEOMETRY,ms:kultura,ms:vymera (keine Namen/Adressen).
- Hintergrund: ČÚZK ZTM_WM und ORTOFOTO_WM (arcgis1), CORS ok.
- Lizenz: Bodenkarte 1:50 000 und 1:1 Mio. sind NICHT CC BY (Metadaten: „copyright“, Zugang ohne Bedingungen). Laut cgs.gov.cz/en/copyright dürfen Kartenausschnitte bzw. Bearbeitungen mit Zitierform und Änderungshinweis weitergegeben werden; sonst schriftliche Genehmigung. Nutzer hat am 2026-11-02 entschieden: veröffentlichen mit ČGS-Zitierform und Änderungshinweis (dist/soilscapes-cz).
- Ausgeliefert: Ordner 07_Bodenkarten/Tschechien (Web-Datei und Detail-Datei mit eingebetteten Kacheln), privates Artifact c32994b2-dc75-4b3e-828e-f384a900aebb.

## 2026-11-02: Prüfrunde v11.4 (Bayern) / v1.2 (Westböhmen)
- Fehler behoben (beide Karten): Nutzungskacheln blieben nach Heraus- und Hineinzoomen auf „wait“ hängen.
- Westböhmen: Maske auf Gebietsumriss beschnitten (D.region), LPIS mit eigenem Pool (4) und Abbruch veralteter Anfragen, ZABAGED-Kacheln ohne Platzlimit; Statistik und Nutzungsanteile aus ungeneralisierten Flächen (20.991 km² statt 20.686 km²); Merkpunkte in UTM33; Pilzfunktionen auch per Link/Import gesperrt; Texte korrigiert (Raster etwa 80 m bzw. 260 m am Boden).
- Beide: Nachbarkarten-Link übersetzt Nutzungsauswahl, fällt ohne Überschneidung auf Übersicht zurück; Beschriftungen ohne Überlappung; Quellenzeile auf dem Handy einzeilig; Auswahllisten mit aria-label.

## 2026-11-02: v11.7 (Bayern) / v1.3 (Westböhmen)
- Pilzsuche Westböhmen: Bodengruppen aus ČGS-Bodenkarte (pz_cz.py, units[leg].zc = [sauer, basisch, wasser]); sauer 5.564 km², basisch 976 km², Wasserspeicher 1.775 km². Hangrichtung, Wetter, iNaturalist, SoilGrids-Gegenprobe aktiv; Baumarten und Thünen-pH ausgeblendet (nur Deutschland).
- Säureanzeige: mesobasisch (TKSP) mit WRB „Dystric“ wird jetzt als „mittel basenhaltig“ angezeigt, nicht als „basenarm“.
- Gebäude: ZABAGED-Layer 99 (dlzab99.py, 2.099.794 Objekte, 714.538 im Gebiet) je Kachel gepuffert (6 m), vereinigt, zurückgenommen (-4 m) als Layer 99 „bebaute Fläche“ in lutiles; Kacheln 19,3 MB statt 12,0 MB.
- Speicher (beide Karten, Handy): Daten aus Textelement statt JS-String, PNG/Bin nach Gebrauch frei, generalisierte Ebene erst beim Hineinzoomen und in Schritten, in der Detailansicht nach 2,5 s freigegeben; CZ-Generalisierung je Einheit und 0,27°×0,18°-Zelle gebündelt (6.286 statt 30.791 Objekte). JS-Heap Handy: Übersicht BY 155 → 23 MB, CZ 118 → 22 MB; Zoom 13 BY 162 → 45 MB, CZ 190 → 27 MB; Zoom 10 CZ 180 → 103 MB.
- Offen: weiße Spalten zwischen ZABAGED-Flächen (je Fläche auf 15 m vereinfacht beim Download).

## 2026-11-02: v11.8 / v1.4
- Deckkraft je Ebene (Nutzung, Pilzböden, Hangrichtung, pH-Karte, Baumarten, Fundmeldungen) als Pane-Opacity, im Link als oe=; Standortknopf (watchPosition, nichts gespeichert).
- ZABAGED neu mit maxAllowableOffset 3 m (dlzab3.py, zab3/, lutiles3_cz.py): weiße Spalten weg; Kacheln 27,2 MB.
- Validierung (scripts/validierung): iNaturalist research grade, acc<=250 m, offen; ausgedünnt je Beobachter/Art/1-km-Zelle; Basis alle Pilzfunde. Bayern n=18.487: LfU-Waldwert sauer 1,65 (1,46-1,85), basisch 1,84 (1,47-2,16); BAG500 1,70/1,36; Thünen 0-30 1,31/2,02; LfU Acker für sauer ungeeignet. Westböhmen n=5.394: sauer 1,41 (1,24-1,60), basisch n=14 zu wenig.

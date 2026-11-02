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
- Lizenz: Bodenkarte 1:50 000 und 1:1 Mio. sind NICHT CC BY (Metadaten: „copyright“, Zugang ohne Bedingungen). Laut cgs.gov.cz/en/copyright dürfen Kartenausschnitte bzw. Bearbeitungen mit Zitierform und Änderungshinweis weitergegeben werden; sonst schriftliche Genehmigung. Deshalb Daten (dist/soilscapes-cz) noch NICHT öffentlich auf Pages, bis der Nutzer entscheidet.
- Ausgeliefert: Ordner 07_Bodenkarten/Tschechien (Web-Datei und Detail-Datei mit eingebetteten Kacheln), privates Artifact c32994b2-dc75-4b3e-828e-f384a900aebb.

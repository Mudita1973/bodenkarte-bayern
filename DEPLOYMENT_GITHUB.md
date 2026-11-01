# GitHub-Upload und spätere Veröffentlichung

Dieses Projekt soll zunächst privat unter dem Konto `Mudita1973` gespeichert werden. Die Veröffentlichung der Website ist ein eigener Schritt. Keine Zugangsdaten, Benutzer-Merklisten oder lokalen Notizen sind Teil des Uploads.

## Nach dem Repository-Upload

1. Repository-Inhalt und Sichtbarkeit kontrollieren.
2. Für eine Website zwischen GitHub Pages und einem anderen statischen Hosting wählen. Mit GitHub Free benötigt Pages ein öffentliches Repository. Ein öffentliches Repository macht den enthaltenen Quellcode und die Kartendateien für alle zugänglich. Ein privates Repository mit unterstütztem kostenpflichtigem Plan macht die Pages-Website nicht automatisch privat.
3. Erst nach ausdrücklicher Freigabe für eine öffentliche Karte die Veröffentlichung einrichten. Bei GitHub Pages in Settings → Pages als Quelle GitHub Actions wählen.
4. Unter Actions den Workflow „Publish Bodenkarte to GitHub Pages“ manuell starten. Der Workflow lädt ausschließlich `dist/` hoch. Kein automatischer Start durch einen normalen Commit.
5. Die vom erfolgreichen Deployment ausgegebene HTTPS-Adresse öffnen und die App auf echten Geräten prüfen. Eine hergeleitete Adresse allein ist kein Beleg für eine Veröffentlichung.

Die App verwendet relative Pfade und einen Service Worker mit Scope `./`. Das unterstützt sowohl eine eigene Domain als auch GitHub-Projektseiten unter einem Repository-Unterpfad. GitHub ignoriert die Datei `dist/_headers`; die App verlangt keine Erweiterung des standardmäßigen Service-Worker-Scopes.

## Quellen

- https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages
- https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

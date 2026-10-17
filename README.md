# Investment Cockpit – kostenlose Webversion V7.0 (Bereitstellungspaket)

**Kein Hosting- oder Datenanbieter-Abo erforderlich.** Die Preise und Analystendaten im historischen Archiv sind nicht unabhängig verifiziert und dürfen nicht als aktuelle Live-Daten interpretiert werden.

## Veröffentlichung über GitHub Pages (einfachster kostenloser Weg)

1. Bei GitHub kostenlos anmelden, ein neues **öffentliches** Repository (z. B. `investment-cockpit`) erstellen.
2. Sämtliche Dateien dieses Pakets in die **Wurzel** des Repositorys hochladen – auch den Ordner `.github/workflows` (beim Entpacken versteckte Ordner anzeigen).
3. Repository → **Settings → Pages → Build and deployment → Deploy from a branch → main → /(root) → Save**.
4. Repository → **Actions → Kostenlose Marktdaten aktualisieren → Run workflow** ausführen.
5. Nach der Veröffentlichung die Website öffnen: `https://DEIN-GITHUB-NAME.github.io/investment-cockpit/`.
6. Unter **Aktienanalyse → Live-Marktdaten** prüfen, ob Preise mit echtem Zeitstempel geladen wurden; Fehlversuche erscheinen unter **Daten & Einstellungen → Provider-Status**.

**Privatheit:** Ein öffentliches GitHub-Repository und GitHub Pages sind öffentlich. Das Dashboard enthält keine Zugangsdaten. Für rein private Nutzung bitte noch keinen Depotbestand, Kaufpreise oder andere persönliche Informationen hochladen. Ohne Cloud-Anmeldung läuft der aktuelle Build auch offline als historische HTML-Vorschau, aber `index.html` direkt lokal geöffnet kann JSON-Daten wegen Browser-Sicherheit nicht abrufen.

## Aktualisierung

GitHub Actions läuft werktags 21:35 UTC nach Marktschluss der USA. Das ist ein Best-Effort-Zeitplan, keine garantierte Datenaktualisierung. Workflow kann manuell gestartet werden. GitHub Free für öffentliche Standard-Repositories und GitHub Pages haben Nutzungsgrenzen/Verfügbarkeitsbedingungen. Wenn Yahoo den inoffiziellen Chart-Zugang sperrt, bleiben Daten als alt gekennzeichnet; es gibt keine garantierte kostenlose API-Verfügbarkeit. TTM-P/E, historisches Forward-P/E, Analystenrevisionen und Gesamt-Score werden ohne belegbare Daten **nicht** als live ausgewiesen.

## Datenintegrität

- Kein API-Key im Browser, kein lokaler Python-Server.
- Unadjusted Tages-Schlusskurse. YTD ist reine Preisentwicklung, **kein** Total Return.
- Kein belegter vollständiger Point-in-Time-Backtest. Bestehende Forschungsansichten unverändert, aber als unvalidiert zu verstehen.
- Bei Datenfehlern keine erfundenen Werte; bereits erfolgreich publizierte Werte nur als `stale` gekennzeichnet.
- Automatischer GitHub-Workflow benötigt `contents: write` und ggf. Repository Actions-Schreibrechte.

## Lokaler technischer Test

`python -m http.server 8000` im entpackten Ordner, dann `http://localhost:8000/` aufrufen. `python update_data.py` ist optional und braucht Internetzugang.

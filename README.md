# Investment Cockpit V7.3

Kostenloses öffentliches Research-Dashboard auf GitHub Pages. Keine Depotbestände, Zugangsdaten oder kostenpflichtigen Dienste.

## Dashboard und Vergleich

Übersicht mit Datenabdeckung, vollständigen Scores, Befunden, Profilfilter und durchsuchbarer Aktienliste. Score-Verlauf vergleicht bis zu vier Aktien auf fixer 0–100-Skala; vollständige Scores, Teilpunkte und Abdeckung sind getrennte Ansichten. Kurse bleiben separat über bis zu fünf Jahre vergleichbar.

## Unveränderliche beobachtete Historie

Der erste tatsächlich vorhandene Snapshot pro Wiener Kalendertag und Modellversion wird unter `data/snapshots/` gespeichert. `data/score-history.json` enthält die Zusammenfassung und SHA-256-Prüfsummen. Intraday-Läufe überschreiben den ersten Stand nicht. V7.1 und V7.2 bleiben getrennt; kein rückwirkend erfundener Verlauf, keine Interpolation fehlender Punkte. CSV-Export und Original-JSON stehen im Verlauf bereit. Dies ist ein öffentliches Git-Archiv, kein manipulationssicherer externer Zeitstempeldienst.

## Datenprüfung

Kursabgleich am identischen Handelstag (2%) und TTM-P/E gegen Kurs/TTM-EPS bei identischer Währung (8%) prüfen Konsistenz innerhalb desselben Anbieters. Eine SEC-Stichprobe für MSFT, AAPL, NVDA und JPM prüft vier gemeldete Quartals-EPS bei gleichem Berichtsende (15%). Summe der Quartals-EPS kann wegen Verwässerung und Splits vom TTM-EPS abweichen. Nicht verfügbare SEC-Daten bleiben ungeprüft. Auffällige Werte sperren die Bewertungs-Komponente. Forward-P/E bleibt ein nicht unabhängig bestätigter Anbieterquotient.

## Branchenmodelle

Bewertung 30, Wachstum 25, Qualität 20, Revisionen 15, Marktrisiko 10 Punkte. Fehlende Kategorien werden nicht hochgerechnet; Gesamtwert nur bei 100% Abdeckung. Unterschiedliche Profile nicht als gemeinsame Rangliste interpretieren.

- Operativ: P/E, Umsatzwachstum, operative Marge, EPS-Konsensrevisionen.
- Banken/Versicherer: Kurs/Buchwert, Gewinnwachstum, ROE, EPS-Konsensrevisionen. Kein CET1-/Solvenzmodell.
- REIT: AFFO-Multiple, AFFO-Wachstum, Ausschüttungsdeckung und Emittenten-Guidance-Revision.
- BDC: Kurs/NAV, NAV-Entwicklung, NII-Deckung und Verschuldung. Keine GAAP-EPS als NII-Ersatz.
- Holding: Buchwert als ausdrücklich begrenzter Proxy; fehlende Look-through-Daten bleiben offen.
- Royalty: annualisierter Quartals-Cashflow und Ausschüttungsdeckung; keine unterstellte TTM-Zeitreihe.

Die genauen linearen Schwellen und Quellen sind in „Branchenmodelle“ und den Einzeltiteln sichtbar. Primärdaten für O, ARCC und KRP in `data/sector-inputs.json` wurden anhand verlinkter Berichte erfasst und müssen bei neuen Berichten gepflegt werden; nach 210 Tagen verfallen sie. Fehlende Spezialkennzahlen werden nicht ersetzt. Keine Kaufempfehlung und kein historischer Backtest.

## Datenlauf und Tests

GitHub Actions läuft werktags 21:35 UTC, manuell und bei relevanten Quelländerungen. Yahoo Finance via yfinance ist kostenloser Best-Effort-Zugriff ohne Verfügbarkeitsgarantie. SHA-fingerprinted Browserassets verhindern veraltete Skriptkopien. Bei komplett fehlgeschlagenem Kursabruf wird nicht veröffentlicht.

```
python -m unittest discover -s tests -v
node tests/test_research.cjs
node tests/test_history.cjs
node --check dashboard.js
```

Pages benötigt `index.html`, beide JS-Dateien und `data/`; Python und Tests werden nicht ausgeliefert.

## Monatliche Rückrechnung (separate Modellvariante)

`reconstruct.py` berechnet 60 abgeschlossene Monatsenden. Die Oberfläche unter „Score-Verlauf → Rückrechnung · 5 Jahre“ vergleicht bis zu vier Aktien, einzelne Komponenten und Abdeckung; Monatsdetails zeigen Eingaben und Quellen. CSV und JSON sind exportierbar. Die Rückrechnung wird nicht in das unveränderliche beobachtete Archiv geschrieben.

Startabdeckung: 48 Original-Quartalsmeldungen von Microsoft und Apple ab September 2020 bis Juni 2026, kompakt in `data/historical-reports.json`. Andere Aktien erhalten ausschließlich historische Risikopunkte. Ein Bericht darf erst nach seinem Veröffentlichungstag und vor dem tatsächlichen Kursstichtag genutzt werden. Datumsgleiche Veröffentlichungen werden konservativ ausgeschlossen. Keine späteren Kennzahlen oder Analystenschätzungen werden rückwärts eingesetzt. Finanzdaten verfallen nach 210 Tagen.

Gleiche V7.2-Schwellen, eigene Modellversion `research-v7.2-reconstruction-v1`: quartalsweises Umsatzwachstum, TTM-Marge aus vier zusammenhängenden Quartalen, KGV-Näherung aus der Summe gerundeter diluted Quartals-EPS und historische Volatilität. EPS-Summe ist wegen Rundung und veränderter gewichteter Aktienzahlen kein exaktes TTM-EPS. Für die beiden Emittenten sind seit 2020 keine Aktiensplits im berechneten Fenster einzurechnen. Revisionen fehlen: maximal 85% Abdeckung, kein hochgerechneter Gesamt-Score. Heute geladene Kursreihen und Emittentenseiten können rückwirkend geändert worden sein; Quellenhashes sind keine historischen Zeitstempel. Auswahl-/Survivorship-Bias bleibt bestehen. Kein Rendite-Backtest.

`tools/collect_reconstruction_sources.py` erstellt das Quellenpaket erneut (lxml und Poppler/pdftotext erforderlich; separat von der täglichen CI). Neue Quartalsmeldungen müssen dort ergänzt und geprüft werden. Die CI berechnet monatliche Stände aus dem geprüften Paket und aktuellen historischen Kursreihen neu. Sie archiviert diese Rückrechnung ausdrücklich nicht als damals beobachtete Daten.

## V7.3 Oberfläche: Einordnung und beobachtete Veränderungen

`insights.js` stellt Verfügbarkeit, Aktualität, Plausibilität und begrenzte Primärbestätigung getrennt dar. Hohe Modellabdeckung wird nicht als unabhängig bestätigte Datenqualität dargestellt. Teil-Scores zeigen belegte Punkte und Abdeckung getrennt, keine missverständliche Teilpunkte/Abdeckung-Bruchdarstellung.

Frühere Aktienlisten, Quantum-Zahlen, Bewertungshistorien, Gewichtslabore, externe Diagnostik und explorative Backtests liegen unter Archiv. Bestehende Deep Links bleiben gültig. Sie sind andere Daten-/Modellstände und validieren das aktuelle Modell nicht.

Der Aktienvergleich verwendet die Kennzahlen des jeweiligen Profils (P/B, ROE, AFFO, NAV/NII, Cash available). Anbieter-P/E und Forward-P/E bleiben als zusätzliche, nicht ersetzende Referenzquotienten zugänglich. Modellversion, Berichtsende und Quellen sind sichtbar.

„Score-Veränderungen“ vergleicht zwei vollständige Original-Snapshots aus dem beobachteten Archiv. Nur bei identischer Modellversion, Profil und Gewichten werden gemeinsam belegte Komponenten subtrahiert. Hinzugekommene/verlorene Abdeckung erhält keine scheinbare Punktedifferenz. Gesamtänderungen gibt es nur bei vollständigen vergleichbaren Scores; Modellwechsel werden nebeneinander ohne numerischen Delta gezeigt. Eingabeänderungen und gespeicherte Regeln sind keine kausale Attribution. Gleiches Kursdatum an mehreren Archivdaten wird ausdrücklich genannt. Die Score-Methodik selbst bleibt research-v7.2.0.

Zusätzlicher Check: `node tests/test_insights.cjs`.

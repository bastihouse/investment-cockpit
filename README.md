# Investment Cockpit V7.2

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

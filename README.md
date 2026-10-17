# Investment Cockpit V7.1

Kostenlose persönliche Research-Webversion auf GitHub Pages. Öffentliche Marktdaten, keine Depotbestände oder Zugangsdaten. Keine kostenpflichtigen Dienste konfiguriert.

## Neue Funktionen

- Fünf Jahre Kurshistorie, soweit vorhanden; Ansichten 1M, 6M, YTD, 1J und 5J.
- Vergleich von bis zu vier Aktien auf gemeinsamen Handelstagen, Kursrendite in jeweiliger Handelswährung, ohne Dividenden und ohne FX-Konvertierung.
- TTM-P/E und Forward-P/E direkt von Yahoo Finance über yfinance, sofern vorhanden. Forward-P/E ist ein Anbieterwert, kein unabhängig bestätigtes FY1-/NTM-P/E.
- Transparent Research V7.1: Bewertung 30, Wachstum 25, Qualität 20, EPS-Revisionen 15, Risiko 10 Punkte. Jede Komponente hat nachvollziehbare Eingaben und Grenzen.
- Fehlende Kategorien werden nicht hochgerechnet. Gesamtwert nur bei 100% Abdeckung. Sonderprofile erhalten keine operativen Fundamental-Scores.
- Abrufzeit und jüngstes Berichtsdatum separat. Erfolgreicher Abruf bedeutet keine unabhängige Verifizierung.

## Datenlauf

GitHub Actions aktualisiert werktags um 21:35 UTC und nach Änderungen an Daten-/Programmdateien. Neue Daten werden in einem eigenen Pages-Job veröffentlicht. Quellen sind inoffizielle, kostenlose Best-Effort-Zugriffe auf Yahoo Finance, kein Verfügbarkeitsversprechen. Der Workflow installiert die unter requirements.txt festgelegte Bibliothek. Keine API-Schlüssel notwendig.

TTM-P/E und Forward-P/E sind direkt gelieferte Anbieterquotienten. Verlust-/Null-Quotienten bleiben leer. Ein Bericht unbekannten Alters oder älter als 210 Tage verhindert fundamentale Score-Punkte. Stale-Fundamentaldaten bleiben nur in der Diagnose und werden nicht als aktuelle P/E-Werte ausgegeben. Alle Kurse fehlgeschlagen: Veröffentlichung wird abgebrochen.

## Score-Methodik

Zwischen den Grenzen wird linear skaliert und an 0 bzw. Maximalpunkten gedeckelt:

| Kategorie | 0 Punkte | Maximale Punkte |
| --- | --- | --- |
| TTM-P/E /30 | ≥40× | ≤10×, nur positiv |
| Umsatzwachstum /25 | ≤−5% | ≥25% |
| Operative Marge /20 | ≤0% | ≥30% |
| +1y EPS-Konsensrevision ggü. 30 Tagen /15 | ≤−10% | ≥+10%, mindestens 3 Analysten |
| Annualisierte Tagesvolatilität /10 | ≥60% | ≤15%, mindestens 201 adjustierte Schlusskurse |

Das ist ein heuristisches Momentbild, keine Bewertung des inneren Unternehmenswertes. Nur ähnliche Branchen und gleiche Profile vergleichen. Banken, Versicherer, REIT, BDC, Holding und Royalty erhalten keine ersatzweise berechneten operativen Punkte. Keine Kaufempfehlung. Kein historischer Backtest dieses Modells. Historische Archivansichten bleiben ausdrücklich unvalidierte Forschungsdaten.

## Entwicklung und Prüfung

- python -m unittest discover -s tests -v
- node tests/test_research.cjs
- node --check research.js
- python update_data.py (Internet und requirements.txt erforderlich)

Die statische Website benötigt nur index.html, research.js und data/. Python-Programme und Tests werden nicht im Pages-Artefakt ausgeliefert.

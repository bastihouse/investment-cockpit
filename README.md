# Investment Cockpit V7.5

## Eigener Bereich für Datenqualität (22.10.2026)

Universumsfilter enthalten nur noch Alle Aktien und S&P 500 Top 100; die bisherige 32er-Auswahl ist in allen aktuellen Ansichten entfernt. Der Header zeigt Investment Research ohne Aktienanzahl. Der Hauptbereich Daten heißt Datenqualität. Kursverfügbarkeit, Primärprüfung, Statusanzeige, Berichtsprüfung und Qualitätshinweise sind dort gebündelt. Die erste Übersicht beginnt direkt mit der Aktienliste. Datencheck-Spalte und Primärhinweise auf mobilen Übersichtskarten sind dort ausgeblendet; Prüfdetails bleiben im eigenen Bereich und in Einzelaktienansichten verfügbar. Such-/Watchlist-Filter und Sortierung bleiben bestehen.

Syntax, bestehende Experience-/Discovery-Prüfungen und DOM-Integration mit tatsächlichen Daten bestanden: keine Original-Auswahl in aktuellen Filtern, Qualitätsblöcke im eigenen Tab, Header ohne Aktienanzahl, unveränderte Suchrücksetzung, Navigation und historische Charts. Live-Abnahme erfolgreich: https://github.com/bastihouse/investment-cockpit/actions/runs/39745817249 (Refresh 65 Sekunden, Deployment 8 Sekunden). Header ohne Aktienanzahl, genau zwei Universumsoptionen und Qualitätsblöcke im eigenen Tab bestätigt. Score-Sortierung bleibt nach Neuladen erhalten. Smartphone/Tablet ohne horizontale Überbreite (375/375 und 753/753 CSS-Pixel); mobiler Datenqualität-Einstieg geprüft.

## Vereinfachte Oberfläche (22.10.2026)

Sechs aufgabenbezogene Einstiege: Übersicht, Aktien, Watchlists, Vergleichen, Verlauf und Daten. Gleiche Struktur im mobilen Menü, direkte Hauptziele ohne überraschenden Sprung zur zuletzt besuchten Unteransicht. Ältere Modellansichten sind nicht mehr in der Navigation auswählbar; alte Hash-Lesezeichen führen zur passenden aktuellen Ansicht. Interne Legacy-Elemente bleiben inert, da Datenladefunktionen sie weiterhin referenzieren. Keine Löschung historischer Nachweise oder persönlicher Watchlists.

Die Übersicht zeigt Titel, kompakte Gesamtkennzahlen und die durchsuchbare Aktienliste zuerst. Doppelte Einstiegsleisten entfallen; Marktüberblick, Änderungsfeed und Berichtsprüfung sind gemeinsam aufklappbar. Such-/Universums-/Watchlist-/Sortierfelder sind beschriftet, Filter lassen sich gemeinsam zurücksetzen. Score-Erläuterung im Dialog. Sortierwahl und Watchlists bleiben browserlokal erhalten. Tägliche und rekonstruierte Score-Verläufe bleiben nutzbar, historische Stände alter Modelle sind in Modell- und Datumswahlen nicht mehr auswählbar. Keine Vermischung von Modellversionen.

## Gespeicherte Sortierung und Watchlist-Filter (20.10.2026)

Sortierspalte und Richtung werden je Tabelle lokal unter `cockpit-table-sorts-v1` gespeichert und nach Neuladen anhand des Spaltennamens wiederhergestellt. Getrennte Tabellen behalten getrennte Wahlen; verschwundene Spalten werden ignoriert. Desktop-Kopfzeilen, mobile Spaltenauswahl und der bisherige Übersichtsfilter verwenden dieselbe Speicherung. Änderungen lesen vor dem Speichern den aktuellen Präferenzstand, um andere Tabellenwahlen aus weiteren Tabs zu erhalten. Beschädigte Präferenzen verhindern die Bedienung nicht; bei einem Schreibfehler gilt die neue Reihenfolge nur im laufenden Aufruf und die Oberfläche meldet den Fehler.

Die Aktienübersicht enthält einen Watchlist-Filter mit Trefferzahl, kombinierbar mit Aktienuniversum und Textsuche. Filterwahl bleibt lokal über Neuladen erhalten (`cockpit-overview-watchlist-v1`). Listenänderungen, Umbenennen, Entfernen, Import/Reset und Änderungen aus anderen Tabs werden über den vorhandenen Workspace übernommen. Eine entfernte gewählte Liste setzt den Filter mit Hinweis auf alle Aktien zurück. Leere Listen zeigen keine zufälligen Gesamttreffer. Marktkennzahlen und Research-Rangfolge oberhalb der Aktienliste bleiben global, was beim aktiven Filter ausdrücklich angezeigt wird. Keine Übertragung von Listen oder Notizen.

Syntax und erweiterte Node-Prüfungen bestanden. Integration mit tatsächlichen Daten einschließlich neu erzeugter Dokumentinstanz: Wiederherstellung unabhängiger Tabellenwahlen und Watchlist, kombinierte Suche/Universum, Umbenennen, leere Liste, Quota-Schreibfehler, defekte Präferenzen und Rückfall nach gelöschter Liste bestanden; keine JavaScript-Fehler.


## Tabellen über Spaltenköpfe sortieren (20.10.2026)

Alle Datenspalten von Tabellen mit Kopfzeile erhalten bedienbare Sortierköpfe: erster Klick aufsteigend, erneuter Klick absteigend, sichtbare Richtung sowie aria-sort und Tastaturbedienung. Reine Aktionsspalten und leere Köpfe bleiben ohne Sortierung. Neu eingefügte Tabellen und Tabellenkopien in Informationsdialogen werden ebenfalls angebunden. Deutsche Dezimal-/Tausenderformate, Vorzeichen, Datumswerte und natürliche Namensreihenfolge werden berücksichtigt; fehlende Werte stehen in beiden Richtungen zuletzt. Gleichstände bleiben stabil.

Eine aktive Sortierung wird nach Aktualisierung, Suche und Filtern innerhalb der vorhandenen Tabelle erneut angewendet. Bestehende Zeilen und ihre Aktionen werden umgeordnet, nicht neu erstellt; zusammengefasste Hinweiszeilen bleiben getrennt. Die Sortierung wird nicht über einen vollständigen Seitenreload gespeichert. Auf Smartphones erhalten als Karten dargestellte Tabellen eine vollständige Spaltenauswahl mit Richtungswechsel. Der bisherige Übersichts-Sortierfilter und die Kopfsortierung zeigen keine widersprüchliche Auswahl.

Aktien im Vergleich behalten beim Sortieren ihre Tickerzuordnung zu Watchlist-Sternen. Unit-Prüfungen für Zahlen, Vorzeichen, Datum, numerische Ticker und fehlende Werte ergänzt. DOM-Abnahme mit tatsächlichen Daten: Kurs-/YTD-Sortierung, Persistenz bei Suche, mobile Auswahl und Kartenreihenfolge, Details-Listener, fehlende Werte, Datumsfolge, neue Zeilen, Tabellenkopien sowie Watchlist-Zuordnung nach umgekehrter Reihenfolge bestanden; keine JavaScript-Fehler.


## Watchlist-Sterne direkt an Aktien (20.10.2026)

Sterne in der Aktienübersicht (Tabelle und mobile Karten), Live-Kurstabelle, aktueller Score-Liste, aktuellem Aktienvergleich, Detailansicht, Branchenvergleich, Scanner und Datenlücken-Karten. Ein gefüllter Stern zeigt die Mitgliedschaft in mindestens einer Liste; der zugängliche Name nennt die Anzahl. Ein kompakter Dialog erlaubt Zuordnung zu mehreren Listen, Entfernen, Rückgängig sowie das Anlegen einer neuen Liste mit Aktie. Browserlokale Speicherung verwendet unverändert die vorhandene validierte Arbeitsfläche; bestehende Notizen bleiben beim Hinzufügen zu anderen Listen erhalten.

Sterne werden nach Such-/Filterwechseln und Änderungen aus anderen Tabs synchronisiert. Der Dialog unterstützt native Tastaturbedienung, Escape, Fokusrückgabe und Dark/Light-Themes; Listenbezeichnungen werden als Text dargestellt. Schreibfehler melden keinen Erfolg. Vorhandene Export-/Importfunktionen bleiben nutzbar.

Prüfung: JavaScript-Syntax und bestehende Research-Hub-Prüfung bestanden. DOM-Integration mit tatsächlichen Daten einschließlich Mehrfachzuordnung, neuer Liste, Notizerhalt, Rückgängig, simulierter Speicherquota, Suche ohne doppelte Sterne und externem Speicherereignis bestanden; keine JavaScript-Fehler.


## Benchmark, Watchlists und gespeicherte Vergleiche (19.10.2026)

Neue Ansichten unter Aktienanalyse: `#benchmarkCompare`, `#watchlists` und `#comparisonWorkspace`. Benchmarkvergleich mit SPY als S&P-500-ETF-Proxy und elf US-Sektor-ETFs, historischen EUR/USD- und USD/KRW-Kursen, Wahl USD/EUR, Kursrendite oder dividendenbereinigter Anbieternäherung, drei Monaten bis fünf Jahren, gemeinsamen Start-/Endtagen und CSV. `benchmarks.py` erfasst 14 Reihen separat vom Aktienuniversum; fehlgeschlagene Abrufe behalten den ursprünglichen Cache-Zeitstempel. Der laufende UTC-Tag bleibt ausgeschlossen. FX nur rückwärts, höchstens vier Kalendertage; keine Interpolation oder Vorwärtsdaten. Lange Kurslücken und extreme Basissprünge sperren den Vergleich. ETF-Gebühren sind im Marktpreis enthalten, persönliche Steuern/Transaktionskosten fehlen; keine Behauptung offizieller Index-Gesamtrenditen oder risikobereinigten Alphas. Branchenauswahl von Aktie 1 beruht auf dem aktuellen Anbieter-Sektor und bleibt ein US-Proxy.

Watchlists: mehrere benannte Listen, Aktien hinzufügen/entfernen, persönliche Research-Notizen, Suche/Sortierung, Übergabe von bis zu vier ausgewählten Aktien, rückgängig machbares Entfernen sowie JSON-Export/Import. Speicherung ausschließlich im Browser unter `cockpit-research-workspace-v1`; Listen und Notizen werden nicht serverseitig übertragen oder zwischen Geräten synchronisiert. Import ersetzt erst nach ausdrücklicher Bestätigung. Versionen, Größen, Zeichenketten und Ticker werden geprüft; Speicherfehler melden keinen Erfolg. Texte werden escaped gerendert. Veraltete Snapshot-/Kurs-/Kennzahlenstände zeigen keinen scheinbar aktuellen Watchlist-Score.

Vergleichsansicht: benannte Konfigurationen für Score- und Benchmarkvergleiche, Wiederöffnen mit aktuellen veröffentlichten Daten, historische Punkte- oder Rangverläufe, Kategorie-Heatmap, Originalabdeckung und basisgeprüfte Kategorieunterschiede zur ersten Aktie. Rang nur innerhalb der Auswahl bei gleichen Profilen und gemeinsamer Basis; fehlende Werte bleiben Lücken, Gleichstände erhalten denselben Rang. Historische Kategorien nutzen dieselbe `CockpitHistory.comparisonSeries`-Logik wie die bestehende Rückrechnung. Übergaben aus Kursvergleich und Rückrechnung sowie zurück zu Quellen/Benchmark sind integriert. Gespeicherte Einstellungen sind keine eingefrorenen Datensnapshots.

Geprüft: 61 Python-Tests, neun Node-Prüfdateien, Integration mit echten 114 Aktienreihen, 14 Benchmark-/FX-Reihen, Währungswechsel, Samsung/USD-Vergleich, lokale Notizen, sichere Textdarstellung, Presets, Heatmap, Rang und Undo ohne JavaScript-Fehler. Workflow erzeugt Benchmarkdaten täglich und veröffentlicht die neue JS-Datei mit SHA-Fingerprint.

## Historische Aktienbasis und Vergleich (19.10.2026, Folgeausbau)

Aktueller Stand: 2.893 Kennzahlenperioden aus 2.416 Quelldokumenten für alle 114 Aktienpositionen. Neu: Unilever und Shell mit exakt bezeichneten IFRS-Berichtswährungen, sechs Samsung-Konzernjahresabschlüsse in Mio. KRW und 13 Acomo-Jahres-/Halbjahresmeldungen in Mio. EUR. Verfügbarkeitsdaten kommen aus Einreichungen oder datierten Originalmeldungen, nicht aus dem Berichtsende. Jahresreihen sind keine lückenlosen Quartalsreihen. Fehlendes operatives Ergebnis wird nicht durch bereinigten Gewinn ersetzt. UL-EPS in EUR wird nicht mit dem USD-ADR-Kurs verrechnet; auch Shell-ADR-EPS bleibt offen.

Für AMD, Broadcom, Walmart, Qualcomm und Costco sind 133 zusätzliche Perioden mit belegter EPS-/Aktienbasis hinterlegt. Diluted EPS wird gegen Gewinn und gewichtete verwässerte Aktienzahl derselben Einreichung/Periode abgeglichen. TTM verwendet berichtetes FY, vier Quartale oder berichtetes YTD + vorheriges FY − vorheriges YTD als explizite Näherung. Keine erfundenen Q4-EPS. Rohwerte, Faktoren, Operanden, Einreichungsdaten und Splitbelege bleiben im Paket. Die Kursabfrage speichert Split-Ereignisse; Abweichungen vom geprüften Paket sperren diese Bewertung. Andere Instrumente werden nicht pauschal freigegeben. Keine historischen Analystenrevisionen: weiterhin kein vollständiger historischer 100-Punkte-Score.

Exxon (alte CIK 34088) und BlackRock (alte CIK 1364742) erhalten 43 zusätzliche Vorgängerperioden nach belegter 1:1-Fortführung. GE-Vernova- und Sandisk-Abspaltungen erhalten keine Kursgeschichte der Mutter. Ursprüngliche Einreichungsdaten bleiben unverändert.

„Score-Verlauf → Rückrechnung · 5 Jahre“ vergleicht bis zu vier Aktien. Standard: nur gemeinsam belegte Kategorien je Monat, originale Punkte und originale Abdeckung separat. Unterschiedliche Profile haben gemeinsam nur Marktrisiko. Wechsel des Komponentensatzes unterbrechen Verbindungslinien. Kategoriebeiträge am gewählten Monatsende, eigener Abdeckungsverlauf, Eingaben-/EPS-Belege und CSV mit Vergleichsbasis ergänzen den Chart. Aus dem Branchenvergleich können Auswahlen direkt übernommen werden. Separate Rückrechnungsvariante `research-v7.5-reconstruction-v2`, unveränderte Schwellen/Gewichte und unverändertes beobachtetes Archiv.

Quellenpflege außerhalb der täglichen CI: `python tools/collect_international_history.py`, `python tools/collect_predecessor_history.py`, `python tools/audit_historical_eps.py`. Quellenpakete `historical-international.json`, `historical-predecessors.json` und `historical-eps-audit.json` werden fingerprintet geladen. EPS-Overlays greifen nur bei identischem Ticker, Berichtsende, Periodenlänge, Publikationsdatum und ursprünglichem Dokumenthash. Prüfung: 58 Python-Tests, acht Node-Prüfdateien sowie Integration mit tatsächlichen Daten.

Kostenloses öffentliches Research-Dashboard auf GitHub Pages. Keine Depotbestände, Zugangsdaten oder kostenpflichtigen Dienste.

## Research-Erweiterungen (19.10.2026)

Umgesetzt in der Reihenfolge Historie → Datenlücken → Branchenvergleich → Opportunity-Scanner. Neue Ansichten: `#financialHistory`, `#researchGaps`, `#sectorPeers`, `#opportunityScanner`.

- Historie: 2.526 zusätzliche SEC-XBRL-Kennzahlenperioden; insgesamt 2.799 Perioden für 110 Aktienpositionen aus 2.339 verknüpften Quelldokumenten. Alle 82 neu aufgenommenen Aktien haben Periodendaten. Rohwerte, Quartale/Jahre/Halbjahre, Einreichungs-/Veröffentlichungsdaten, Q4-Ableitung und Quellen werden angezeigt; SVG-Chart, Tastatur-/Touch-Auswahl und CSV. Neue SEC-EPS-Bewertungen bleiben ohne verifizierte Aktien-/Splitbasis offen. Vier internationale Titel bleiben ohne geeignete historische Quellen. Kurze Historien nach Gesellschaftswechseln werden nicht mit Vorgängerfirmen gleichgesetzt.
- Datenlücken: gesperrtes und insgesamt offenes Modellgewicht, Aktualität, Historie und begrenzter Primärumfang; keine Gleichsetzung mit potenziellem Punktegewinn. P1/P2/P3, Suche, Universums- und Themenfilter, konkrete Prüfaufträge, CSV.
- Branchenvergleich: gleiches Modell, Profil, Branchenlabel, Kategorien und Abdeckung. Unter drei Emittenten keine Rangfolge; Bewertungsmedian erst ab fünf unterschiedlichen Emittenten. GOOG/GOOGL werden für Mediane einmal gezählt. Bis zu vier Aktien in den bestehenden Kurs-/Kennzahlenvergleich übernehmen; CSV.
- Scanner: feste Recherchefilter für Score +5, P/E −10% bei gleicher EPS-/Berichtsbasis, Bewertung ≥20% unter vergleichbarem Peer-Median mit Mindestpunkten bei Wachstum/Qualität, und Kurs ≥20% unter dem adjustierten 252-Handelstage-Hoch (mindestens 201 gültige Beobachtungen). Kein erfundener Vergleichsstand für neue Aktien; veraltete Daten blenden Signale aus. Jede Fundstelle zeigt Auslöser, Datenstand und Lücken. Keine Prognosevalidierung.

`historical_sources.py` lädt und fingerprintet Originalpakete plus `data/historical-sec/part-*.json`. `discovery.py` erzeugt `data/research-discovery.json` nach der Rückrechnung. Kuratierung: `python tools/collect_sec_history.py`; die Quellenbeschaffung läuft bewusst nicht automatisch in CI. Der bestehende tägliche Workflow berechnet die Ansichten aus veröffentlichten Kursen und kuratierten Quellen neu. Lokale Integration: 53 Python-Tests, acht Node-Prüfdateien, reale 114 Kursreihen und archivierte Original-Snapshots. Details siehe `IMPLEMENTATION_REPORT.md`.

Aktuelle Erweiterung (19.10.2026): feste Top-100-Auswahl nach Indexgewichts-Näherung aus den offiziellen täglichen SPY-Beständen vom 16.10.2026. 100 Aktienpositionen einschließlich getrennter Aktienklassen; 18 Überschneidungen mit den bisherigen 32 Aktien ergeben 114 eindeutige Positionen und 82 Ergänzungen. Keine automatische Rotation. `data/sp500-selection.json` enthält Ränge, Fondsgewichte, Quell-URL, Datenstand und SHA256; Fondsgewichte sind ausdrücklich keine unabhängig bestätigten Original-S&P-Gewichte. Die bisherigen Aktien bleiben enthalten. Filter für Übersicht, aktuelle Scores und Kurstabelle sind synchronisiert; historische Vergleiche behalten ihre eigene Aktienauswahl. Aktuelle Kurs- und Kennzahlenabrufe erfolgen mit maximal drei parallelen Aufgaben. Die Tagesarchive bleiben unverändert; neue Aktien werden erst in künftigen Archivständen beobachtet. Historische Originalkennzahlen wachsen schrittweise, fehlende Eingaben werden nicht ersetzt. Banken, Versicherer und REITs der Erweiterung verwenden passende Sonderprofile.

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

Pages benötigt `index.html`, die sieben JS-Dateien (`insights`, `research`, `dashboard`, `reconstruction`, `workspace`, `research_next`, `experience`) und `data/`; Python und Tests werden nicht ausgeliefert.

## Monatliche Rückrechnung (separate Modellvariante)

`reconstruct.py` berechnet 60 abgeschlossene Monatsenden. Die Oberfläche unter „Score-Verlauf → Rückrechnung · 5 Jahre“ vergleicht bis zu vier Aktien, einzelne Komponenten und Abdeckung; Monatsdetails zeigen Eingaben und Quellen. CSV und JSON sind exportierbar. Die Rückrechnung wird nicht in das unveränderliche beobachtete Archiv geschrieben.

Abdeckung: 140 Original-Quartalsmeldungen von Microsoft, Apple, NVIDIA, Alphabet, Meta und Amazon ab 2020/2021 bis Juni/Juli 2026, kompakt in `data/historical-reports.json`. Andere Aktien erhalten ausschließlich historische Risikopunkte. Ein Bericht darf erst nach seinem Veröffentlichungstag und vor dem tatsächlichen Kursstichtag genutzt werden. Datumsgleiche Veröffentlichungen werden konservativ ausgeschlossen. Keine späteren Kennzahlen oder Analystenschätzungen werden rückwärts eingesetzt. Finanzdaten verfallen nach 210 Tagen.

Gleiche V7.2-Schwellen, eigene Modellversion `research-v7.2-reconstruction-v2`: quartalsweises Umsatzwachstum, TTM-Marge aus vier zusammenhängenden Quartalen, KGV-Näherung aus der Summe gerundeter diluted Quartals-EPS und historische Volatilität. EPS-Summe ist wegen Rundung und veränderter gewichteter Aktienzahlen kein exaktes TTM-EPS. Gemeldete EPS bleiben unverändert im Quellenpaket. Ein belegter späterer Splitfaktor normalisiert die EPS auf dieselbe Aktienbasis wie die splitbereinigten historischen Kurse (NVIDIA 4:1/10:1, Alphabet und Amazon 20:1). Publication-Date statt Berichtsende bestimmt die ursprüngliche Aktienbasis. Unbelegte Basis sperrt die KGV-Näherung. Revisionen fehlen: maximal 85% Abdeckung, kein hochgerechneter Gesamt-Score. Heute geladene Kursreihen und Emittentenseiten können rückwirkend geändert worden sein; Quellenhashes sind keine historischen Zeitstempel. Auswahl-/Survivorship-Bias bleibt bestehen. Kein Rendite-Backtest.

`tools/collect_reconstruction_sources.py` erstellt das Quellenpaket erneut (lxml und Poppler/pdftotext erforderlich; separat von der täglichen CI). Neue Quartalsmeldungen müssen dort ergänzt und geprüft werden. Die CI berechnet monatliche Stände aus dem geprüften Paket und aktuellen historischen Kursreihen neu. Sie archiviert diese Rückrechnung ausdrücklich nicht als damals beobachtete Daten.

## V7.3 Oberfläche: Einordnung und beobachtete Veränderungen

`insights.js` stellt Verfügbarkeit, Aktualität, Plausibilität und begrenzte Primärbestätigung getrennt dar. Hohe Modellabdeckung wird nicht als unabhängig bestätigte Datenqualität dargestellt. Teil-Scores zeigen belegte Punkte und Abdeckung getrennt, keine missverständliche Teilpunkte/Abdeckung-Bruchdarstellung.

Frühere Aktienlisten, Quantum-Zahlen, Bewertungshistorien, Gewichtslabore, externe Diagnostik und explorative Backtests liegen unter Archiv. Bestehende Deep Links bleiben gültig. Sie sind andere Daten-/Modellstände und validieren das aktuelle Modell nicht.

Der Aktienvergleich verwendet die Kennzahlen des jeweiligen Profils (P/B, ROE, AFFO, NAV/NII, Cash available). Anbieter-P/E und Forward-P/E bleiben als zusätzliche, nicht ersetzende Referenzquotienten zugänglich. Modellversion, Berichtsende und Quellen sind sichtbar.

„Score-Veränderungen“ vergleicht zwei vollständige Original-Snapshots aus dem beobachteten Archiv. Nur bei identischer Modellversion, Profil und Gewichten werden gemeinsam belegte Komponenten subtrahiert. Hinzugekommene/verlorene Abdeckung erhält keine scheinbare Punktedifferenz. Gesamtänderungen gibt es nur bei vollständigen vergleichbaren Scores; Modellwechsel werden nebeneinander ohne numerischen Delta gezeigt. Eingabeänderungen und gespeicherte Regeln sind keine kausale Attribution. Gleiches Kursdatum an mehreren Archivdaten wird ausdrücklich genannt. Die Score-Methodik selbst bleibt research-v7.2.0.

Zusätzlicher Check: `node tests/test_insights.cjs`.


## V7.4: Aktienansicht, Änderungen und Chartbedienung

`workspace.js` bündelt Kursverlauf, profilabhängige Kennzahlen, fünf Score-Komponenten, Rückrechnung und Quellen in „Aktienanalyse → Aktien im Detail“. Dashboard-Details führen direkt zum gewählten Unternehmen. Historische Monatsdetails zeigen Komponenten und verwendete Quartalsmeldungen. Der aktuelle vollständige Research-Score wird weiterhin getrennt von rekonstruierten Teilpunkten gezeigt.

„Was ist neu?“ nutzt die letzten beiden archivierten Stände derselben Modellversion: veränderte Punkte/Eingaben, neueres Berichtsende im Anbieterbestand und offene Primärprüfungen. Neue Berichtsstände sind keine vollständige Earnings-Erkennung oder unabhängige Quellenbestätigung. Bei identischen Kursstichtagen werden keine neuen Marktereignisse behauptet.

Kurs-, beobachtete Score- und Rückrechnungs-Charts besitzen eine gemeinsame Stichtagsanzeige für alle ausgewählten Linien. Maus, Berührung, Links/Rechts, Home/End und ein natives Datums-Auswahlfeld werden unterstützt. Im Rückrechnungsvergleich öffnet ein Klick oder Enter den Monat für Details. Auf schmalen Bildschirmen zeigt das Dashboard Aktienkarten; Navigation und Bedienelemente bleiben per Touch bedienbar.

Die Ergänzung erfolgt mit `tools/extend_reconstruction_sources.py` und `tools/collect_alphabet_sources.py` (lxml/Poppler). Beide ergänzen das geprüfte Quellenpaket, statt beim einzelnen Abruffehler bestehende Berichte zu löschen. Neue Meldungen und Splits müssen weiterhin geprüft ergänzt werden. Zusätzliche Regression: `node tests/test_workspace.cjs`.


## V7.5: Eingabeprüfung, zusätzliche Originalberichte, Monitor und Score-Diagnostik

Das Live-Modell heißt jetzt `research-v7.5.0`, die Rückrechnung `research-v7.5-reconstruction-v1`. Gewichte und Skalen bleiben gleich; neue Sperrregeln und historische Branchenmethoden begründen eigene Versionen. Frühere beobachtete Stände bleiben unverändert. Modellwechsel erhalten keine scheinbare Score-Differenz.

`validation.py` prüft Antwortsymbol, Berichts-/Handelswährung, P/B gegen Kurs/Buchwert und extreme Buchwertquotienten. Berkshire B braucht eine ausdrücklich belegte B-Buchwertbasis; es gibt keine automatische A/B-Skalierung. Große Sprünge in adjustierten Kursreihen sperren das Marktrisiko zur Prüfung. Sperren gelten je Kategorie. Vier belegte Original-Quartals-EPS können als begrenzte Primärreferenz dienen, ausschließlich bei passender Periode, Währung und dokumentierter Splitbasis. Dies bestätigt weder Kurs noch Konsens oder Fair Value.

`data/historical-extensions.json` ergänzt 133 Originalberichte: JPM 27, Allianz 25, Siemens Energy 24, Realty Income 27, Ares Capital 15, LVMH 13 und Generali 2. Zusammen mit den bisherigen 140 Meldungen sind 273 Originalberichte von 13 Emittenten hinterlegt. Jedes Dokument hat Veröffentlichung, Periode, Original-URL und SHA256. Halbjahres-/Jahresperioden bleiben so gekennzeichnet. Operative TTM-Marge: vier Quartale, ein FY oder H1 + vorheriges FY − vorheriges H1. LVMH-Halbjahresvergleiche verwenden die Vorjahres-H1-Spalte, nicht die benachbarte FY-Spalte. Die zuvor fehlenden H1-Berichte 2022/2024 stammen aus den Original-PDFs der Emittentenmeldungen; ein falsch verlinkter Präsentationsanhang wird nicht als Abschluss verwendet. Generali 2024/2025 verwendet den berichteten IFRS-Gruppengewinn, nicht den bereinigten Gewinn; Buchwert je Aktie und vergleichbare IFRS-ROE bleiben offen. Fehlende Berichte erzeugen Lücken. Europäische EPS-Bewertungen bleiben ohne belegte historische Aktienbasis gesperrt.

Der Berichtsmonitor prüft zusätzlich die offiziellen Berichtskataloge von JPMorgan, Allianz und Siemens Energy. Die Meta-RSS-Adresse entspricht dem aktuellen offiziellen RSS-Link. Die Quellenstatistik trennt einzelne Endpunkte von Unternehmen mit mindestens einer erreichbaren Quelle. Katalogperioden sind keine Veröffentlichungsdaten: Solche Fundstellen tragen `publishedAt: null` und bleiben in der Prüfqueue, ohne Finanzzahlen oder Scores automatisch zu ändern. Nicht erkennbare Katalogstrukturen werden als Fehler ausgewiesen, nicht als erfolgreicher leerer Suchlauf. Lokale Nachkuratierung der vier Lücken: `python tools/collect_gap_sources.py` (lxml und Poppler; nicht Teil der automatischen Finanzdatenfreigabe).

JPM nutzt berichteten Gewinn, Buchwert und annualisierte Quartals-ROE (keine ROTCE). Allianz nutzt berichteten Anteilseignergewinn; Core-EPS/ROE werden nicht als GAAP-Kennzahlen ersetzt. IFRS17/IFRS9 ist gekennzeichnet. Siemens Energy nutzt keinen bereinigten Gewinn als operativen IFRS-Gewinn; fehlende Q4-Margen bleiben offen. REITs nutzen originales AFFO und historische Ausschüttungsdeckung je Aktie, eine ausdrücklich andere Variante als die aktuelle Gesamtbetragsdeckung. BDCs nutzen NAV, GAAP-NII, Ausschüttung und Verschuldung; Core-EPS ist kein NII-Ersatz. Weitere Unternehmen und fehlende Kennzahlen bleiben sichtbar unvollständig.

`tools/collect_expanded_sources.py` ist ein separater, manuell zu prüfender Sammler (lxml/Poppler); die gespeicherte SEC-Exhibit-Auswahl liegt unter `tools/sec-report-links.json`. Er aktualisiert das Quellenpaket, ohne fehlgeschlagene Dokumente durch geschätzte Werte zu ersetzen. Vier dokumentierte Sammlerfehler betreffen drei fehlende Perioden und eine nicht passende Sondermeldung. Neue Exhibit-Links müssen nach unabhängiger Quellenprüfung ergänzt werden.

`monitor_reports.py` läuft täglich mit dem Datenjob. Unter „Daten → Quartalsberichte“ stehen Anbieter-Berichtswechsel für alle 32 Aktien sowie konfigurierte offizielle RSS-/SEC-Prüfungen. Die Oberfläche unterscheidet neue Anbieterperiode, spätere Fundstelle, fehlende erste Quelle und hinterlegte Referenz. Nicht erreichbare Quellen bleiben unbekannt. Weder ein Treffer noch kein Treffer bestätigt geprüfte Zahlen oder vollständige Earnings-Abdeckung. Kandidaten aktualisieren keine kuratierten Eingaben automatisch; es werden keine externen Nachrichten versandt.

`evaluation.py` erstellt „Aktienanalyse → Score-Auswertung“: feste Regeln, 6/12 Kalendermonate, Einstieg erst zum nächsten verfügbaren adjustierten Schlusskurs nach dem Signal; nur gereifte Ergebnisse. Vor 2024 liegt der Entwicklungszeitraum, ab 2024 der Prüfzeitraum. Entwicklungsfenster über der Grenze werden entfernt. Feste Januar-/Juli- beziehungsweise Januar-Anker und zusätzliche Überlappungsprüfung verhindern überlappende Fenster je Aktie/Horizont. Kein Fit und keine Gewichtsoptimierung. Vergleichbare Segmente halten Modell, Profil, Abdeckung, Komponenten und Wachstumsperiode getrennt; Rangkorrelation braucht mindestens vier Aktien derselben Stichtagskohorte. Rückrechnung und beobachtetes Archiv werden separat ausgewertet. Noch unreife beobachtete Horizonte bleiben offen. CSV/JSON und Einzelbeobachtungen legen Grenzen und Kurstage offen.

Die Zeitteilung ist rückblickend und kein damals versiegelter Holdout. Heutiges Universum, nachträglich geladene Kursreihen, kleine Stichproben, fehlende Kosten und FX begrenzen die Aussage. Die Diagnose belegt keine Prognosekraft oder Überrendite.


## Kompakte Oberfläche, Themen und erklärbare Veränderungen

`experience.js` ergänzt verständliche Treiberkarten in „Score-Veränderungen“: Kurs-/Bewertungsdaten, veränderte Kennzahlen, Anbieter-Berichtsperioden, Konsens, Risiko und Datenfreigaben. Kategorie-Punktedifferenzen stammen ausschließlich aus den Originalständen. Reine Kurseffekte werden nur bei unveränderter passender Kennzahl, Währung und entsprechend proportionaler Bewertungsquote benannt. Sonst bleibt die gemeinsame Änderung sichtbar; es gibt keine erfundene Kausalzerlegung. Modellwechsel und neue/verlorene Abdeckung erhalten keine scheinbaren Gesamtgewinne. Alle ursprünglichen Werte/Regeln bleiben aufklappbar. EPS, Buchwert und Eingabesperren sind jetzt ebenfalls im Eingabevergleich enthalten. Das Research-Modell und das unveränderliche Archiv werden dadurch nicht geändert.

Die Kopfzeile enthält keine Versions- oder Kostenlosigkeitswerbung. Dark/Light folgt zunächst der Systempräferenz; eine ausdrücklich gewählte Einstellung wird unter `cockpit-theme` lokal gespeichert. Die Darstellung benötigt weder Konto noch neue Dienste. Längere Texte, Quellen und Berechnungen öffnen auf Wunsch native Infodialoge mit Escape/Schließen und Fokusrückgabe. Kurze Hinweise auf Teilbewertungen, fehlende Daten und Forschung bleiben sichtbar.

Unter 760 Pixeln stehen ein Navigationdialog, eine feste Schnellnavigation, 44-Pixel-Bedienelemente und native Auswahlfelder mit 16-Pixel-Schrift zur Verfügung. Aktienvergleich, Scores und Score-Veränderungen erhalten Karten statt breiter Tabellen. Zusätzliche Quellen/Quotienten bleiben aus den Vergleichskarten erreichbar. Charts berechnen Achsen und Plotbreite aus der tatsächlich verfügbaren Breite; Datumswahl und gemeinsame Stichtagsanzeige bleiben erhalten. Reagiert auf Breitenänderungen und behält die Auswahl bei. `responsive-preview.html` zeigt echte 390-/768-Pixel-Iframe-Viewports für die visuelle Abnahme; dies ersetzt keinen Test auf einem physischen iPhone.

Prüfungen: `node tests/test_experience.cjs` für Treiber, EPS-Basis, Berichtswechsel, Freigaben und Modellgrenzen. Lokale DOM-Integration prüft Theme-Speicherung, Dialoge/Fokus, Navigation, Vergleichskarten und 350-Pixel-Charts. Die neue UI-Datei wird mit SHA-Fingerprint veröffentlicht.

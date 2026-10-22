# Research-Erweiterung 19.10.2026

## Eigener Bereich für Datenqualität (22.10.2026)

Universumsfilter enthalten nur noch Alle Aktien und S&P 500 Top 100; die bisherige 32er-Auswahl ist in allen aktuellen Ansichten entfernt. Der Header zeigt Investment Research ohne Aktienanzahl. Der Hauptbereich Daten heißt Datenqualität. Kursverfügbarkeit, Primärprüfung, Statusanzeige, Berichtsprüfung und Qualitätshinweise sind dort gebündelt. Die erste Übersicht beginnt direkt mit der Aktienliste. Datencheck-Spalte und Primärhinweise auf mobilen Übersichtskarten sind dort ausgeblendet; Prüfdetails bleiben im eigenen Bereich und in Einzelaktienansichten verfügbar. Such-/Watchlist-Filter und Sortierung bleiben bestehen.

Syntax, bestehende Experience-/Discovery-Prüfungen und DOM-Integration mit tatsächlichen Daten bestanden: keine Original-Auswahl in aktuellen Filtern, Qualitätsblöcke im eigenen Tab, Header ohne Aktienanzahl, unveränderte Suchrücksetzung, Navigation und historische Charts. Live-Abnahme nach Veröffentlichung.

## Vereinfachte Oberfläche (22.10.2026)

Sechs aufgabenbezogene Einstiege: Übersicht, Aktien, Watchlists, Vergleichen, Verlauf und Daten. Gleiche Struktur im mobilen Menü, direkte Hauptziele ohne überraschenden Sprung zur zuletzt besuchten Unteransicht. Ältere Modellansichten sind nicht mehr in der Navigation auswählbar; alte Hash-Lesezeichen führen zur passenden aktuellen Ansicht. Interne Legacy-Elemente bleiben inert, da Datenladefunktionen sie weiterhin referenzieren. Keine Löschung historischer Nachweise oder persönlicher Watchlists.

Die Übersicht zeigt Titel, kompakte Gesamtkennzahlen und die durchsuchbare Aktienliste zuerst. Doppelte Einstiegsleisten entfallen; Marktüberblick, Änderungsfeed und Berichtsprüfung sind gemeinsam aufklappbar. Such-/Universums-/Watchlist-/Sortierfelder sind beschriftet, Filter lassen sich gemeinsam zurücksetzen. Score-Erläuterung im Dialog. Sortierwahl und Watchlists bleiben browserlokal erhalten. Tägliche und rekonstruierte Score-Verläufe bleiben nutzbar, historische Stände alter Modelle sind in Modell- und Datumswahlen nicht mehr auswählbar. Keine Vermischung von Modellversionen.

Geprüft: JavaScript-Syntax, bestehende Kernprüfungen sowie DOM-Integration mit echten Daten für Navigation, mobile Menübedienung, alte Lesezeichen, aktuelle Modellwahl, erhaltene Diagramme und Suchrücksetzung. Live-Abnahme erfolgreich: https://github.com/bastihouse/investment-cockpit/actions/runs/39744267727 (Refresh 70 Sekunden, Deployment 9 Sekunden). Sechs Hauptbereiche, Suche und Filterrücksetzung (1/114 → 114/114), Score-Hilfe, täglicher Verlauf mit zehn Chart-Punkten und genau einem versteckten aktuellen Modell geprüft. Mobile Menüwahl öffnet Watchlists und schließt den Dialog; Vergleichseinstieg und Unterbereiche nutzbar. Smartphone 390px und Tablet 768px ohne horizontale Seitenüberbreite (375/375 bzw. 753/753 CSS-Pixel). Keine physischen Geräte geprüft. Bestehende Sortier-/Watchlist-Integration einschließlich Neuladen und Speicherfehlern bestanden; keine JavaScript-Fehler in der DOM-Integration.

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


## Folgeauftrag: Benchmarkvergleich, Watchlists, Vergleichsansicht

Umgesetzt sind drei neue Ansichten: konsistenter Renditevergleich mit SPY und elf US-Sektor-ETF-Proxies, lokale Watchlists mit Notizen und Sicherung sowie benannte Vergleichskonfigurationen mit historischen Rängen, Heatmap und Kategorieunterschieden. Gemeinsame abgeschlossene Tage und gemeinsame Darstellungswährung verhindern lokale-Währungs-Mischvergleiche. Dividendenbereinigung bleibt eine Anbieternäherung, ETF-Proxies bleiben von offiziellen Indexrenditen getrennt. Datenabrufstatus und Cache-Zeitstempel bleiben nachvollziehbar. Kein aktueller UTC-Tag, kein zukünftiger FX-Wert, Carry höchstens vier Tage. Fehlende historische Kategorien werden nicht hochgerechnet; Ränge gelten ausschließlich für gleiche Profile und gemeinsame Kategorien in der Auswahl.

Watchlists, Notizen und Presets bleiben ausschließlich lokal. JSON-Import ist versioniert und validiert; Überschreiben erfordert eine ausdrückliche Bestätigung in der Oberfläche. Entfernen ist rückgängig machbar. Private Inhalte landen weder im Repository noch in generierten Marktdatendateien. Gespeicherte Vergleiche verwenden bei erneutem Öffnen aktuelle veröffentlichte Daten.

Lokale Prüfung: 61 Python-Tests, neun Node-Prüfdateien und DOM-Integration mit tatsächlichen Daten bestanden. Alle 14 Benchmark-/FX-Reihen erreichbar. EUR-Preisvergleich Samsung/Microsoft/SPY: 237 gemeinsame abgeschlossene Beobachtungen 20.10.2025 bis 16.10.2026 im geprüften Stand. Watchlist-Anlage, sichere Notiz mit HTML-Zeichen, Speicherung, Sortierung, Übergabe, Wiederherstellen eines Presets und Undo ohne JavaScript-Fehler geprüft. Die folgenden Abschnitte dokumentieren vorherige Ausbaustufen.

## Folgeauftrag: EPS-/Splitbasis, verbleibende Historien und Score-Vergleich

Umgesetzt: 133 zusätzliche EPS-Basisprüfungen für AMD/AVGO/WMT/QCOM/COST, 51 internationale Kennzahlenperioden für UL/SHEL/005930/ACOMO sowie 43 belegte Vorgängerperioden für XOM/BLK. Insgesamt 2.893 Perioden für 114 Positionen aus 2.416 verknüpften Dokumenten. EPS-Overlays bleiben vom Rohpaket getrennt und sind an dessen genaue Quellenidentität gebunden. Kein pauschales Freischalten unreviewter Instrumente. Operanden werden im selben Filing gegen Gewinn/Aktienzahl abgeglichen, spätestens zur Originalveröffentlichung verfügbar; spätere Vergleichsperioden werden nicht zurückdatiert. Berichtete FY-/YTD-EPS sind eine TTM-Näherung und ersetzen keine fehlenden Quartals-EPS.

Lokal ergeben sich 297 zusätzliche Monatsbewertungen mit EPS-Näherung bei den fünf ergänzten Instrumenten. Alle vier bisher fehlenden internationalen Titel haben Kennzahlenperioden, aber keine erfundene lückenlose Quartals-/Bewertungsabdeckung. Internationale ADR-, Währungs- und sonstige ungeklärte EPS-Basen bleiben gesperrt. Börsennotierungen von GEV/SNDK werden nicht vor ihren eigenständigen Handelsbeginn verlängert.

Erweiterter Vier-Aktien-Vergleich: gemeinsam belegte Kategorien je Monat als Standard, originale Abdeckung separat, Kategoriebeiträge am ausgewählten Stichtag, Abdeckungsverlauf, Wechsel der Vergleichsbasis, CSV mit Komponenten und Maximalpunkten sowie direkte Übergabe aus Peer-Gruppen. Profilübergreifend ist nur Marktrisiko gemeinsam; Verbindungslinien werden bei Basiswechseln unterbrochen. Rückrechnung v2, beobachtetes Archiv unverändert.

58 Python-Prüfungen und acht Node-Prüfdateien bestanden; Quellenhashbindung, Publikationsgrenzen, Splitabweichungen, EPS-/Aktienzahlkonflikte, YTD-Arithmetik, internationale Einheiten und Vorgängergrenzen geprüft. Die folgenden Abschnitte dokumentieren den vorherigen Ausbau und dessen damaligen Datenstand.

Angeforderte Reihenfolge: 1 Historische Kennzahlen, 4 Datenlücken, 2 Branchenvergleich, 3 Opportunity-Scanner. Alle vier Funktionen sind implementiert.

## Daten und Methodik

97 zusätzliche Aktienpositionen haben SEC-XBRL-Perioden; zusammen mit den bestehenden Emittentenquellen ergeben sich 110 von 114 Positionen. Alle 82 Universums-Ergänzungen sind enthalten. 2.799 Kennzahlenperioden aus 2.339 verknüpften Quelldokumenten; Einreichungen können mehrere Perioden enthalten. Einreichungsdaten werden konservativ nach dem tatsächlichen Handelsschluss verfügbar. Jahres-/Halbjahres-/Quartalswerte bleiben getrennt. Q4-Ableitung ist explizit Jahreswert minus neun Monate, ohne EPS-Subtraktion; Operanden, Konzepte, Accession und Quelldatei-Hash sind erhalten. Erstes passendes öffentliches Filing je Periode; keine Rückdatierung späterer Veröffentlichungen. Aktuelle SEC-Aggregate sind keine damals archivierte Datenbank und können nachträgliche Änderungen enthalten.

EPS-Bewertungen neuer Quellen bleiben ohne geprüfte Aktien-/Splitbasis gesperrt. Banken und Versicherungen verwenden berichtete Gewinnwerte; REIT-/Royalty-/Holding-Spezialkennzahlen werden durch Umsatz oder operative Marge nicht ersetzt. Für Gesellschaftswechsel gibt es keinen unbelegten Vorgänger-Backfill. Samsung, Unilever, Shell und Acomo haben in diesem Paket keine passende historische Primärreihe.

## Funktionen

- Historische Kennzahlen: adaptive SVGs mit Touch-/Tastatur-Stichtagswahl, Periodenart, Kennzahl, Quellendetails und CSV; Übergang zur Score-Rückrechnung.
- Priorisierte Lücken: aktuelle Sperren/offenes Gewicht, Datenalter, historische Abdeckung und Primärumfang; P1/P2/P3 und konkrete Prüfaufträge. Fehlendes Gewicht ist keine erwartete Verbesserung.
- Peer-Gruppen: identisches Modell, Profil, Branche, Abdeckung und Komponentensatz; Rangfolge ab drei Emittenten, Bewertungsmedian ab fünf. Aktienklassen im Median dedupliziert. Vergleichsübergabe bis vier Aktien.
- Scanner: feste Schwellen, reale integritätsgeprüfte Archivdateien, kein Delta bei fehlendem früherem Stand oder extremem Kurs-/Aktienbasiswechsel. P/E nur bei nahezu gleichem EPS und gleicher Periode. Peer-Abschlag nur mit Mindestpunkten bei Wachstum/Qualität. Drawdown ohne erkennbare Kursbasis-Sprünge, mit mindestens 201 gültigen adjustierten Schlusskursen. Treffer sind Recherchehinweise, keine Handelsstrategie.

## Prüfung

53 Python-Tests und acht Node-Prüfdateien bestanden. Source-Invarianten, Q4-Arithmetik, Zeitgrenzen, gesperrte EPS-Basis, Profil-/Abdeckungsgrenzen, dünne Peer-Gruppen, Aktienklassenduplikate, fehlende Baselines, Zukunftsdaten und fehlerhafte Kursbasis geprüft. DOM-Integration mit realem Datensatz: Historienchart/Periodenwahl, Berkshire-Nettoergebnis, Lückenfilter, Übergabe in Aktienvergleich und Scannerfilter ohne JavaScript-Fehler.

Lokaler Datenabgleich: 607 gereifte retrospektive Diagnosefälle; keine gereiften beobachteten Resultate. 8 Aktien mit Priorität 1, 35 Aktien mit Recherche-Signal (8 Peer-Abschläge, 31 Kursrückgänge, Überschneidungen möglich). Keine Score-/P/E-Veränderungssignale bei den vorhandenen kurzen und weitgehend unveränderten Vergleichsständen. Diese Zahlen gelten für den geprüften Stand und werden beim produktiven Lauf neu berechnet.

## Sinnvolle nächste Schritte

1. Historische EPS-/Splitbasis und Spezialkennzahlen gezielt anhand der Lückenqueue ergänzen.
2. Historien von Vorgängerfirmen bei Gesellschaftswechseln separat prüfen.
3. Neue beobachtete Tagesstände sammeln und die festen Signale nach ausreichend gereiften Zeitfenstern auswerten.

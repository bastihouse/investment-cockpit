# Research-Erweiterung 19.10.2026

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

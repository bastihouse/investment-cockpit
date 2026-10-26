# Investment Cockpit V7.5

Status am 26.10.2026: Vollständig auf GitHub veröffentlicht und auf GitHub Pages live. Die GitHub-Integration verweigert weiterhin Schreibzugriffe (HTTP 403); die Veröffentlichung gelang über den wieder verfügbaren GitHub-Browsereditor und Datei-Upload. Erfolgreicher Workflow: https://github.com/bastihouse/investment-cockpit/actions/runs/40312434981 (refresh 72 Sekunden, deploy 10 Sekunden). Alle sieben zuletzt ausstehenden Code-/Testdateien stimmen per Git-Blob-SHA mit dem geprüften lokalen Stand überein. Live geprüft: fünf Hauptbereiche ohne separaten Verlauf, gemeinsame Score-Linien (gestrichelt/durchgezogen), QQQ-Renditevergleich, Methodikerklärung und vereinfachte Datenqualität. Smartphone-/Tablet-Layouts in echten 390-/768-Pixel-Iframes visuell geprüft; kein Test auf physischen Geräten. Desktop ohne horizontale Seitenüberbreite. Einzelne Browser-Automationsabfragen in den Iframes liefen in Timeouts; die Navigation wurde anschließend visuell bestätigt. Keine kostenpflichtigen Dienste und keine Änderung der Score-Regeln oder privaten Watchlists.

## Gemeinsamer Vergleich und einfache Score-Erklärungen (26.10.2026)

Ein einziger Vergleichsbereich ersetzt die vier bisherigen Vergleichs-Unteransichten und den separaten Verlaufseinstieg. Zwei Aktien als Start; weitere Aktien, Index-ETF-Benchmarks und Branchenmediane dynamisch per Plus ergänzen oder entfernen. Keine künstliche Vier-Aktien-Grenze. Kennzahlenwahl mit Score, Komponenten, Abdeckung, Kurs, Kurs-/dividendenbereinigter Renditenäherung, KGV, Forward-KGV, Geschäftszahlen und vorhandenen numerischen Spezialkennzahlen. Historischer Verlauf und aktueller Stand im selben Arbeitsbereich. Browserlokale Auswahl unter cockpit-unified-comparison-v1, CSV mit Herkunft und Berechnungsbasis; bisherige Watchlists bleiben erhalten.

Historische Rückrechnungen sind gestrichelt, tatsächlich gespeicherte Beobachtungen durchgezogen; Farbe bezeichnet die Aktie. Gesamtwerte nur bei vollständiger Abdeckung, keine Hochrechnung von Teilpunkten und keine erfundenen historischen Analystenschätzungen. Basiswechsel, fehlende Werte und längere Datenlücken unterbrechen die Linien. Renditen verwenden gemeinsame Handelstage und historische FX-Kurse mit maximal vier Tagen Rückgriff. ETFs haben keine erfundenen Unternehmens-Scores. Branchenmediane verwenden mindestens drei geeignete heutige Universumsmitglieder; wechselnde Zusammensetzung und eingeschränkte Branchen-/Profilvergleichbarkeit bleiben ausdrücklich erklärt.

Methodik im Header erklärt die fünf Gewichte, tatsächlichen Schwellen, lineare Zwischenwerte, Spezialprofile und Grenzen in Alltagssprache. Einzelaktien erklären Bedeutung und Berechnung je Kategorie; Zeitstempel sind lesbar in Wiener Zeit. Auch der Einzelaktien-Score-Chart zeigt beide historischen Herkünfte.

Nasdaq: kein gesonderter vollständiger Nasdaq-100-Import im bisherigen Bestand. Neuer Filter für vorhandene Nasdaq-notierte Aktien anhand der vom Anbieter gelieferten Börsenmetadaten. QQQ ergänzt den Nasdaq-100 als ausdrücklich bezeichneten ETF-Proxy im Benchmark-Datenlauf. Die Provider-Metadaten und Quellen bleiben sichtbar. Datenqualität hat nur noch einen Einstieg; ausführliche Prüfungen und Quellen sind aufklappbar über eine Themenauswahl erreichbar.

Offener Ausbauwunsch von Sebastian: später die Top 100 Aktien des STOXX Europe 600 nach Indexgewicht importieren. In dieser Änderung noch kein Europa-Import.

Validierung: Kernprüfungen für Herkunft, Teil-/Gesamtwerte, fehlende historische Schätzungen, Segmentgrenzen und gemeinsame Renditebasis; Benchmark-Katalog einschließlich QQQ; vollständige Python-Prüfungen und DOM-Integration. Live-Abnahme am 26.10.2026 erfolgt; Details im Veröffentlichungsstatus.

## Eigener Bereich für Datenqualität (22.10.2026)

Universumsfilter enthalten nur noch Alle Aktien und S&P 500 Top 100; die bisherige 32er-Auswahl ist in allen aktuellen Ansichten entfernt. Der Header zeigt Investment Research ohne Aktienanzahl. Der Hauptbereich Daten heißt Datenqualität. Kursverfügbarkeit, Primärprüfung, Statusanzeige, Berichtsprüfung und Qualitätshinweise sind dort gebündelt. Die erste Übersicht beginnt direkt mit der Aktienliste. Datencheck-Spalte und Primärhinweise auf mobilen Übersichtskarten sind dort ausgeblendet; Prüfdetails bleiben im eigenen Bereich und in Einzelaktienansichten verfügbar. Such-/Watchlist-Filter und Sortierung bleiben bestehen.

Syntax, bestehende Experience-/Discovery-Prüfungen und DOM-Integration mit tatsächlichen Daten bestanden: keine Original-Auswahl in aktuellen Filtern, Qualitätsblöcke im eigenen Tab, Header ohne Aktienanzahl, unveränderte Suchrücksetzung, Navigation und historische Charts. Live-Abnahme erfolgreich: https://github.com/bastihouse/investment-cockpit/actions/runs/39745817249 (Refresh 65 Sekunden, Deployment 8 Sekunden). Header ohne Aktienanzahl, genau zwei Universumsoptionen und Qualitätsblöcke im eigenen Tab bestätigt. Score-Sortierung bleibt nach Neuladen erhalten. Smartphone/Tablet ohne horizontale Überbreite (375/375 und 753/753 CSS-Pixel); mobiler Datenqualität-Einstieg geprüft.

## Vereinfachte Oberfläche (22.10.2026)

Sechs aufgabenbezogene Einstiege: Übersicht, Aktien, Watchlists, Vergleichen, Verlauf und Daten. Gleiche Struktur im mobilen Menü, direkte Hauptziele ohne überraschenden Sprung zur zuletzt besuchten Unteransicht. Ältere Modellansichten sind nicht mehr in der Navigation auswählbar; alte Hash-Lesezeichen führen zur passenden aktuellen Ansicht. Interne Legacy-Elemente bleiben inert, da Datenladefunktionen sie weiterhin referenzieren. Keine Löschung historischer Nachweise oder persönlicher Watchlists.

Die Übersicht zeigt Titel, kompakte Gesamtkennzahlen und die durchsuchbare Aktienliste zuerst. Doppelte Einstiegsleisten entfallen; Marktüberblick, Änderungsfeed und Berichtsprüfung sind gemeinsam aufklappbar. Such-/Universums-/Watchlist-/Sortierfelder sind beschriftet, Filter lassen sich gemeinsam zurücksetzen. Score-Erläuterung im Dialog. Sortierwahl und Watchlists bleiben browserlokal erhalten. Tägliche und rekonstruierte Score-Verläufe bleiben nutzbar, historische Stände alter Modelle sind in Modell- und Datumswahlen nicht mehr auswählbar. Keine Vermischung von Modellversionen.

Geprüft: JavaScript-Syntax, bestehende Kernprüfungen sowie DOM-Integration mit echten Daten für Navigation, mobile Menübedienung, alte Lesezeichen, aktuelle Modellwahl, erhaltene Diagramme und Suchrücksetzung. Live-Abnahme erfolgreich: https://github.com/bastihouse/investment-cockpit/actions/runs/39744267727 (Refresh 70 Sekunden, Deployment 9 Sekunden). Sechs Hauptbereiche, Suche und Filterrücksetzung (1/114 → 114/114), Score-Hilfe, täglicher Verlauf mit zehn Chart-Punkten und genau einem versteckten aktuellen Modell geprüft. Mobile Menüwahl öffnet Watchlists und schließt den Dialog; Vergleichseinstieg und Unterbereiche nutzbar. Smartphone 390px und Tablet 768px ohne horizontale Seitenüberbreite (375/375 bzw. 753/753 CSS-Pixel). Keine physischen Geräte geprüft. Bestehende Sortier-/Watchlist-Integration einschließlich Neuladen und Speicherfehlern bestanden; keine JavaScript-Fehler in der DOM-Integration.

## Gespeicherte Sortierung und Watchlist-Filter (20.10.2026)

Sortierspalte und Richtung werden je Tabelle lokal unter `cockpit-table-sorts-v1` gespeichert und nach Neuladen anhand des Spaltennamens wiederhergestellt. Getrennte Tabellen behalten getrennte Wahlen; verschwundene Spalten werden ignoriert. Desktop-Kopfzeilen, mobile Spaltenauswahl und der bisherige Übersichtsfilter verwenden dieselbe Speicherung. Änderungen lesen vor dem Speichern den aktuellen Präferenzstand, um andere Tabellenwahlen aus weiteren Tabs zu erhalten. Beschädigte Präferenzen verhindern die Bedienung nicht; bei einem Schreibfehler gilt die neue Reihenfolge nur im laufenden Aufruf und die Oberfläche meldet den Fehler.

Die Aktienübersicht enthält einen Watchlist-Filter mit Trefferzahl, kombinierbar mit Aktienuniversum und Textsuche. Filterwahl bleibt lokal über Neuladen erhalten (`cockpit-overview-watchlist-v1`). Listenänderungen, Umbenennen, Entfernen, Import/Reset und Änderungen aus anderen Tabs werden über den vorhandenen Workspace übernommen. Eine entfernte gewählte Liste setzt den Filter mit Hinweis auf alle Aktien zurück. Leere Listen zeigen keine zufälligen Gesamttreffer. Marktkennzahlen und Research-Rangfolge oberhalb der Aktienliste bleiben global, was beim aktiven Filter ausdrücklich angezeigt wird. Keine Übertragung von Listen oder Notizen.

Syntax und erweiterte Node-Prüfungen bestanden. Integration mit tatsächlichen Daten einschließlich neu erzeugter Dokumentinstanz: Wiederherstellung unabhängiger Tabellenwahlen und Watchlist, kombinierte Suche/Universum, Umbenennen, leere Liste, Quota-Schreibfehler, defekte Präferenzen und Rückfall nach gelöschter Liste bestanden; keine JavaScript-Fehler.


Erfolgreicher finaler Workflow: https://github.com/bastihouse/investment-cockpit/actions/runs/39399953545 (Refresh 74 Sekunden, Deployment 9 Sekunden). Live-Abnahme: Watchlist mit drei Aktien, Score absteigend, vollständiges Neuladen mit gleicher Auswahl und Reihenfolge, Microsoft-Suche mit einem Treffer und S&P-Universum mit zwei Treffern. Smartphone 390px und Tablet 768px stellen die gespeicherte Auswahl korrekt wieder her; keine horizontale Seitenüberbreite (375/375 bzw. 753/753 CSS-Pixel). Temporäre Testliste entfernt und Rückfall auf alle 114 Aktien mit Hinweis bestätigt. Keine physische Geräteprüfung.

## Einheitliche Tabellensortierung (20.10.2026)

Datenspalten über klickbare Kopfzeilen auf-/absteigend sortierbar, mit Richtungsanzeige, aria-sort und Tastaturbedienung. Automatische Anbindung dynamischer Tabellen und Tabellenkopien. Aktive Sortierung wird nach Suche, Filter und neuer Datenanzeige im bestehenden Tabellenelement wieder angewendet. Deutsche Zahlenformate, negative Werte, Namen und Datumswerte; fehlende Werte zuletzt. Aktionsspalten ohne Daten bleiben ausgenommen. Zusammengefasste Hinweiszeilen werden nicht unter die Daten gemischt.

Mobile Kartenansichten bekommen dieselbe Spaltenauswahl und einen Richtungswechsel; bestehende Karten bleiben mit den Tabellen synchronisiert. Die Übersicht zeigt eine Kopfsortierung auch im bisherigen Sortierfeld konsistent. Watchlist-Zuordnungen im direkten Aktienvergleich hängen an der Aktie und nicht an der Zeilennummer.

Erweiterte Node-Prüfung und tatsächliche DOM-Integration bestanden: Kurs-/YTD-Reihenfolge, Vorzeichen, fehlende Werte, Datum, Suchpersistenz, mobile Auswahl, Detailaktionen, neue Zeilen, Tabellenkopien und Watchlist-Sterne nach umgekehrter Vergleichsreihenfolge. Keine JavaScript-Fehler. Sortierwahl wird im laufenden Seitenaufruf gehalten, nicht über vollständiges Neuladen gespeichert.

Erfolgreicher finaler Workflow: https://github.com/bastihouse/investment-cockpit/actions/runs/39384497021 (Refresh 76 Sekunden, Deployment 12 Sekunden; bestehende 61 Python-Tests und neun Node-Prüfdateien einschließlich neuer Sortierprüfungen bestanden). Live: 163 Sortierköpfe eingebunden, Aktienvergleich nach Name umgekehrt mit passenden NVDA/MSFT-Sternen, Score absteigend mit MU an erster Stelle, Beibehaltung nach Microsoft-Suche und Rückkehr zur Gesamtliste, YTD aufsteigend mit negativen Werten, Detailaktion öffnet weiterhin die richtige Aktie. Smartphone 390px: Score-Spaltenauswahl und Absteigend-Schalter sortieren Karten korrekt; Tablet 768px: Namenssortierung per Tabellenkopf. Beide ohne horizontale Seitenüberbreite. Keine physische Geräteprüfung.


## Watchlist-Sterne an Aktien (20.10.2026)

Sterne in Übersicht und mobilen Karten, Live-Kurstabelle, aktuellen Score-/Vergleichsansichten, Aktien-Detailansicht, Branchenvergleich, Scanner und Datenlücken-Karten. Gefüllter Stern bei Mitgliedschaft in mindestens einer Liste, zugängliche Beschriftung mit Listenanzahl. Kompakter nativer Dialog mit Mehrfachzuordnung, neuer Liste samt Aktie, Entfernen und Rückgängig. Vorhandene Notizen bleiben beim Hinzufügen in weitere Listen erhalten. Browserlokale Speicherung und JSON-Sicherung verwenden unverändert dasselbe Datenformat.

Syntaxprüfung und Research-Hub-Prüfung bestanden. Tatsächliche DOM-Integration prüft Mehrfachzuordnung, Listennamen als sicheren Text, neue Liste, Notizerhalt, Rückgängig, simulierte Speicherquota ohne falsche Erfolgsmeldung, Suche ohne doppelte Sterne, Änderungen aus anderen Tabs und den Fall ohne vorhandene Listen. Keine JavaScript-Fehler.

Erfolgreich veröffentlicht: https://github.com/bastihouse/investment-cockpit/actions/runs/39374288010 (Refresh 69 Sekunden, Deployment 10 Sekunden; bestehende 61 Python-Tests und neun Node-Prüfdateien im Workflow). Live geprüft: neue Liste über Stern, zwei Listen je Aktie, gefüllter Stern nach Neuladen, Entfernen/Rückgängig, Suche ohne doppelte Sterne, Wechsel NVDA/MSFT, Escape mit Fokusrückgabe und Synchronisation zwischen Tabs. Smartphone 390px: Stern in Aktienkarte, Dialog 356px breit ohne innere Überbreite, Zuordnung und Rückgängig; Tablet 768px: 440px-Dialog. Dark-Mode-Farben geprüft und ursprüngliches Theme wiederhergestellt. Temporäre QA-Listen entfernt. Keine physische Geräteprüfung.


## Benchmarkvergleich, Watchlists und Vergleichsansicht (19.10.2026)

Drei integrierte Ansichten unter Aktienanalyse: bis zu vier Aktien gegen SPY beziehungsweise elf US-Sektor-ETF-Proxies, historische Umrechnung nach USD/EUR, gemeinsame abgeschlossene Handelstage, Kursrendite oder dividendenbereinigte Anbieternäherung, Renditeabstand in Prozentpunkten, Drawdown und CSV. Kein offizieller Index-Total-Return und kein risikobereinigtes Alpha. Fehlende/veraltete Daten, längere Lücken und auffällige Basissprünge sperren die Darstellung.

Mehrere lokale Watchlists mit Notizen, Suche, Sortierung, direkter Vergleichsübergabe, Wiederherstellung entfernter Einträge sowie validierter JSON-Sicherung. Watchlists, Notizen und gespeicherte Vergleiche bleiben im Browserprofil; kein Servertransfer und keine automatische Gerätesynchronisation. Schreibfehler und beschädigte Sicherungen erzeugen keine falsche Erfolgsmeldung.

Historische Vergleichsansicht mit bis zu vier Aktien, Punkte- und Auswahlrangverlauf, Kategorien-Heatmap, Unterschieden zur Referenzaktie, Quellenübergabe, CSV und benannten Einstellungen. Gemeinsame Kategorien und Profile werden beachtet; fehlende Revisionen bleiben offen, keine Hochrechnung auf 100. Gespeicherte Einstellungen verwenden beim erneuten Öffnen die jeweils veröffentlichten Daten.

61 Python-Tests, neun Node-Prüfdateien und Integration mit echten Daten bestanden. Integration deckt EUR/USD/KRW, gemeinsame Handelstage, Watchlist-Notizen, gespeicherte Ansichten, Ranggrenzen und Rückgängig ab; keine JavaScript-Fehler.

Finale Veröffentlichung erfolgreich: https://github.com/bastihouse/investment-cockpit/actions/runs/39307078064 (Refresh 77 Sekunden, Deployment 24 Sekunden). Live-Abnahme: MSFT/NVDA gegen SPY über 250 gemeinsame abgeschlossene Handelstage vom 20.10.2025 bis 16.10.2026, USD/EUR, Kurs-/dividendenbereinigte Basis, XLK-Branchenproxy und CSV; Watchlist mit zwei Aktien, gespeicherter Notiz nach Neuladen, Umbenennen, Vergleichsübergabe und Rückgängig. Benannte Rangansicht nach Neuladen wieder geöffnet; gemischte Profile MSFT/JPM erhalten keinen gemeinsamen Rang; Quellenübergabe bestätigt. Smartphone 390px: Benchmark, Rangchart, Heatmap und Notizspeicherung ohne horizontale Überbreite, adaptiver 320×300-Chart; Tablet 768px: Benchmark und Vergleich ohne horizontale Überbreite. Temporäre QA-Listen und Vergleich entfernt. Keine Prüfung auf physischer Hardware.

## EPS-Basis, internationale Historien und historischer Vier-Aktien-Vergleich (19.10.2026)

Folgeauftrag 1–3 umgesetzt und veröffentlicht. 133 zusätzliche EPS-Basisprüfungen für AMD/AVGO/WMT/QCOM/COST; lokal 297 zusätzliche Monatsbewertungen mit belegter EPS-Näherung. Belegte Splits, verwässerte Aktienzahlen, Gewinn und EPS derselben Einreichung bleiben nachvollziehbar. Direkte FY-EPS beziehungsweise vier Quartale oder YTD + vorheriges FY − vorheriges YTD sind ausdrücklich TTM-Näherungen. Abweichende Split-Ereignisse der Kursreihe sperren die Bewertung. Andere unbestätigte Instrumente erhalten keine automatische Freigabe.

51 neue internationale Perioden schließen die bislang fehlenden vier Titel (Samsung, Acomo, Unilever, Shell); 43 Quellenperioden ergänzen die belegte 1:1-Vorgängerfortführung bei Exxon und BlackRock. Insgesamt 2.893 Kennzahlenperioden aus 2.416 verknüpften Quelldokumenten für 114/114 Aktienpositionen. Jahres- und Halbjahresreihen bleiben als solche gekennzeichnet; keine Behauptung lückenloser Quartals- oder Bewertungsdaten. Internationale ADR-/Währungsbasen und historische Revisionen bleiben offen.

Vier-Aktien-Vergleich mit gemeinsamer Kategorienbasis je Monat, getrennter Originalabdeckung, sichtbaren Kategoriebeiträgen, zusätzlichem Abdeckungsverlauf und CSV mit Komponenten/Maximalpunkten. Wachstumsperioden müssen übereinstimmen, bank-/versicherungsspezifische Qualitätsbasen ebenfalls; profilübergreifend nur Marktrisiko. Unterbrechungen bei Wechsel der Vergleichsbasis. Direkte Übergabe aus dem Branchenvergleich und EPS-/Splitbelege im kompakten Quelldialog. Rückrechnung `research-v7.5-reconstruction-v2`; unveränderte Gewichte und unverändertes beobachtetes Archiv.

58 Python-Tests und acht Node-Prüfdateien bestanden; tatsächliche Datenintegration ohne JavaScript-Fehler. Erfolgreicher finaler Lauf: https://github.com/bastihouse/investment-cockpit/actions/runs/39303615340 (Refresh 74 Sekunden, Deployment 8 Sekunden). Live geprüft: vier Kurven und vier Abdeckungslinien, 85-Punkte-Basis AVGO/AMD/WMT/QCOM, 65 gemeinsame mögliche Punkte mit Costco statt Qualcomm, Profilwechsel auf JPM begrenzt gemeinsame Kategorien auf Risiko, Peer-Übergabe MU/NVDA, CSV-Download mit Vergleichsbasis, alle vier internationalen Quellencharts sowie XOM-/BLK-Vorgängerreihen. Smartphone 390px: vier Beitragskarten, adaptiver 320×150-Abdeckungschart, keine horizontale Überbreite einschließlich Quelldialog; Tablet 768px: keine horizontale Überbreite, 677×150-Chart. Die Responsive-Vorschau kann ihre Frames nun explizit auf aktuelle Assets aktualisieren.

## Historische Kennzahlen, Datenlücken, Branchenvergleich und Scanner (19.10.2026)

In der beauftragten Reihenfolge 1 → 4 → 2 → 3 umgesetzt und veröffentlicht. 2.799 historische Kennzahlenperioden aus 2.339 Quelldokumenten für 110 von 114 Aktien; alle 82 Ergänzungen haben historische Perioden. Quartals-, Halbjahres- und Jahreswerte bleiben getrennt. Neue SEC-EPS-Bewertungen bleiben ohne verifizierte Aktien-/Splitbasis gesperrt; internationale sowie Vorgängerhistorien bleiben als Lücken sichtbar.

Neu sind Quellencharts mit Periodenwahl und CSV, priorisierte Datenlücken, Vergleichsgruppen nach Branche und Modell einschließlich Übergabe an den Aktienvergleich sowie ein Scanner mit festen, erklärten Filtern. Fehlende frühere Beobachtungen erzeugen keine erfundenen Score-Veränderungen. Historische Archive und Modellgewichte bleiben unverändert.

Veröffentlichung erfolgreich: https://github.com/bastihouse/investment-cockpit/actions/runs/39262884986 (Refresh 66 Sekunden, Deployment 8 Sekunden). 53 Python-Tests, acht Node-Prüfdateien und Integration mit echten Daten bestanden. Live geprüft: Jahres-/Quartalswahl, acht P1-Lücken, Branchenvergleich mit acht Halbleiter-Emittenten und Übergabe von MU/NVDA, Scanner-Filter. Smartphone 390px: alle vier neuen Ansichten ohne horizontale Überbreite, adaptiver 320px-Chart und mobile Navigation; Tablet 768px: Scanner ohne horizontale Überbreite. Aktueller Live-Datenstand 19.10.2026, 15:46:09 Wiener Zeit. Scanner-Treffer hängen vom jeweils erzeugten Datenstand und den gewählten Filtern ab.

## Erweiterung um S&P-500-Top-100 (19.10.2026)

Fester Auswahlstand 16.10.2026, anhand der offiziellen täglichen SPY-Bestände nach Fondsgewicht absteigend. Die Gewichte sind eine offengelegte Näherung für streubesitzbereinigte Indexgewichte; Original-S&P-Gewichte sind nicht unabhängig bestätigt. 100 Aktienpositionen, getrennte Aktienklassen, 18 Überschneidungen, 82 Ergänzungen, insgesamt 114 Aktien. Bisherige 32 Titel bleiben erhalten. Auswahl, Quelle und SHA256 sind in `data/sp500-selection.json` gespeichert. Keine automatische Rotation.

Umgesetzt: synchronisierte Filter für Übersicht, Kurstabelle und aktuelle Scores; Rang-/Gewichtshinweise; Quelldetails im Dialog; dynamische Größenprüfung und Datenqualitätszähler; begrenzter paralleler Datenabruf (3 Aufgaben); passende Profile für neue Banken, Versicherer und REITs. Historische Originalkennzahlen bleiben separat belegt, Tagesarchive werden nicht rückwirkend um neue Aktien ergänzt. Lokale Prüfung: 46 Python-Tests, sieben Node-Prüfdateien, DOM-Integration mit 114→100→32→114 und synchronisierten Filterzuständen ohne JavaScript-Fehler.

Produktiver Datenjob: https://github.com/bastihouse/investment-cockpit/actions/runs/39256149942. Datenabruf erfolgreich in 61 Sekunden: 114 aktuelle Kursreihen, alle 82 neuen Aktien mit Kurs, 102 vollständige Modell-Scores, zwölf Teilbewertungen. Vollständigkeit des Modells ist keine unabhängige Bestätigung der Kennzahlen.

Finale Veröffentlichung erfolgreich: https://github.com/bastihouse/investment-cockpit/actions/runs/39256671721 (Refresh 63 Sekunden, Deployment 97 Sekunden). Live-Abnahme: Filter 114/100/32, synchronisierte Kurs-/Score-Auswahl, konsistente globale Übersichtszähler 114 Kurse und 102 vollständige Modell-Scores, Broadcom als neue Aktie mit YTD-Kurschart (199 Handelstage), Quellen-/Auswahldetails. Smartphone 390px und Tablet 768px geprüft; keine horizontale Überbreite, auch bei geöffneten Quellenhinweisen und Top-100-Auswahl. Der Vergleich historischer Scores benötigt weiterhin je Aktie belegte historische Eingaben; keine Übertragung heutiger Kennzahlen in frühere Monate.

Live-Modell: research-v7.5.0. Rückrechnung: research-v7.5-reconstruction-v1. Unveränderte Gewichte; neue Eingabesperren und historische Branchenvarianten bleiben durch Modellversionen getrennt.

Enthalten: kategorieweise Aktienklasse-/Währungs-/Kursbasisprüfung; 269 Originalberichte von zwölf Emittenten; offizielle Berichts-Prüfqueue; 6-/12-Monats-Score-Diagnostik mit zeitlicher Trennung und gereiften Ergebnissen.

Lokale Prüfung: 39 Python-Regressionsprüfungen, sechs Node-Prüfdateien und DOM-Integration der neuen Ansichten. Echte vorhandene Kursreihen: 60 Monatsenden, 32 Aktien, 88 retrospektive Ergebnisfälle, keine gereiften beobachteten Ergebnisse. Fehlende Kennzahlen bleiben offen. Keine nachgewiesene Prognosekraft.

Die Veröffentlichung erfolgt über den bestehenden GitHub-Pages-Workflow. Generierte lokale Platzhalter werden nicht hochgeladen; CI erstellt die aktuellen Daten.

GitHub-Pages-Lauf 39162860335: erfolgreich, Datenjob 56 Sekunden und Deployment 11 Sekunden. Live geprüft: Segmente/Horizonte, Zeitteilung, Berichtsfilter und Berkshire-B-Bewertungssperre.


## Aktuelle Oberflächen-Erweiterung (19.10.2026)

Umfang: Treiberkarten für gespeicherte Score-Veränderungen, kompakte Infodialoge, bereinigte Kopfzeile, gespeicherter Dark/Light-Modus sowie mobile Navigation/Karten und adaptive Charts. Keine Änderungen am Research-Modell oder seinen Gewichten. 39 Python-Prüfungen, sieben Node-Prüfdateien, Syntaxprüfungen und lokale DOM-Integration bestanden.

Veröffentlichungsfreigabe am 19.10.2026 ausdrücklich erteilt. Die Dateien sind im öffentlichen Repository und über GitHub Pages veröffentlicht. Finaler erfolgreicher Workflow: https://github.com/bastihouse/investment-cockpit/actions/runs/39215197863.

Visuelle Live-Abnahme in Desktop-, 390- und 768-Pixel-Ansichten abgeschlossen: Theme-Wechsel/Persistenz, Dialoge/Escape/Fokusrückgabe, mobile Navigation, Vergleichskarten, adaptive Chartbreite, historische Monatswahl und Quellen sowie getrennte Modellvergleiche. Keine horizontale Überbreite der getesteten Seiten. Kopfzeile ohne Versions-/Kostenlosigkeitsangaben; Modellmetadaten stehen im Infodialog. Ein Test auf einem physischen iPhone ist nicht enthalten.

## Quellen und historische Lücken (19.10.2026)

Neu: unabhängige Emittentenkataloge für JPMorgan, Allianz und Siemens Energy, korrigierter offizieller Meta-RSS-Link, getrennte Zählung von Endpunkten und erreichten Unternehmen. Unbekannte Veröffentlichungsdaten bleiben unbekannt; Erkennung ändert keine kuratierten Finanzzahlen automatisch. Strukturfehler ergeben keine irreführend erfolgreichen Leerläufe.

Vier verifizierte Originalberichte ergänzt: LVMH H1 2022/H1 2024, Generali FY 2024/FY 2025. Insgesamt 273 Originalberichte von 13 Unternehmen. Generali-Jahresgewinne sind keine Quartalszahlen und keine bereinigten Gewinne; fehlende Buchwert-/ROE-Eingaben bleiben offen. Die Allianz-FY-2022-Textlücke bleibt sichtbar. Lokale Prüfung: 44 Python-Tests, sieben Node-Prüfdateien, Syntaxprüfungen und DOM-Integration ohne Fehler. Rückrechnung mit vorhandenen Kursreihen: 89 retrospektive Ergebnisfälle, keine gereiften beobachteten Ergebnisse. Erreichbarkeit ist netzwerkabhängig; der produktive Monitor zeigt die tatsächlichen Ergebnisse seines jeweiligen Laufs. HTML-Fehlerseiten zählen nicht als erfolgreiche leere RSS-Feeds.

Final veröffentlicht und live geprüft: https://github.com/bastihouse/investment-cockpit/actions/runs/39217502698 (Refresh 59 Sekunden, Deployment 25 Sekunden, erfolgreich). Produktiver Monitor: 6/19 Endpunkte, 6/12 konfigurierte Unternehmen mit mindestens einer erreichbaren Quelle; die neuen JPMorgan-/Siemens-Energy-Kataloge sind erreichbar, der Allianz-Katalog bleibt in diesem Lauf nicht erreichbar. Generali/Allianz-Vergleich für März 2026 und Generali-Originalquellendialog einschließlich Veröffentlichungsdatum, 12-Monats-Basis und fehlender Bewertungs-/ROE-Eingaben geprüft.

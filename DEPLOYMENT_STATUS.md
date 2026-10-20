# Investment Cockpit V7.5

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

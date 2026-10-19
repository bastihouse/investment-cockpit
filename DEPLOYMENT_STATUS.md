# Investment Cockpit V7.5

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

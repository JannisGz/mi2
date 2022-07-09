# KP "Medizinische Informatik" II: Visualisierung medizinischer Daten

## Aufgabenstellung

Ziel des Komplexpraktikums war die Entwicklung eines Systems, das
aus Apple-Smart-Watches, bzw. aus IPhones Gesundheitsdaten
extrahieren kann, diese als FHIR-Ressourcen auf einem entsprechenden
Server zur Verfügung stellt und sowohl für Patienten als auch
behandelnde Hausärzte auf einer grafischen Oberfläche zur Verfügung stellt.

## Lösung

### Datenextraktion und Harmonisierung

Als Grundlage wurde hier die Einthoven App verwendet. Da diese noch einige
Fehler und nicht alle benötigten Funktionen enthielt, wurde die
App entsprechend erweitert. Die verwendete Version ist in diesem Repo hinterlegt 
und muss auf den genutzten Smartphones installiert werden.

### FHIR-Server

Als FHIR-Server wird ein Docker-Image des "HAPI FHIR JPA"-Servers genutzt.
Im Verzeichnis "FHIR-Server" ist eine Anleitung zum Aufsetzen des Servers hinterlegt.
Der Server muss während der Verwendung der Anwendung jederzeit zur Verfügung stehen.

### Anwendung

Die eigentliche Anwendung ist im Verzeichnis "Anwendung" hinterlegt. Es handelt sich
um einen FLASK-Server (Python) mit eigener SQL-Lite Datenbank. In dieser Datenbank
werden Benutzer und Freigaberechte geführt. Die medizinischen Daten der Patienten
werden im oben genannten FHIR-Server geführt.
Zum Starten der Anwendung sind die folgenden Schritte notwendig:
- Auf einer Konsole in das Hauptverzeichnis navigieren (mi2)
- "python3 -m venv auth" ausführen (Erzeugt neue Ausführungsumgebung)
- "source auth/bin/activate" ausführen (Wechselt zur erstellten Umgebung)
- "pip install -r requirements.txt" ausführen (Installiert benötigte Module)
- "export FLASK_APP=Anwendung" ausführen (Legt Name der zu startenden Anwendung fest)
- "export FLASK_DEBUG=1" ausführen (Legt Debug-Level fest)
- "flask run --host="0.0.0.0" ausführen (Startet den Server)
- Auf der Kommandozeile sollte ausgegeben werden unter welche Adresse die Login-Seite des Servers verfügbar ist
---
title: Web Access
description: Copy Paste Web Access Instructions
published: true
date: 2026-07-14T14:09:52.130Z
tags: hermes, private
editor: markdown
dateCreated: 2026-07-14T14:09:52.130Z
---

```
Konfiguriere den Webzugriff dieses Hermes Agents ausschließlich ohne kostenpflichtige Subscription.

Vorgaben:

1. Verwende SearXNG für web_search:
   - URL: https://search.pub.bitbull.ch
   - Environment-Datei: $HERMES_HOME/.env
   - Variable: SEARXNG_URL=https://search.pub.bitbull.ch
   - Konfiguration:
     web:
       search_backend: searxng

2. SearXNG ist search-only.
   Trage SearXNG niemals als web_extract-Backend ein.

3. Prüfe vor jeder Änderung die offizielle Hermes-Dokumentation:
   https://hermes-agent.nousresearch.com/docs/user-guide/features/web-search

4. Verwende web_extract nur, wenn ein tatsächlich verfügbarer Extract-Provider vorhanden ist:
   - self-hosted Firecrawl über FIRECRAWL_API_URL
   - oder ein ausdrücklich bereitgestellter API-Key für Tavily, Exa, Parallel oder Firecrawl

5. Wenn kein Extract-Provider verfügbar ist:
   - keinen kostenpflichtigen Provider vortäuschen
   - keinen falschen API-Key eintragen
   - web_extract nicht auf einen search-only Provider routen
   - als Fallback den lokalen/CDP-Browser verwenden

6. Verwende CDP für:
   - JavaScript-rendernde Seiten
   - Seiten, die HTTP-seitig keinen brauchbaren Inhalt liefern
   - Screenshots
   - visuelle Verifikation
   - interaktive Webseiten

   Der CDP-Endpunkt kommt aus:
   BROWSER_CDP_URL

   Den Wert niemals ausgeben oder in Logs schreiben.

7. Deaktiviere nicht benötigte Web-/Cloud-Provider in:
   $HERMES_HOME/config.yaml

   Typische deaktivierte Provider ohne Credentials:
   - web-tavily
   - web-exa
   - web-parallel
   - web-firecrawl
   - web-brave-free
   - web-xai
   - web-ddgs
   - browser-browserbase
   - browser-firecrawl
   - browser-browser-use

8. Prüfe die exakten Plugin-Namen aus plugin.yaml.
   web-brave-free verwendet einen Bindestrich, nicht web-brave_free.

9. Sichere vor jeder Konfigurationsänderung:
   $HERMES_HOME/config.yaml
   $HERMES_HOME/.env

10. Teste anschließend:

   a) YAML-/Hermes-Konfiguration laden

   b) SearXNG:
      GET $SEARXNG_URL/search?q=test&format=json

   c) Hermes-Suche:
      web_search mit einer realen Testabfrage

   d) web_extract:
      Erwartet entweder einen echten Extract-Erfolg
      oder einen klaren Fehler, wenn nur SearXNG verfügbar ist

   e) CDP:
      öffentliche Testseite laden
      Snapshot erstellen
      Console-Fehler prüfen
      bei Screenshotbedarf visuell verifizieren

11. Behaupte niemals, dass web_extract funktioniert, wenn nur SearXNG konfiguriert ist.
   Melde diese Einschränkung ausdrücklich.

12. Nach Änderungen Hermes/Gateway neu starten beziehungsweise eine neue Session öffnen.
```
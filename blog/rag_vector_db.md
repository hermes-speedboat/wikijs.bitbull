---
title: Qdrant Vector DB overview
description: Get started with vector DBs and RAG
published: true
date: 2026-03-19T07:39:09.081Z
tags: ai, rag, qdrant
editor: markdown
dateCreated: 2026-03-19T07:33:55.141Z
---

# Zusammenfassung  
Qdrant ist eine moderne Open-Source-Vektordatenbank und Suchmaschine, spezialisiert auf die schnelle Ähnlichkeitssuche im hochdimensionalen Raum. Sie speichert „Punkte“ (engl. *points*), bestehend aus einem **Vektor** (Embedding), einem eindeutigen **ID** und optionalen **Metadaten** (Payload). Qdrant nutzt als Hauptindex den graphbasierten HNSW-Algorithmus (Hierarchisch Navigierbarer Kleinwelt-Graph) zur Approximate Nearest Neighbors-Suche (ANN) und unterstützt als Distanzmaße **Euklidische Distanz**, **Cosinus-Ähnlichkeit** und **Skalarprodukt (Dot)**【22†L323-L326】. Daten werden in *Collections* organisiert, die aus einem oder mehreren **Shards** bestehen; Punkte werden standardmäßig per konsistentem Hash auf Shards verteilt【30†L9-L17】. Für Ausfallsicherheit und Hochverfügbarkeit können Shards mit einer einstellbaren **Replication Factor** mehrfach im Cluster repliziert werden【31†L25-L33】.  

Qdrant bietet zwei Speicher-Modi: **In-Memory** (Vektoren vollständig im RAM) und **Memmap (on-disk)** (Vektoren via Speicherabbild auf Festplatte)【26†L407-L410】【51†L186-L194】. Der In-Memory-Modus liefert maximale Geschwindigkeit, während Memmap bei großen Datensätzen die RAM-Auslastung begrenzt. Zusätzlich lassen sich **Payload-Felder** und Indizes auf Festplatte auslagern, um RAM zu sparen (Konfiguration: `payload_on_disk`, `on_disk: true`)【59†L281-L289】【51†L216-L224】. Das Write-Ahead-Log (WAL) garantiert Datenintegrität: Jede Operation wird zuerst sequenziell ins WAL geschrieben【58†L708-L717】, danach in *Segmenten* (neue Datenblöcke) abgelegt. Jeder Punkt erhält dabei intern eine **Versionsnummer**; veraltete Schreibvorgänge (niedrigere Version) werden beim Einspielen aus dem WAL ignoriert【58†L712-L717】.  

*Punkte* in Qdrant haben folgende Eigenschaften: eine 64-Bit-ID (oder UUID)【13†L292-L300】, einen/viele Vektor(e) (bei Named- oder Multivector-Support mehrere mit je eigenem Metrik), ein optionales Payload (JSON-Metadaten)【26†L400-L407】, sowie eine intern verwaltete Version. Feldtypen im Payload können Integer, Float, Bool, Keyword (String), Geo, Datetime oder Arrays davon sein【18†L572-L582】【54†L321-L329】. Es gibt keine harte Begrenzung der Payload-Größe – sie ist nur durch Hardware-Ressourcen limitiert【59†L281-L290】. Große Payloads können durch `payload_on_disk: true` komplett auf Festplatte gehalten werden【59†L282-L289】. Für Filter und hybride Suche spielt das Payload eine zentrale Rolle: Es ermöglicht, Suchergebnisse nach Attributen einzugrenzen (z.B. *Zeitraum*, *Schlagwörter*, *Preisklasse*). Qdrant kann für jedes Payload-Feld einen Index anlegen, um Filter effizient zu unterstützen【36†L326-L335】. Die Kombination aus Vektorsuche (Semantik) und Payload-Filtern (business-relevante Bedingungen) erlaubt präzisere Abfragen【36†L326-L335】【36†L335-L338】.  

Beim Einfügen eines Punktes durchläuft Qdrant typischerweise diese Schritte:

- **Client-API & Batching:** Mittels REST oder Client-SDK ruft der Nutzer `upsert` oder `batch upsert` auf und übermittelt Punkt-ID, Vektor und Payload. Bulk-Uploads können in Batches erfolgen, um Overhead zu minimieren【36†L367-L375】【49†L13-L20】.  
- **Serialisierung:** Punkte werden in ein internes Format überführt, Vektoren (Float-Arrays) und JSON-Payloads serialisiert.  
- **WAL-Schreiben:** Der Vorgang wird im **Write-Ahead Log** (WAL) mit einer Sequenznummer protokolliert【58†L708-L717】. Nach Eintrag im WAL ist der Schreibvorgang durabel – Daten gehen bei Absturz nicht verloren.  
- **Segment-Erstellung:** Der Punkt wird in einem oder mehreren **Segmenten** gespeichert (Segment ist eine Speichereinheit, entweder im RAM oder als Memory-Mapped-File auf der Festplatte)【51†L186-L194】. Neue Punkte sammeln sich zunächst in einem aktiven Segment.  
- **Index-Update:** Nach Überschreiten bestimmter Schwellwerte (z.B. `indexing_threshold`) wird der HNSW-Graph aktualisiert – wahlweise können Indexierungsparameter angepasst werden. Für sehr große Uploads empfiehlt sich zeitweiliges Deaktivieren des HNSW (`m=0`) oder Setzen von `indexing_threshold=0`, um den Graph-Aufbau auf später zu verschieben【51†L111-L119】【51†L135-L143】. Bei Named- oder Sparse-Vektoren geschieht der Index-Aufbau analog (Sparse-Vektoren werden bei Upsert immer sofort indiziert【51†L90-L99】).  
- **Persistenz und Merging:** Segmente werden periodisch zusammengeführt („compaction“), um die Anzahl der Segmente zu reduzieren und Speicher effizienter zu nutzen【51†L186-L194】. Bei aktivem Memory-Mapped-Modus bleiben rohe Daten auf Platte, wobei das Betriebssystem sie bei Zugriffen paginiert.  

```mermaid
flowchart LR
    subgraph Schreibpfad
      Client[Client API (Upsert)]
      WAL[WAL (Sequenzielles Log)]
      Segment[Segment (RAM/Memmap)]
      HNSW[HNSW-Index aktualisieren]
      Merge[Segment-Merge / Optimizer]
    end
    Client --> WAL
    WAL --> Segment
    Segment --> HNSW
    HNSW -. optional .-> Merge
```
*Abbildung: Ablaufschema des Einfügens eines Punktes in Qdrant (Vereinfachung)*

Beim **Update** eines bestehenden Punktes werden ähnliche Schritte durchlaufen: Ein Upsert mit derselben ID überschreibt Vektor und Payload atomar. Für feingranulare Updates bietet Qdrant spezielle Endpunkte: Zum Beispiel `update_payload` oder `delete_payload`, die nur Teile des Payloads ändern【13†L286-L294】【16†L2420-L2428】. Unter der Haube arbeitet Qdrant auch hier mit WAL und Versionierung, um Schreibkonflikte zu vermeiden: Der Storage speichert zu jedem Punkt eine Versionsnummer (aus WAL), und eingehende Updates mit älteren Versionen werden verworfen【58†L712-L717】. Für verteilte Anwendungen empfiehlt sich **optimistische Parallelität** über Bedingungs-Updates: Man kann ein Payload-Feld z.B. `version` oder `timestamp` anlegen und beim Update per Filter prüfen, dass es unverändert ist, wie im Beispiel【16†L2451-L2459】. Löschen eines Punktes setzt einen Tombstone und kann in einer späteren Compaction wirklich aus Speicher entfernt werden.  

| Update-Strategie       | Beschreibung                                                                 | Vor- und Nachteile                                                                                   |
|------------------------|------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| **Einfaches Upsert**   | Punkt vollständig neu einfügen/überschreiben (Atomarer Vorgang).              | *+ Einfach und sicher (eine Anfrage).*<br>*– Bei vielen Änderungen hoher I/O-Aufwand.*                  |
| **Bedingtes Update**   | Punkt nur aktualisieren, wenn Filter (z.B. `version`=x) erfüllt ist.          | *+ Ermöglicht Konsistenz (optim. Parallelität).*<br>*– Komplexer, Mehraufwand für Filter und Fehler.*  |
| **Teil-Update**        | Nur Payload-Attribute anpassen (API `update_payload` / `delete_payload`).     | *+ Geringerer Overhead, flexibel.*<br>*– Keine Vektor-Updates (nur Metadaten).*                          |
| **Tombstone & Neu**    | Punkt löschen (Tombstone) und ggf. neu einfügen.                             | *+ Alte Daten bleiben erhalten (kann rückgängig gemacht werden).*<br>*– Braucht später Compaction.*    |

Für den Einsatz in **Produktionssystemen** wird empfohlen, große Bulk-Uploads mit optimierten Einstellungen durchzuführen: Beispielsweise können während des Uploads der HNSW-Graph auf `m=0` gesetzt und `indexing_threshold` auf 0 konfiguriert werden, um den Indexaufbau zu verzögern【51†L111-L119】【51†L135-L143】. Nach Abschluss lädt man diese Konfiguration zurück (z.B. `m=16`, `indexing_threshold` auf Standard) und lässt den Index einmalig aufbauen. Ebenso kann man die Option `on_disk: true` für Vektoren nutzen, um direkt im Memmap-Modus zu schreiben【51†L198-L207】. All diese Maßnahmen minimieren Arbeitsspeicher und Rechenlast während der Aufnahme, erfordern jedoch einen späteren Indexbauschritt oder etwas zusätzlichen Aufwand für Optimizer.  

## LLM-gestützte Suche mit Qdrant  
Bei der Suche mit großen Sprachmodellen (LLMs) agiert Qdrant als hochperformanter Vektorindex in der Retrieval-Pipeline. Der typische Ablauf ist: Der Nutzer stellt eine textuelle oder sonstige Anfrage. Diese wird **einerseits** mittels eines Embedding-Modells (häufig ein LLM oder spezialisierter Encoder, z.B. OpenAI oder FastEmbed【18†L475-L484】) in einen Vektor (Query-Embedding) überführt. **Andererseits** kann optional zusätzlich ein *Keyword-/Sparse-Vektor* generiert werden (z.B. über BM25 oder Text-Encoder)【38†L293-L302】. Beide Vektoren werden über Qdrant abgefragt. Qdrant kann hybride Abfragen (neue Query API) ausführen, bei denen dense und sparse Vektoren kombiniert werden【39†L133-L142】【39†L150-L157】. Darüber hinaus können Filter auf Payload angewandt werden (z.B. Kategorie == X).  

1. **Embedding-Generierung:** Innerhalb derselben Anwendung oder per externem Service wird der Query-Text an ein Modell geschickt. Die Erzeugung eines LLM-Embeddings kann Latenz von einigen Dutzend bis Hunderten Millisekunden verursachen; üblicherweise batcht man Anfragen, wenn man viele parallele Queries hat. Qdrant Cloud bietet sogar eingebettete Dienste (FastEmbed oder integrierte Inference) für minimierte Latenz【18†L473-L482】【18†L505-L513】. Ergebnisse des Embedding-API-Aufrufs können zwischengespeichert werden, um wiederholte Queries zu beschleunigen.  

2. **Ähnlichkeitssuche:** Der Vektor wird an Qdrant gesendet (z.B. REST-Endpoint `/collections/<col>/points/search` oder neue Query-API). Qdrant sucht mit HNSW ANN die *n* ähnlichsten Vektoren (Nearest Neighbors)【22†L318-L325】【28†L7-L10】. Falls Payload-Filter vorliegen, werden im Hintergrund passende Punkte via Payload-Index ermittelt【36†L326-L335】 und nur diese beim HNSW-Search berücksichtigt (Filterable HNSW【28†L61-L64】). Das Ergebnis sind ID-Liste plus optionalen Payloads. Qdrant kann auch *Hybrid Queries* ausführen, die gleichzeitig dense und sparse Suchen kombinieren und die Resultate in einem einzigen Schritt zurückliefern【39†L133-L142】. 

3. **Post-Processing / Reranking:** Oft werden die ersten Treffer weiter verfeinert. Moderne Ansätze nutzen LLMs oder Cross-Encoder: Beispielsweise kann ein ColBERT-Modell (Late-Interaction) oder eine LLM-Ranking-Pipeline auf die zurückgegebenen Dokumente angewendet werden, um die endgültige Rangfolge zu verbessern【38†L323-L332】【39†L133-L142】. Qdrant unterstützt mehrstufige Abfragen und Fusion: Man kann z.B. über die Query-API zuerst Vektorsuche, dann Reranker-Aufruf (jetzt direkt auf dem Server) definieren【39†L90-L98】. Außerdem existiert ein *Relevance-Feedback* Query: Man überführt positives bzw. negatives Feedback zu einem Punkt in einen zusätzlichen Vektorraum-Query, um in einer zweiten Runde relevantere Dokumente zu finden【43†L31-L39】【43†L133-L142】. 

4. **Antwort-Generierung / Prompt-Engineering:** Im Umfeld von LLMs kann der Text der gefundenen Dokumente in die weitere Generierung (z.B. RAG – Retrieval Augmented Generation) eingespeist werden. Dabei muss man darauf achten, Relevanz und Kodierweise von Texten abzustimmen (z.B. Text-Trunks, Zusammenfassungen). Qdrant selbst bietet keine Prompts, aber liefert die passenden Inhalte für Prompts eines LLM (z.B. eine Zusammenfassung des nächstliegenden Textes).  

5. **System-Optimierungen:** Um Latenz zu reduzieren, wird oft gepuffert („batched“) auf Ebene der Embedding-Aufrufe und der Qdrant-Abfragen. Qdrant kann asynchron genutzt werden (Async API【44†L133-L142】). Wiederholte Embedding-Ergebnisse werden gecached. Bei sehr hohen Anforderungen lohnt es sich, Embedding-Modelle (FastEmbed) lokal laufen zu lassen, um Rundlaufzeit zu sparen【18†L473-L482】【18†L489-L497】. Zudem skaliert Qdrant horizontal über Shards/Replicas, was durch erhöhte Knoten die Such-Latenz und parallele Anfragenlast verbessert【31†L25-L33】.  

**Diagramm: Hybrid-Query-Pipeline (vereinfacht)**  

```mermaid
flowchart TD
    QueryText["User Query (Text)"] -->|Embedding| DenseEmb("Dense Embedding (LLM)")
    QueryText -->|Optional| SparseEmb("Sparse Embedding (BM25/Text)")
    DenseEmb --> QdrantSearch["Qdrant: Ähnlichkeitssuche"]
    SparseEmb --> QdrantSearch
    QdrantSearch --> PayloadFilter{"Filter mit Payload"}
    PayloadFilter --> CandidateDocs["Kandidat-Dokumente (IDs)"]
    CandidateDocs -->|Reranking (optional)| FinalRanked["Endgültiges Ranking"]
    FinalRanked -->|Antwort| Response["Nutzer-Response / LLM"]
```

Die Kombination von **dichten (LLM-)Vektoren** mit **schlanken (sparse) Vektoren** führt zu einer Hybrid-Suche: Dichte Vektoren fangen den semantischen Kontext ein, Sparse-Vektoren (oder Volltext) sichern exakte Schlüsselwörter ab【36†L340-L342】【39†L150-L157】. Qdrant unterstützt bereits eigene Sparse-Indizes und deren Fusion. Der Anwender muss nur spezifizieren, welche Methode (dense, sparse, hybrid) er verwendet, und kann die neue *Query API* für mehrstufige Pipelines nutzen【39†L90-L98】【39†L133-L142】. So lassen sich z.B. zunächst per ANN 100 Kandidaten holen, diese dann mit einem Cross-Encoder final bewerten.  

**Leistungsüberlegungen:** Qdrant selbst liefert bei ausreichend RAM extrem niedrige Latenzen (typ. einige Millisekunden pro Suche bei kleinen K und mittelgroßen Datensätzen)【31†L0-L4】. Der Flaschenhals bei LLM-Suche ist oft das Embedding (Hunderten ms) oder Netzwerklatenz. Daher ist es üblich, Embedding und Suchanfragen parallel/batch zu schicken und Caching zu nutzen. Relevance-Feedback oder Mehrstufen-Anfragen erhöhen zwar die Komplexität, können aber die Resultatqualität deutlich steigern【43†L125-L134】. Qdrant empfiehlt, die Effektivität solcher Erweiterungen stets mit Metriken wie `precision@k` oder NDCG zu prüfen【39†L99-L107】. Schließlich lässt sich die Infrastruktur (Anzahl Knoten, Shards, Replikas, RAM-Größe) nach Bedarf skalieren, um Anforderungen an Durchsatz und Latenz gerecht zu werden【31†L25-L33】【55†L277-L287】.  

**Quellen:** Offizielle Qdrant-Dokumentation (Manage-Data, Storage, Indexing, Search-Konzept) sowie Blog-Beiträge und Tutorials von Qdrant wurden für diese Analyse herangezogen【22†L280-L287】【26†L407-L410】【36†L326-L335】【51†L186-L194】【58†L708-L717】【59†L281-L290】.  


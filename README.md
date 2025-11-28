# Sistema Multi-Agente su Kubernetes 

Questo progetto implementa un sistema multi-agente utilizzando Kubernetes, LangGraph, Docker, Ollama.

**Il sistema è composto da:**
* **4 Agenti specializzati** incapsulati in 4 container Docker diversi.
* Un **Orchestrator** implementato con LangGraph.
* Un servizio **LLM locale** basato su Ollama.

## Struttura del Progetto

* `agent_e1` / `agent_e2`: Agenti operativi per la raccolta/generazione dei dati iniziali.
* `agent_analyze`: Agente dedicato all'aggregazione e analisi dei risultati.
* `agent_final`: Agente per la sintesi finale e la generazione del report.
* `orchestrator`: Il componente di controllo (Job) che gestisce la sequenza di esecuzione.
* `k8s`: Manifesti Kubernetes per il deployment dei servizi.


## Prerequisiti

* [Docker Desktop] con Kubernetes abilitato nelle impostazioni
* PowerShell o un terminale equivalente

---

## 1. Prima Esecuzione (Setup)

Questi passaggi vanno eseguiti solo la prima volta, oppure quando viene modificato il codice sorgente degli agenti e si devono ricostruire le immagini Docker.

### A. Build delle Immagini Docker
Costruire le immagini locali per ogni componente eseguendo questi comandi nella root del progetto:

```bash
docker build -t mas-e1:v1 ./agent_e1
docker build -t mas-e2:v1 ./agent_e2
docker build -t mas-analyze:v1 ./agent_analyze
docker build -t mas-final:v1 ./agent_final
docker build -t mas-orchestrator:v1 ./orchestrator

``` 
### B. Esecuzione e Monitoraggio
Una volta costruite le immagini, esegui i seguenti comandi per avviare il sistema su Kubernetes:

```bash
# 1. Pulisci eventuali esecuzioni precedenti (se presenti)
kubectl delete job orchestrator-job --ignore-not-found

# 2. Avvia i servizi e l'orchestrator
kubectl apply -f k8s/

# 3. Verifica che i Pod siano stati creati e siano in stato 'Running' o 'Completed'
kubectl get pods

# 4. Leggi i log dell'Orchestrator in tempo reale
# Nota: usa 'jobs/orchestrator-job' per non dover cercare il nome casuale del pod
kubectl logs -f jobs/orchestrator-job
























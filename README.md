# Sistema Multi-Agente su Kubernetes 

Questo progetto implementa un sistema multi-agente utilizzando **Kubernetes, RabbitMQ, LangGraph, Docker, Ollama.**

**Il sistema è composto da:**
* **RabbitMQ:** gestisce le code e garantisce la persistenza dei task.
* Un servizio **LLM locale** basato su Ollama.
* Un **Orchestrator** implementato con LangGraph, invia task alle code e attende le risposte
(pattern RPC su AMQP).
* **4 Agenti specializzati** incapsulati in 4 container Docker diversi:
-   `agent_e1` / `agent_e2`: elaborazioni preliminari in parallelo.
-   `agent_analyze`: analisi critica (con **scaling orizzontale**).
-   `agent_final`: sintesi e generazione risposta finale.


## Struttura del Progetto
```plaintext
tesi-mas-k8s/
├── k8s/                        # Manifesti per il deployment Kubernetes
│   ├── 00-metrics-server.yaml  # Server metriche per HPA
│   ├── 01-ollama.yaml          # LLM e Storage Persistente
│   ├── 02-agents.yaml          # Deployment dei 4 Agenti (Consumer)
│   ├── 03-orchestrator.yaml    # Job di esecuzione del workflow
│   ├── 04-hpa.yaml             # Regole di Horizontal Pod Autoscaling
│   └── 05-rabbitmq.yaml        # Message Broker
├── agent_e1/                   # Codice sorgente Agente E1
├── agent_e2/                   # Codice sorgente Agente E2
├── agent_analyze/              # Codice sorgente Agente Analisi
├── agent_final/                # Codice sorgente Agente Finale
├── orchestrator/               # Logica LangGraph e Client RabbitMQ
└── docker-compose.yml
```

* `agent_e1` / `agent_e2`: Agenti operativi per la raccolta/generazione dei dati iniziali.
* `agent_analyze`: Agente dedicato all'aggregazione e analisi dei risultati.
* `agent_final`: Agente per la sintesi finale e la generazione del report.
* `orchestrator`: Il componente di controllo (Job) che gestisce la sequenza di esecuzione.
* `k8s`: Manifesti Kubernetes per il deployment dei servizi.


## Prerequisiti

* [Docker Desktop] con Kubernetes abilitato nelle impostazioni
* PowerShell o un terminale equivalente

---

## Installazione e Avvio

### 1️⃣ Build delle immagini Docker

Eseguire nella root del progetto:

``` powershell
docker build -t mas-e1:v1 ./agent_e1
docker build -t mas-e2:v1 ./agent_e2
docker build -t mas-analyze:v1 ./agent_analyze
docker build -t mas-final:v1 ./agent_final
docker build -t mas-orchestrator:v1 ./orchestrator
```

------------------------------------------------------------------------

### 2️⃣ Deployment dell'infrastruttura

Avviare i servizi in ordine:

``` powershell
# 1. Infrastruttura base
kubectl apply -f k8s/00-metrics-server.yaml
kubectl apply -f k8s/01-ollama.yaml
kubectl apply -f k8s/05-rabbitmq.yaml

# 2. Agenti Worker
kubectl apply -f k8s/02-agents.yaml

# 3. Auto-scaling (HPA)
kubectl apply -f k8s/04-hpa.yaml
```

Verificare lo stato dei pod:

``` powershell
kubectl get pods -w
```

------------------------------------------------------------------------

### 3️⃣ Esecuzione del Workflow (Orchestrator)

``` powershell
# Pulisci job precedenti
kubectl delete job orchestrator-job --ignore-not-found

# Avvia l’orchestratore
kubectl apply -f k8s/03-orchestrator.yaml
```

------------------------------------------------------------------------

## Monitoraggio e Metriche

### A. Log e Report finale

``` powershell
kubectl logs -f job/orchestrator-job
```

------------------------------------------------------------------------

### B. Dashboard RabbitMQ

``` powershell
kubectl port-forward service/rabbitmq-service 15672:15672
```

Accesso → http://localhost:15672\
Credenziali: **user / password**

------------------------------------------------------------------------

### C. Scalabilità Automatica (HPA)

``` powershell
kubectl get hpa -w
```

Se il carico CPU supera il target (20%), Kubernetes incrementerà
automaticamente le repliche di `agent_analyze`.

------------------------------------------------------------------------

## Pulizia

Per rimuovere l'intero sistema:

``` powershell
kubectl delete -f k8s/
```

------------------------------------------------------------------------























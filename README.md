Sistema Multi-Agente su Kubernetes (MAS-K8s)

Questo progetto implementa un sistema multi-agente per l’analisi scientifica utilizzando Kubernetes.
Il sistema è composto da:

4 agenti specializzati

un orchestrator (Job)

un servizio LLM locale basato su Ollama

📋 Prerequisiti

Docker Desktop (con Kubernetes abilitato)

PowerShell o un terminale equivalente

🚀 1. Prima Esecuzione Assoluta (Setup)

Questi passaggi vanno eseguiti solo la prima volta, oppure quando modifichi il codice degli agenti e devi ricostruire le immagini Docker.

A. Build delle Immagini Docker

Costruisci le immagini locali per ogni componente:

docker build -t mas-e1:v1 ./agent_e1
docker build -t mas-e2:v1 ./agent_e2
docker build -t mas-analyze:v1 ./agent_analyze
docker build -t mas-final:v1 ./agent_final
docker build -t mas-orchestrator:v1 ./orchestrator

B. Deploy su Kubernetes

Avvia tutti i servizi (Agenti, Ollama e Orchestrator):

kubectl apply -f k8s/

C. Monitoraggio Iniziale (IMPORTANTE)

La prima volta, il pod Ollama impiegherà un po’ di tempo per scaricare il modello AI (anche diversi GB).

Controlla lo stato dei pod:

kubectl get pods


Attendi che tutti siano in stato Running.

Per seguire lo stato dell’orchestrator:

# Sostituisci con il nome reale del pod (es. orchestrator-job-xxxxx)
kubectl logs -f orchestrator-job-XXXXX

🔄 2. Esecuzioni Successive (Start Programma)

Gli Agenti e Ollama restano sempre attivi (sono Deployments).
Per avviare un nuovo ciclo di analisi, devi semplicemente ricreare il Job orchestrator.

Riavviare il processo di analisi

Esegui in sequenza:

# 1. Cancella il job completato/vecchio
kubectl delete job orchestrator-job

# 2. Crea un nuovo job per avviare una nuova analisi
kubectl apply -f k8s/

Visualizzare l’Output

Trova il nome del nuovo pod dell’orchestrator:

kubectl get pods


Poi leggi i log:

kubectl logs -f orchestrator-job-NUOVO_NOME

🛠️ Comandi Utili di Manutenzione
Controllare se Ollama ha finito di scaricare il modello
kubectl logs -l app=ollama

Controllare i log di un agente specifico (es. E1)
kubectl logs -l app=mas-e1

Spegnere tutto e pulire Kubernetes
kubectl delete -f k8s/

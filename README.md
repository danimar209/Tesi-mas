<<<<<<< HEAD
Sistema Multi-Agente su Kubernetes (MAS-K8s)
Questo progetto implementa un sistema multi-agente per l'analisi scientifica utilizzando Kubernetes. Il sistema è composto da 4 agenti specializzati, un orchestrator (Job) e un servizio LLM locale (Ollama).

📋 Prerequisiti
Docker Desktop (con Kubernetes abilitato)

PowerShell (o terminale compatibile)

🚀 1. Prima Esecuzione Assoluta (Setup)
Questi comandi servono per costruire le immagini e avviare l'infrastruttura. Vanno eseguiti solo la prima volta o se modifichi il codice sorgente degli agenti.

A. Build delle Immagini Docker
Costruisci le immagini locali per tutti i componenti:

PowerShell

docker build -t mas-e1:v1 ./agent_e1
docker build -t mas-e2:v1 ./agent_e2
docker build -t mas-analyze:v1 ./agent_analyze
docker build -t mas-final:v1 ./agent_final
docker build -t mas-orchestrator:v1 ./orchestrator
B. Deploy su Kubernetes
Avvia tutti i servizi (Agenti, Ollama e Orchestrator):

PowerShell

kubectl apply -f k8s/
C. Monitoraggio Iniziale (Importante!)
La prima volta, il pod ollama impiegherà del tempo per scaricare il modello AI (diversi GB).

Controlla lo stato dei pod:

PowerShell

kubectl get pods
Attendi che tutti siano in stato Running.

Segui i log dell'orchestrator per vedere il progresso:

PowerShell

# Sostituisci con il nome reale del pod (es. orchestrator-job-xxxxx)
kubectl logs -f orchestrator-job-XXXXX
🔄 2. Esecuzioni Successive (Start Programma)
Una volta che il sistema è attivo, gli Agenti e Ollama restano sempre accesi in attesa (sono Deployments). Per far ripartire il processo di analisi, devi solo riavviare il "direttore d'orchestra" (Job).

Comandi per riavviare il task:
Lancia questi due comandi in sequenza:

PowerShell

# 1. Cancella il job completato/vecchio
kubectl delete job orchestrator-job

# 2. Crea un nuovo job per avviare una nuova analisi
kubectl apply -f k8s/
Visualizzare l'Output
Trova il nome del nuovo pod e leggi l'output:

PowerShell

# Trova il nome del nuovo pod (quello con AGE basso, pochi secondi)
kubectl get pods

# Leggi i risultati
kubectl logs -f orchestrator-job-NUOVO_NOME
🛠️ Comandi Utili di Manutenzione
Controllare se Ollama ha finito di scaricare il modello:

PowerShell

kubectl logs -l app=ollama
Controllare i log di un agente specifico (es. Agente E1): Se qualcosa va storto durante l'esecuzione, controlla l'agente che ha fallito:

PowerShell

kubectl logs -l app=mas-e1
Spegnere tutto e pulire: Se vuoi fermare il sistema e rimuovere tutto da Kubernetes:

PowerShell

kubectl delete -f k8s/
=======

>>>>>>> 5331396d86b8373a4119c8c5656a7d9f9e5ae1c1

# Sistema Multi-Agente su Kubernetes (MAS-K8s)

Questo progetto implementa un sistema multi-agente per l’analisi scientifica utilizzando Kubernetes.

**Il sistema è composto da:**
* **4 Agenti specializzati**
* Un **Orchestrator** (Job Kubernetes)
* Un servizio **LLM locale** basato su Ollama

## 📋 Prerequisiti

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (con Kubernetes abilitato nelle impostazioni)
* PowerShell o un terminale equivalente

---

## 🚀 1. Prima Esecuzione Assoluta (Setup)

Questi passaggi vanno eseguiti solo la prima volta, oppure quando modifichi il codice sorgente degli agenti e devi ricostruire le immagini Docker.

### A. Build delle Immagini Docker
Costruisci le immagini locali per ogni componente eseguendo questi comandi nella root del progetto:

```bash
docker build -t mas-e1:v1 ./agent_e1
docker build -t mas-e2:v1 ./agent_e2
docker build -t mas-analyze:v1 ./agent_analyze
docker build -t mas-final:v1 ./agent_final
docker build -t mas-orchestrator:v1 ./orchestrator

kubectl delete job orchestrator-job

kubectl get pods

kubectl apply -f k8s/


kubectl get pods

kubectl logs -f orchestrator-job-g2xzx

PS C:\Users\dani2\Desktop\tesi-mas-k8s> git add .
PS C:\Users\dani2\Desktop\tesi-mas-k8s> git commit -m "Aggiornamento codice e readme"

PS C:\Users\dani2\Desktop\tesi-mas-k8s> git push























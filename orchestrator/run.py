import requests
import json
import time
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

# --- URL AGGIORNATI PER KUBERNETES (DNS interno) ---
AGENT_E1_URL = "http://agent-e1-service:8000/invoke"
AGENT_E2_URL = "http://agent-e2-service:8000/invoke"
AGENT_ANALYZE_URL = "http://agent-analyze-service:8000/invoke"
AGENT_FINAL_URL = "http://agent-final-service:8000/invoke"
OLLAMA_URL = "http://ollama-service:11434" # Nota: ollama-service

TASK = """Due stati quantistici con energie E1 ed E2 hanno una vita media di 10^-9 sec e 10^-8 sec, rispettivamente. 
Vogliamo distinguere chiaramente questi due livelli di energia. 
Quale delle seguenti opzioni potrebbe essere la loro differenza di energia in modo che possano essere chiaramente risolti?
Choices: (A) 10^-9 eV, (B) 10^-11 eV, (C) 10^-8 eV, (D) 10^-4 eV"""

class GraphState(TypedDict):
    task: str
    e1_uncertainty: str
    e2_uncertainty: str
    analysis: str
    final_answer: str
    analysis_attempts: int
    max_attempts: int

# --- NODI AGENTE ---

def node_calc_e1(state: GraphState) -> dict:
    print("-> [PARALLELO] Chiamata a agent_e1...", flush=True)
    try:
        resp = requests.post(AGENT_E1_URL, json={"task": state['task']})
        resp.raise_for_status()
        return {"e1_uncertainty": resp.json()['output']}
    except Exception as e:
        print(f"Errore E1: {e}", flush=True)
        return {"e1_uncertainty": "Error"}

def node_calc_e2(state: GraphState) -> dict:
    print("-> [PARALLELO] Chiamata a agent_e2...", flush=True)
    try:
        resp = requests.post(AGENT_E2_URL, json={"task": state['task']})
        resp.raise_for_status()
        return {"e2_uncertainty": resp.json()['output']}
    except Exception as e:
        print(f"Errore E2: {e}", flush=True)
        return {"e2_uncertainty": "Error"}

def node_analyze(state: GraphState) -> dict:
    print("-> Chiamata a agent_analyze...", flush=True)
    payload = {
        "task": state['task'],
        "e1_uncertainty": state['e1_uncertainty'],
        "e2_uncertainty": state['e2_uncertainty']
    }
    resp = requests.post(AGENT_ANALYZE_URL, json=payload)
    return {"analysis": resp.json()['output'], "analysis_attempts": state['analysis_attempts'] + 1}

def node_final_answer(state: GraphState) -> dict:
    print("-> Chiamata a agent_final...", flush=True)
    resp = requests.post(AGENT_FINAL_URL, json={"analysis": state['analysis']})
    return {"final_answer": resp.json()['output']}

def node_router(state: GraphState) -> Literal["continue", "end"]:
    if state['analysis_attempts'] >= state['max_attempts']: return "end"
    if not state['analysis'] or len(state['analysis']) < 20: return "continue"
    return "end"

# --- NODO FORK PER PARALLELISMO ---
def node_fork(state: GraphState):
    # Questo nodo non fa nulla, serve solo come punto di partenza per i rami paralleli
    return

# --- HELPER ---
def wait_for_services():
    print("Attendo servizi...", flush=True)
    # (Logica di attesa semplificata per brevità, usa quella completa se preferisci)
    time.sleep(5) 

def pull_model():
    print("Richiesta download modello...", flush=True)
    try:
        requests.post(f"{OLLAMA_URL}/api/pull", json={"name": "llama3"})
        # Useremmo lo stream, qui semplifichiamo aspettando
        time.sleep(10) 
    except: pass

# --- MAIN ---
if __name__ == "__main__":
    wait_for_services()
    pull_model()
    
    workflow = StateGraph(GraphState)
    
    # Aggiungi nodi
    workflow.add_node("fork", node_fork)
    workflow.add_node("calc_e1", node_calc_e1)
    workflow.add_node("calc_e2", node_calc_e2)
    workflow.add_node("analyze", node_analyze)
    workflow.add_node("final_answer", node_final_answer)
    workflow.add_node("router", node_router)
    
    # --- DEFINIZIONE PARALLELISMO ---
    workflow.set_entry_point("fork")
    
    # Da 'fork' partono due frecce contemporaneamente
    workflow.add_edge("fork", "calc_e1")
    workflow.add_edge("fork", "calc_e2")
    
    # Entrambi i rami confluiscono in 'analyze' (JOIN)
    workflow.add_edge("calc_e1", "analyze")
    workflow.add_edge("calc_e2", "analyze")
    
    # Logica condizionale
    workflow.add_conditional_edges("analyze", node_router, {"continue": "analyze", "end": "final_answer"})
    workflow.add_edge("final_answer", END)
    
    app = workflow.compile()
    
    print("--- INIZIO GRAFO PARALLELO ---", flush=True)
    start_time = time.time()
    
    res = app.invoke({"task": TASK, "analysis_attempts": 0, "max_attempts": 2})
    
    
    end_time = time.time()
    print(f"--- FINE. Tempo totale: {end_time - start_time:.2f}s ---", flush=True)
    print(f"Risultato: {res['final_answer']}", flush=True)
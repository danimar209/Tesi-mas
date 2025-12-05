import pika
import uuid
import json
import time
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

# Configurazione RabbitMQ
RABBITMQ_HOST = 'rabbitmq-service'
RABBITMQ_USER = 'user'
RABBITMQ_PASS = 'password'

# Nomi delle Code
QUEUE_E1 = 'queue_e1'
QUEUE_E2 = 'queue_e2'
QUEUE_ANALYZE = 'queue_analyze'
QUEUE_FINAL = 'queue_final'

TASK = """Due stati quantistici con energie E1 ed E2 hanno una vita media di 10^-9 sec e 10^-8 sec, rispettivamente. 
Vogliamo distinguere chiaramente questi due livelli di energia. 
Quale delle seguenti opzioni potrebbe essere la loro differenza di energia in modo che possano essere chiaramente risolti?
Choices: (A) 10^-9 eV, (B) 10^-11 eV, (C) 10^-8 eV, (D) 10^-4 eV"""

# --- VARIABILI GLOBALI PER STATISTICHE ---
STATS = {
    "total_bytes_sent": 0,
    "total_bytes_received": 0,
    "total_messages": 0,
    "details": []
}

# --- CLIENT RABBITMQ RPC (STRUMENTATO) ---
class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.response = None
        self.corr_id = None
        self.connect()

    def connect(self):
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        while True:
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
                self.channel = self.connection.channel()
                result = self.channel.queue_declare(queue='', exclusive=True)
                self.callback_queue = result.method.queue
                self.channel.basic_consume(
                    queue=self.callback_queue,
                    on_message_callback=self.on_response,
                    auto_ack=True)
                return
            except Exception as e:
                print(f"   [!] Connessione RabbitMQ fallita, riprovo tra 2s...", flush=True)
                time.sleep(2)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, queue_name, payload_dict):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        
        # 1. Calcolo Byte Inviati
        body_json = json.dumps(payload_dict)
        bytes_sent = len(body_json.encode('utf-8'))
        
        print(f"   [MQ ->] Inviando a '{queue_name}' ({bytes_sent} bytes)...", flush=True)
        
        start_time = time.time() # Start Cronometro
        
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=body_json)
        
        # Attesa bloccante
        while self.response is None:
            self.connection.process_data_events(time_limit=None)
        
        end_time = time.time() # Stop Cronometro
        duration = end_time - start_time
        
        # 2. Calcolo Byte Ricevuti
        bytes_received = len(self.response)
        
        # 3. Aggiornamento Statistiche Globali
        STATS["total_bytes_sent"] += bytes_sent
        STATS["total_bytes_received"] += bytes_received
        STATS["total_messages"] += 1
        STATS["details"].append({
            "agent": queue_name,
            "duration": duration,
            "bytes_in": bytes_sent,
            "bytes_out": bytes_received
        })

        print(f"   [MQ <-] Risposta da '{queue_name}' ricevuta in {duration:.4f}s ({bytes_received} bytes)", flush=True)
        
        return json.loads(self.response)

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()

# --- LANGGRAPH STATE ---
class GraphState(TypedDict):
    task: str
    e1_uncertainty: str
    e2_uncertainty: str
    analysis: str
    final_answer: str
    analysis_attempts: int
    max_attempts: int

# --- NODI DEL GRAFO ---

def node_calc_e1(state: GraphState) -> dict:
    mq = RabbitMQClient()
    try:
        resp = mq.call(QUEUE_E1, {"task": state['task']})
        return {"e1_uncertainty": resp['output']}
    finally:
        mq.close()

def node_calc_e2(state: GraphState) -> dict:
    mq = RabbitMQClient()
    try:
        resp = mq.call(QUEUE_E2, {"task": state['task']})
        return {"e2_uncertainty": resp['output']}
    finally:
        mq.close()

def node_analyze(state: GraphState) -> dict:
    mq = RabbitMQClient()
    try:
        payload = {
            "task": state['task'],
            "e1_uncertainty": state['e1_uncertainty'],
            "e2_uncertainty": state['e2_uncertainty']
        }
        resp = mq.call(QUEUE_ANALYZE, payload)
        return {"analysis": resp['output'], "analysis_attempts": state['analysis_attempts'] + 1}
    finally:
        mq.close()

def node_final_answer(state: GraphState) -> dict:
    mq = RabbitMQClient()
    try:
        resp = mq.call(QUEUE_FINAL, {"analysis": state['analysis']})
        return {"final_answer": resp['output']}
    finally:
        mq.close()

def node_fork(state): return

def node_router(state: GraphState) -> Literal["continue", "end"]:
    if state['analysis_attempts'] >= state['max_attempts']: return "end"
    if not state['analysis'] or len(state['analysis']) < 20: return "continue"
    return "end"

# --- MAIN ---
def print_final_report(start_total, end_total):
    print("\n" + "="*50, flush=True)
    print("       REPORT ESECUZIONE ORCHESTRATORE       ", flush=True)
    print("="*50, flush=True)
    print(f"Tempo Totale Esecuzione: {end_total - start_total:.4f} secondi", flush=True)
    print(f"Messaggi Scambiati (RPC): {STATS['total_messages']}", flush=True)
    print(f"Totale Dati Inviati:      {STATS['total_bytes_sent']} bytes", flush=True)
    print(f"Totale Dati Ricevuti:     {STATS['total_bytes_received']} bytes", flush=True)
    print("-" * 50, flush=True)
    print(f"{'AGENTE':<20} | {'DURATA (s)':<10} | {'IN (byte)':<10} | {'OUT (byte)':<10}", flush=True)
    print("-" * 50, flush=True)
    for stat in STATS["details"]:
        print(f"{stat['agent']:<20} | {stat['duration']:<10.4f} | {stat['bytes_in']:<10} | {stat['bytes_out']:<10}", flush=True)
    print("="*50 + "\n", flush=True)

if __name__ == "__main__":
    print("--- AVVIO ORCHESTRATORE ---", flush=True)
    
    workflow = StateGraph(GraphState)
    workflow.add_node("fork", node_fork)
    workflow.add_node("calc_e1", node_calc_e1)
    workflow.add_node("calc_e2", node_calc_e2)
    workflow.add_node("analyze", node_analyze)
    workflow.add_node("final_answer", node_final_answer)
    workflow.add_node("router", node_router)
    
    workflow.set_entry_point("fork")
    workflow.add_edge("fork", "calc_e1")
    workflow.add_edge("fork", "calc_e2")
    workflow.add_edge("calc_e1", "analyze")
    workflow.add_edge("calc_e2", "analyze")
    workflow.add_conditional_edges("analyze", node_router, {"continue": "analyze", "end": "final_answer"})
    workflow.add_edge("final_answer", END)
    
    app = workflow.compile()
    
    start_time_total = time.time()
    res = app.invoke({"task": TASK, "analysis_attempts": 0, "max_attempts": 2})
    end_time_total = time.time()

    print_final_report(start_time_total, end_time_total)
    
    print(f"RISPOSTA FINALE: {res['final_answer']}", flush=True)
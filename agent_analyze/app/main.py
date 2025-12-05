import pika
import json
import os
import time
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- CONFIGURAZIONE AGENTE ANALISI ---
QUEUE_NAME = 'queue_analyze'

PROMPT_TEMPLATE = """Sei un analista di fisica.
Task: {task}
Opzioni: (A) 10^-9 eV, (B) 10^-11 eV, (C) 10^-8 eV, (D) 10^-4 eV

Calcolo Incertezza 1: {e1_uncertainty}
Calcolo Incertezza 2: {e2_uncertainty}

Sub-task:
1. Identifica quale incertezza (Delta E1 o Delta E2) è più grande. Questa è l'incertezza "dominante".
2. Spiega che per 'risolvere chiaramente' i livelli, la differenza di energia tra loro deve essere *significativamente maggiore* dell'incertezza dominante.
3. Confronta l'incertezza dominante con le opzioni (A, B, C, D).
4. Scegli l'unica opzione che è *significativamente maggiore* dell'incertezza dominante. Motiva la scelta."""

# --- CONFIGURAZIONE COMUNE ---
RABBITMQ_HOST = 'rabbitmq-service'
RABBITMQ_USER = 'user'
RABBITMQ_PASS = 'password'

llm = ChatOllama(
    model="llama3",
    base_url=os.environ.get("OLLAMA_BASE_URL"),
    temperature=0.0
)

def process_message(ch, method, props, body):
    print(f" [x] Ricevuto messaggio: {body}", flush=True)
    data = json.loads(body)
    
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    chain = prompt | llm | StrOutputParser()
    
    try:
        result = chain.invoke(data)
    except Exception as e:
        result = f"Error: {e}"

    response = {"output": result}

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id=props.correlation_id),
                     body=json.dumps(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(" [x] Risposta inviata", flush=True)

def main():
    print(f"Agente {QUEUE_NAME} avviato. Connessione a RabbitMQ...", flush=True)
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
            channel = connection.channel()
            break
        except Exception:
            print("RabbitMQ non pronto, riprovo tra 5s...", flush=True)
            time.sleep(5)

    channel.queue_declare(queue=QUEUE_NAME)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_message)

    print(f" [*] In attesa su coda '{QUEUE_NAME}'", flush=True)
    channel.start_consuming()

if __name__ == "__main__":
    main()
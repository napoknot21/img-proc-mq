import pika, json

from settings.config import RABBITMQ_SERVER, TASK_QUEUE
from rabbitmq_consumer import process_message
from settings.environment import load_environment_variables

def main():
    # Charger et valider les variables d'environnement
    load_environment_variables()

    # Connexion à RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER))
    channel = connection.channel()

    # Déclarer la queue
    channel.queue_declare(queue=TASK_QUEUE, durable=True)

    print(f"[*] Waiting for messages in {TASK_QUEUE}...")
    channel.basic_consume(queue=TASK_QUEUE, on_message_callback=process_message)
    channel.start_consuming()

if __name__ == "__main__":
    main()

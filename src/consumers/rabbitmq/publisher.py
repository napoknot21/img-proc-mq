import pika, json
from .connection import get_connection

def publish_result (queue_name, message):
    """Publie un message dans une queue."""
    connection = get_connection()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)

    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2)  # Message persistant
    )

    print(f"[+] Published result to queue {queue_name}: {message}")
    connection.close()

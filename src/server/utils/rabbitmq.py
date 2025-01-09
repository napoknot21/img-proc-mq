import pika
from config.config import RABBITMQ_SERVER

def get_rabbitmq_connection(server):
    """Create a connection to RabbitMQ."""
    print(f"[*] Connecting to RabbitMQ server at {server}...")
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(server))
        print("[*] Successfully connected to RabbitMQ.")
        return connection
    except Exception as e:
        print(f"[!] Failed to connect to RabbitMQ: {e}")
        raise


def publish_to_queue(server, queue_name, message):
    print(f"[*] we have this {server}")
    connection = get_rabbitmq_connection(server)
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)

    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=message,
        properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
    )
    connection.close()


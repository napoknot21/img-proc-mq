import json, pika
from rabbitmq.connection import get_channel


def publish_result (server, queue_name, message) :
    """
    Publishes a result message to the specified RabbitMQ queue.

    Args:
        server (str): RabbitMQ server address.
        queue_name (str): The name of the RabbitMQ queue.
        message (str): The message to publish.
    """
    try:

        connection, channel = get_channel(server)
        channel.queue_declare(queue=queue_name, durable=True)

        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)  # Persistent message
        )
        print(f"[+] Published result to queue '{queue_name}': {message}")
    
    except Exception as e :

        print(f"[-] Error publishing message: {e}")

    finally:
        connection.close()


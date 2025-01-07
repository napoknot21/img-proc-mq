import pika
from config.config import RABBITMQ_SERVER

def get_rabbitmq_connection(server):
    connection = pika.BlockingConnection(pika.ConnectionParameters(server))
    return connection

def publish_to_queue(server, queue_name, message):
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


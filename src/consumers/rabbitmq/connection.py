import pika
from settings.config import RABBITMQ_SERVER

def get_connection():
    """Crée une connexion à RabbitMQ."""
    return pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER))

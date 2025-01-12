import pika
import os, json
from PIL import Image
from io import BytesIO

from settings.config import *
from core.image_processor import compress_image
from rabbitmq.publisher import publish_result


def process_message(ch, method, properties, body):
    """
    Callback for processing a message from RabbitMQ.

    Args:
        ch (BlockingChannel): The RabbitMQ channel.
        method (Basic.Deliver): Delivery details for the message.
        properties (BasicProperties): Message properties.
        body (bytes): The message body.
    """
    message = json.loads(body)
    file_path = ROOT_STORAGE_FOLDER + message.get("file_path")

    if not file_path:

        print("\n[-] Invalid message received 1\n")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    try:
        
        print(f"\n[*] Processing file: {file_path}\n")
        compressed_path = compress_image(file_path)
        
        # Publier le résultat dans la queue
        result_message = json.dumps({
            "original_path": file_path,
            "compressed_path": compressed_path
        })

        publish_result(RABBITMQ_SERVER, RESULT_QUEUE, result_message)
        print(f"\n[+] Result sent to {RESULT_QUEUE}\n")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:

        print(f"\n[-] Failed to process file {file_path}: {e}\n")
        ch.basic_nack(delivery_tag=method.delivery_tag)

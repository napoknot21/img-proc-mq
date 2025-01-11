import pika
import os, json
from PIL import Image
from io import BytesIO

from settings.config import *
from image_processor import compress_image
from rabbitmq.publisher import publish_result


def process_message(ch, method, properties, body):
    """Callback pour traiter un message depuis RabbitMQ."""
    message = json.loads(body)
    file_path = message.get("file_path")
    if not file_path:
        print("[!] Invalid message received")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    try:
        print(f"[*] Processing file: {file_path}")
        compressed_path = compress_image(file_path)
        
        # Publier le résultat dans la queue
        result_message = json.dumps({
            "original_path": file_path,
            "compressed_path": compressed_path
        })

        publish_result(RESULT_QUEUE, result_message)
        print(f"[*] Result sent to {RESULT_QUEUE}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[!] Failed to process file {file_path}: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)

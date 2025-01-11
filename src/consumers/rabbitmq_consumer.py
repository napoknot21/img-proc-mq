import json, pika
from image_processor import ImageProcessor
from rabbitmq.publisher import publish_result
from settings.config import *

def process_message(ch, method, properties, body):
    """Callback pour traiter un message depuis RabbitMQ."""
    message = json.loads(body)
    file_path = message.get("file_path")
    if not file_path:
        print("[-] Invalid message received")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    try:
        print(f"[*] Processing file: {file_path}")

        processor = ImageProcessor(COMPRESSION_QUALITY, OUTPUT_FORMAT)
        compressed_data = processor.compress_image(file_path)

        result_message = json.dumps({
            "original_path": file_path,
            "compressed_data": compressed_data.hex()
        })
        publish_result(RESULT_QUEUE, result_message)
        print(f"\n[+] Result sent to {RESULT_QUEUE}\n")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"\n[-] Failed to process file {file_path}: {e}\n")
        ch.basic_nack(delivery_tag=method.delivery_tag)

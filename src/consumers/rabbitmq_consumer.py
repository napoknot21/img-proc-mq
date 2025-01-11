import json
from image_processor import ImageProcessor
from rabbitmq.publisher import publish_result
from settings.config import RESULT_QUEUE

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

        processor = ImageProcessor()
        compressed_data = processor.compress_image(file_path)

        result_message = json.dumps({
            "original_path": file_path,
            "compressed_data": compressed_data.hex()
        })
        publish_result(RESULT_QUEUE, result_message)
        print(f"[*] Result sent to {RESULT_QUEUE}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[!] Failed to process file {file_path}: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)

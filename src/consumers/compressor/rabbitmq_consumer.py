import json
from PIL import Image
from io import BytesIO
from config.settings import RESULT_QUEUE, COMPRESSION_QUALITY, OUTPUT_FORMAT
from utils.rabbitmq import publish_result

def compress_image(input_path):
    """Compresse une image et retourne le fichier compressé en mémoire."""
    image = Image.open(input_path)
    compressed_image = BytesIO()
    image.save(compressed_image, format=OUTPUT_FORMAT, quality=COMPRESSION_QUALITY)
    compressed_image.seek(0)
    return compressed_image.getvalue()

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
        compressed_data = compress_image(file_path)
        
        # Publier le résultat dans la queue
        result_message = json.dumps({
            "original_path": file_path,
            "compressed_data": compressed_data.hex()  # Convertir les données binaires en hexadécimal
        })
        publish_result("rabbitmq", RESULT_QUEUE, result_message)
        print(f"[*] Result sent to {RESULT_QUEUE}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[!] Failed to process file {file_path}: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)
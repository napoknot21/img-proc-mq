import os, json, pika
from PIL import Image
from io import BytesIO

from utils.rabbitmq import publish_result

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/app/uploads")
RESULT_QUEUE = os.getenv("RESULT_QUEUE", "result_queue")

def compress_image(input_path):
    """Compresse une image et retourne le fichier compressé en mémoire."""
    image = Image.open(input_path)
    compressed_image = BytesIO()
    image.save(compressed_image, format="JPEG", quality=85)
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

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
    channel = connection.channel()
    channel.queue_declare(queue="image_tasks", durable=True)
    print("[*] Waiting for messages...")
    channel.basic_consume(queue="image_tasks", on_message_callback=process_message)
    channel.start_consuming()

if __name__ == "__main__":
    main()

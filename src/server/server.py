import os, json, pika
from flask import Flask, request, jsonify
from io import BytesIO
from threading import Thread

from utils.rabbitmq import publish_to_queue
from utils.file_handler import allowed_file, save_file
from config.config import *

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"message": "File type not allowed"}), 400

    # Sauvegarder l'image dans le dossier uploads
    file_path = save_file(file)

    # Publier le chemin de l'image dans RabbitMQ
    task_message = json.dumps({
        "file_path": file_path,
        "action": "compress"
    })
    publish_to_queue(RABBITMQ_SERVER, TASK_QUEUE, task_message)

    return jsonify({"message": "File uploaded successfully", "file_path": file_path}), 200


def listen_to_results():
    """Écoute la queue des résultats pour récupérer les images compressées."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER))
    channel = connection.channel()
    channel.queue_declare(queue=RESULT_QUEUE, durable=True)

    def callback(ch, method, properties, body):
        message = json.loads(body)
        original_path = message["original_path"]
        compressed_data = bytes.fromhex(message["compressed_data"])  # Convertir hex en binaire

        # Sauvegarder l'image compressée dans `downloads/`
        compressed_path = os.path.join(app.config['DOWNLOAD_FOLDER'], f"compressed_{os.path.basename(original_path)}")
        with open(compressed_path, "wb") as f:
            f.write(compressed_data)
        
        print(f"[*] Compressed image saved to {compressed_path}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=RESULT_QUEUE, on_message_callback=callback)
    channel.start_consuming()


# Lancer l'écoute des résultats dans un thread séparé
Thread(target=listen_to_results, daemon=True).start()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT_FLASK)

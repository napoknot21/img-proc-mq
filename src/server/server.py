import os
import json
import pika
from flask import Flask, request, jsonify, send_file
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
    """Handle image upload and send to RabbitMQ."""
    if 'image' not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"message": "File type not allowed"}), 400

    # Save the uploaded image
    file_path = save_file(file)

    # Publish the task to RabbitMQ
    task_message = json.dumps({
        "file_path": file_path,
        "action": "compress"
    })
    publish_to_queue(RABBITMQ_SERVER, TASK_QUEUE, task_message)

    return jsonify({"message": "File uploaded successfully", "file_path": file_path}), 200


@app.route('/status', methods=['GET'])
def check_status():
    """Check if the compressed image is ready."""
    file_name = request.args.get('file_name')
    if not file_name:
        return jsonify({"message": "File name is missing"}), 400

    compressed_path = os.path.join(app.config['DOWNLOAD_FOLDER'], f"compressed_{os.path.basename(file_name)}")
    if os.path.exists(compressed_path):
        return jsonify({
            "status": "completed",
            "download_url": f"/download?file_name=compressed_{os.path.basename(file_name)}"
        }), 200
    else:
        return jsonify({"status": "processing"}), 200


@app.route('/download', methods=['GET'])
def download_file():
    """Allow client to download the compressed image."""
    file_name = request.args.get('file_name')
    if not file_name:
        return jsonify({"message": "File name is missing"}), 400

    file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], file_name)
    if not os.path.exists(file_path):
        return jsonify({"message": "File not found"}), 404

    return send_file(file_path, as_attachment=True)


def listen_to_results():
    """Listen to the result queue for compressed images."""
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER))
        channel = connection.channel()
        channel.queue_declare(queue=RESULT_QUEUE, durable=True)

        def callback(ch, method, properties, body):
            try:
                message = json.loads(body)
                original_path = message["original_path"]
                compressed_data = bytes.fromhex(message["compressed_data"])  # Convert hex to binary

                # Save the compressed image in the downloads folder
                compressed_path = os.path.join(
                    app.config['DOWNLOAD_FOLDER'], f"compressed_{os.path.basename(original_path)}"
                )
                with open(compressed_path, "wb") as f:
                    f.write(compressed_data)

                print(f"[*] Compressed image saved to {compressed_path}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                print(f"[!] Error processing message: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        channel.basic_consume(queue=RESULT_QUEUE, on_message_callback=callback)
        channel.start_consuming()
    except pika.exceptions.AMQPConnectionError as e:
        print(f"[!] Failed to connect to RabbitMQ: {e}")
    except Exception as e:
        print(f"[!] Unexpected error in listen_to_results: {e}")


# Launch the listener for results in a separate thread
Thread(target=listen_to_results, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT_FLASK)

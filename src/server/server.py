"""
Distributed Image Processing Server
-----------------------------------

This module implements a Flask-based server that handles image upload, 
compression, and retrieval using RabbitMQ for task distribution and 
processing.

Endpoints:
    - `/upload` (POST): Accepts an image file for processing.
    - `/status` (GET): Checks the status of the compressed image.
    - `/download` (GET): Downloads the processed (compressed) image.

RabbitMQ:
    - Publishes tasks to the `TASK_QUEUE`.
    - Consumes results from the `RESULT_QUEUE`.

Global Variables:
    - `UPLOAD_FOLDER`: Directory for storing uploaded images.
    - `DOWNLOAD_FOLDER`: Directory for storing compressed images.
    - `RABBITMQ_SERVER`: Address of the RabbitMQ server.
    - `TASK_QUEUE`: Name of the queue for task distribution.
    - `RESULT_QUEUE`: Name of the queue for processing results.

Dependencies:
    - Flask
    - Flask-CORS
    - pika
    - PIL (Pillow)
"""
import os, json, pika

from flask import Flask, request, jsonify, send_file, url_for
from flask_cors import CORS
from threading import Thread

from utils.rabbitmq import publish_message, consume_messages
from utils.file_handler import allowed_file, save_file
from config.config import *

# Flask app configuration
app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

# Ensure required folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


@app.route('/upload', methods=['POST'])
def upload_image () :
    """
    Endpoint to upload an image for processing.
    
    This endpoint validates the uploaded image, saves it in the `UPLOAD_FOLDER`, 
    and sends a task message to RabbitMQ for processing.

    Returns:
        JSON response with the upload status and file path.
        - 200: Successful upload.
        - 400: Missing or invalid file.
    """
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

    publish_message(RABBITMQ_SERVER, TASK_QUEUE, task_message)
    
    return jsonify({"message": "File uploaded successfully", "file_path": file_path}), 200



@app.route('/status', methods=['GET'])
def check_status () :
    """
    Endpoint to check the processing status of an image.
    
    This endpoint checks if the compressed image exists in the `DOWNLOAD_FOLDER`.
    If processed, it provides a download link; otherwise, it indicates 
    that the image is still being processed.

    Query Parameters:
        - file_name (str): The name of the original image file.

    Returns:
        JSON response with the processing status:
        - "completed": Includes a download link.
        - "processing": Indicates that the image is still being processed.
        - 400: Missing file name.
    """
    file_name = request.args.get('file_name')

    if not file_name:
        return jsonify({"message": "File name is missing"}), 400

    compressed_path = os.path.join(app.config['DOWNLOAD_FOLDER'], f"compressed_{os.path.basename(file_name)}")
    
    if os.path.exists(compressed_path):

        download_url = url_for('download_file', file_name=f"compressed_{os.path.basename(file_name)}", _external=True)
        return jsonify({
            "status": "completed",
            "download_url": download_url
        }), 200

    else:
        return jsonify({"status": "processing"}), 200



@app.route('/download', methods=['GET'])
def download_file () :
    """
    Endpoint to download the processed (compressed) image.
    
    This endpoint serves the compressed image from the `DOWNLOAD_FOLDER` as a file download.

    Query Parameters:
        - file_name (str): The name of the compressed image file.

    Returns:
        - The image file as an attachment (200).
        - 404: If the file does not exist.
        - 400: If the file name is missing.
    """
    file_name = request.args.get('file_name')
    
    if not file_name:
        print("[-] Error: File name is missing")
        return jsonify({"message": "File name is missing"}), 400

    file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], file_name)
    
    if not os.path.exists(file_path):
        print(f"[-] Error: Compressed file not found: {file_path}")
        return jsonify({"message": "File not found"}), 404

    print("[+] Downloading compressed image: {file_path}...")
    return send_file(file_path, as_attachment=True)



def listen_to_results () :
    """
    Background thread to listen to the RabbitMQ result queue.
    
    This function consumes messages from the `RESULT_QUEUE` and processes the results:
        - Saves the compressed image in the `DOWNLOAD_FOLDER`.
        - Logs success or failure for each message.
    """
    def process_result (ch, method, properties, body) :
        
        try:
            
            message = json.loads(body)
            original_path = message["original_path"]
            compressed_path = message["compressed_path"]

            if os.path.exists(compressed_path):
                print(f"[*] Compressed image saved: {compressed_path}")
            else:
                print(f"[-] Compressed file not found: {compressed_path}")

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:

            print(f"[-] Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    consume_messages(RABBITMQ_SERVER, RESULT_QUEUE, process_result)



# Start listening in a separate thread
Thread(target=listen_to_results, daemon=True).start()



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT_FLASK)

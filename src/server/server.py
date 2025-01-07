from flask import Flask, request, jsonify
import os
import json
from utils.rabbitmq import publish_to_queue
from utils.file_handler import allowed_file, save_file
from config.config import RABBITMQ_SERVER, QUEUE_NAME, UPLOAD_FOLDER

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_image():
    # Check if a file is included in the request
    if 'image' not in request.files:
        return jsonify({"message": "No file part"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"message": "File type not allowed"}), 400

    # Save the file locally
    file_path = save_file(file)

    # Publish the task to RabbitMQ
    task_message = json.dumps({"file_path": file_path, "action": "process"})
    publish_to_queue(RABBITMQ_SERVER, QUEUE_NAME, task_message)

    return jsonify({"message": "File uploaded successfully", "task_id": file_path}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


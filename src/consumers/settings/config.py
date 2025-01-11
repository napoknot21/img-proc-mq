import os

# RabbitMQ settings
RABBITMQ_SERVER = os.getenv("RABBITMQ_SERVER", "rabbitmq")
TASK_QUEUE = os.getenv("TASK_QUEUE", "image_tasks")
RESULT_QUEUE = os.getenv("RESULT_QUEUE", "result_queue")

# Compression settings
COMPRESSION_QUALITY = 85
OUTPUT_FORMAT = "JPEG"

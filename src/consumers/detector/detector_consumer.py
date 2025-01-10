import pika
import json

def process_message(ch, method, properties, body):
    message = json.loads(body)
    file_path = message.get("file_path")

    print(f"[*] Detecting objects in: {file_path}")
    detection_result = {"file_path": file_path, "objects_detected": ["cat", "dog"]}

    # Publier dans results_queue
    connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
    channel = connection.channel()
    channel.queue_declare(queue="results_queue", durable=True)
    channel.basic_publish(
        exchange='',
        routing_key="results_queue",
        body=json.dumps(detection_result),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()

    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
    channel = connection.channel()
    channel.queue_declare(queue="detection_tasks", durable=True)

    print("[*] Waiting for messages in detection_tasks. To exit press CTRL+C")
    channel.basic_consume(queue="detection_tasks", on_message_callback=process_message)
    channel.start_consuming()

if __name__ == "__main__":
    main()

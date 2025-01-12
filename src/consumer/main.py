import pika, json

from rabbitmq.connection import get_channel
from settings.config import RABBITMQ_SERVER, TASK_QUEUE
from settings.environment import load_environment_variables
from core.compressor_consumer import process_message

def main () :
    """
    Main entry point for the RabbitMQ consumer.
    - Loads environment variables.
    - Establishes a RabbitMQ connection.
    - Starts consuming messages from the task queue.
    """
    # Load and validate environment variables
    load_environment_variables()

    # Get channel and declare queue
    connection, channel = get_channel(RABBITMQ_SERVER)
    channel.queue_declare(queue=TASK_QUEUE, durable=True)

    print(f"[*] Waiting for messages in {TASK_QUEUE}...")

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=TASK_QUEUE, on_message_callback=process_message)
    
    try:

        channel.start_consuming()

    except KeyboardInterrupt:

        print("\n[-] Consumer stopped manually. Bye !\n")

    finally:

        connection.close()


if __name__ == "__main__":
    main()

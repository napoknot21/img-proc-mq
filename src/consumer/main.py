import pika, json

from rabbitmq.connection import get_channel
from settings.config import RABBITMQ_SERVER, TASK_QUEUE
from settings.environment import load_environment_variables
from core.compressor_consumer import process_message

def main () :
    """
    Entry point for the RabbitMQ consumer application.
    
    This function initializes the environment, connects to RabbitMQ, and starts 
    consuming messages from the specified task queue. Messages are processed 
    using the callback function `process_message`.

    Steps:
        1. Load and validate environment variables.
        2. Establish a connection to RabbitMQ.
        3. Declare the task queue and configure basic QoS.
        4. Start consuming messages from the task queue.

    Raises:
        KeyboardInterrupt: Handles manual interruption by the user to gracefully
                           stop the consumer.

    Prints:
        - Confirmation of successful RabbitMQ connection.
        - A message indicating the consumer is waiting for tasks.
        - A message when the consumer is manually stopped.

    Environment Variables:
        - RABBITMQ_SERVER: Address of the RabbitMQ server.
        - TASK_QUEUE: Name of the task queue to consume messages from.
    
    Notes:
        The `process_message` callback function is used to handle each message 
        received from the queue. RabbitMQ channels and connections are closed 
        gracefully upon termination.

    Example:
        To run the consumer:
        $ python main.py
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

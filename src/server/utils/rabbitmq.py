import pika

def get_rabbitmq_connection (server) :
    """
    Create and return a connection to RabbitMQ.
    Args:
        server (str): RabbitMQ server address.
    Returns:
        pika.BlockingConnection: RabbitMQ connection instance.
    """
    try :
        connection = pika.BlockingConnection(pika.ConnectionParameters(server))
        
        print(f"[+] Successfully connected to {server}")
        return connection

    except Exception as e :

        print(f"[-] Failed to connect to RabbitMQ: {e}")
        raise



def publish_message (server, queue_name, message) :
    """
    Publish a message to a specified RabbitMQ queue.
    Args:
        server (str): RabbitMQ server address.
        queue_name (str): The name of the RabbitMQ queue.
        message (str): The message to publish.
    """
    try :
        connection = get_rabbitmq_connection(server)
        
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent  # Make the message persistent
            )
        )
        
        print(f"[+] Message published to {queue_name}")
        connection.close()
        
    except Exception as e :

        print(f"[-] Error publishing message: {e}")
        raise



def consume_messages (server, queue_name, callback) :
    """
    Consume messages from a RabbitMQ queue with a callback function.
    Args:
        server (str): RabbitMQ server address.
        queue_name (str): The name of the RabbitMQ queue.
        callback (function): Callback function to process messages.
    """
    try:

        connection = get_rabbitmq_connection(server)

        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)

        print(f"[*] Waiting for messages in {queue_name}...")
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=queue_name, on_message_callback=callback)
        channel.start_consuming()

    except Exception as e:

        print(f"[-] Error consuming messages: {e}")
        raise
        

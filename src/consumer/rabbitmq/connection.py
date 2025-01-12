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
        
        print(f"\n[+] Successfully connected to {server}\n")
        return connection

    except Exception as e :

        print(f"\n[-] Failed to connect to RabbitMQ: {e}\n")
        raise



def get_channel (server) :
    """
    Establishes a connection and returns a RabbitMQ channel.

    Returns:
        (connection, channel): The connection and channel objects.
    """
    connection = get_rabbitmq_connection(server)
    channel = connection.channel()

    return connection, channel
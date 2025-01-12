import os
from settings.config import RABBITMQ_SERVER, TASK_QUEUE, RESULT_QUEUE

def load_environment_variables():
    """
    Validate that all required environment variables are set and not empty.

    Environment Variables:
        - RABBITMQ_SERVER: Address of the RabbitMQ server.
        - TASK_QUEUE: Name of the RabbitMQ task queue.
        - RESULT_QUEUE: Name of the RabbitMQ result queue.

    Raises:
        EnvironmentError: If any required environment variable is missing or empty.

    Prints:
        Confirmation that all required environment variables are set.
    """
    required_env_vars = {
        "RABBITMQ_SERVER": RABBITMQ_SERVER,
        "TASK_QUEUE": TASK_QUEUE,
        "RESULT_QUEUE": RESULT_QUEUE
    }

    for var_name, var_value in required_env_vars.items():
        if not var_value:
            raise EnvironmentError(f"[-] Missing or empty environment variable: {var_name}")

    print("[*] All required environment variables are set.")

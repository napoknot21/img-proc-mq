import os
from settings.config import RABBITMQ_SERVER, TASK_QUEUE, RESULT_QUEUE

def load_environment_variables():
    """Charge et valide les variables d'environnement requises."""
    required_env_vars = {
        "RABBITMQ_SERVER": RABBITMQ_SERVER,
        "TASK_QUEUE": TASK_QUEUE,
        "RESULT_QUEUE": RESULT_QUEUE
    }

    for var_name, var_value in required_env_vars.items():
        if not var_value:
            raise EnvironmentError(f"[-] Missing or empty environment variable: {var_name}")

    print("[*] All required environment variables are set.")

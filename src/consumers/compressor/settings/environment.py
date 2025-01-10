import os

def load_environment_variables():
    """Charge et valide les variables d'environnement requises."""
    required_env_vars = ["RABBITMQ_SERVER", "TASK_QUEUE", "RESULT_QUEUE"]
    for var in required_env_vars:
        if var not in os.environ:
            raise EnvironmentError(f"Missing required environment variable: {var}")

    print("[*] All required environment variables are set.")


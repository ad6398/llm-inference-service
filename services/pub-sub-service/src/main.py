import yaml
from loguru import logger
import pika
from publisher import publish_message
from subscriber import start_consuming

# Load configuration
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

RABBITMQ_HOST = config["rabbitmq"]["host"]
RABBITMQ_QUEUE = config["rabbitmq"]["queue"]

def main():
    logger.info("Starting Pub-Sub Service")

    # Start RabbitMQ subscriber
    start_consuming(RABBITMQ_HOST, RABBITMQ_QUEUE)

if __name__ == "__main__":
    main()

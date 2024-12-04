import pika
from loguru import logger
import time

def publish_message(rabbitmq_host, queue_name, message):
    """
    Publishes a single message to RabbitMQ.
    """
    try:
        # Connect to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
        channel = connection.channel()

        # Ensure the queue exists
        channel.queue_declare(queue=queue_name, durable=True)

        # Publish the message
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)  # Make the message persistent
        )
        time.sleep(1)

        logger.info(f"Published message to queue '{queue_name}': {message}")
    except Exception as e:
        logger.error(f"Failed to publish message: {e}")
    finally:
        connection.close()

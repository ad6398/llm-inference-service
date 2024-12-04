import pika
from loguru import logger
import time

def callback(ch, method, properties, body):
    """
    Callback function to process a plain string message from RabbitMQ.
    """
    try:
        # Decode the message from bytes to string
        message = body.decode()
        print(f"Processing message: {message}")

        # Acknowledge the message after successful processing
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("Message acknowledged successfully!")
    except Exception as e:
        print(f"Error processing message: {e}")
        # Optionally reject the message without requeuing
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def start_consuming(rabbitmq_host, queue_name):
    """
    Sets up RabbitMQ consumer to listen for messages on the given queue.
    """
    try:
        # Connect to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
        channel = connection.channel()

        # Ensure the queue exists
        channel.queue_declare(queue=queue_name, durable=True)

        # Set up message consumption
        channel.basic_qos(prefetch_count=1)  # Limit unacknowledged messages
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=False  # Explicit acknowledgment required
        )

        time.sleep(2)

        logger.info(f"Waiting for messages in queue: {queue_name}...")
        channel.start_consuming()
    except Exception as e:
        logger.error(f"Error in subscriber: {e}")
    finally:
        connection.close()

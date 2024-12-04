from publisher import publish_message

# RabbitMQ host and queue name
RABBITMQ_HOST = "localhost"
QUEUE_NAME = "task_queue"

# Example messages
messages = [
    f"Message {i}: Hello, RabbitMQ! This is test message {i}."
    for i in range(1, 11)  # Generate 10 messages
]

# Publish each message
for message in messages:
    publish_message(RABBITMQ_HOST, QUEUE_NAME, message)
    print(f"Published: {message}")

print("All messages have been sent successfully!")

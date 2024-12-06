import pika
import json
from sqlalchemy import create_engine, Column, String, Table, MetaData

# Database Configuration
POSTGRES_USER = "cml-user"
POSTGRES_PASSWORD = "cml-is-cool"
POSTGRES_DB = "result-db"
DB_HOST = "db-service"
DB_PORT = 5432

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define the table structure
jobs_table = Table(
    "jobs",
    metadata,
    Column("job_id", String, primary_key=True),
    Column("result", String),
)
# Create the table if it doesn't exist
metadata.create_all(engine)

# RabbitMQ Configuration
RMQ_HOST = "rabbitmq-service"
RMQ_PORT = 5672
QUEUE_NAME = "task_queue"

def connect_to_rabbitmq():
    """Establish a RabbitMQ connection and channel."""
    try:
        connection_params = pika.ConnectionParameters(
            host=RMQ_HOST,
            port=RMQ_PORT,
            heartbeat=30,  # Send heartbeats every 30 seconds
            blocked_connection_timeout=300  # Timeout for blocked connections
        )
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        return connection, channel
    except Exception as e:
        print(f"Error connecting to RabbitMQ: {str(e)}")
        raise

# Establish RabbitMQ connection
# connection = pika.BlockingConnection(pika.ConnectionParameters(host=RMQ_HOST, port=RMQ_PORT))
# channel = connection.channel()
# channel.queue_declare(queue=QUEUE_NAME)

connection, channel = connect_to_rabbitmq()

def process_task(ch, method, properties, body):
    """
    Callback function to process tasks from RabbitMQ.
    """
    try:
        task = json.loads(body)  # Parse the task from RabbitMQ
        job_id = task["job_id"]
        prompt = task.get("prompt", "default prompt")  # Extract prompt (if any)

        # Simulate processing (inference) with a dummy result
        generated_text = f"Processed prompt: {prompt}"

        # Store the result in the database
        with engine.connect() as conn:
            conn.execute(jobs_table.insert().values(job_id=job_id, result=generated_text))

        print(f"Processed job_id: {job_id}, Result: {generated_text}")

    except Exception as e:
        print(f"Error processing task: {e}")

# Set up RabbitMQ consumer
channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_task, auto_ack=True)

print("Waiting for tasks. To exit, press CTRL+C")
channel.start_consuming()

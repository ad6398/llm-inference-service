import pika
import json
from vllm import LLM, SamplingParams
from sqlalchemy import create_engine, Column, String, Table, MetaData

# Configure the SQL database
DATABASE_URL = "postgresql://user:password@db-service/dbname"
engine = create_engine(DATABASE_URL)
metadata = MetaData()
jobs_table = Table(
    "jobs",
    metadata,
    Column("job_id", String, primary_key=True),
    Column("result", String),
)
metadata.create_all(engine)

# Configure RabbitMQ connection
RMQ_HOST = "rabbitmq-service"
RMQ_PORT = 5672
QUEUE_NAME = "task_queue"

connection = pika.BlockingConnection(pika.ConnectionParameters(host=RMQ_HOST, port=RMQ_PORT))
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME)

# Initialize the LLM
llm = LLM(model="facebook/opt-125m")
sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

def process_task(ch, method, properties, body):
    """Callback to process incoming tasks."""
    task = json.loads(body)
    job_id = task["job_id"]
    prompt = task["prompt"]

    # Perform inference
    outputs = llm.generate([prompt], sampling_params)
    generated_text = outputs[0].outputs[0].text

    # Store results in the database
    with engine.connect() as conn:
        conn.execute(jobs_table.insert().values(job_id=job_id, result=generated_text))
    
    print(f"Processed job_id: {job_id}, Result: {generated_text}")

# Consume messages
channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_task, auto_ack=True)
print("Waiting for tasks. To exit, press CTRL+C")
channel.start_consuming()

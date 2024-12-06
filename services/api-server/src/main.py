from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pika
import json
import uuid
from sqlalchemy import create_engine, Table, MetaData, select
import time

# Database configuration
DATABASE_URL = "postgresql://cml-user:cml-is-cool@db-service:5432/result-db"
engine = create_engine(DATABASE_URL)
metadata = MetaData()
jobs_table = Table(
    "jobs",
    metadata,
    autoload_with=engine
)

# RabbitMQ configuration
RMQ_HOST = "rabbitmq-service"
RMQ_PORT = 5672
QUEUE_NAME = "task_queue"

# FastAPI application
app = FastAPI()

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


# Initialize RabbitMQ connection and channel
connection, channel = connect_to_rabbitmq()

def ensure_channel():
    """Ensure RabbitMQ channel is open, retry if closed."""
    global connection, channel
    retries = 5  # Number of retries
    delay = 2  # Delay in seconds between retries

    for attempt in range(retries):
        try:
            if connection.is_closed or channel.is_closed:
                print(f"Retrying RabbitMQ connection... Attempt {attempt + 1}/{retries}")
                connection, channel = connect_to_rabbitmq()
            return channel
        except Exception as e:
            print(f"Failed to reconnect to RabbitMQ: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise HTTPException(status_code=500, detail="Could not reconnect to RabbitMQ after multiple attempts.")

# Define request and response models
class ChatRequest(BaseModel):
    text: str

class StatusResponse(BaseModel):
    job_id: str
    status: str
    result: str = None

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Accepts a prompt from the user, creates a job_id, queues it in RabbitMQ,
    and returns the job_id.
    """
    try:
        job_id = str(uuid.uuid4())
        task = {"job_id": job_id, "prompt": request.text}

        # Ensure RabbitMQ channel is open
        channel = ensure_channel()

        # Send task to RabbitMQ
        channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=json.dumps(task))

        return {"job_id": job_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending task to RabbitMQ: {str(e)}")

@app.get("/status/{job_id}", response_model=StatusResponse)
async def status(job_id: str):
    """
    Checks the status of the job by querying the database.
    If the job result is found, it returns the result.
    Otherwise, it indicates that the job is still processing.
    """
    try:
        with engine.connect() as conn:
            query = select(jobs_table).where(jobs_table.c.job_id == job_id)
            result = conn.execute(query).fetchone()

        if result:
            return {"job_id": job_id, "status": "completed", "result": result["result"]}
        else:
            return {"job_id": job_id, "status": "processing"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying the database: {str(e)}")

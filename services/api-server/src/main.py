from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pika
import json
import uuid
from sqlalchemy import create_engine, Table, MetaData, select

# Database configuration
DATABASE_URL = "postgresql://user:password@db-service/dbname"
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

# RabbitMQ connection setup
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RMQ_HOST, port=RMQ_PORT))
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME)

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
    job_id = str(uuid.uuid4())
    task = {"job_id": job_id, "prompt": request.text}

    # Send task to RabbitMQ
    channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=json.dumps(task))

    return {"job_id": job_id}


@app.get("/status/{job_id}", response_model=StatusResponse)
async def status(job_id: str):
    """
    Checks the status of the job by querying the database.
    If the job result is found, it returns the result.
    Otherwise, it indicates that the job is still processing.
    """
    with engine.connect() as conn:
        query = select(jobs_table).where(jobs_table.c.job_id == job_id)
        result = conn.execute(query).fetchone()

    if result:
        return {"job_id": job_id, "status": "completed", "result": result["result"]}
    else:
        return {"job_id": job_id, "status": "processing"}


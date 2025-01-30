# Distributed LLM Inference Service

## Introduction
The project aims to design and deploy a scalable, efficient cloud-based inference service for large language models (LLMs) using Kubernetes on Google Cloud. Leveraging vLLM, an open-source library for optimizing LLMs, the service addresses challenges in memory consumption and latency.

---

## Prerequisites
Before proceeding, ensure you have:
- A Google Cloud Platform (GCP) account
- `gcloud` CLI installed and authenticated
- `kubectl` CLI installed and configured
- Docker installed and configured to push images to a container registry

---

## Deployment Steps

### 1. Setup GKE Cluster
Create a GKE cluster on GCP and authenticate with:
```sh
 gcloud container clusters get-credentials final-project --region us-central1 --project cml-finals
```

### 2. Verify Kubernetes Deployments and Services
Check existing deployments and services:
```sh
kubectl get deployments
kubectl get svc
```

### 3. Deploy Database Service
```sh
cd db-service
kubectl apply -f deployment-db.yaml
kubectl apply -f service-db.yaml
```

### 4. Deploy Pub-Sub Service
```sh
cd pub-sub-service/deployment
kubectl apply -f deployment-pub-sub.yaml
kubectl apply -f service-pub-sub.yaml
```

### 5. Test Database Service and RabbitMQ
Ensure both services are running before proceeding.

### 6. Install NVIDIA GPU API (If Required)
```sh
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.13.0/nvidia-device-plugin.yml
```

### 7. Build and Deploy LLM Service
```sh
cd llm-service
docker build . -t ad060398/llm-service --no-cache --platform=linux/amd64
docker push ad060398/llm-service
kubectl apply -f deployment/deployment-llm-service.yaml
kubectl apply -f deployment/service-llm-service.yaml
```

### 8. Build and Deploy API Server
```sh
cd api-server
docker build . -t ad060398/api-server --no-cache --platform=linux/amd64
docker push ad060398/api-server
kubectl apply -f deployment/deployment-api-server.yaml
kubectl apply -f deployment/service-api-server.yaml
```

### 9. Verify Running Services
```sh
kubectl get pods  # List running pods
kubectl logs <pod_name>  # View logs for a specific pod
kubectl get svc  # List services
```

### 10. Send API Requests
Retrieve the external IP of the API server from `kubectl get svc` and use it to test the service:
```sh
curl -X POST http://<external-ip>/chat \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello, LLM!"}'

curl http://<external-ip>/status/<job_id>
```

---

## Performance Testing
### 1. Run Load Test with Locust
```sh
locust load_test.py
```
### 2. Open Locust UI
Access Locust dashboard via:
```sh
http://localhost:8089
```
Configure and start the test from the web interface.

---

## Conclusion
Following these steps will set up and deploy all services required for the project. Ensure each service is running correctly before proceeding to the next step. If you encounter issues, use `kubectl logs` and `kubectl describe` to debug any deployment errors.



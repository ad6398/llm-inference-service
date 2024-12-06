# llm-inference-service
An efficient LLM inference service

1. Setup a GKE cluster on GCP
2. gcloud container clusters get-credentials final-project --region us-central1 --project cml-finals
3. kubectl get deployments
4. kubectl get svc
5. DB service
   1. cd db-service
   2. kubectl apply -f deployment-db.yaml
   3. kubectl apply -f service-db.yaml
6. Pub-Sub service
   1. cd pub-sub-service/deployment
   2. kubectl apply -f deployment-pub-sub.yaml
   3. kubectl apply -f service-pub-sub.yaml
7. Test db-service and rmq
8. Build llm service
   1. cd llm-service
   2. docker build . -t ad060398/llm-service --no-cache --platform=linux/amd64
   3. docker push ad060398/llm-service
   4. kubectl apply -f deployment/deployment-llm-service.yaml
   5. kubectl apply -f deployment/service-llm-service.yaml
9. Build api-server
   1. cd api-server
   2. docker build . -t ad060398/api-server --no-cache --platform=linux/amd64
   3. docker push ad060398/api-server
   4. kubectl apply -f deployment/deployment-api-server.yaml
   5. kubectl apply -f deployment/service-api-server.yaml

10. Above steps should run all the services. list pods using kubectl get pods and look at logs using kubectl logs <pod_name>
11. List services using kubectl get svc and it will show external ip of api-server service. Use it to send request as below
        1. curl -X POST http://<external-ip>/chat \
				-H "Content-Type: application/json" \
				-d '{"text": "Hello, LLM!"}'
		2. curl http://<external-ip>/status/<job_id>



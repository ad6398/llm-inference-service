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
7. Test db-service

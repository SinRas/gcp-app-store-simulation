# --- Configuration Variables (REPLACE THESE) ---
export PROJECT_ID="PLACEHOLDER-GCP-PROJECT-ID"  # $(gcloud config get-value project)
export BUCKET_NAME="PLACEHOLDER-GCS-BUCKET-NAME"
export REGION="PLACEHOLDER-REGION"  # Assuming same region for all services
export AR_REPO="PLACEHOLDER-AR-REPO"
export PUBSUB_TOPIC_NAME="PLACEHOLDER-PUBSUB-TOPIC-NAME"

# --- Docker Image ---
export IMAGE_TAG=${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}/gcs-publisher:v1


# --- Pub/Sub Topic ---
export PUBSUB_TOPIC="projects/${PROJECT_ID}/topics/${PUBSUB_TOPIC_NAME}"


###################################################
# --- Build and Push Image ---
docker build -t ${IMAGE_TAG} .
docker push ${IMAGE_TAG}


# --- Kubectl ---
kubectl apply -f publisher-deployment.yaml
kubectl delete -f publisher-deployment.yaml
kubectl get pods
kubectl scale deployment appstore-publisher-deployment --replicas=0
kubectl scale deployment appstore-publisher-deployment --replicas=2
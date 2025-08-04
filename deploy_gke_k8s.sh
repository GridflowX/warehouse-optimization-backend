#!/bin/bash

# Exit on error
set -e
source .env
# Set your Google Cloud project ID here
PROJECT_ID= $PROJECT_ID

# Services and paths
services=("mainbackend" "guidewayoptimization" "packageandretrievaloptimization" "wtpalletsoptimization")
folders=("MainBackend" "GuideWayOptimization" "PackageAndRetrievalOptimization" "WtPalletsOptimization")

# Authenticate Docker with GCR
echo "Authenticating Docker with GCR..."
gcloud auth configure-docker

# Build, tag, and push to GCR
echo "Building, tagging, and pushing Docker images to GCR..."
for i in "${!services[@]}"; do
  svc=${services[$i]}
  dir=${folders[$i]}
  echo "Building $svc from ./$dir"
  docker build -t gcr.io/$PROJECT_ID/$svc:latest ./$dir
  echo "Pushing gcr.io/$PROJECT_ID/$svc:latest"
  docker push gcr.io/$PROJECT_ID/$svc:latest
done

# Update deployment YAMLs with GCR image paths
echo "Updating deployment YAMLs with GCR image paths..."
for svc in "${services[@]}"; do
  yaml_file="${svc}-deployment.yaml"
  if [[ -f "$yaml_file" ]]; then
    echo "Updating image in $yaml_file"
    sed -i.bak -E "s|image: .*|image: gcr.io/${PROJECT_ID}/${svc}:latest|" "$yaml_file"
  else
    echo "$yaml_file not found"
  fi
done

# Apply YAMLs to Kubernetes
echo "Deploying to GKE..."
kubectl apply -f .

echo "Done! Run 'kubectl get pods' to check pod status."

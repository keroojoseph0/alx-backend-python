#!/bin/bash

# Check if minikube is installed
if ! command -v minikube &> /dev/null
then
    echo "Minikube is not installed. Please install minikube first."
    exit 1
fi

# Show minikube version
minikube version

# Start Kubernetes cluster
minikube start

# Verify cluster is running
kubectl cluster-info

# Retrieve available pods
kubectl get pods -A

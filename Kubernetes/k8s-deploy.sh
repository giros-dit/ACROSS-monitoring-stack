#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

# Create kind cluster
#kind create cluster

# Create ConfigMap from the configuration file config.json
kubectl create configmap config-json --from-file=config/config.json

# Create ConfigMap for test metrics files
TEST_FILES=""
for file in $SCRIPT_DIR/config/test_metrics/*; do
    TEST_FILES+=" --from-file=$file"
done
kubectl create configmap test-metrics-configmap $TEST_FILES

kubectl create configmap ml-config --from-file=config/ml-config/ml-config.txt


# Install Cert-Manager and FlinKubernetes/scripts/flink-test.shk Operator
#kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.8.1/cert-manager.yaml
#kubectl wait --for=condition=available --timeout=600s deployment/cert-manager -n cert-manager
#kubectl wait --for=condition=available --timeout=600s deployment/cert-manager-webhook -n cert-manager
#kubectl wait --for=condition=available --timeout=600s deployment/cert-manager-cainjector -n cert-manager

#kubectl apply -f https://github.com/spotify/flink-on-k8s-operator/releases/download/v0.5.1-alpha.3/flink-operator.yaml
#kubectl wait --for=condition=available --timeout=600s deployment/flink-operator-controller-manager -n flink-operator-system

# Load docker images into kind cluster
IMAGES=(
    "mariovicente/router-node-exporter"
    "mariovicente/node-exporter-collector"
    "mariovicente/kafka-producer"
    "mariovicente/flink-operator"
    "mariovicente/ml"
)
#for image in "${IMAGES[@]}"; do
#    kind load docker-image "$image:latest"
#done

# Deployments for NDT Data Fabric and Node Exporter Collector
kubectl apply -f ./templates/node-exporter-collector.yaml
kubectl apply -f ./templates/zookeeper.yaml
kubectl apply -f ./templates/kafka.yaml
kubectl wait --for=condition=ready --timeout=600s pod -l service=kafka-broker

# Create Kafka topics
chmod +x ./scripts/create-topics-kafka.sh
./scripts/create-topics-kafka.sh

# Deploy Telegraf agent
#kubectl apply -f ./templates/telegraf.yaml

# Deploy Apache Flink Operator Cluster
kubectl apply -f ./templates/flink-cluster.yaml

# Deploy Flink Job submitters and Machine Learning Dummies for each router
ROUTERS=$(jq -r '.routers[] | keys[]' config/config.json)
for router in $ROUTERS; do
    kubectl apply -f "./templates/jobs/flink-job-submitter-${router}.yaml"
    kubectl apply -f "./templates/ml/ml-${router}.yaml"
    kubectl wait --for=condition=complete --timeout=600s "job/flink-job-submitter-test-${router}"
done

#kubectl wait --for=condition=available --timeout=600s deployment/telegraf

# Deploy Kafka producer microservice in order to start the telemetry system
kubectl apply -f ./templates/kafka-producer.yaml
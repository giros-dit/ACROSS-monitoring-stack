#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

for ((i=1; i<=50; i++))
do
    kubectl apply -f ./templates/jobs/flink-job-submitter-r1.yaml
    kubectl wait --for=condition=complete --timeout=600s "job/flink-job-submitter-test-r1"
    kubectl delete job/flink-job-submitter-test-r1
done
# kafka producer - Dockerfile.

# The base image is Ubuntu 22.04 LTS ("jammy").
FROM ubuntu:jammy

# Some labels are defined to store metadata.
LABEL image_version="1.0.1"
LABEL app_version="1.0.1"

LABEL author="Mario Vicente Albertos"
LABEL maintainer="mariov22 <mario.vicente.albertos@alumnos.upm.es>"
LABEL description="Docker image for kafka producer microservice."

# Variables to automatically install/update tzdata.
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Madrid

# Update base image with new packages.
RUN apt-get update && apt-get dist-upgrade -y && apt-get autoremove -y && apt-get autoclean

# Install some basic tools and dependencies.
RUN apt-get install -y --no-install-recommends bash python3 python3-pip openssl net-tools wget curl iputils-ping

# Install Python dependencies/requirements using PIP.
COPY ./requirements.txt .
RUN python3 -m pip install -r requirements.txt

# Create application's directory and copy the script.
RUN mkdir -p /kafka_producer
COPY * /kafka_producer

# Switch to application's directory as main WORKDIR.
WORKDIR /kafka_producer


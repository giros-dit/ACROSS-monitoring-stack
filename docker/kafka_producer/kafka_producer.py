#!/usr/bin/env python
from kafka import KafkaProducer
import requests
import json
import time
import os

 # Configuración de Kafka Producer que envia las métricas de prometheus-node-exporter-collector a Kafka
producer = KafkaProducer(
	# Endpoint del broker de Kafka (dirección del servidor Kafka) escuchando las métricas que se envían al bus
	bootstrap_servers = ['kafka:9092'],
	# Transformar los datos json que devuelve node-exporter-collector a binarios Kafka
	value_serializer = lambda v: json.dumps(v).encode('utf-8'),
	# key_serializer = lambda k: str(k).encode('utf-8')
	acks = 'all'
	# retries = 2
)

 # Extraer las métricas de los endpoints que expone node-exporter-collector dada la url de un exporter
def scrape_metrics(node_exporter_collector_url):
	try:
	 	 # Petición HTTP GET a prometheus-node-exporter-collector
		response = requests.get(node_exporter_collector_url)
	 	 # Comprobar que la petición HTTP GET se realizó correctamente
		response.raise_for_status()
		return response.json()
	except requests.exceptions.RequestException as e:
		print("Error al realizar las peticiones a {node_exporter_collector_url}: {e}")
		return None

 # Filtrar las métricas en función de las interfaces de red de interés
def filter_device(metric):
	# Filtrar en el array de métricas las pertenecientes a la interfaz de red de interés
	#filtered_devices = [
	#	{
	#		"labels": value["labels"],
	#		"value": value["value"]
	#	}
	#	for value in metric.get('values', [])
	#	if any(label["name"] == "device" and label["value"] == "eth4" for label in value.get("labels", []))
		# ¡¡TODO!!: Filtrar varias interfaces de interés en los equipos de red
	#]
	filtered_devices = [
		value for value in metric.get('values', [])
	]
	# Devuelve las métricas filtradas en funcion de la interfaz de red
	return{
		"name": metric["name"],
		"description": metric.get("description", ""),
		"type": metric.get("type", ""),
		"values": filtered_devices
	}
	
# ¡¡TODO!!: Realizar la función de agregación para todas las métricas de interés
network_metrics = [
	"node_network_receive_bytes_total",
	"node_network_receive_packets_total",
	"node_network_transmit_bytes_total",
	"node_network_transmit_packets_total"
]

 # Filtrar las métricas extraidas de prometheus-node-exporter-collector
def filter_metrics(metrics):
 # Comprobar que las métricas se han extraído correctamente
	if metrics:
		 # Extraer los campos que indican el exporter objetivo y el timestamp de las métricas extraídas
		node_exporter = metrics.get('node_exporter')
		epoch_timestamp = metrics.get('epoch_timestamp')
		 # Filtrar las métricas que se envían a kafka ('node_network')
		filtered_metrics = [
			filter_device(metric) for metric in metrics.get('metrics', [])
			if metric['name'] in network_metrics
		]
		 # Crear un nuevo json con el node-exporter objetivo, el timestamp de las métricas y las métricas filtradas
		return {
			'node_exporter': node_exporter,
			'epoch_timestamp': epoch_timestamp,
			'metrics': filtered_metrics
		}
	else:
		return None

 # Mandar las métricas extraídas de prometheus-node-exporter-collector a Kafka
def kafka_metrics(metrics, topic):
	try:
	 	 # Enviar las métricas a Kafka con su correspondiente 'topic'
		producer.send(topic, metrics)
	 	 # Comprobar que las métricas se envían inmediatamente
		producer.flush()
		print("Métricas enviadas a Kafka con topic: {topic} correctamente")
	except Exception as e:
		print("Error al enviar las métricas a Kafka: {e}")
	
 # Función principal que envía las métricas que recoge de prometheus-node-exporter-collector a Kafka
def main():
	node_exporter_collector_urls = [
		os.getenv('COLLECTOR_EXPORTER_1'),
		os.getenv('COLLECTOR_EXPORTER_2')
	]
	 # Crear un topic por cada nodo de la red
	kafka_topic_1 = os.getenv('KAFKA_TOPIC_1')
	kafka_topic_2 = os.getenv('KAFKA_TOPIC_2')
	
	while True:
		for url in node_exporter_collector_urls:
			print(url)
			metrics = scrape_metrics(url)
			if metrics:
				filtered_metrics = filter_metrics(metrics)
				if filtered_metrics and filtered_metrics['metrics']:
					if url == node_exporter_collector_urls[0]:
						kafka_metrics(filtered_metrics, kafka_topic_1)
					# ¡¡TODO!!: Diferneciar las métricas que se publican en kafka para cada node exporter
					if url == node_exporter_collector_urls[1]:
						kafka_metrics(filtered_metrics, kafka_topic_2)
		time.sleep(1)

if __name__ == "__main__":
	main()
			

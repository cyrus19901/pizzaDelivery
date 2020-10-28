import pika
import json
import random
import time
import uuid
from datetime import datetime

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='rpc_queue')

def makePizza(ch,method,props,pizzaDetails):
	orderId = uuid.uuid4()
	responsePayload = {'orderId': str(orderId),
						'pizzaType':pizzaDetails['pizzaType'],
						'pizzaQuantity':pizzaDetails['pizzaType'],
						'price':pizzaDetails['price'],
						'notes':pizzaDetails['notes'],
						'readyAt' : getTimestamp()}

	print(str(responsePayload))

	ch.basic_publish(exchange='',
					routing_key='completed_order',
					properties=pika.BasicProperties(
					reply_to='rpc_queue',
					correlation_id=str("completed"),
					),
					body=str(responsePayload))
	ch.basic_ack(delivery_tag=method.delivery_tag)

def on_request(ch, method, props, body):
	payload = json.loads(body.decode('utf-8'))
	if payload == None:
		print("Something went wrong")
	else:
		user =  payload['user']['name']
		print("New order received for : " + user )
		print("Order received at : " + getTimestamp()) 
		makeTime = random.randint(20,30)
		print("Estimated wait time : "+ str(makeTime) + 'mins')
		makePizza(ch,method,props,payload['order'])

def getTimestamp():
	now = datetime.now()
	current_time = now.strftime("%H:%M:%S")
	return current_time

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)

print(" [x] Awaiting RPC requests")
channel.start_consuming()
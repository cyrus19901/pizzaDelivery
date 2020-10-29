import pika
import json
import random
import time
import uuid
import threading
from datetime import datetime
queue = {}

class PizzaMakingService(object):

	def __init__(self):
		self.connection = pika.BlockingConnection(
			pika.ConnectionParameters(host='localhost'))
		self.channel = self.connection.channel()
		result = self.channel.queue_declare('rpc_queue', exclusive=True)
		self.callback_queue = result.method.queue
		self.channel.basic_qos(prefetch_count=1)
		self.channel.basic_consume(
			queue='rpc_queue',
			on_message_callback=self.on_request,auto_ack=True)
		print(" [x] Awaiting RPC requests")
		self.channel.start_consuming()

	def on_response(self, ch, method, props, body):
		self.response = body

	def call(self, payload,queueName):
		self.response = None
		self.corr_id = str(uuid.uuid4())
		queue[self.corr_id] = None
		self.channel.basic_publish(
			exchange='',
			routing_key=queueName,
			properties=pika.BasicProperties(
				reply_to=self.callback_queue,
				correlation_id=self.corr_id,
			),
			body=json.dumps(payload))
		while self.response is None:
			self.connection.process_data_events()
		queue[self.corr_id] = self.response
		return self.response
			
	def makePizza(self,ch,method,props,pizzaDetails):
		time.sleep(random.randint(20,30))
		orderId = uuid.uuid4()
		responsePayload = {'orderId': str(orderId),
							'name': pizzaDetails['user']['name'],
							'pizzaType':pizzaDetails['order']['pizzaType'],
							'pizzaQuantity':pizzaDetails['order']['quantity'],
							'price':pizzaDetails['order']['price'],
							'notes':pizzaDetails['order']['notes'],
							'readyAt' : self.getTimestamp()}
		self.channel.queue_declare('completed_order')
		self.corr_id = str(uuid.uuid4())
		self.channel.basic_publish(
			exchange='',
			routing_key='completed_order',
			properties=pika.BasicProperties(
				reply_to='completed_order',
				correlation_id=self.corr_id,
			),
			body=json.dumps(responsePayload))

	def on_request(self ,ch, method, props, body):
		payload = json.loads(body.decode('utf-8'))
		if payload == None:
			print("Something went wrong")
		else:
			user =  payload['user']['name']
			print("New order received for : " + user )
			print("Order received at : " + self.getTimestamp()) 
			makeTime = random.randint(20,30)
			print("Estimated wait time : "+ str(makeTime) + 'mins')
			self.makePizza(ch,method,props,payload)

	def getTimestamp(self):
		now = datetime.now()
		current_time = now.strftime("%H:%M:%S")
		return current_time

PizzaMakingService()

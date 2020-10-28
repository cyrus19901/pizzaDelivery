from flask import Flask, render_template,request
import pika
import json
import uuid
import threading
app = Flask(__name__)
queue = {}


class PizzaRpcClient(object):

	def __init__(self):
		self.connection = pika.BlockingConnection(
			pika.ConnectionParameters(host='localhost'))
		self.channel = self.connection.channel()
		self.orderNumber =0
		result = self.channel.queue_declare('', exclusive=True)
		self.callback_queue = result.method.queue
		self.channel.basic_consume(
			queue=self.callback_queue,
			on_message_callback=self.on_response,
			auto_ack=True)


	def resp(self):
		self.channel = self.connection.channel()
		self.channel.basic_consume(
			queue='completed_order',
			on_message_callback=self.on_response,
			auto_ack=True)

	def on_response(self, ch, method, props, body):
		print(body)
		if self.corr_id == props.correlation_id:
			self.response = body

	def on_request(ch, method, props, body):
		print("here")
		payload = json.loads(body.decode('utf-8'))
		print(payload)

	def call(self, payload,queueName):
		self.response = None
		self.corr_id = str(uuid.uuid4())
		queue[self.corr_id] = None
		self.orderNumber += 1
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

	# def call2(self):
	# 	newResult = self.channel.queue_declare(queue='completed_order')
	# 	callback_queue = newResult.method.queue
	# 	print(callback_queue)
	# 	self.channel.basic_consume(
	# 		queue=callback_queue,
	# 		on_message_callback=self.on_request,
	# 		auto_ack=True)


@app.route("/getStatus",methods=['GET', 'POST'])
def send_results():
	newOrder_rpc = PizzaRpcClient()
	threading.Thread(target=newOrder_rpc.resp).start()
	return render_template("home.html")

@app.route('/',methods=['GET', 'POST'])
def index():
	return render_template("home.html")

@app.route('/newOrder', methods=['GET', 'POST'])
def createOrder():
	payload = request.json
	newOrder_rpc = PizzaRpcClient()
	threading.Thread(target=newOrder_rpc.call, args=(payload,'rpc_queue')).start()
	return render_template("home.html")

if __name__ == '__main__':
    app.run(debug=True)
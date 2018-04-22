# /usr/bin/env python
import re
from flask import Flask, request, url_for, jsonify
from celery import Celery
from celery.utils.log import get_task_logger
from celery.signals import celeryd_init
from twilio.twiml.messaging_response import MessagingResponse

# used for async tcp server
import asyncore
import socket
import logging


flask_app = Flask(__name__)
flask_app.config['SECRET_KEY'] = 'top-secret!'

# Celery configuration
flask_app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
flask_app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# Celery object
celery = Celery(flask_app.name, broker=flask_app.config['CELERY_BROKER_URL'])
celery.conf.update(flask_app.config)
celery_logger = get_task_logger(flask_app.name)

"""
@app.route('/status')
def taskstatus():
	task = run_pic_server.AsyncResult(app.config['SERVER_TASK_ID'])
	if task.state == 'PENDING':
		response = {
			'state': task.state,
			'current': 0,
			'total': 1,
			'status': 'Pending...'
		}
	elif task.state != 'FAILURE':
		response = {
			'state': task.state,
			'current': task.info.get('current', 0),
			'total': task.info.get('total', 1),
			'status': task.info.get('status', '')
		}
		if 'result' in task.info:
			response['result'] = task.info['result']
	else:
		# something went wrong in the background job
		response = {
			'state': task.state,
			'current': 1,
			'total': 1,
			'status': str(task.info),  # this is the exception raised
		}
	return jsonify(response)
"""

@flask_app.route("/", methods=['GET','POST'])
def sms_service_request():
	"""Respond to incoming messages with a friendly SMS."""
		
#   recvd_msg = request.form['Body']

#   # Start our response
#   resp = MessagingResponse()

#   in_dic = actions.get(recvd_msg)
#   
#   # if command is present in dictionary
#   if (in_dic == None):
#	   action_msg = "I only understand the following commands: " + str(actions.keys())
#   else:
#	   action_msg = actions[recvd_msg]()

#   # Add a message
#   resp.message("Ahoy! Thanks so much for your message. " + action_msg)

	#pic_server = run_pic_server.AsyncResult(app.config['SERVER_TASK_ID'])
	#water_lvl = pic_server.result
	resp = "sms_service!"

	return str(resp)

def sms_ahoy_reply():
	return "waterPIC will keep your plants moisty and tasty"

def plant_status():
	return "plants are alright"

def water_chili():
	return "watering chili plant!"

actions = { "Hi"	 : sms_ahoy_reply,   \
			"Status" : plant_status,	 \
			"Water chili" : water_chili }


@celery.task(bind=True)
def run_pic_server(self):
	"""Background task that runs a the tcp server that connects to the plant watering units."""
	
	logging.basicConfig(level=logging.DEBUG, format='%(name)s:[%(levelname)s]: %(message)s')
	HOST = "192.168.1.72"
	PORT = 1112
	self.update_state(state='PROGRESS',
						  meta={'current': 0, 'total': 100,
								'status': "started"})
	s = PICServer((HOST,PORT), self)
	self.config['SERVER_HANDLE'] = s
	celery_logger.info("Starting server")
	asyncore.loop()
	return {'status': 'Closed server!'}


"""Server stuff"""
class PICServer(asyncore.dispatcher):
	def __init__(self, address, updater):
		asyncore.dispatcher.__init__(self)
		self.logger = logging.getLogger('PICServer')
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.set_reuse_addr()
		self.bind(address)
		self.address = self.socket.getsockname()
		self.updater = updater								# Used for information passing through redis
		self.logger.debug('binding to %s', self.address)
		self.listen(5)
		self.clients = dict()

	def dummy():
		self.clients['1'].data_to_write.insert(0, "Status")

	def handle_accept(self):
		# Called when a client connects to our socket
		client_info = self.accept()
		if client_info is not None:
			self.logger.debug('handle_accept() -> %s', client_info[1])
			#print('handle_accept() -> %s' % client_info[1])
			ch = ClientHandler(client_info[0], client_info[1], self.clients)
	

class ClientHandler(asyncore.dispatcher):
	def __init__(self, sock, address, clients_dic):
		asyncore.dispatcher.__init__(self, sock)
		self.logger = logging.getLogger('Client ' + str(address))
		self.data_to_write = []
		self.name = "no name"
		self.clients_dic = clients_dic


	def id_ready(self):
		return self.got_id

	def handler_name(self):
		return self.name

	def writable(self):
		return bool(self.data_to_write)

	def handle_write(self):
		data = self.data_to_write.pop()
		sent = self.send(data[:1024])
		if sent < len(data):
			remaining = data[sent:]
			self.data.to_write.append(remaining)
		self.logger.debug('handle_write() -> (%d) "%s"', sent, data[:sent].rstrip())
		print('handle_write() -> (%d) "%s"' % (sent, data[:sent].rstrip()))

	def handle_read(self):
		data = self.recv(1024)
		self.logger.debug('handle_read() -> (%d) "%s"', len(data), data.rstrip())
		print('handle_read() -> (%d) "%s"' % (len(data), data.rstrip()))
		if (data == "Connected to PIC"):
			self.data_to_write.insert(0, "Hello!")
		elif (re.search('PICy', data)):
			m = re.search('PICy #(.+?)', data)
			self.name = m.group(1)
			self.clients_dic[self.name] = self
	
	def handle_close(self):
		self.logger.debug('handle_close()')
		self.close()
""" End server stuff"""



if __name__ == "__main__":
	task = run_pic_server.apply_async()
	flask_app.config['SERVER_TASK_ID'] = task.id
	flask_app.run(debug=False)

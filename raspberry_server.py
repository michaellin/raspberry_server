#!/usr/bin/env python
''' Async TCP server to make first tests of newly received GPS trackers '''

import asyncore
import socket
import logging
import redis
import threading
import time
import Queue

class Server(asyncore.dispatcher):
	def __init__(self, address, redis_handlr):
		asyncore.dispatcher.__init__(self)
		self.logger = logging.getLogger('Server')
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.set_reuse_addr()
		self.bind(address)
		self.address = self.socket.getsockname()
		self.logger.debug('binding to %s', self.address)
		self.listen(5)
		self.r = redis_handlr
		self.p_recv = self.r.pubsub()
		self.p_recv.subscribe('to_broadcast')
		self.connections = []
		#self.con_count = 0

	def writable(self):
		msg = self.p_recv.get_message()
		if (msg):
			data = msg['data']
			self.logger.debug(data)
			for c in self.connections:
				c.data_to_write.append(msg)
			if (data == "status"):
				r.publish('broadcast_rsp', 'all good')

	def handle_accept(self):
		# Called when a client connects to our socket
		client_info = self.accept()
		if client_info is not None:
			self.logger.debug('handle_accept() -> %s', client_info[1])
			#ClientHandler(client_info[0], client_info[1], self.clients, str(self.con_count))
			ch = ClientHandler(client_info[0], client_info[1])
			self.connections.append(ch)
	

class ClientHandler(asyncore.dispatcher):
	#def __init__(self, sock, address, clients_dic, handler_id):
	def __init__(self, sock, address):
		asyncore.dispatcher.__init__(self, sock)
		self.logger = logging.getLogger('Client ' + str(address))
		self.data_to_write = []
	
	def writable(self):
		return bool(self.data_to_write)

	def handle_write(self):
		data = self.data_to_write.pop()
		sent = self.send(data[:1024])
		if sent < len(data):
			remaining = data[sent:]
			self.data.to_write.append(remaining)
		self.logger.debug('handle_write() -> (%d) "%s"', sent, data[:sent].rstrip())

	def handle_read(self):
		data = self.recv(1024)
		self.logger.debug('handle_read() -> (%d) "%s"', len(data), data.rstrip())
		self.data_to_write.insert(0, data)
	
	def handle_close(self):
		self.logger.debug('handle_close()')
		self.close()

def main(redis_handlr):
	logging.basicConfig(level=logging.DEBUG, format='%(name)s:[%(levelname)s]: %(message)s')
	HOST = "192.168.1.72"
	PORT = 1112
	s = Server((HOST,PORT), redis_handlr)
	asyncore.loop(timeout = 0.5)

if __name__ == '__main__':
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
####p = r.pubsub()
####p.subscribe(**{'hi': handlr})
	main(r)
####server = threading.Thread(target=main, args=[r])
####server.daemon = True
####server.start()
####while(True):
####	time.sleep(1)
####	print("hi")

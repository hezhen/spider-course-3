import hashlib

from socket_server import ServerSocket
import protocol_constants as pc
import json
import time
from thread import *
from pymongo import MongoClient

import networkx as nx

import signal
import sys


constants = {
	'reorder_period': 1200, # 20 mins
	'connection_lost_period': 30, # 30s
}

class CrawlMaster:
	clients = {}

	server_status = pc.STATUS_RUNNING

	last_rereoder_time = time.time()

	is_reordering = False

	def __init__(self, mongo_host='localhost'):
		self.mongo_client = MongoClient(mongo_host, 27017)
		self.db = self.mongo_client.spider
		self.server = ServerSocket(self.on_message)
		self.server.start()

	def on_message(self, msg):
		# print 'Heart Beat request' + msg
		request = json.loads(msg)
		type = request[pc.MSG_TYPE]
		client_state = {}
		response = {}
		response[pc.SERVER_STATUS] = self.server_status
		if type == pc.REGISTER:
			client_id = self.get_free_id()
			client_state['status'] = pc.STATUS_RUNNING
			client_state['time'] = time.time()
			self.clients[client_id] = client_state
			print client_id + ' registerd'
			return client_id
		elif type == pc.UNREGISTER:
			client_id = request.get(pc.CLIENT_ID)
			del self.clients[client_id]
			print client_id + ' unregisterd'
			return json.dumps(response)
		
		client_id = request.get(pc.CLIENT_ID)

		if client_id is None:
			response[pc.ERROR] = pc.ERR_NOT_FOUND
			return json.dumps(response)
		print client_id + ' heartbeat msg: ' + type
		if type == pc.HEARTBEAT:
			if self.server_status is not self.clients[client_id]['status']:
				if self.server_status == pc.STATUS_RUNNING:
					response[pc.ACTION_REQUIRED] = pc.RESUME_REQUIRED
				elif self.server_status == pc.STATUS_PAUSED:
					response[pc.ACTION_REQUIRED] = pc.PAUSE_REQUIRED
				elif self.server_status == pc.STATUS_SHUTDOWN:
					response[pc.ACTION_REQUIRED] = pc.SHUTDOWN_REQUIRED
				return json.dumps(response)
		else:
			client_state['status'] = type
			client_state['time'] = time.time()
			self.clients[client_id] = client_state

		return json.dumps(response)

	def get_free_id(self):
		i = 0
		for key in self.clients:
			if i < int(key):
				break
			i += 1
		return str(i)


	def reorder_queue(self):
		g = nx.DiGraph()
		cursor = self.db.urlpr.find()
		for site in cursor:
			url = site['url']
			links = site['links']
			for link in links:
				g.add_edge(url, link)
		pageranks = nx.pagerank(g, 0.9)
		for url, pr in pageranks.iteritems():
			print 'updating %s pr: %f' % (url, pr)
			record = {'pr': pr}
			self.db.mfw.update_one({'_id': hashlib.md5(url).hexdigest()}, {'$set': record}, upsert=False)


	def periodical_check(self):
		clients_status_ok = True

		if self.is_reordering is False and time.time() - self.last_rereoder_time > constants['reorder_period']:
			self.server_status = pc.STATUS_PAUSED
			self.is_reordering = True
		
		for cid, state in self.clients.iteritems():
			# no heart beat for 2 mins, remove it
			if time.time() - state['time'] > constants['connection_lost_period']:
				# remove it from client list 
				# del client[cid]
				# set client status to be CONNECTION_LIST
				self.clients[cid]['status'] = pc.STATUS_CONNECTION_LOST
				continue

			if state['status'] != self.server_status:
				clients_status_ok = False
				break

		if clients_status_ok and self.server_status == pc.STATUS_PAUSED and self.is_reordering:
			self.reorder_queue()
			self.last_rereoder_time = time.time()
			is_reordering = False
			self.server_status = pc.STATUS_RUNNING


crawl_master = CrawlMaster()

start_new_thread(crawl_master.periodical_check, ())

def exit_signal_handler(signal, frame):
	crawl_master.server.close()
	sys.exit(1)
signal.signal(signal.SIGINT, exit_signal_handler)
signal.pause()